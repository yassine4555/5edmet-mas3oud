from flask import Flask
from flask_migrate import Migrate
from config.config import Config
from models import db, User, Invite, File, Meeting

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

# Register blueprints
from routes.users import users_bp
from routes.invites import invites_bp
from routes.files import files_bp
from routes.meetings import meetings_bp

app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(invites_bp, url_prefix='/invites')
app.register_blueprint(files_bp, url_prefix='/file')
app.register_blueprint(meetings_bp, url_prefix='/meetings')

@app.route('/')
def index():
    try:
        # Check DB connection
        db.session.execute(db.text('SELECT 1'))
        return {"status": "SAVING_SERVER Ready", "db_connection": "OK"}
    except Exception as e:
        return {"status": "SAVING_SERVER Error", "db_connection": str(e)}, 500

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "service": "SAVING_SERVER",
        "version": "1.0"
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
