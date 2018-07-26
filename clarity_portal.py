from flask_script import Manager

from portal import app

manager = Manager(app)

if __name__ == "__main__":
    manager.run()
