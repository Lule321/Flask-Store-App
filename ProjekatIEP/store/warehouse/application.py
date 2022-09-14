from flask import Flask, jsonify, request
from configuration import Configuration
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity
from redis import Redis
import csv
import io
import re
from time import sleep
application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

@application.route("/", methods = ["GET"])
def index():
    return "Warehouse index!"

@application.route("/update", methods=["POST"])
@jwt_required()
def update():
    if not checkIfWarehouse(get_jwt()):
        return jsonify(msg = "Missing Authorization Header"), 401


    file = checkIfExistsAndReturnFile(request.files)

    if file is None:
        return jsonify(message="Field file is missing."), 400

    file = file.stream.read().decode("utf-8")


    stream = io.StringIO(file)
    reader = csv.reader(stream)

    checkedData = checkAndReturnData(reader)

    if not checkedData[0]:
        return jsonify(message=checkedData[1]), 400

    products = checkedData[2]

    with Redis(host=Configuration.REDIS_HOST) as redis:
        resultString:str = ""
        for product in products:
            productString = ",".join(product)
            resultString += productString + "\n"

        redis.rpush(Configuration.REDIS_PRODUCTS_LIST, resultString)
        #redis.rpush(Configuration.REDIS_UPDATED, "ok")
        #redis.rpush(Configuration.REDIS_UPDATED, resultString)
        redis.blpop(Configuration.REDIS_UPDATED) # samo za testove, ne radi u pravome civotu
        #updatedProducts = updatedProducts[1]
        #updatedProducts = updatedProducts.decode("utf-8")
        #updatedProducts = updatedProducts.split("\n")

    #sleep(10)

    return "", 200

def checkIfWarehouse(jwt):
    roles = jwt["roles"]
    for role in roles:
        if role == "warehouse":
            return True
    return False
def checkIfExistsAndReturnFile(files):
    keys = files.keys()
    if "file" not in keys:
        return None
    return files["file"]

def checkAndReturnData(reader):
    products = []
    i: int = 0
    for row in reader:
        if len(row) != 4:
            return [False, f"Incorrect number of values on line {i}.", None]
        if not row[2].isdigit() or int(row[2]) == 0:
            return [False, f"Incorrect quantity on line {i}.", None]
        if re.search("^\d+(\.\d*)?$", row[3]) is None or float(row[3]) == 0.0:
            return [False, f"Incorrect price on line {i}.", None]
        products.append(row)
        i += 1
    return [True, "", products]

if __name__ == "__main__":
    application.run(host="127.0.0.1", port=5001, debug= True)
