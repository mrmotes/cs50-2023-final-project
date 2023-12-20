from flask import Blueprint, render_template, request, redirect, url_for
from helpers import apology, statuses
from helpers import *

submissions_bp = Blueprint("submissions", __name__, template_folder="film-festival-manager/templates/submissions", static_folder="static")


@submissions_bp.route("/", methods=["GET"])
@login_required
def list_submissions():
    user_role = session["user_type"]
    if request.method == "GET":
        submissions = get_all_submissions()
        return render_template("film-festival-manager/submissions/list-submissions.html", submissions=submissions, user_role=user_role)


@submissions_bp.route("/create-submission", methods=["GET", "POST"])
@login_required
@role_required(role=["Admin", "Submitter"])
def create_submission():
    if request.method == "GET":
        events = get_active_events()
        categories = get_active_categories()
        return render_template("film-festival-manager/submissions/create-submission.html", events=events, categories=categories)
    elif request.method == "POST":
        title_original_language = request.form.get("submission-title-original-language")
        title_english_language = request.form.get("submission-title-english-language")
        synopsis = request.form.get("submission-synopsis")
        event_id = request.form.get("submission-event")
        category_id = request.form.get("submission-category")
        country_of_production = request.form.get("submission-country-of-production")
        url = request.form.get("submission-url")
        password = request.form.get("submission-password")
        duration = request.form.get("submission-duration")
        submitted_by = get_user_by_id(session["user_id"])["username"]
        db.execute("""
                INSERT INTO submissions (
                title_original_language,
                title_english_language,
                synopsis,
                event_id,
                category_id,
                country_of_production,
                url,
                password,
                duration,
                submitted_by
                ) VALUES(
                :title_original_language,
                :title_english_language,
                :synopsis,
                :event_id,
                :category_id,
                :country_of_production,
                :url,
                :password,
                :duration,
                :submitted_by
                )
                """,
                title_original_language=title_original_language,
                title_english_language=title_english_language,
                synopsis=synopsis,
                event_id=event_id,
                category_id=category_id,
                country_of_production=country_of_production,
                url=url,
                password=password,
                duration=duration,
                submitted_by=submitted_by)
        return redirect(url_for("submissions.list_submissions"))


@submissions_bp.route("/update", methods=["GET"])
@login_required
@role_required(role=["Admin", "Submitter"])
def update_submission():
    submission_id = request.args.get("submission_id")
    submission = db.execute("SELECT * FROM submissions WHERE id = :id", id=submission_id)
    if not submission:
        return apology("issue getting submission for {}".format(submission_id))
    submission = submission[0]
    events = db.execute("SELECT * FROM events WHERE status != 'Inactive' ORDER BY status, name")
    categories = db.execute("SELECT * FROM categories WHERE status != 'Inactive' ORDER BY status, name")
    return render_template("film-festival-manager/submissions/update-submission.html", submission=submission, categories=categories, events=events, statuses=statuses())


@submissions_bp.route("/update", methods=["POST"])
@login_required
@role_required(role=["Admin", "Submitter"])
def update_submission_post():
    user = db.execute("SELECT username FROM users WHERE id = :id", id=session["user_id"])
    if not user:
        return apology("issue getting current user")
    user = user[0]
    updated_submission_id = request.form.get("updated-submission")
    updated_title_original_language = request.form.get("updated-title-original-language")
    updated_title_english_language = request.form.get("updated-title-english-language")
    updated_synopsis = request.form.get("updated-synopsis")
    updated_event = int(request.form.get("updated-event"))
    updated_category = int(request.form.get("updated-category"))
    updated_country_of_production = request.form.get("updated-country-of-production")
    updated_url = request.form.get("updated-url")
    updated_password = request.form.get("updated-password")
    updated_duration = request.form.get("updated-duration")
    updated_status = request.form.get("updated-status")
    submission = db.execute("SELECT * FROM submissions WHERE id = :id", id=updated_submission_id)
    if not submission:
        return apology("issue getting submission for {}".format(updated_submission_id))
    submission = submission[0]
    if submission["title_original_language"] != updated_title_original_language:
        db.execute("UPDATE submissions SET title_original_language = :updated_value, updated_by = :username, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_submission_id, username=user["username"], updated_value=updated_title_original_language)
    if submission["title_english_language"] != updated_title_english_language:
        db.execute("UPDATE submissions SET title_english_language = :updated_value, updated_by = :username, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_submission_id, username=user["username"], updated_value=updated_title_english_language)
    if submission["synopsis"] != updated_synopsis:
        db.execute("UPDATE submissions SET synopsis = :updated_value, updated_by = :username, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_submission_id, username=user["username"], updated_value=updated_synopsis)
    if int(submission["event_id"]) != updated_event:
        db.execute("UPDATE submissions SET event_id = :updated_value, updated_by = :username, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_submission_id, username=user["username"], updated_value=updated_event)
    if submission["category_id"] != updated_category:
        db.execute("UPDATE submissions SET category_id = :updated_value, updated_by = :username, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_submission_id, username=user["username"], updated_value=updated_category)
    if submission["country_of_production"] != updated_country_of_production:
        db.execute("UPDATE submissions SET country_of_production = :updated_value, updated_by = :username, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_submission_id, username=user["username"], updated_value=updated_country_of_production)
    if submission["url"] != updated_url:
        db.execute("UPDATE submissions SET url = :updated_value, updated_by = :username, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_submission_id, username=user["username"], updated_value=updated_url)
    if submission["password"] != updated_password:
        db.execute("UPDATE submissions SET password = :updated_value, updated_by = :username, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_submission_id, username=user["username"], updated_value=updated_password)
    if submission["duration"] != updated_duration:
        db.execute("UPDATE submissions SET duration = :updated_value, updated_by = :username, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_submission_id, username=user["username"], updated_value=updated_duration)
    if submission["status"] != updated_status:
        db.execute("UPDATE submissions SET status = :updated_value, updated_by = :username, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_submission_id, username=user["username"], updated_value=updated_status)
    return redirect(url_for("submissions.list_submissions"))
