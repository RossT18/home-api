import json
from pydantic import BaseModel
from enum import StrEnum


class QuestionFilter(StrEnum):
    ALL = "all"
    INCORRECT = "incorrect"
    UNANSWERED = "unanswered"
    INCORRECT_OR_UNANSWERED = "incorrect_or_unanswered"

class CategoryEnum(StrEnum):
    A_LONG_AND_ILLUSTRIOUS_HISTORY = "a_long_and_illustrious_history"
    A_MODERN_THRIVING_SOCIETY = "a_modern_thriving_society"
    UK_GOVERNMENT_THE_LAW_AND_YOUR_ROLE = "uk_government_the_law_and_your_role"
    THE_VALUES_AND_PRINCIPLES_OF_THE_UK = "the_values_and_principles_of_the_uk"
    WHAT_IS_THE_UK = "what_is_the_uk"
    EXAM_QUESTIONS = "exam_questions"

class Category(BaseModel):
    id: int
    name: CategoryEnum
    friendly_name: str

class Answer(BaseModel):
    """List of options and text explanation."""
    options: list[str]
    text: str

    def load_from_json(json_str: str) -> 'Answer':
        data = json.loads(json_str)
        
        options = data.get("options", [])
        if "," in options:
            options = [opt.strip() for opt in options.split(",")]
        elif isinstance(options, str):
            options = [options.strip()]

        text = data.get("text", "")
        return Answer(options=options, text=text)

class Question(BaseModel):
    id: int
    answer: Answer
    category: int
    options: dict[str, str]
    question: str

class Result(BaseModel):
    question_id: int
    correct: bool
    datetime: str
