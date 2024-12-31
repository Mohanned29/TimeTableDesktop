import json

# ywdiiiii 3jzt nkhdem data
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
                "subjects": subjects.copy()
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
                    "subjects": base_subjects[stream].copy()
                }
                year_entry["sections"].append(section_entry)
        high_school["years"].append(year_entry)
    return high_school

def generate_teachers(teacher_count=50):
    teachers = []
    subjects_pool = [
        "Islamic", "Arabic", "French", "English", "Math",
        "History and Geography", "Civil", "Sport", "Physics", "Science"
    ]
    high_school_subjects = [
        "Science", "Physics", "History and Geography", "Sport"
    ]
    all_subjects = list(set(subjects_pool + high_school_subjects))
    
    for i in range(1, teacher_count + 1):
        teacher = {
            "name": f"Teacher_{i}",
            "subjects": []
        }
        num_subjects = 2 + (i % 3)
        assigned_subjects = set()
        while len(assigned_subjects) < num_subjects:
            subject = all_subjects[(i + len(assigned_subjects)) % len(all_subjects)]
            assigned_subjects.add(subject)
        teacher["subjects"] = [{"name": subj} for subj in assigned_subjects]
        teachers.append(teacher)
    return teachers

def generate_rooms(room_count=20):
    rooms = []
    for i in range(1, room_count + 1):
        if i % 5 == 0:
            room_type = "science"
        elif i % 5 == 1:
            room_type = "sport"
        else:
            room_type = "general"
        room = {
            "name": f"Room_{i}",
            "type": room_type
        }
        rooms.append(room)
    return rooms

def main():
    data = {
        "middle_school": generate_middle_school(),
        "high_school": generate_high_school(),
        "teachers": generate_teachers(),
        "rooms": generate_rooms()
    }
    
    with open('schedule_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("schedule_data.json has been generated successfully.")

if __name__ == "__main__":
    main()
