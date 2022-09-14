import os

databaseURL = os.environ["DATABASE_URL"]

class Configuration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseURL}/storedb"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"