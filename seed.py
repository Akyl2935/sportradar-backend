import json
from app.models.database import get_connection, create_tables


# this function inserts a team into the database
def insert_team(cursor, team, teams_cache):
    if team is not None:
        team_slug = team['slug']
        if team_slug in teams_cache:
            # team already exists so we just get the id from cache
            team_id = teams_cache[team_slug]
            return team_id
        else:
            team_name = team['name']
            team_official_name = team['officialName']
            team_abbreviation = team['abbreviation']
            team_country_code = team['teamCountryCode']

            cursor.execute(
                "INSERT INTO teams (name, official_name, slug, abbreviation, team_country_code) VALUES (?, ?, ?, ?, ?)",
                (team_name, team_official_name, team_slug, team_abbreviation, team_country_code)
            )
            new_team_id = cursor.lastrowid
            teams_cache[team_slug] = new_team_id
            return new_team_id
    else:
        # team is None so we return None
        return None


# this function inserts a stage into the database
def insert_stage(cursor, stage, stages_cache):
    stage_id_key = stage['id']
    if stage_id_key in stages_cache:
        # already in cache so just return the id
        existing_id = stages_cache[stage_id_key]
        return existing_id
    else:
        stage_name = stage['name']
        stage_ordering = stage['ordering']

        cursor.execute(
            "INSERT INTO stages (name, ordering) VALUES (?, ?)",
            (stage_name, stage_ordering)
        )
        new_stage_id = cursor.lastrowid
        stages_cache[stage_id_key] = new_stage_id
        return new_stage_id


def seed():
    # create the tables first
    create_tables()

    # connect to database
    conn = get_connection()
    cursor = conn.cursor()

    # open json file and load data
    file = open('data/events.json', 'r')
    data = json.load(file)
    file.close()

    # insert the sport
    sport_name = "Football"
    cursor.execute("INSERT INTO sports (name) VALUES (?)", (sport_name,))
    sport_id = cursor.lastrowid

    # get the first event to grab competition info
    all_events = data['data']
    first_event = all_events[0]
    competition_name = first_event['originCompetitionName']
    competition_slug = first_event['originCompetitionId']

    # insert competition
    cursor.execute(
        "INSERT INTO competitions (name, slug, _sport_id) VALUES (?, ?, ?)",
        (competition_name, competition_slug, sport_id)
    )
    competition_id = cursor.lastrowid

    # caches for teams and stages
    teams_cache = {}
    stages_cache = {}

    # loop through all events
    for i in range(len(all_events)):
        event = all_events[i]

        # insert home team
        home_team = event['homeTeam']
        home_team_id = insert_team(cursor, home_team, teams_cache)

        # insert away team
        away_team = event['awayTeam']
        away_team_id = insert_team(cursor, away_team, teams_cache)

        # insert the stage for this event
        event_stage = event['stage']
        stage_id = insert_stage(cursor, event_stage, stages_cache)

        # get event fields
        event_season = event['season']
        event_status = event['status']
        event_date = event['dateVenue']
        event_time = event['timeVenueUTC']
        venue_id = None

        # insert the event
        cursor.execute(
            """INSERT INTO events (season, status, date_venue, time_venue_utc,
            _home_team_id, _away_team_id, _competition_id, _stage_id, _venue_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (event_season, event_status, event_date, event_time,
             home_team_id, away_team_id, competition_id, stage_id, venue_id)
        )
        event_id = cursor.lastrowid

        # check if there is a result
        event_result = event['result']
        if event_result is not None:
            home_goals = event_result['homeGoals']
            away_goals = event_result['awayGoals']
            winner = event_result.get('winner')
            message = event_result.get('message')

            cursor.execute(
                "INSERT INTO results (_event_id, home_goals, away_goals, winner, message) VALUES (?, ?, ?, ?, ?)",
                (event_id, home_goals, away_goals, winner, message)
            )

    # save everything to database
    conn.commit()
    conn.close()
    print("Data seeded successfully!")


if __name__ == '__main__':
    seed()
