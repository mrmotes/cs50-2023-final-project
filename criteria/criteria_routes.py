from flask import Blueprint, render_template, request, redirect, url_for
from helpers import apology, statuses
from helpers import *

criteria_bp = Blueprint("criteria", __name__, template_folder="templates/film-festival-manager/criteria", static_folder="static")


@criteria_bp.route("/", methods=["GET"])
@login_required
@role_required(role=["Admin"])
def list_evaluation_criteria():
    criteria = db.execute("SELECT id AS 'ID', name AS 'Evaluation Criteria', description AS 'Description', status AS 'Status' FROM criteria")
    category_criteria = db.execute("SELECT category_criteria.criteria_id, categories.name FROM category_criteria LEFT JOIN categories ON categories.id = category_criteria.category_id WHERE category_criteria.is_active = 1")
    for record in criteria:
        categories = [category["name"] for category in category_criteria if category["criteria_id"] == record["ID"]]
        record["Categories"] = ", ".join(categories)
    return render_template("film-festival-manager/criteria/list-evaluation-criteria.html", criteria=criteria)


@criteria_bp.route("/create-evaluation-criteria", methods=["GET", "POST"])
@login_required
@role_required(role=["Admin"])
def create_evaluation_criteria():
    active_categories = get_active_categories()
    if request.method == "GET":
        return render_template("film-festival-manager/criteria/create-criteria.html", categories=active_categories, statuses=statuses())
    elif request.method == "POST":
        criteria_name = request.form.get("criteria-name")
        criteria_description = request.form.get("criteria-description")
        criteria_status = request.form.get("criteria-status")
        new_criteria_id = db.execute("INSERT INTO criteria (name, description, status) VALUES(:name, :description, :status)", name=criteria_name, description=criteria_description, status=criteria_status)
        for category in active_categories:
            category_switch = request.form.get(str(category["id"]))
            if category_switch:
                category_criteria_id = int(str(category["id"]) + str(new_criteria_id))
                db.execute("INSERT INTO category_criteria (id, category_id, criteria_id, is_active) VALUES(:id, :category_id, :criteria_id, 1)", id=category_criteria_id, category_id=category["id"], criteria_id=new_criteria_id)
        return redirect(url_for("criteria.list_evaluation_criteria"))


@criteria_bp.route("/update-evaluation-criteria", methods=["GET"])
@login_required
@role_required(role=["Admin"])
def update_evaluation_criteria():
    criteria_id = request.args.get("criteria_id")
    criteria = get_criteria_by_id(criteria_id)
    if not criteria:
        return apology("issue getting criteria for {}".format(criteria_id))
    criteria_category_ids = [x["category_id"] for x in db.execute("SELECT category_id FROM category_criteria WHERE criteria_id = :id AND is_active = 1", id=criteria_id)]
    active_categories = get_active_categories()
    for category in active_categories:
        category["active_for_criteria"] = category["id"] in criteria_category_ids
    return render_template("film-festival-manager/criteria/update-evaluation-criteria.html", criteria=criteria, categories=active_categories, statuses=statuses())


@criteria_bp.route("/update-evaluation-criteria", methods=["POST"])
@login_required
@role_required(role=["Admin"])
def update_evaluation_criteria_post():
    active_categories = get_active_categories()
    updated_criteria_id = request.form.get("updated-criteria-id")
    updated_criteria_name = request.form.get("updated-criteria-name")
    updated_criteria_description = request.form.get("updated-criteria-description")
    updated_criteria_status = request.form.get("updated-criteria-status")
    criteria_to_update = get_criteria_by_id(updated_criteria_id)
    if not criteria_to_update:
        return apology("issue getting criteria for {}".format(updated_criteria_id))
    if criteria_to_update["name"] != updated_criteria_name:
        db.execute("UPDATE criteria SET name = :name, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_criteria_id, name=updated_criteria_name)
    if criteria_to_update["description"] != updated_criteria_description:
        db.execute("UPDATE criteria SET description = :description, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_criteria_id, description=updated_criteria_description)
    if criteria_to_update["status"] != updated_criteria_status:
        db.execute("UPDATE criteria SET status = :status, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_criteria_id, status=updated_criteria_status)
    for category in active_categories:
        category_switch = request.form.get(str(category["id"]))
        category_criteria_id = int(str(updated_criteria_id) + str(category["id"]))
        category_criteria = db.execute("SELECT * FROM category_criteria WHERE id = :id", id=category_criteria_id)
        needs_insert = len(category_criteria) != 1
        is_active = 1 if category_switch else 0
        if needs_insert:
            db.execute("INSERT INTO category_criteria (id, category_id, criteria_id, is_active) VALUES(:id, :category_id, :criteria_id, :is_active)", id=category_criteria_id, criteria_id=updated_criteria_id, category_id=category["id"], is_active=is_active)
        else:
            db.execute("UPDATE category_criteria SET is_active = :is_active WHERE id = :id", id=category_criteria_id, is_active=is_active)
    return redirect(url_for("criteria.list_evaluation_criteria"))
