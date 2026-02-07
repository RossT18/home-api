from pydantic import BaseModel
from enum import StrEnum


class QuestionFilter(StrEnum):
  ALL = "all"
  INCORRECT = "incorrect"
  UNANSWERED = "unanswered"
  INCORRECT_OR_UNANSWERED = "incorrect_or_unanswered"

class Category(StrEnum):
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
      self.EXAM_QUESTIONS: "Exam questions"
    }.get(self, "Unknown Category")
  

  def is_file(self) -> bool:
    return {
      self.A_LONG_AND_ILLUSTRIOUS_HISTORY: False,
      self.A_MODERN_THRIVING_SOCIETY: False,
      self.UK_GOVERNMENT_THE_LAW_AND_YOUR_ROLE: False,
      self.THE_VALUES_AND_PRINCIPLES_OF_THE_UK: True,
      self.WHAT_IS_THE_UK: True,
      self.EXAM_QUESTIONS: True
    }.get(self, False)

class Answer(BaseModel):
  """List of options and text explanation."""
  options: list[str]
  text: str

class Question(BaseModel):
  category: Category
  text: str
  options: dict[str, str]

class QuestionAnswer(BaseModel):
  identifier: str
  question: Question
  answer: Answer

class RawResults(BaseModel):
  answers: str
  dt: str