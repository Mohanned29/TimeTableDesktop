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
        section_room_prefix = "MS_Room_" if self.level == "middle_school" else "HS_Room_"
        section_name = self.section['section']
        for room in self.rooms:
            if room['name'] == f"{section_room_prefix}{section_name}":
                return room['name']
        logger.error(f"No room assigned to section {section_name}")
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
        normalized_subject = subject_name.strip().lower()
        suitable_teachers = [
            teacher for teacher in self.teachers
            if any(s['name'].strip().lower() == normalized_subject for s in teacher['subjects'])
        ]
        suitable_teacher_indices = [self.teacher_map[teacher['name']] for teacher in suitable_teachers]
        if not suitable_teacher_indices:
            suitable_teacher_indices = [self.teacher_map["No teacher available"]]
        return suitable_teacher_indices

    def generate_schedule(self):
        sessions = []
        session_vars = []
        session_teachers = []
        no_teacher_vars = []

        days = ["dimanche", "lundi", "mardi", "mercredi", "jeudi"]
        num_days = len(days)
        slots = list(range(1, 9))
        num_slots = len(slots)
        room_name = self.get_assigned_room()
        if not room_name:
            logger.error(f"No room assigned to section {self.section['section']}")
            return []

        subjects = self.section['subjects']

        for subject in subjects:
            for _ in range(subject['coef']):
                sessions.append(subject)

        for idx, session in enumerate(sessions):
            day_var = self.model.NewIntVar(0, num_days - 1, f'session_{idx}_day')
            slot_var = self.model.NewIntVar(1, num_slots, f'session_{idx}_slot')
            teacher_var = self.model.NewIntVar(0, self.num_teachers - 1, f'session_{idx}_teacher')
            no_teacher_var = self.model.NewBoolVar(f'session_{idx}_no_teacher')
            
            self.model.Add(teacher_var == self.teacher_map["No teacher available"]).OnlyEnforceIf(no_teacher_var)
            self.model.Add(teacher_var != self.teacher_map["No teacher available"]).OnlyEnforceIf(no_teacher_var.Not())
            
            session_vars.append((day_var, slot_var, teacher_var))
            session_teachers.append(session['name'])
            no_teacher_vars.append(no_teacher_var)

        for i in range(len(session_vars)):
            for j in range(i + 1, len(session_vars)):
                day_i, slot_i, _ = session_vars[i]
                day_j, slot_j, _ = session_vars[j]
                overlap = self.model.NewBoolVar(f'overlap_{i}_{j}')
                self.model.Add(day_i == day_j).OnlyEnforceIf(overlap)
                self.model.Add(slot_i == slot_j).OnlyEnforceIf(overlap)
                self.model.Add(overlap == 0)

        for idx, (day_var, slot_var, teacher_var) in enumerate(session_vars):
            subject_name = session_teachers[idx]
            suitable_teachers = self.find_suitable_teacher(subject_name)
            if suitable_teachers:
                self.model.AddAllowedAssignments([teacher_var], [[t] for t in suitable_teachers])
            else:
                self.model.Add(teacher_var == self.teacher_map["No teacher available"])

        for t in range(self.num_teachers - 1):
            teacher_sessions = [(day_var, slot_var) for day_var, slot_var, teacher_var in session_vars]
            for i in range(len(teacher_sessions)):
                for j in range(i + 1, len(teacher_sessions)):
                    day_i, slot_i = teacher_sessions[i]
                    day_j, slot_j = teacher_sessions[j]
                    conflict = self.model.NewBoolVar(f'teacher_{t}_conflict_{i}_{j}')
                    self.model.Add(day_i == day_j).OnlyEnforceIf(conflict)
                    self.model.Add(slot_i == slot_j).OnlyEnforceIf(conflict)
                    self.model.Add(conflict == 0).OnlyEnforceIf([
                        session_vars[i][2] == t,
                        session_vars[j][2] == t
                    ])

        for idx, session in enumerate(sessions):
            if session['name'].strip().lower() == "sport":
                day_var, slot_var, teacher_var = session_vars[idx]
                allowed_slot_pairs = [(1, 2), (3, 4), (5, 6), (7, 8)]
                possible_start_slots = [pair[0] for pair in allowed_slot_pairs]
                self.model.AddAllowedAssignments([slot_var], [[s] for s in possible_start_slots])

        self.model.Minimize(sum(no_teacher_vars))

        status = self.solver.Solve(self.model)

        if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
            for idx, (day_var, slot_var, teacher_var) in enumerate(session_vars):
                day = self.solver.Value(day_var)
                slot = self.solver.Value(slot_var)
                teacher_idx = self.solver.Value(teacher_var)
                subject_name = session_teachers[idx]

                if subject_name.strip().lower() == "sport":
                    slot_pair = next(((s, e) for s, e in [(1,2), (3,4), (5,6), (7,8)] if s == slot), None)
                    if slot_pair:
                        time_start = self.time_slots(slot_pair[0])['start']
                        time_end = self.time_slots(slot_pair[1])['end']
                        slot_str = f"{slot_pair[0]}-{slot_pair[1]}"
                    else:
                        time_start = self.time_slots(slot)['start']
                        time_end = self.time_slots(slot)['end']
                        slot_str = f"{slot}"
                else:
                    time_start = self.time_slots(slot)['start']
                    time_end = self.time_slots(slot)['end']
                    slot_str = f"{slot}"

                teacher_name = "No teacher available" if teacher_idx == self.num_teachers - 1 \
                    else self.teachers[teacher_idx]['name']

                self.schedule.append({
                    "day": days[day],
                    "room": room_name,
                    "subject": subject_name,
                    "teacher": teacher_name,
                    "time": f"{time_start} - {time_end}",
                    "slot": slot_str,
                    "section": self.section['section'],
                    "stream": self.section.get('stream')
                })
            return self.schedule
        else:
            logger.error("No feasible solution found.")
            self.schedule = []
            for idx, session in enumerate(sessions):
                subject_name = session['name']
                day = 0
                slot = 1
                if subject_name.strip().lower() == "sport":
                    slot_pair = (1, 2)
                    time_start = self.time_slots(slot_pair[0])['start']
                    time_end = self.time_slots(slot_pair[1])['end']
                    slot_str = f"{slot_pair[0]}-{slot_pair[1]}"
                else:
                    time_start = self.time_slots(slot)['start']
                    time_end = self.time_slots(slot)['end']
                    slot_str = f"{slot}"
                teacher_name = "No teacher available"
                self.schedule.append({
                    "day": days[day] if day < len(days) else "vendredi",
                    "room": room_name,
                    "subject": subject_name,
                    "teacher": teacher_name,
                    "time": f"{time_start} - {time_end}",
                    "slot": slot_str,
                    "section": self.section['section'],
                    "stream": self.section.get('stream')
                })
            return self.schedule