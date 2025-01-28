from src.schedule_generator import ScheduleGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info(f"Total teachers loaded: {len(self.teachers)}")

    def generate_schedules(self):
        schedules = {}

        middle_teachers = [t for t in self.teachers if t['name'].startswith("MS_Teacher_")]
        high_teachers = [t for t in self.teachers if t['name'].startswith("HS_Teacher_")]

        logger.info(f"Middle school teachers found: {len(middle_teachers)}")
        logger.info(f"High school teachers found: {len(high_teachers)}")

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
            year_schedule_data = {
                "year": year_number,
                "sections": []
            }

            for section in sections:
                logger.info(f"Generating schedule for {level} {year_number} {section['section']}")
                logger.info(f"Available teachers: {[t['name'] for t in teachers]}")

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
                year_schedule_data["sections"].append(section_schedule)

            level_schedule["years"].append(year_schedule_data)

        return level_schedule
