from src.schedule_generator import ScheduleGenerator

class ScheduleManager:
    def __init__(self, data, rooms, teachers):
        """
        :param data: Dictionary containing 'middle_school' and/or 'high_school' data
        :param rooms: List of rooms
        :param teachers: List of teachers
        """
        self.data = data
        self.rooms = rooms
        self.teachers = teachers

    def generate_schedules(self):
        schedules = {}

        if 'middle_school' in self.data:
            schedules['middle_school'] = self.generate_level_schedule('middle_school', self.data['middle_school'])

        if 'high_school' in self.data:
            schedules['high_school'] = self.generate_level_schedule('high_school', self.data['high_school'])

        return schedules

    def generate_level_schedule(self, level, level_data):
        level_schedule = {"years": []}
        for year_entry in level_data['years']:
            year_number = year_entry['year']
            year_schedule = {
                "year": year_number,
                "sections": []
            }

            for section_entry in year_entry['sections']:
                section_name = section_entry['section']
                subjects = section_entry['subjects']
                stream = section_entry.get('stream') if level == 'high_school' else None

                generator = ScheduleGenerator(
                    level=level,
                    year=year_number,
                    section=section_entry,
                    rooms=self.rooms,
                    teachers=self.teachers
                )
                schedule = generator.generate_schedule()

                section_info = {
                    "section": section_name,
                    "stream": stream,
                    "schedule": schedule
                }
                year_schedule["sections"].append(section_info)

            level_schedule["years"].append(year_schedule)
        return level_schedule
