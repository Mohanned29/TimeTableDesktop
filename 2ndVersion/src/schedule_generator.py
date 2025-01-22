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
        """
        Assign a dedicated room to the class (section).
        """
        section_room_prefix = "MS_Room_" if self.level == "middle_school" else "HS_Room_"
        section_name = self.section['section']
        for room in self.rooms:
            if room['name'] == f"{section_room_prefix}{section_name}":
                return room['name']
        logger.error(f"No room assigned to section {section_name}")
        return None

    def time_slots(self, slot):
        """
        Helper method to get time slot details.
        """
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
        """
        Find teachers who are qualified to teach the given subject.
        """
        suitable_teachers = [
            teacher for teacher in self.teachers
            if any(s['name'].lower() == subject_name.lower() for s in teacher['subjects'])
        ]
        suitable_teacher_indices = [self.teacher_map[teacher['name']] for teacher in suitable_teachers]
        suitable_teacher_indices.append(self.teacher_map["No teacher available"])
        return suitable_teacher_indices

    def generate_schedule(self):
        sessions = []
        session_vars = []
        session_teachers = []

        days = ["dimanche" , "lundi", "mardi", "mercredi", "jeudi"]
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
            session_vars.append((day_var, slot_var, teacher_var))
            session_teachers.append(session['name'])

        for idx, (day_var, slot_var, teacher_var) in enumerate(session_vars):
            subject_name = session_teachers[idx].lower()
            suitable_teachers = self.find_suitable_teacher(subject_name)
            self.model.AddAllowedAssignments([teacher_var], [[t] for t in suitable_teachers])

        for t in range(self.num_teachers):
            for d in range(num_days):
                for s in slots:
                    assigned_sessions = []
                    for idx, (day_var, slot_var, teacher_var) in enumerate(session_vars):
                        if t == self.num_teachers -1:
                            continue
                        is_assigned = self.model.NewBoolVar(f'session_{idx}_assigned_to_teacher_{t}_day_{d}_slot_{s}')
                        self.model.Add(teacher_var == t).OnlyEnforceIf(is_assigned)
                        self.model.Add(teacher_var != t).OnlyEnforceIf(is_assigned.Not())
                        self.model.Add(day_var == d).OnlyEnforceIf(is_assigned)
                        self.model.Add(day_var != d).OnlyEnforceIf(is_assigned.Not())
                        self.model.Add(slot_var == s).OnlyEnforceIf(is_assigned)
                        self.model.Add(slot_var != s).OnlyEnforceIf(is_assigned.Not())
                        assigned_sessions.append(is_assigned)
                    if assigned_sessions:
                        self.model.Add(sum(assigned_sessions) <= 1)

        for idx, session in enumerate(sessions):
            if session['name'].lower() == "sport":
                day_var, slot_var, teacher_var = session_vars[idx]
                allowed_slot_pairs = [
                    (1,2),  # 8:00 -10:00
                    (3,4),  # 10:00 -12:00
                    (5,6),  # 13:30 -15:30
                    (7,8)   # 15:30 -17:30
                ]
                possible_start_slots = [pair[0] for pair in allowed_slot_pairs]
                self.model.AddAllowedAssignments([slot_var], [[s] for s in possible_start_slots])

        status = self.solver.Solve(self.model)

        if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
            for idx, (day_var, slot_var, teacher_var) in enumerate(session_vars):
                day = self.solver.Value(day_var)
                slot = self.solver.Value(slot_var)
                teacher_idx = self.solver.Value(teacher_var)
                subject_name = session_teachers[idx]
                time_start = self.time_slots(slot)['start']
                time_end = self.time_slots(slot)['end']
                if subject_name.lower() == "sport":
                    slot_pair = None
                    for pair in [(1,2), (3,4), (5,6), (7,8)]:
                        if slot == pair[0]:
                            slot_pair = pair
                            break
                    if slot_pair:
                        time_start = self.time_slots(pair[0])['start']
                        time_end = self.time_slots(pair[1])['end']
                        slot_str = f"{pair[0]}-{pair[1]}"
                    else:
                        slot_str = f"{slot}"
                else:
                    slot_str = f"{slot}"
                if teacher_idx == self.num_teachers -1:
                    teacher_name = "No teacher available"
                else:
                    teacher_name = self.teachers[teacher_idx]['name']
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
            for idx, session in enumerate(sessions):
                subject_name = session['name']
                day = 0
                slot = 1
                if subject_name.lower() == "sport":
                    slot_pair = (1,2)
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