from flask import Blueprint, render_template, request, redirect, url_for
from helpers import apology, statuses
from helpers import *

categories_bp = Blueprint("categories", __name__, template_folder="templates/film-festival-manager/categories", static_folder="static")


@categories_bp.route("/", methods=["GET"])
@login_required
@role_required(role=["Admin"])
def list_categories():
    # evaluation_criteria = get_active_evaluation_criteria()
    evaluation_criteria = db.execute("SELECT category_id, (SELECT name FROM criteria WHERE id = category_criteria.criteria_id) AS 'name' FROM category_criteria WHERE is_active = 1")
    categories = db.execute("SELECT categories.id AS 'ID', categories.name AS 'Category', categories.status AS 'Status', events.name AS 'Event' FROM categories LEFT JOIN events ON events.id = categories.event_id")
    for category in categories:
        category_criteria = [criteria["name"] for criteria in evaluation_criteria if criteria["category_id"] == category["ID"]]
        category["Evaluation Criteria"] = ", ".join(category_criteria)
    return render_template("film-festival-manager/categories/list-categories.html", categories=categories)


@categories_bp.route("/create-category", methods=["GET", "POST"])
@login_required
@role_required(role=["Admin"])
def create_category():
    evaluation_criteria = get_active_evaluation_criteria()
    if request.method == "GET":
        events = get_active_events()
        return render_template("film-festival-manager/categories/create-category.html", events=events, statuses=statuses(), evaluation_criteria=evaluation_criteria)

    elif request.method == "POST":
        category_name = request.form.get("category-name")
        category_status = request.form.get("category-status")
        category_event_id = request.form.get("category-event")
        if not category_name:
            return apology("you must input a category name")
        new_category_id = db.execute("INSERT INTO categories (name, status, event_id) VALUES(:name, :status, :event_id)", name=category_name, status=category_status, event_id=category_event_id)
        for criteria in evaluation_criteria:
            criteria_switch = request.form.get(str(criteria["id"]))
            if criteria_switch:
                category_criteria_id = int(str(new_category_id) + str(criteria["id"]))
                db.execute("INSERT INTO category_criteria (id, category_id, criteria_id, is_active) VALUES(:id, :category_id, :criteria_id, 1)", id=category_criteria_id, category_id=new_category_id, criteria_id=criteria["id"])
        return redirect(url_for("categories.list_categories"))


@categories_bp.route("/update-category", methods=["GET"])
@login_required
@role_required(role=["Admin"])
def update_category():
    category_id = request.args.get("category_id")
    if not category_id:
        return apology("Category ID not provided", 404)

    category = get_category_by_id(category_id)

    if not category:
        return apology("Category not found", 404)
    evaluation_criteria = get_active_evaluation_criteria()
    criteria_category_ids = [x["criteria_id"] for x in db.execute("SELECT criteria_id FROM category_criteria WHERE category_id = :id AND is_active = 1", id=category_id)]
    for value in evaluation_criteria:
        value["active_for_category"] = value["id"] in criteria_category_ids
    events = get_active_events()
    return render_template("film-festival-manager/categories/update-category.html", category=category, events=events, evaluation_criteria=evaluation_criteria,  statuses=statuses())


@categories_bp.route("/update-category", methods=["POST"])
@login_required
@role_required(role=["Admin"])
def update_category_post():
    if request.method == "POST":
        evaluation_criteria = get_active_evaluation_criteria()
        updated_category_id = request.form.get("updated-category-id")
        updated_name = request.form.get("updated-category-name")
        updated_event_id = request.form.get("updated-category-event")
        updated_status = request.form.get("updated-category-status")
        category_to_update = db.execute("SELECT id, name, event_id, status FROM categories WHERE id = :id", id=updated_category_id)

        if not category_to_update:
            return apology("issue getting category for {}".format(updated_category_id))
        category_to_update = category_to_update[0]

        if category_to_update["name"] != updated_name:
            db.execute("UPDATE categories SET name = :name, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_category_id, name=updated_name)
        if category_to_update["event_id"] != updated_event_id:
            db.execute("UPDATE categories SET event_id = :event_id, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_category_id, event_id=updated_event_id)
        if category_to_update["status"] != updated_status:
            db.execute("UPDATE categories SET status = :status, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_category_id, status=updated_status)
        for record in evaluation_criteria:
            criteria_switch = request.form.get(str(record["id"]))
            category_criteria_id = int(str(updated_category_id) + str(record["id"]))
            category_criteria = db.execute("SELECT * FROM category_criteria WHERE id = :id", id=category_criteria_id)
            needs_insert = len(category_criteria) != 1
            is_active = 1 if criteria_switch else 0
            if needs_insert:
                db.execute("INSERT INTO category_criteria (id, category_id, criteria_id, is_active) VALUES(:id, :category_id, :criteria_id, :is_active)", id=category_criteria_id, category_id=updated_category_id, criteria_id=record["id"], is_active=is_active)
            else:
                db.execute("UPDATE category_criteria SET is_active = :is_active WHERE id = :id", id=category_criteria_id, is_active=is_active)
        return redirect(url_for("categories.list_categories"))

    return redirect(url_for("categories.list_categories"))
