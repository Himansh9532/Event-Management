from app import app, db  # Import your app and db from app.py
from flask_script import Manager
from flask_migrate import MigrateCommand

manager = Manager(app)
manager.add_command('db', MigrateCommand)  # Add the db command to manager

if __name__ == "__main__":
    manager.run()  # Run the manager
