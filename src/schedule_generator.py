import random
import logging

logging.basicConfig(level=logging.INFO)

class ScheduleGenerator:
    def __init__(self, level, year, section, rooms, teachers):
        """
        :param level: 'middle_school' or 'high_school'
        :param year: Year data
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
        self.assigned_lectures = set()
        self.teacher_commitments = {}
        self.room_availability = {}
        self.time_slots = self.define_time_slots()
        self.init_availability()

    def define_time_slots(self):
        return {
            1: "8:00 - 9:00",
            2: "9:00 - 10:00",
            3: "10:00 - 11:00",
            4: "11:00 - 12:00",
            5: "13:30 - 14:30",
            6: "14:30 - 15:30",
            7: "15:30 - 16:30"
        }

    def init_availability(self):
        days_of_week = ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]
        for room in self.rooms:
            self.room_availability[room['name']] = {day: [True] * len(self.time_slots) for day in days_of_week}
        for teacher in self.teachers:
            self.teacher_commitments[teacher['name']] = {day: [True] * len(self.time_slots) for day in days_of_week}

    def find_suitable_teacher(self, subject_name, day, slot):
        qualified_teachers = [
            teacher for teacher in self.teachers
            if any(s['name'].lower() == subject_name.lower() for s in teacher['subjects'])
        ]
        random.shuffle(qualified_teachers)
        for teacher in qualified_teachers:
            if self.teacher_commitments[teacher['name']][day][slot - 1]:
                return teacher['name']
        return None

    def find_available_room(self, subject_name, day, slot):
        suitable_rooms = [
            room for room in self.rooms
            if room.get('type', 'general') == 'general'
        ]
        random.shuffle(suitable_rooms)
        for room in suitable_rooms:
            if self.room_availability[room['name']][day][slot - 1]:
                return room['name']
        return None

    def is_slot_conflict(self, section_name, day, slot, subject, teacher):
        for session in self.schedule:
            if session['day'] == day and session['slot'] == slot:
                if session['teacher'] == teacher:
                    return True
                if session['section'] == section_name:
                    return True
                if self.level == 'high_school' and 'stream' in session and 'stream' in session:
                    if session.get('stream') != session.get('stream'):
                        return True
        return False

    def assign_session(self, section_name, stream, subject):
        days_of_week = ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]
        random_day = random.choice(days_of_week)
        available_slots = list(self.time_slots.keys())

        for slot in available_slots:
            if self.is_slot_available(slot, random_day):
                teacher = self.find_suitable_teacher(subject['name'], random_day, slot)
                if not teacher:
                    continue
                if self.is_slot_conflict(section_name, random_day, slot, subject, teacher):
                    continue
                room_name = self.find_available_room(subject['name'], random_day, slot)
                if not room_name:
                    continue
                self.schedule.append({
                    'day': random_day,
                    'room': room_name,
                    'subject': subject['name'],
                    'teacher': teacher,
                    'time': self.time_slots[slot],
                    'slot': slot,
                    'section': section_name,
                    'stream': stream
                })
                self.update_availability(room_name, teacher, random_day, slot)
                break

    def is_slot_available(self, slot, day):
        return any(self.room_availability[room][day][slot - 1] for room in self.room_availability) and \
               any(self.teacher_commitments[teacher][day][slot - 1] for teacher in self.teacher_commitments)

    def update_availability(self, room_name, teacher_name, day, slot):
        self.room_availability[room_name][day][slot - 1] = False
        if teacher_name:
            self.teacher_commitments[teacher_name][day][slot - 1] = False

    def generate_schedule(self):
        for subject in self.section['subjects']:
            stream = self.section.get('stream') if self.level == 'high_school' else None
            for _ in range(subject['coef']):
                self.assign_session(self.section['section'], stream, subject)
        return self.schedule
