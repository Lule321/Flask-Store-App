import os

redis = os.environ["REDIS"]
databaseURL = os.environ["DATABASE_URL"]

class Configuration():
    REDIS_HOST = redis
    #REDIS_HOST = "localhost"
    REDIS_PRODUCTS_LIST = "products"
    REDIS_UPDATED = "updated"
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseURL}/storedb"
    #SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@localhost:3307/storedb"