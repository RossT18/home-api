from app.routers.uklife import init_uklife_tables
from enum import StrEnum
from pydantic import BaseModel
import json
import os
from app.database import get_db


class QuestionInsert(BaseModel):
    question: str
    category_id: int
    options: str
    answer: str

class RawCategory(StrEnum):
    A_LONG_AND_ILLUSTRIOUS_HISTORY = "a_long_and_illustrious_history"
    A_MODERN_THRIVING_SOCIETY = "a_modern_thriving_society"
    UK_GOVERNMENT_THE_LAW_AND_YOUR_ROLE = "uk_government_the_law_and_your_role"
    THE_VALUES_AND_PRINCIPLES_OF_THE_UK = "the_values_and_principles_of_the_uk"
    WHAT_IS_THE_UK = "what_is_the_uk"
    EXAM_QUESTIONS = "exam_questions"

    def get_friendly_name(self) -> str:
        """
        Get a friendly name for the category.
        """
        return {
            self.A_LONG_AND_ILLUSTRIOUS_HISTORY: "A long and illustrious history",
            self.A_MODERN_THRIVING_SOCIETY: "A modern thriving society",
            self.UK_GOVERNMENT_THE_LAW_AND_YOUR_ROLE: "UK government, the law and your role",
            self.THE_VALUES_AND_PRINCIPLES_OF_THE_UK: "The values and principles of the UK",
            self.WHAT_IS_THE_UK: "What is the UK",
            self.EXAM_QUESTIONS: "Exam questions",
        }.get(self, "Unknown Category")

    def is_file(self) -> bool:
        return {
            self.A_LONG_AND_ILLUSTRIOUS_HISTORY: False,
            self.A_MODERN_THRIVING_SOCIETY: False,
            self.UK_GOVERNMENT_THE_LAW_AND_YOUR_ROLE: False,
            self.THE_VALUES_AND_PRINCIPLES_OF_THE_UK: True,
            self.WHAT_IS_THE_UK: True,
            self.EXAM_QUESTIONS: True,
        }.get(self, False)

def read_json_file(file_path: str) -> list[dict]:
    """
    Read a JSON file and return its content.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at {file_path}")
    with open(file_path, 'r') as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                raise ValueError(f"Expected a list in JSON file at {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in file {file_path}: {e}")

def deep_read_json_files(parent_folder: str) -> list[dict]:
    all_data = []
    for root, _, files in os.walk(parent_folder):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            all_data.extend(data)
                except Exception:
                    continue
    return all_data

    

if __name__ == "__main__":
    db_gen = get_db()
    conn = next(db_gen)
    init_uklife_tables(conn)

    # Populate categories
    categories: list[RawCategory] = [category for category in RawCategory]
    print(f"Inserting {len(categories)} into uklife_categories...")
    cursor = conn.executemany(
        "INSERT OR IGNORE INTO uklife_categories (name, friendly_name) VALUES (?, ?)",
        [(category.value, category.get_friendly_name()) for category in categories]
    )
    if skipped := len(categories) - cursor.rowcount:
        print(f"|---- Skipped {skipped} categories that already exist")
    print("Done\n")

    database_categories = conn.execute("SELECT id, name FROM uklife_categories").fetchall()
    category_id_map = {row["name"]: row["id"] for row in database_categories}


    # Populate questions
    questions = []
    print("Loading questions from json files...")
    for category in RawCategory:

        category_questions = []

        if category.is_file():
            file_path = f"app/resources/uklife/questions_2023/{category.value}.json"
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File for category {category} not found at {file_path}")
            category_questions.extend(read_json_file(file_path))
        else:
            file_path = f"app/resources/uklife/questions_2023/{category.value}"
            category_questions.extend(deep_read_json_files(file_path))
        
        print(f"|---- Read {len(category_questions)} questions for category {category}")

        for question in category_questions:
            question_data = QuestionInsert(
                question=question["question"],
                category_id=category_id_map[category.value],
                options=json.dumps(question["options"], sort_keys=True),
                answer=json.dumps(question["answer"], sort_keys=True)
            )
            questions.append(question_data)

    print(f"Finished reading all {len(questions)} questions")

    print("Inserting questions into uklife_questions...")
    cursor = conn.executemany(
        "INSERT OR IGNORE INTO uklife_questions (question, category_id, options, answer) VALUES (?, ?, ?, ?)",
        [(q.question, q.category_id, q.options, q.answer) for q in questions]
    )
    if skipped_questions := len(questions) - cursor.rowcount:
        print(f"|---- Skipped {skipped_questions} questions that already exist")
    print("Done\n")

    conn.commit()
    db_gen.close()
