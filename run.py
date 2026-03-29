# entry point — starts the flask server
from flask import Flask
from app.routes.events import events_bp

app = Flask(__name__, template_folder='app/templates', static_folder='static')

# register the events blueprint (groups all /events routes together)
app.register_blueprint(events_bp)

if __name__ == '__main__':
    # debug=True auto-restarts server when you change code
    app.run(debug=True)
