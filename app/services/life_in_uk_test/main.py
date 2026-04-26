from app.services.life_in_uk_test.models import Question, Answer, QuestionFilter, Result, Category
import json
import sqlite3


def row_to_category(row: sqlite3.Row) -> Category:
    return Category(id=row["id"], name=row["name"], friendly_name=row["friendly_name"])

def read_categories(conn: sqlite3.Connection) -> list[Category]:
    rows = conn.execute("SELECT id, name, friendly_name FROM uklife_categories").fetchall()
    return [row_to_category(r) for r in rows]

def row_to_question(row: sqlite3.Row) -> Question:
    return Question(
        id=row["id"],
        question=row["question"],
        options=json.loads(row["options"]),
        answer=Answer.load_from_json(row["answer"]),
        category=row["category_id"]
    )

def read_questions(conn: sqlite3.Connection, category_ids: list[int]) -> list[Question]:
    rows = conn.execute("""
        SELECT id, question, category_id, options, answer FROM uklife_questions
        WHERE category_id IN ({seq})
    """.format(seq=",".join("?" for _ in category_ids)), category_ids).fetchall()

    return [row_to_question(row) for row in rows]


def row_to_result(row: sqlite3.Row) -> Result:
    return Result(question_id=row["question_id"], datetime=row["datetime"], correct=bool(row["correct"]))

def get_incorrect_question_ids(conn: sqlite3.Connection, use_reset: bool = True) -> list[int]:
    answered = get_results(conn, use_reset)
    return [r.question_id for r in answered if not r.correct]

def get_answered_question_ids(conn: sqlite3.Connection, use_reset: bool = True) -> list[int]:
    answered = get_results(conn, use_reset)
    return [r.question_id for r in answered]

def get_results(conn: sqlite3.Connection, use_reset: bool = True) -> list[Result]:
    query = """
        SELECT question_id, datetime, correct FROM uklife_results
    """
    if use_reset:
        query = """
            SELECT r.question_id, r.datetime, r.correct FROM uklife_results r
            LEFT JOIN uklife_resets res ON r.datetime < res.datetime
            WHERE (res.datetime IS NULL OR r.datetime > res.datetime)
        """

    rows = conn.execute(query).fetchall()
    return [row_to_result(row) for row in rows]

def filter_questions(conn: sqlite3.Connection, questions: list[Question], question_filter: QuestionFilter, use_reset: bool = True) -> list[Question]:
    if question_filter == QuestionFilter.INCORRECT:
        incorrect_question_ids = get_incorrect_question_ids(conn, use_reset)
        return [q for q in questions if q.id in incorrect_question_ids]
    elif question_filter == QuestionFilter.UNANSWERED:
        answered_question_ids = get_answered_question_ids(conn, use_reset)
        return [q for q in questions if q.id not in answered_question_ids]
    elif question_filter == QuestionFilter.INCORRECT_OR_UNANSWERED:
        incorrect_question_ids = get_incorrect_question_ids(conn, use_reset)
        answered_question_ids = get_answered_question_ids(conn, use_reset)
        return [q for q in questions if q.id in incorrect_question_ids or q.id not in answered_question_ids]

    return questions

def record_answer(conn: sqlite3.Connection, question_id: int, correct: bool):
    conn.execute(
        "INSERT INTO uklife_results (question_id, datetime, correct) VALUES (?, datetime('now'), ?)",
        (question_id, int(correct))
    )
    conn.commit()

def record_reset(conn: sqlite3.Connection):
    conn.execute("INSERT INTO uklife_resets (datetime) VALUES (datetime('now'))")
    conn.commit()
