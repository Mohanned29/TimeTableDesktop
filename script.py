import json

def generate_middle_school(years=4, sections_per_year=3):
    middle_school = {"years": []}
    subjects = [
        {"name": "Islamic", "coef": 1},
        {"name": "Arabic", "coef": 5},
        {"name": "French", "coef": 3},
        {"name": "English", "coef": 2},
        {"name": "Math", "coef": 4},
        {"name": "History and Geography", "coef": 3},
        {"name": "Civil", "coef": 1},
        {"name": "Sport", "coef": 1},
        {"name": "Physics", "coef": 2},
        {"name": "Science", "coef": 2}
    ]
    for year in range(1, years + 1):
        year_entry = {"year": year, "sections": []}
        for sec in range(1, sections_per_year + 1):
            section_name = f"{year}M{sec}"
            section_entry = {
                "section": section_name,
                "subjects": [dict(subject) for subject in subjects]
            }
            year_entry["sections"].append(section_entry)
        middle_school["years"].append(year_entry)
    return middle_school

def generate_high_school(years=3, streams=["scientifique", "litterature"], sections_per_stream=5):
    high_school = {"years": []}
    base_subjects = {
        "scientifique": [
            {"name": "Math", "coef": 5},
            {"name": "Arabic", "coef": 3},
            {"name": "French", "coef": 2},
            {"name": "English", "coef": 2},
            {"name": "Science", "coef": 4},
            {"name": "Physics", "coef": 4},
            {"name": "Islamic", "coef": 1},
            {"name": "History and Geography", "coef": 3},
            {"name": "Sport", "coef": 1}
        ],
        "litterature": [
            {"name": "Math", "coef": 4},
            {"name": "Arabic", "coef": 5},
            {"name": "French", "coef": 3},
            {"name": "English", "coef": 2},
            {"name": "Science", "coef": 2},
            {"name": "Physics", "coef": 2},
            {"name": "Islamic", "coef": 1},
            {"name": "History and Geography", "coef": 3},
            {"name": "Sport", "coef": 1}
        ]
    }
    for year in range(1, years + 1):
        year_entry = {"year": year, "sections": []}
        for stream in streams:
            for sec in range(1, sections_per_stream + 1):
                section_name = f"{year}{stream[0].upper()}{sec}"
                section_entry = {
                    "section": section_name,
                    "stream": stream,
                    "subjects": [dict(subject) for subject in base_subjects[stream]]
                }
                year_entry["sections"].append(section_entry)
        high_school["years"].append(year_entry)
    return high_school

def generate_teachers(middle_school_subjects, high_school_subjects, middle_teacher_count=30, high_teacher_count=30):
    teachers = []
    middle_subject_pool = list(set([subj['name'] for subj in middle_school_subjects]))
    middle_subject_count = len(middle_subject_pool)
    for subject in middle_subject_pool:
        teacher = {
            "name": f"MS_Teacher_{subject.replace(' ', '_')}",
            "subjects": [{"name": subject}]
        }
        teachers.append(teacher)
    remaining_middle_teachers = middle_teacher_count - middle_subject_count
    if remaining_middle_teachers > 0:
        for i in range(remaining_middle_teachers):
            subject = middle_subject_pool[i % middle_subject_count]
            teacher = {
                "name": f"MS_Teacher_{middle_subject_pool[i % middle_subject_count]}_{i}",
                "subjects": [{"name": subject}]
            }
            teachers.append(teacher)
    high_subject_pool = list(set([subj['name'] for subj in high_school_subjects]))
    high_subject_count = len(high_subject_pool)
    for subject in high_subject_pool:
        teacher = {
            "name": f"HS_Teacher_{subject.replace(' ', '_')}",
            "subjects": [{"name": subject}]
        }
        teachers.append(teacher)
    remaining_high_teachers = high_teacher_count - high_subject_count
    if remaining_high_teachers > 0:
        for i in range(remaining_high_teachers):
            subject = high_subject_pool[i % high_subject_count]
            teacher = {
                "name": f"HS_Teacher_{high_subject_pool[i % high_subject_count]}_{i}",
                "subjects": [{"name": subject}]
            }
            teachers.append(teacher)
    return teachers

def generate_rooms(middle_sections, high_sections):
    rooms = []
    for section in middle_sections:
        room = {
            "name": f"MS_Room_{section['section']}",
            "type": "general"
        }
        rooms.append(room)
    for section in high_sections:
        room = {
            "name": f"HS_Room_{section['section']}",
            "type": "general"
        }
        rooms.append(room)
    return rooms

def main():
    middle_school = generate_middle_school()
    middle_school_subjects = []
    for year in middle_school['years']:
        for section in year['sections']:
            for subject in section['subjects']:
                middle_school_subjects.append(subject)
    high_school = generate_high_school()
    high_school_subjects = []
    for year in high_school['years']:
        for section in year['sections']:
            for subject in section['subjects']:
                high_school_subjects.append(subject)
    teachers = generate_teachers(middle_school_subjects, high_school_subjects)
    middle_sections = [section for year in middle_school['years'] for section in year['sections']]
    high_sections = [section for year in high_school['years'] for section in year['sections']]
    rooms = generate_rooms(middle_sections, high_sections)
    data = {
        "middle_school": middle_school,
        "high_school": high_school,
        "teachers": teachers,
        "rooms": rooms
    }
    with open('schedule_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
