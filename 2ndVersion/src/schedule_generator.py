import logging
from ortools.sat.python import cp_model

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

        self.days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]
        self.time_slots = {
            0: {"start": "8:00", "end": "9:00"},
            1: {"start": "9:00", "end": "10:00"},
            2: {"start": "10:00", "end": "11:00"},
            3: {"start": "11:00", "end": "12:00"},
            4: {"start": "13:30", "end": "14:30"},
            5: {"start": "14:30", "end": "15:30"},
            6: {"start": "15:30", "end": "16:30"},
            7: {"start": "16:30", "end": "17:30"}
        }

        self.room = self.get_assigned_room()

        self.model = cp_model.CpModel()

    def get_assigned_room(self):

        section_room_prefix = "MS_Room_" if self.level == "middle_school" else "HS_Room_"
        section_name = self.section['section']
        for room in self.rooms:
            if room['name'] == f"{section_room_prefix}{section_name}":
                return room['name']
        logger.error(f"No room assigned to section {section_name}")
        return None

    def find_suitable_teachers_indices(self, subject_name):
        indices = []
        for i, teacher in enumerate(self.teachers):
            for subj in teacher['subjects']:
                if subj['name'].lower() == subject_name.lower():
                    indices.append(i)
                    break
        return indices

    def generate_schedule(self):
        subjects = self.section['subjects']

        sessions = []
        for subject in subjects:
            name = subject['name']
            coef = subject['coef']
            for _ in range(coef):
                sessions.append(name)

        num_days = len(self.days)         # e.g. 5
        num_slots = len(self.time_slots)  # e.g. 8
        num_teachers = len(self.teachers)
        num_sessions = len(sessions)

        x = {}
        for i in range(num_sessions):
            subject_name = sessions[i]
            suitable_teachers = self.find_suitable_teachers_indices(subject_name)
            for d in range(num_days):
                for s in range(num_slots):
                    if subject_name.lower() == "sport":
                        if s not in [0, 2, 4, 6]:
                            continue
                    for t in suitable_teachers:
                        x[(i, d, s, t)] = self.model.NewBoolVar(f"x_{i}_{d}_{s}_{t}")

        for i in range(num_sessions):
            possible_assignments = [key for key in x.keys() if key[0] == i]
            self.model.Add(sum(x[key] for key in possible_assignments) == 1)

        for d in range(num_days):
            for s in range(num_slots):
                for t in range(num_teachers):
                    conflict_sessions = [i for (i2, d2, s2, t2) in x.keys()
                                        if d2 == d and s2 == s and t2 == t]
                    if conflict_sessions:
                        self.model.Add(
                            sum(x[(i, d, s, t)] for i in conflict_sessions) <= 1
                        )

                    next_slot = s + 1
                    if next_slot < num_slots:
                        for i in conflict_sessions:
                            if sessions[i].lower() == "sport":
                                conflict_j = [j for (jj, dd, ss, tt) in x.keys()
                                            if dd == d and ss == next_slot and tt == t]
                                for j in conflict_j:
                                    if j != i:
                                        self.model.Add(x[(i, d, s, t)] + x[(j, d, next_slot, t)] <= 1)

        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            logger.info(f"Found a feasible assignment for section {self.section['section']}.")
            for i in range(num_sessions):
                subject_name = sessions[i]
                for d in range(num_days):
                    for s in range(num_slots):
                        for t in range(num_teachers):
                            if (i, d, s, t) in x:
                                if solver.Value(x[(i, d, s, t)]) == 1:
                                    if subject_name.lower() == "sport" and s in [0, 2, 4, 6]:
                                        time_str = f"{self.time_slots[s]['start']} - {self.time_slots[s+1]['end']}"
                                        slot_label = f"{s+1}-{s+2}"
                                    else:
                                        time_str = f"{self.time_slots[s]['start']} - {self.time_slots[s]['end']}"
                                        slot_label = f"{s+1}"

                                    self.schedule.append({
                                        "day": self.days[d],
                                        "room": self.room,
                                        "subject": subject_name,
                                        "teacher": self.teachers[t]['name'],
                                        "time": time_str,
                                        "slot": slot_label,
                                        "section": self.section['section'],
                                        "stream": self.section.get('stream')
                                    })
        else:
            logger.error(f"No feasible solution found for section {self.section['section']}!")

        return self.schedule
