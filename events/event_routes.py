from flask import Blueprint, render_template, request, redirect, url_for
from helpers import apology, statuses
from helpers import *

events_bp = Blueprint("events", __name__, template_folder="templates/film-festival-manager/", static_folder="static")


@events_bp.route("/", methods=["GET"])
@login_required
@role_required(role=["Admin"])
def list_events():
    events = db.execute("SELECT id AS 'ID', name AS 'Event', status AS 'Status' FROM events")
    return render_template("film-festival-manager/events/list-events.html", events=events)


@events_bp.route("/create-event", methods=["GET", "POST"])
@login_required
@role_required(role=["Admin"])
def create_event():
    if request.method == "GET":
        return render_template("film-festival-manager/events/create-event.html", statuses=statuses())
    elif request.method == "POST":
        event_name = request.form.get("event-name")
        event_status = request.form.get("event-status")
        if not event_name:
            return apology("you must input an event name")

        db.execute("INSERT INTO events (name, status) VALUES(:name, :status)", name=event_name, status=event_status)
        return redirect(url_for("events.list_events"))


@events_bp.route("/update-event", methods=["GET"])
@login_required
@role_required(role=["Admin"])
def update_event():
    event_id = request.args.get("event_id")
    if not event_id:
        return apology("Event ID not provided")

    event = db.execute("SELECT * FROM events WHERE id = :id", id=event_id)
    if not event:
        return apology("issue getting event for {}".format(event_id))

    return render_template("film-festival-manager/events/update-event.html", event=event[0], statuses=statuses())


@events_bp.route("/update-event", methods=["POST"])
@login_required
@role_required(role=["Admin"])
def update_event_post():
    updated_event_id = request.form.get("updated-event-id")
    updated_event_name = request.form.get("updated-event-name")
    updated_event_status = request.form.get("updated-event-status")
    event_to_update = db.execute("SELECT id, name, status FROM events WHERE id = :id", id=updated_event_id)
    if not event_to_update:
        return apology("issue getting event for {}".format(updated_event_id))
    event_to_update = event_to_update[0]
    if event_to_update["name"] != updated_event_name:
        db.execute("UPDATE events SET name = :name, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_event_id, name=updated_event_name)
    if event_to_update["status"] != updated_event_status:
        db.execute("UPDATE events SET status = :status, updated_at = CURRENT_TIMESTAMP WHERE id = :id", id=updated_event_id, status=updated_event_status)
    return redirect(url_for("events.list_events"))
