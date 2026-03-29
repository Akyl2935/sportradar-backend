# all event-related routes live here
from flask import Blueprint, jsonify, request
from app.models.database import get_connection

# blueprint lets us group routes in a separate file instead of cramming everything in run.py
events_bp = Blueprint('events', __name__)


# GET /events — return all events with team names, competition, stage
# uses one JOIN query instead of querying inside a loop (much more efficient)
@events_bp.route('/events', methods=['GET'])
def get_events():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            e.id,
            e.season,
            e.status,
            e.date_venue,
            e.time_venue_utc,
            ht.name AS home_team,
            at.name AS away_team,
            c.name AS competition,
            s.name AS stage,
            r.home_goals,
            r.away_goals,
            r.winner
        FROM events e
        LEFT JOIN teams ht ON e._home_team_id = ht.id
        LEFT JOIN teams at ON e._away_team_id = at.id
        JOIN competitions c ON e._competition_id = c.id
        JOIN stages s ON e._stage_id = s.id
        LEFT JOIN results r ON r._event_id = e.id
    ''')

    # convert each row to a dict so flask can turn it into JSON
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(events)


# GET /events/<id> — return one specific event by id
@events_bp.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            e.id,
            e.season,
            e.status,
            e.date_venue,
            e.time_venue_utc,
            ht.name AS home_team,
            at.name AS away_team,
            c.name AS competition,
            s.name AS stage,
            r.home_goals,
            r.away_goals,
            r.winner
        FROM events e
        LEFT JOIN teams ht ON e._home_team_id = ht.id
        LEFT JOIN teams at ON e._away_team_id = at.id
        JOIN competitions c ON e._competition_id = c.id
        JOIN stages s ON e._stage_id = s.id
        LEFT JOIN results r ON r._event_id = e.id
        WHERE e.id = ?
    ''', (event_id,))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Event not found"}), 404

    return jsonify(dict(row))


# POST /events — add a new event
# expects JSON body with: season, status, date_venue, time_venue_utc,
# _home_team_id, _away_team_id, _competition_id, _stage_id
@events_bp.route('/events', methods=['POST'])
def create_event():
    data = request.get_json()  # parse the JSON body from the request

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO events (season, status, date_venue, time_venue_utc,
        _home_team_id, _away_team_id, _competition_id, _stage_id, _venue_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data['season'],
            data['status'],
            data['date_venue'],
            data['time_venue_utc'],
            data.get('_home_team_id'),      # .get() returns None if key missing
            data.get('_away_team_id'),
            data['_competition_id'],
            data['_stage_id'],
            data.get('_venue_id')
        )
    )

    event_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({"id": event_id, "message": "Event created"}), 201
