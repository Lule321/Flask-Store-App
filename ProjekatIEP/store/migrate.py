from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, upgrade, downgrade, migrate
from models import database, Order, ProductOrder, ProductCategory, Product, Category
from sqlalchemy_utils import database_exists, create_database

application = Flask(__name__)
application.config.from_object(Configuration)

migrateObject = Migrate(application, database)
done = False

if __name__ == "__main__":

    while not done:
        try:
            if not database_exists(Configuration.SQLALCHEMY_DATABASE_URI):
                create_database(Configuration.SQLALCHEMY_DATABASE_URI)

            database.init_app(application)

            with application.app_context() as context:
                init()
                migrate(message = "Production migration")
                upgrade()

                database.session.commit()

                done = True
        except Exception as error:
            print(error)