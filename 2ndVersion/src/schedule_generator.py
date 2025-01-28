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

        num_days = len(self.days)        # e.g. 5
        num_slots = len(self.time_slots) # e.g. 8
        num_teachers = len(self.teachers)
        num_sessions = len(sessions)

        #
        # 1) Create CP-SAT bool variables x[(i, d, s, t)] for valid combos
        #
        x = {}
        for i in range(num_sessions):
            subject_name = sessions[i]
            suitable_teachers = self.find_suitable_teachers_indices(subject_name)
            for d in range(num_days):
                for s in range(num_slots):
                    # Only create "sport" sessions at the valid start slots (0,2,4,6)
                    if subject_name.lower() == "sport" and s not in [0, 2, 4, 6]:
                        continue
                    for t in suitable_teachers:
                        x[(i, d, s, t)] = self.model.NewBoolVar(f"x_{i}_{d}_{s}_{t}")

        #
        # 2) Each session i must be assigned exactly once
        #
        for i in range(num_sessions):
            # gather all x-variables that correspond to this session i
            i_keys = [key for key in x.keys() if key[0] == i]
            self.model.Add(sum(x[k] for k in i_keys) == 1)

        #
        # 3) Teacher conflict constraints:
        #    a) No two sessions share the same (d, s, t)
        #    b) If a session is Sport and occupies (d,s,t), it blocks (d,s+1,t) too
        #

        # Instead of looping over 0..(num_days-1), etc., we only loop over the
        # actual (d,s,t) that appear in x.keys().
        # Then we group by day/slot/teacher to apply the constraints.
        from collections import defaultdict
        
        # a) For each (d, s, t), collect all i
        # b) sum(...) <= 1
        # c) if any i is Sport, block next_slot
        day_slot_teacher_map = defaultdict(list)
        for (i2, d2, s2, t2) in x.keys():
            day_slot_teacher_map[(d2, s2, t2)].append(i2)

        for (d2, s2, t2), conflict_sessions in day_slot_teacher_map.items():
            # a) Teacher can't teach >1 session in the same day/slot
            self.model.Add(
                sum(x[(i2, d2, s2, t2)] for i2 in conflict_sessions) <= 1
            )

            # b) If a session is Sport at slot s2, it also blocks s2+1
            #    We'll look for any j in day_slot_teacher_map[(d2, s2+1, t2)]
            next_slot = s2 + 1
            if next_slot < num_slots:
                next_conflict = day_slot_teacher_map.get((d2, next_slot, t2), [])
                # For each i that’s Sport in conflict_sessions, forbid pairing with j in next_conflict
                for i in conflict_sessions:
                    if sessions[i].lower() == "sport":
                        for j in next_conflict:
                            if j != i:
                                self.model.Add(x[(i, d2, s2, t2)] + x[(j, d2, next_slot, t2)] <= 1)

        #
        # 4) Solve the model
        #
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        #
        # 5) Build self.schedule from solution if feasible
        #
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            logger.info(f"Found a feasible assignment for section {self.section['section']}!")
            # We'll loop directly over x.keys() to avoid any KeyErrors
            for (i2, d2, s2, t2) in x.keys():
                if solver.Value(x[(i2, d2, s2, t2)]) == 1:
                    subject_name = sessions[i2]
                    if subject_name.lower() == "sport" and s2 in [0,2,4,6]:
                        time_str = f"{self.time_slots[s2]['start']} - {self.time_slots[s2+1]['end']}"
                        slot_label = f"{s2+1}-{s2+2}"  # 1-based indexing
                    else:
                        time_str = f"{self.time_slots[s2]['start']} - {self.time_slots[s2]['end']}"
                        slot_label = f"{s2+1}"        # 1-based indexing

                    self.schedule.append({
                        "day": self.days[d2],
                        "room": self.room,
                        "subject": subject_name,
                        "teacher": self.teachers[t2]['name'],
                        "time": time_str,
                        "slot": slot_label,
                        "section": self.section['section'],
                        "stream": self.section.get('stream')
                    })
        else:
            logger.error(f"No feasible solution found for section {self.section['section']}!")

        return self.schedule
