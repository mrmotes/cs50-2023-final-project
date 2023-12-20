import ast
from flask import Blueprint, render_template, request, redirect, url_for
from helpers import apology
from helpers import *

evaluations_bp = Blueprint("evaluations", __name__, template_folder="templates/film-evaluator", static_folder="static")


@evaluations_bp.route("/submissions", methods=["GET"])
@login_required
def pending_evaluation():
    user_category_ids = [x["category_id"] for x in db.execute("SELECT category_id FROM user_categories WHERE user_id = :id AND is_active = 1", id=session["user_id"])]
    submissions = get_submissions_for_user_categories(user_category_ids)
    submissions_available_for_evaluation = []
    for submission in submissions:
        evaluation = evaluation_by_evaluator_and_submission(session["user_id"], submission["ID"])
        if not evaluation:
            submissions_available_for_evaluation.append(submission)
    return render_template("film-evaluator/pending-evaluation.html", submissions=submissions_available_for_evaluation)


@evaluations_bp.route("/create-evaluation", methods=["GET"])
@login_required
def create_evaluation():
    submission_id = request.args.get("submission-id")
    submission = get_submission_by_id(submission_id)
    if not submission:
        return apology("issue getting submission for {}".format(submission_id))
    video_id = submission["url"].split("v=")[1]
    embed_link = f"https://www.youtube.com/embed/{video_id}"
    criteria_ids_for_submission_category = [x["criteria_id"] for x in db.execute("SELECT criteria_id FROM category_criteria WHERE category_id = :submission_category_id AND is_active = 1", submission_category_id=submission["category_id"])]
    submission_criteria = db.execute("SELECT * FROM criteria WHERE id IN (:valid_ids)", valid_ids=criteria_ids_for_submission_category)
    return render_template("film-evaluator/evaluate.html", submission=submission, criteria=submission_criteria, criteria_options=criteria_options() , embed_link=embed_link)




@evaluations_bp.route("/create-evaluation", methods=["POST"])
@login_required
def create_evaluation_post():
    form = request.form
    submission_id = form.get("submission-id")
    additional_notes = form.get("additional-notes")
    evaluation = {}
    total_score = 0
    for key in form.keys():
        if key not in ["submission-id", "additional-notes"]:
            for value in form.getlist(key):
                total_score = total_score + int(value)
                evaluation[key] = int(value)
    db.execute("""
               INSERT INTO evaluations (submission_id, user_id, evaluation, total_score, additional_notes)
               VALUES (:submission_id, :user_id, :evaluation, :total_score, :additional_notes)
               """, submission_id=submission_id, user_id=session["user_id"], evaluation=str(evaluation), total_score=total_score, additional_notes=additional_notes)
    return redirect(url_for("evaluations.evaluations"))


@evaluations_bp.route("/evaluations", methods=["GET"])
@login_required
def evaluations():
    evaluation_data = get_all_evaluations()
    scores = []
    if session["user_type"] == "Admin":
        for row in evaluation_data:
            scores.append(ast.literal_eval(row["Evaluation"]))
        return render_template("film-festival-manager/evaluations/list-evaluations.html", evaluation_data=evaluation_data, scores=scores)
    elif session["user_type"] == "Evaluator":
        user_evaluations = evaluations_by_user_id(session["user_id"])
        for row in user_evaluations:
            scores.append(ast.literal_eval(row["Evaluation"]))
        return render_template("film-evaluator/evaluations.html", evaluation_data=user_evaluations, scores=scores)
    return apology("access denied")


@evaluations_bp.route("/update-evaluation", methods=["GET"])
@login_required
def update_evaluation():
    evaluation_id = request.args.get("evaluation-id")
    evaluation_data = get_evaluation_by_id(evaluation_id)

    if not evaluation_data:
        return apology("Issue getting evaluation for id {}".format(evaluation_id))
    if session["user_id"] != evaluation_data["user_id"]:
        return apology("Access denied")

    submission = get_submission_by_id(evaluation_data["submission_id"])
    evaluation_notes = evaluation_data["additional_notes"]
    evaluation = ast.literal_eval(evaluation_data["evaluation"])
    video_id = submission["url"].split("v=")[1]
    embed_link = f"https://www.youtube.com/embed/{video_id}"
    print(evaluation)
    return render_template("film-evaluator/update-evaluation.html", submission=submission, evaluation=evaluation, evaluation_id=evaluation_id, evaluation_notes=evaluation_notes, embed_link=embed_link, criteria_options=criteria_options())


@evaluations_bp.route("/update-evaluation", methods=["POST"])
@login_required
def update_evaluation_post():
    form = request.form
    evaluation_id = form.get("evaluation-id")
    print(evaluation_id)
    evaluation = get_evaluation_by_id(evaluation_id)
    updated_notes = form.get("additional-notes")
    if not evaluation:
        return apology("Issue getting evaluation for id {}".format(evaluation_id))
    if session["user_id"] != evaluation["user_id"]:
        return apology("Access denied")
    updated_evaluation = {}
    updated_total_score = 0
    for key in form.keys():
        if key not in ["evaluation-id", "additional-notes"]:
            for value in form.getlist(key):
                updated_total_score = updated_total_score + int(value)
                updated_evaluation[key] = int(value)
    if updated_evaluation != ast.literal_eval(evaluation["evaluation"]):
        db.execute("UPDATE evaluations SET evaluation = :evaluation, total_score = :total_score, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=evaluation_id, evaluation=str(updated_evaluation), total_score=updated_total_score)
    if updated_notes != evaluation["additional_notes"]:
        db.execute("UPDATE evaluations SET additional_notes = :notes, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=evaluation_id, notes=updated_notes)
    return redirect(url_for("evaluations.evaluations"))
