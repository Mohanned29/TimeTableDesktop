from src.schedule_generator import ScheduleGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScheduleManager:
    def __init__(self, data):
        self.data = data
        self.rooms = data.get('rooms', [])
        self.teachers = data.get('teachers', [])

    def generate_schedules(self):
        schedules = {}
        middle_teachers = [teacher for teacher in self.teachers if teacher['name'].startswith("MS_Teacher_")]
        high_teachers = [teacher for teacher in self.teachers if teacher['name'].startswith("HS_Teacher_")]

        if 'middle_school' in self.data:
            middle_schedule = self.generate_level_schedule(
                'middle_school',
                self.data['middle_school'],
                middle_teachers
            )
            schedules['middle_school'] = middle_schedule

        if 'high_school' in self.data:
            high_schedule = self.generate_level_schedule(
                'high_school',
                self.data['high_school'],
                high_teachers
            )
            schedules['high_school'] = high_schedule

        return schedules

    def generate_level_schedule(self, level, level_data, teachers):
        level_schedule = {"years": []}
        years = level_data.get('years', [])

        for year_entry in years:
            year_number = year_entry.get('year')
            sections = year_entry.get('sections', [])
            year_schedule = {
                "year": year_number,
                "sections": []
            }

            for section in sections:
                generator = ScheduleGenerator(
                    level=level,
                    year=year_number,
                    section=section,
                    rooms=self.rooms,
                    teachers=teachers
                )
                schedule = generator.generate_schedule()

                section_schedule = {
                    "section": section.get('section'),
                    "stream": section.get('stream'),
                    "schedule": schedule
                }
                year_schedule["sections"].append(section_schedule)

            level_schedule["years"].append(year_schedule)

        return level_schedule
