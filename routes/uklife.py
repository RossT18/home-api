from enum import StrEnum
from typing import Annotated
from fastapi import APIRouter, Query
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import json
import os
import random
from pydantic.utils import deep_update

from cache import CachedValue


router = APIRouter(
  prefix='/uklife',
  tags=['uklife']
)

class QuestionRequest(BaseModel):
  count: int = 24
  categories: list[str] = []

class Category(StrEnum):
  A_LONG_AND_ILLUSTRIOUS_HISTORY = "a_long_and_illustrious_history"
  A_MODERN_THRIVING_SOCIETY = "a_modern_thriving_society"
  UK_GOVERNMENT_THE_LAW_AND_YOUR_ROLE = "uk_government_the_law_and_your_role"
  THE_VALUES_AND_PRINCIPLES_OF_THE_UK = "the_values_and_principles_of_the_uk"
  WHAT_IS_THE_UK = "what_is_the_uk"

  def get_friendly_name(self) -> str:
    """
    Get a friendly name for the category.
    """
    return {
      self.A_LONG_AND_ILLUSTRIOUS_HISTORY: "A long and illustrious history",
      self.A_MODERN_THRIVING_SOCIETY: "A modern thriving society",
      self.UK_GOVERNMENT_THE_LAW_AND_YOUR_ROLE: "UK government, the law and your role",
      self.THE_VALUES_AND_PRINCIPLES_OF_THE_UK: "The values and principles of the UK",
      self.WHAT_IS_THE_UK: "What is the UK"
    }.get(self, "Unknown Category")
  

  def is_file(self) -> bool:
    return {
      self.A_LONG_AND_ILLUSTRIOUS_HISTORY: False,
      self.A_MODERN_THRIVING_SOCIETY: False,
      self.UK_GOVERNMENT_THE_LAW_AND_YOUR_ROLE: False,
      self.THE_VALUES_AND_PRINCIPLES_OF_THE_UK: True,
      self.WHAT_IS_THE_UK: True
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

@router.get('/questions', response_model=list[QuestionAnswer])
def get_questions(count: Annotated[int, Query()] = 24,
                 categories: Annotated[list[Category], Query(min_length=1)] = []) -> list[QuestionAnswer]:
  """
  Get a list of questions about UK life.
  """

  all_questions: list[QuestionAnswer] = []

  for category in categories:
    all_questions.extend(get_questions_by_category(category))

  random.shuffle(all_questions)
  all_questions = all_questions[:count]

  return all_questions

@router.get('/categories', response_model=dict[Category, str])
def get_categories():
  """ Get a list of categories for UK life questions.
  """
  return {category.value: category.get_friendly_name() for category in Category}

class RawResults(BaseModel):
  answers: str
  dt: str

uklife_scores = CachedValue('uklife_scores')

@router.post('/record')
def record_results(raw_results: RawResults):
  """
  Record the results of a test attempt.
  """

  if not raw_results.answers or not raw_results.dt:
    raise ValueError("Answers and date-time are required.")
  

  dt = raw_results.dt
  answers = json.loads(raw_results.answers)

  def save_results(existing_scores):
    return deep_update(existing_scores, jsonable_encoder({ dt: answers }))

  uklife_scores.save(save_results)



def deep_read_json_files(parent_folder: str) -> list[dict]:
  all_data = []
  for root, _, files in os.walk(parent_folder):
    for file in files:
      if file.endswith('.json'):
        file_path = os.path.join(root, file)
        try:
          with open(file_path, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
              all_data.extend(data)
        except Exception:
          continue
  return all_data

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

def get_questions_by_category(category: Category) -> list[QuestionAnswer]:
  """
  Get questions by category.
  """

  data = []

  if category.is_file():
    file_path = f"static/uklife/questions_2023/{category.value}.json"
    if not os.path.exists(file_path):
      raise FileNotFoundError(f"File for category {category} not found at {file_path}")
    data = read_json_file(file_path)
  else:
    file_path = f"static/uklife/questions_2023/{category.value}"
    data = deep_read_json_files(file_path)

  qas = []
  for i, raw_qa in enumerate(data):
    question = Question(text=raw_qa['question'], category=category, options=raw_qa['options'])
    answer = Answer(options=raw_qa['answer']['options'].split(', '), text=raw_qa['answer']['text'])
    qas.append(QuestionAnswer(identifier=f"{category.value}-{i}", question=question, answer=answer))

  return qas
