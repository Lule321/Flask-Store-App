from configuration import Configuration
from flask import Flask
from models import User, UserRole, database


application = Flask(__name__)
application.config.from_object(Configuration)

if __name__ == "__main__":
    database.init_app(application)
    with application.app_context():
        do = True
        while do:
            try:
                userRoles = UserRole.query.filter(UserRole.id > 1).all()

                for userRole in userRoles:
                    database.session.delete(userRole)
                    database.session.commit()

                users = User.query.filter(User.id > 1).all()

                for user in users:
                    database.session.delete(user)
                    database.session.commit()
                do = False
            except Exception as e:
                print(e)


