from flask import Blueprint, render_template, request, redirect, url_for
from helpers import apology, statuses, user_roles
from helpers import *

users_bp = Blueprint("users", __name__, template_folder="templates/film-festival-manager/users", static_folder="static")


@users_bp.route("/", methods=["GET"])
@login_required
@role_required(role=["Admin"])
def list_users():
    users = db.execute("SELECT id AS 'ID', username AS 'User', type AS 'Role', status AS 'Status' FROM users")
    user_categories = db.execute("SELECT user_categories.user_id, categories.name FROM user_categories LEFT JOIN categories ON categories.id = user_categories.category_id WHERE user_categories.is_active = 1")
    for user in users:
        categories = [user_category["name"] for user_category in user_categories if user_category["user_id"] == user["ID"]]
        user["Categories"] = ", ".join(categories)
    return render_template("film-festival-manager/users/list-users.html", users=users)



@users_bp.route("/update-user", methods=["GET"])
@login_required
@role_required(role=["Admin"])
def update_user():
    user_id = request.args.get("user_id")
    if not user_id:
        return apology("User ID not provided", 404)

    user = get_user_by_id(user_id)
    if not user:
        return apology("issue getting user for {}".format(user_id))
    user_category_ids = [x["category_id"] for x in db.execute("SELECT category_id FROM user_categories WHERE user_id = :id AND is_active = 1", id=user_id)]
    active_categories = get_active_categories()
    for category in active_categories:
        category["active_for_user"] = category["id"] in user_category_ids
    return render_template("film-festival-manager/users/update-user.html", user=user, categories=active_categories, statuses=statuses(), roles=user_roles())


@users_bp.route("/update-user", methods=["POST"])
@login_required
@role_required(role=["Admin"])
def update_user_post():
    active_categories = get_active_categories()
    updated_user_name = request.form.get("updated-user-name")
    updated_user_id = request.form.get("updated-user-id")
    updated_user_status = request.form.get("updated-user-status")
    updated_user_role = request.form.get("updated-user-role")
    user = get_user_by_id(updated_user_id)
    if not user:
        return apology("issue getting user for {}".format(updated_user_id))
    if user["username"] != updated_user_name:
        db.execute("UPDATE users SET username = :name, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_user_id, name=updated_user_name)
    if user["status"] != updated_user_status:
        db.execute("UPDATE users SET status = :status, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_user_id, status=updated_user_status)
    if user["type"] != updated_user_role:
        db.execute("UPDATE users SET type = :role, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_user_id, role=updated_user_role)
    for category in active_categories:
        category_switch = request.form.get(str(category["id"]))
        user_category_id = int(str(updated_user_id) + str(category["id"]))
        user_category = db.execute("SELECT * FROM user_categories WHERE id = :id", id=user_category_id)
        needs_insert = len(user_category) != 1
        is_active = 1 if category_switch else 0
        if needs_insert:
            db.execute("INSERT INTO user_categories (id, user_id, category_id, is_active) VALUES(:id, :user_id, :category_id, :is_active)", id=user_category_id, user_id=updated_user_id, category_id=category["id"], is_active=is_active)
        else:
            db.execute("UPDATE user_categories SET is_active = :is_active WHERE id = :id", id=user_category_id, is_active=is_active)
    return redirect(url_for("users.list_users"))
