# Sports Event Calendar

A web app that displays sports events and lets you add new ones. Built with Python (Flask) and SQLite.

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Create the database and seed it with sample data:
```
python seed.py
```

3. Run the server:
```
python run.py
```

4. Open `http://127.0.0.1:5000` in your browser.

## Project Structure

- `run.py` — starts the flask server
- `seed.py` — loads events.json into the database
- `app/models/database.py` — db connection and table definitions
- `app/routes/events.py` — API endpoints (GET/POST events, teams, etc.)
- `app/templates/index.html` — frontend page
- `static/style.css` — styling
- `data/events.json` — sample event data
- `schema/erd table.pdf` — ERD diagram

## API Endpoints

- `GET /events` — returns all events with team names, competition, stage, and results
- `GET /events/<id>` — returns a single event
- `POST /events` — adds a new event
- `GET /teams` — list of teams (used for dropdowns)
- `GET /competitions` — list of competitions
- `GET /stages` — list of stages

## Decisions and Assumptions

- Picked **SQLite** because it needs no setup and works out of the box with Python
- Database follows **3NF** — teams, stages, competitions, and venues are in separate tables to avoid repeating data
- Foreign keys use the **underscore prefix** naming (`_home_team_id`, `_competition_id`, etc.) as required
- Home/away team fields are nullable since some matches have TBD teams
- The GET /events query uses **JOINs** instead of querying in a loop to keep it efficient
- Frontend is vanilla HTML + JS, no frameworks — kept it simple
