import json
import random

def generate_sample_data():
    middle_school_data = {
        "years": [
            {
                "year": 1,
                "sections": [
                    {
                        "section": "1M1",
                        "subjects": [
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
                    },
                    {
                        "section": "1M2",
                        "subjects": [
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
                ]
            },
            {
                "year": 2,
                "sections": [
                    {
                        "section": "2M1",
                        "subjects": [
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
                ]
            }
        ]
    }

    high_school_data = {
        "years": [
            {
                "year": 1,
                "sections": [
                    {
                        "section": "1S1",
                        "stream": "science",
                        "subjects": [
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
                    },
                    {
                        "section": "1L1",
                        "stream": "litterature",
                        "subjects": [
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
                ]
            },
            {
                "year": 3,
                "sections": [
                    {
                        "section": "3L3",
                        "stream": "litterature",
                        "subjects": [
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
                    },
                    {
                        "section": "3L4",
                        "stream": "litterature",
                        "subjects": [
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
                ]
            }
        ]
    }

    teachers = []
    subjects_list = ["English", "Sport", "Arabic", "History and Geography",
                     "Math", "Physics", "Science", "Islamic", "French", "Civil"]
    for level_prefix in ["MS", "HS"]:
        for subject_name in subjects_list:
            for i in range(2):
                teacher_entry = {
                    "name": f"{level_prefix}_Teacher_{subject_name}_{i}",
                    "subjects": [{"name": subject_name}]
                }
                teachers.append(teacher_entry)

    rooms = []
    for year in range(1, 5):
        for s in range(1, 4):
            rooms.append({
                "name": f"MS_Room_{year}M{s}",
                "type": "general"
            })
    for year in range(1, 4):
        for s in range(1, 6):
            rooms.append({"name": f"HS_Room_{year}S{s}", "type": "general"})
            rooms.append({"name": f"HS_Room_{year}L{s}", "type": "general"})

    data = {
        "middle_school": middle_school_data,
        "high_school": high_school_data,
        "teachers": teachers,
        "rooms": rooms
    }

    return data

if __name__ == "__main__":
    data = generate_sample_data()
    with open("sample_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Sample JSON data has been written to sample_data.json")
