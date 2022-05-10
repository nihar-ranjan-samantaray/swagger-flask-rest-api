"""Flask CLI/Application entry point."""
import os

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_cors import CORS

from app.main import create_app, db
from app import api_bp

from applogger import logger

app = create_app(os.environ.get('BOILERPLATE_ENV') or 'dev')

CORS(app)

app.register_blueprint(api_bp)
app.app_context().push()

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def run():
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__=="__main__":
    manager.run()
