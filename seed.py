import json
from app.models.database import get_connection, create_tables


# helper to insert a team only once — same team can appear in multiple events
# we use a cache dict to track which teams are already in the db by their slug
def insert_team(cursor, team, cache):
    if team is None:
        return None  # some events have no home team (TBD matches)
    if team['slug'] in cache:
        return cache[team['slug']]  # already inserted, just return the id

    # ? placeholders prevent SQL injection — sqlite fills them in safely with the tuple values
    cursor.execute(
        "INSERT INTO teams (name, official_name, slug, abbreviation, team_country_code) VALUES (?, ?, ?, ?, ?)",
        (team['name'], team['officialName'], team['slug'], team['abbreviation'], team['teamCountryCode'])
    )
    cache[team['slug']] = cursor.lastrowid  # save the generated id so we don't insert again
    return cursor.lastrowid


# same idea as insert_team — "ROUND OF 16" shows up multiple times, only insert once
def insert_stage(cursor, stage, cache):
    if stage['id'] in cache:
        return cache[stage['id']]

    cursor.execute(
        "INSERT INTO stages (name, ordering) VALUES (?, ?)",
        (stage['name'], stage['ordering'])
    )
    cache[stage['id']] = cursor.lastrowid
    return cursor.lastrowid


def seed():
    create_tables()
    conn = get_connection()
    cursor = conn.cursor()

    # load json data
    with open('data/events.json', 'r') as f:
        data = json.load(f)

    # insert sport first — other tables depend on it
    # lastrowid gives us the auto-generated id right after inserting
    cursor.execute("INSERT INTO sports (name) VALUES (?)", ("Football",))
    sport_id = cursor.lastrowid

    # insert competition once (all events share the same one)
    first_event = data['data'][0]
    cursor.execute(
        "INSERT INTO competitions (name, slug, _sport_id) VALUES (?, ?, ?)",
        (first_event['originCompetitionName'], first_event['originCompetitionId'], sport_id)
    )
    competition_id = cursor.lastrowid

    # track already inserted teams/stages to avoid duplicates
    teams_cache = {}
    stages_cache = {}

    for event in data['data']:
        # insert teams (returns None if team is null)
        home_team_id = insert_team(cursor, event['homeTeam'], teams_cache)
        away_team_id = insert_team(cursor, event['awayTeam'], teams_cache)

        # insert stage
        stage_id = insert_stage(cursor, event['stage'], stages_cache)

        # insert the event itself
        cursor.execute(
            """INSERT INTO events (season, status, date_venue, time_venue_utc,
            _home_team_id, _away_team_id, _competition_id, _stage_id, _venue_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (event['season'], event['status'], event['dateVenue'], event['timeVenueUTC'],
             home_team_id, away_team_id, competition_id, stage_id, None)
        )
        event_id = cursor.lastrowid

        # insert result if it exists
        if event['result'] is not None:
            result = event['result']
            cursor.execute(
                "INSERT INTO results (_event_id, home_goals, away_goals, winner, message) VALUES (?, ?, ?, ?, ?)",
                (event_id, result['homeGoals'], result['awayGoals'], result.get('winner'), result.get('message'))
            )

    conn.commit()
    conn.close()
    print("Data seeded successfully!")


if __name__ == '__main__':
    seed()
