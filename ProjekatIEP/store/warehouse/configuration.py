import os

redis = os.environ["REDIS"]

class Configuration():
    REDIS_HOST = redis
    #REDIS_HOST = "localhost"
    REDIS_PRODUCTS_LIST="products"
    REDIS_UPDATED = "updated"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"

