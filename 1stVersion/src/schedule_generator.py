import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScheduleGenerator:
    def __init__(self, level, year, section, rooms, teachers):
        """
        :param level: 'middle_school' or 'high_school'
        :param year: Year number
        :param section: Section data
        :param rooms: List of rooms
        :param teachers: List of teachers
        """
        self.level = level
        self.year = year
        self.section = section
        self.rooms = rooms
        self.teachers = teachers
        self.schedule = []
        self.teacher_commitments = {}
        self.room = self.get_assigned_room()
        self.time_slots = self.define_time_slots()
        self.init_availability()

    def define_time_slots(self):
        return {
            1: {"start": "8:00", "end": "9:00"},
            2: {"start": "9:00", "end": "10:00"},
            3: {"start": "10:00", "end": "11:00"},
            4: {"start": "11:00", "end": "12:00"},
            5: {"start": "13:30", "end": "14:30"},
            6: {"start": "14:30", "end": "15:30"},
            7: {"start": "15:30", "end": "16:30"},
            8: {"start": "16:30", "end": "17:30"}
        }

    def init_availability(self):
        days_of_week = ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]
        for teacher in self.teachers:
            self.teacher_commitments[teacher['name']] = {day: [True]*len(self.time_slots) for day in days_of_week}

    def get_assigned_room(self):
        section_room_prefix = "MS_Room_" if self.level == "middle_school" else "HS_Room_"
        section_name = self.section['section']
        for room in self.rooms:
            if room['name'] == f"{section_room_prefix}{section_name}":
                return room['name']
        logger.error(f"No room assigned to section {section_name}")
        return None

    def find_suitable_teacher(self, subject_name):
        suitable_teachers = [
            teacher for teacher in self.teachers
            if any(s['name'].lower() == subject_name.lower() for s in teacher['subjects'])
        ]
        random.shuffle(suitable_teachers)
        return suitable_teachers

    def assign_session(self, subject, day, slot):
        subject_name = subject['name']
        coef = subject['coef']
        if subject_name.lower() == "sport":
            possible_slot_pairs = [
                (1,2),  # 8:00 -10:00
                (3,4),  # 10:00 -12:00
                (5,6),  # 13:30 -15:30
                (7,8)   # 15:30 -17:30
            ]
            slot_pair = None
            for pair in possible_slot_pairs:
                if slot in pair:
                    slot_pair = pair
                    break
            if not slot_pair:
                logger.warning(f"Slot {slot} is not valid for sport sessions.")
                return False

            suitable_teachers = self.find_suitable_teacher(subject_name)
            for teacher in suitable_teachers:
                if all(self.teacher_commitments[teacher['name']][day][s-1] for s in slot_pair):
                    self.schedule.append({
                        "day": day,
                        "room": self.room,
                        "subject": subject_name,
                        "teacher": teacher['name'],
                        "time": f"{self.time_slots[slot_pair[0]]['start']} - {self.time_slots[slot_pair[1]]['end']}",
                        "slot": f"{slot_pair[0]}-{slot_pair[1]}",
                        "section": self.section['section'],
                        "stream": self.section.get('stream')
                    })
                    for s in slot_pair:
                        self.teacher_commitments[teacher['name']][day][s-1] = False
                    return True
            logger.warning(f"No available teacher for sport on {day} during slots {slot_pair}.")
            return False
        else:
            suitable_teachers = self.find_suitable_teacher(subject_name)
            for teacher in suitable_teachers:
                if self.teacher_commitments[teacher['name']][day][slot-1]:
                    self.schedule.append({
                        "day": day,
                        "room": self.room,
                        "subject": subject_name,
                        "teacher": teacher['name'],
                        "time": f"{self.time_slots[slot]['start']} - {self.time_slots[slot]['end']}",
                        "slot": slot,
                        "section": self.section['section'],
                        "stream": self.section.get('stream')
                    })
                    self.teacher_commitments[teacher['name']][day][slot-1] = False
                    return True
            logger.warning(f"No available teacher for {subject_name} on {day} during slot {slot}.")
            return False

    def generate_schedule(self):
        subjects = self.section['subjects']
        random.shuffle(subjects)
        for subject in subjects:
            coef = subject['coef']
            for _ in range(coef):
                assigned = False
                attempts = 0
                max_attempts = 100
                while not assigned and attempts < max_attempts:
                    day = random.choice(["lundi", "mardi", "mercredi", "jeudi", "vendredi"])
                    if subject['name'].lower() == "sport":
                        possible_slot_pairs = [
                            (1,2),
                            (3,4),
                            (5,6),
                            (7,8)
                        ]
                        slot_pair = random.choice(possible_slot_pairs)
                        slot = slot_pair[0]
                        assigned = self.assign_session(subject, day, slot)
                    else:
                        slot = random.randint(1,8)
                        assigned = self.assign_session(subject, day, slot)
                    attempts +=1
                if not assigned:
                    logger.error(f"Failed to assign session for {subject['name']} after {max_attempts} attempts.")
        return self.schedule
