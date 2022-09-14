from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database, Role, User, UserRole
from sqlalchemy_utils import database_exists, create_database

application = Flask(__name__)
application.config.from_object(Configuration)


migrateObject = Migrate(application, database)

done = False

#skloni posle if

if __name__ == "__main__":

    while not done:
        try:
            if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
                create_database(application.config["SQLALCHEMY_DATABASE_URI"])

            database.init_app(application)

            with application.app_context() as context:
                init()
                migrate(message="Production migration")
                upgrade()

                adminRole = Role(name="admin")
                customerRole = Role(name="customer")
                warehouseRole = Role(name="warehouse")

                database.session.add(adminRole)
                database.session.add(customerRole)
                database.session.add(warehouseRole)
                database.session.commit()

                admin = User(email="admin@admin.com", forename = "admin", surname = "admin", password = "1")

                database.session.add(admin)
                database.session.commit()

                userRole = UserRole(
                    userId = admin.id,
                    roleId = adminRole.id
                )

                database.session.add(userRole)
                database.session.commit()
                done = True
        except Exception as error:
            print(error)