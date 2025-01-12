from ortools.sat.python import cp_model
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScheduleGenerator:
    def __init__(self, level, year, section, rooms, teachers):
        self.level = level
        self.year = year
        self.section = section
        self.rooms = rooms
        self.teachers = teachers
        self.schedule = []
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.teacher_map = {teacher['name']: idx for idx, teacher in enumerate(self.teachers)}
        self.teacher_map["No teacher available"] = len(self.teachers)
        self.num_teachers = len(self.teachers) + 1

    def get_assigned_room(self):
        prefix = "MS_Room_" if self.level == "middle_school" else "HS_Room_"
        for room in self.rooms:
            if room['name'] == f"{prefix}{self.section['section']}":
                return room['name']
        logger.error(f"No room assigned to section {self.section['section']}")
        return None

    def time_slots(self, slot):
        return {
            1: {"start": "8:00", "end": "9:00"},
            2: {"start": "9:00", "end": "10:00"},
            3: {"start": "10:00", "end": "11:00"},
            4: {"start": "11:00", "end": "12:00"},
            5: {"start": "13:30", "end": "14:30"},
            6: {"start": "14:30", "end": "15:30"},
            7: {"start": "15:30", "end": "16:30"},
            8: {"start": "16:30", "end": "17:30"}
        }.get(slot, {"start": "Unknown", "end": "Unknown"})

    def find_suitable_teacher(self, subject_name):
        suitable = [
            teacher for teacher in self.teachers
            if any(s['name'].lower() == subject_name.lower() for s in teacher['subjects'])
        ]
        indices = [self.teacher_map[t['name']] for t in suitable]
        indices.append(self.teacher_map["No teacher available"])
        return indices

    def generate_schedule(self):
        sessions = []
        session_vars = []
        session_teachers = []
        days = ["dimanche", "lundi", "mardi", "mercredi", "jeudi"]
        room_name = self.get_assigned_room()
        if not room_name:
            return []
        for subj in self.section['subjects']:
            for _ in range(subj['coef']):
                sessions.append(subj)
        for i, s in enumerate(sessions):
            d_var = self.model.NewIntVar(0, len(days) - 1, f"d_{i}")
            slot_var = self.model.NewIntVar(1, 8, f"s_{i}")
            t_var = self.model.NewIntVar(0, self.num_teachers - 1, f"t_{i}")
            session_vars.append((d_var, slot_var, t_var))
            session_teachers.append(s['name'])
        for i, (d_var, slot_var, t_var) in enumerate(session_vars):
            name = session_teachers[i].lower()
            teachers_ok = self.find_suitable_teacher(name)
            self.model.AddAllowedAssignments([t_var], [[x] for x in teachers_ok])
        for t in range(self.num_teachers):
            for d in range(len(days)):
                for s in range(1, 9):
                    assigned = []
                    for i, (d_var, slot_var, t_var) in enumerate(session_vars):
                        if t == self.num_teachers - 1:
                            continue
                        b = self.model.NewBoolVar(f"b_{i}_{t}_{d}_{s}")
                        self.model.Add(t_var == t).OnlyEnforceIf(b)
                        self.model.Add(t_var != t).OnlyEnforceIf(b.Not())
                        self.model.Add(d_var == d).OnlyEnforceIf(b)
                        self.model.Add(d_var != d).OnlyEnforceIf(b.Not())
                        self.model.Add(slot_var == s).OnlyEnforceIf(b)
                        self.model.Add(slot_var != s).OnlyEnforceIf(b.Not())
                        assigned.append(b)
                    if assigned:
                        self.model.Add(sum(assigned) <= 1)
        for i, s in enumerate(sessions):
            if s['name'].lower() == "sport":
                d_var, slot_var, t_var = session_vars[i]
                self.model.AddAllowedAssignments([slot_var], [[1], [3], [5], [7]])
        for i, s1 in enumerate(sessions):
            if s1['name'].lower() == "sport":
                d1, sl1, t1 = session_vars[i]
                for j, s2 in enumerate(sessions):
                    if j == i:
                        continue
                    d2, sl2, t2 = session_vars[j]
                    dm = self.model.NewBoolVar(f"dm_{i}_{j}")
                    tm = self.model.NewBoolVar(f"tm_{i}_{j}")
                    eqs = self.model.NewBoolVar(f"eqs_{i}_{j}")
                    eqs_next = self.model.NewBoolVar(f"eqsnext_{i}_{j}")
                    ovlp = self.model.NewBoolVar(f"ovlp_{i}_{j}")
                    self.model.Add(d1 == d2).OnlyEnforceIf(dm)
                    self.model.Add(d1 != d2).OnlyEnforceIf(dm.Not())
                    self.model.Add(t1 == t2).OnlyEnforceIf(tm)
                    self.model.Add(t1 != t2).OnlyEnforceIf(tm.Not())
                    self.model.Add(sl2 == sl1).OnlyEnforceIf(eqs)
                    self.model.Add(sl2 != sl1).OnlyEnforceIf(eqs.Not())
                    self.model.Add(sl2 - sl1 == 1).OnlyEnforceIf(eqs_next)
                    self.model.Add(sl2 - sl1 != 1).OnlyEnforceIf(eqs_next.Not())
                    self.model.AddBoolOr([eqs, eqs_next]).OnlyEnforceIf(ovlp)
                    self.model.AddBoolAnd([eqs.Not(), eqs_next.Not()]).OnlyEnforceIf(ovlp.Not())
                    conflict = self.model.NewBoolVar(f"c_{i}_{j}")
                    self.model.AddBoolAnd([dm, tm, ovlp]).OnlyEnforceIf(conflict)
                    self.model.Add(conflict == 0)
        no_teacher_flags = []
        for i, (d_var, slot_var, t_var) in enumerate(session_vars):
            nt = self.model.NewBoolVar(f"no_teacher_{i}")
            self.model.Add(t_var == self.num_teachers - 1).OnlyEnforceIf(nt)
            self.model.Add(t_var != self.num_teachers - 1).OnlyEnforceIf(nt.Not())
            no_teacher_flags.append(nt)
        self.model.Minimize(sum(no_teacher_flags))
        status = self.solver.Solve(self.model)
        if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
            schedule = []
            for i, (d_var, slot_var, t_var) in enumerate(session_vars):
                d = self.solver.Value(d_var)
                s = self.solver.Value(slot_var)
                t = self.solver.Value(t_var)
                name = session_teachers[i]
                st = self.time_slots(s)['start']
                et = self.time_slots(s)['end']
                if name.lower() == "sport":
                    sp = None
                    for pair in [(1,2), (3,4), (5,6), (7,8)]:
                        if s == pair[0]:
                            sp = pair
                            break
                    if sp:
                        st = self.time_slots(sp[0])['start']
                        et = self.time_slots(sp[1])['end']
                        sl_str = f"{sp[0]}-{sp[1]}"
                    else:
                        sl_str = f"{s}"
                else:
                    sl_str = f"{s}"
                if t == self.num_teachers - 1:
                    tn = "No teacher available"
                else:
                    tn = self.teachers[t]['name']
                schedule.append({
                    "day": days[d],
                    "room": room_name,
                    "subject": name,
                    "teacher": tn,
                    "time": f"{st} - {et}",
                    "slot": sl_str,
                    "section": self.section['section'],
                    "stream": self.section.get('stream')
                })
            return schedule
        else:
            schedule = []
            logger.error("No feasible solution found.")
            for s in sessions:
                day = 0
                slot = 1
                ts = self.time_slots(slot)['start']
                te = self.time_slots(slot)['end']
                ss = f"{slot}"
                if s['name'].lower() == "sport":
                    sp = (1,2)
                    ts = self.time_slots(sp[0])['start']
                    te = self.time_slots(sp[1])['end']
                    ss = f"{sp[0]}-{sp[1]}"
                schedule.append({
                    "day": days[day],
                    "room": room_name,
                    "subject": s['name'],
                    "teacher": "No teacher available",
                    "time": f"{ts} - {te}",
                    "slot": ss,
                    "section": self.section['section'],
                    "stream": self.section.get('stream')
                })
            return schedule
