from typing import Annotated
from app.database import get_db
import sqlite3
from app.services.life_in_uk_test.models import Question, QuestionFilter, Category
from app.services.life_in_uk_test.main import read_questions, record_reset, filter_questions, record_answer, read_categories
from fastapi import APIRouter, Depends, Query
from random import sample


router = APIRouter(
  prefix='/uklife',
  tags=['uklife']
)

@router.get("/categories", response_model=list[Category])
def list_categories(db: sqlite3.Connection = Depends(get_db)):
    """Return all life in the UK test categories."""
    return read_categories(db)

@router.get("/questions", response_model=list[Question])
def get_questions(
        db: sqlite3.Connection = Depends(get_db),
        count: Annotated[int, Query()] = 24,
        category_ids: Annotated[list[int], Query()] = [],
        filter: Annotated[QuestionFilter, Query()] = QuestionFilter.ALL
    ):
    if len(category_ids) == 0:
        # If no categories specified, get all category ids
        category_ids = [cat.id for cat in read_categories(db)]
    questions = read_questions(db, category_ids)
    filtered_questions = filter_questions(db, questions, filter)

    return sample(filtered_questions, min(count, len(filtered_questions)))

@router.post("/answer")
def submit_answer(
        db: sqlite3.Connection = Depends(get_db),
        question_id: int = Query(),
        correct: bool = Query(),
    ):
    record_answer(db, question_id, correct)

@router.delete("/reset")
def reset_results(db: sqlite3.Connection = Depends(get_db)):
    """
    Reset the recorded results.

    Note: Resetting results does not delete past answers, but instead
    makes them as inactive by not considering answers recorded before the reset datetime.

    For example,
    Answering a question incorrectly, then resetting,
    then getting incorrect questions using the filter,
    the question will not be returned.
    """
    record_reset(db)

def init_uklife_tables(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS uklife_categories (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL UNIQUE,
            friendly_name TEXT NOT NULL
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS uklife_questions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            question    TEXT NOT NULL,
            category_id INTEGER NOT NULL,

            -- options JSON structure:
            -- {
            --     "A": "Option text",
            --     "B": "Option text",
            --     "C": "Option text",
            --     "D": "Option text"
            -- }
            options     TEXT NOT NULL,
            
            -- answer JSON structure:
            -- {
            --     "options": "B, D",
            --     "text": "Explanation of the answer"
            -- }
            answer      TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES uklife_categories(id),
            UNIQUE(question, category_id, options, answer)
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS uklife_results (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            datetime    TEXT NOT NULL,
            correct     INTEGER NOT NULL CHECK(correct IN (0, 1)),
            FOREIGN KEY (question_id) REFERENCES uklife_questions(id)
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS uklife_resets (datetime TEXT NOT NULL);
    """)
