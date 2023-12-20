import ast
from flask import redirect, render_template, session
from functools import wraps
from cs50 import SQL


db = SQL("sqlite:///film.db")

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def role_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get("user_type") not in role:
                return apology("You may not access this page")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def user_roles():
    return ["Admin", "Evaluator", "Submitter", "Jury"]

def statuses():
    return ["Active", "Pending", "Inactive"]

def evaluations_by_user_id(user_id):
    return db.execute("""
                      SELECT id as 'ID',
                     (SELECT CASE
                        WHEN title_original_language = "" AND title_english_language != "" THEN title_english_language
                        WHEN title_english_language = "" AND title_original_language != "" THEN title_original_language
                        WHEN title_original_language != "" AND title_english_language != "" THEN title_original_language || ' (' || title_english_language || ')'
                      END AS 'Title' FROM submissions WHERE id = submission_id) AS 'Title',
                      evaluation as 'Evaluation',
                      additional_notes AS 'Comments'
                      FROM evaluations WHERE user_id = :id""", id=user_id)

def get_active_events():
    return db.execute("SELECT * FROM events WHERE status != 'Inactive' ORDER BY status, name")

def get_active_categories():
    return db.execute("SELECT * FROM categories WHERE status != 'Inactive' ORDER BY status, name")

def get_active_evaluation_criteria():
    return db.execute("SELECT * FROM criteria WHERE status = 'Active'")

def get_all_submissions():
    return db.execute("""
                      SELECT id AS 'ID',
                      CASE
                        WHEN title_original_language = "" AND title_english_language != "" THEN title_english_language
                        WHEN title_english_language = "" AND title_original_language != "" THEN title_original_language
                        WHEN title_original_language != "" AND title_english_language != "" THEN title_original_language || ' (' || title_english_language || ')'
                      END AS 'Title',
                      (SELECT name FROM events WHERE id = submissions.event_id) AS Event,
                      (SELECT name FROM categories WHERE id = submissions.category_id) AS Category,
                      country_of_production AS 'Country of Production',
                      duration AS 'Duration',
                      status AS 'Status'
                      FROM submissions
                      """)

def get_submissions_for_user_categories(user_categories):
    return db.execute("""
                    SELECT id AS 'ID',
                    CASE
                        WHEN title_original_language = "" AND title_english_language != "" THEN title_english_language
                        WHEN title_english_language = "" AND title_original_language != "" THEN title_original_language
                        WHEN title_original_language != "" AND title_english_language != "" THEN title_original_language || ' (' || title_english_language || ')'
                    END AS 'Title',
                    (SELECT name FROM events WHERE id = submissions.event_id) AS Event,
                    (SELECT name FROM categories WHERE id = submissions.category_id) AS Category,
                    country_of_production AS 'Country of Production',
                    duration AS 'Duration'
                    FROM submissions WHERE status = 'Active' AND category_id IN (:user_categories)
                    """, user_categories=user_categories)

def get_all_evaluations():
    return db.execute("""
                      SELECT id AS 'ID',
                      (SELECT CASE
                        WHEN title_original_language = "" AND title_english_language != "" THEN title_english_language
                        WHEN title_english_language = "" AND title_original_language != "" THEN title_original_language
                        WHEN title_original_language != "" AND title_english_language != "" THEN title_original_language || ' (' || title_english_language || ')'
                      END AS 'Title' FROM submissions WHERE id = submission_id) AS 'Title',
                      (SELECT username FROM users WHERE id = user_id) AS 'Evaluator',
                      evaluation as 'Evaluation',
                      additional_notes AS 'Comments',
                      created_at AS 'Created At',
                      updated_at AS 'Updated At'
                      FROM evaluations
                      """)


def get_submission_by_id(submission_id):
    submission = db.execute("""
                            SELECT id,
                                CASE
                                    WHEN title_original_language = "" AND title_english_language != "" THEN title_english_language
                                    WHEN title_english_language = "" AND title_original_language != "" THEN title_original_language
                                    WHEN title_original_language != "" AND title_english_language != "" THEN title_original_language || ' (' || title_english_language || ')'
                                END AS 'title',
                            (SELECT name FROM categories WHERE id = submissions.category_id) AS category,
                            category_id,
                            synopsis,
                            country_of_production,
                            url,
                            duration
                            FROM submissions WHERE id = :id
                            """, id=submission_id)
    return submission[0] if submission else None

def get_user_by_id(user_id):
    user = db.execute("SELECT * FROM users WHERE id = :id", id=user_id)
    return user[0] if user else None

def get_category_by_id(category_id):
    category = db.execute("SELECT * FROM categories WHERE id = :id", id=category_id)
    return category[0] if category else None

def get_criteria_by_id(criteria_id):
    criteria = db.execute("SELECT * FROM criteria WHERE id = :id", id=criteria_id)
    return criteria[0] if criteria else None

def get_evaluation_by_id(evaluation_id):
    evaluation = db.execute("SELECT * FROM evaluations WHERE id = :evaluation_id", evaluation_id=evaluation_id)
    return evaluation[0] if evaluation else None


def evaluation_by_evaluator_and_submission(user_id, submission_id):
    evaluation = db.execute("SELECT evaluation FROM evaluations WHERE user_id = :user_id AND submission_id = :submission_id", user_id=user_id, submission_id=submission_id)
    return ast.literal_eval(evaluation[0]["evaluation"]) if evaluation else None

def criteria_options():
    return [1, 2, 3, 4, 5]
