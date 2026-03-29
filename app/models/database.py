import sqlite3


# connect to db and configure it
def get_connection():
    conn = sqlite3.connect('sports_calendar.db', timeout=10)  # timeout avoids "database is locked" errors
    conn.row_factory = sqlite3.Row  # lets us access columns by name 
    conn.execute("PRAGMA foreign_keys = ON")  # sqlite has foreign keys off by default, this enforces them
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # lookup tables (no dependencies)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            official_name TEXT,
            slug TEXT,
            abbreviation TEXT,
            team_country_code TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS venues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT,
            country TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ordering INTEGER
        )
    ''')

    # competition belongs to a sport
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS competitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT,
            _sport_id INTEGER NOT NULL,
            FOREIGN KEY (_sport_id) REFERENCES sports(id)
        )
    ''')

    # main events table - each event is a match between two teams
    # _home_team_id / _away_team_id point to teams table (nullable because some matches have TBD teams)
    # _competition_id / _stage_id are required - every event must belong to a competition and stage
    # _venue_id is nullable because not every event has a stadium assigned yet
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            season INTEGER NOT NULL,
            status TEXT NOT NULL,
            date_venue DATE NOT NULL,
            time_venue_utc TIME,
            _home_team_id INTEGER, 
            _away_team_id INTEGER,
            _competition_id INTEGER NOT NULL,
            _stage_id INTEGER NOT NULL,
            _venue_id INTEGER,
            FOREIGN KEY (_home_team_id) REFERENCES teams(id),
            FOREIGN KEY (_away_team_id) REFERENCES teams(id),
            FOREIGN KEY (_competition_id) REFERENCES competitions(id),
            FOREIGN KEY (_stage_id) REFERENCES stages(id),
            FOREIGN KEY (_venue_id) REFERENCES venues(id)
        )
    ''')

    # match result tied to one event (1:1)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            _event_id INTEGER NOT NULL,
            home_goals INTEGER,
            away_goals INTEGER,
            winner TEXT,
            message TEXT,
            FOREIGN KEY (_event_id) REFERENCES events(id)
        )
    ''')

    # save changes and close
    conn.commit()
    conn.close()


# run directly to create tables
if __name__ == '__main__':
    create_tables()
    print("Tables created successfully!")
