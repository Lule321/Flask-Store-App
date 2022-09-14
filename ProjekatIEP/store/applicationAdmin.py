from flask import Flask, jsonify, request
from configuration import Configuration
from flask_jwt_extended import jwt_required, get_jwt, JWTManager
from models import database, Product, ProductOrder, Category
from sqlalchemy import func, and_
application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)
from datetime import datetime

@application.route("/", methods = ["GET"])
def index():
    return str(datetime.now())

@application.route("/productStatistics", methods=["GET"])
@jwt_required()
def productStaticstics():

    if not checkIfAdmin(get_jwt()):
        return jsonify(msg = "Missing Authorization Header"), 401

    #products2 = Product.query.filter(ProductOrder.query.filter(ProductOrder.productId == Product.id).exists()).all()
    products = database.session.query(Product.name, func.sum(ProductOrder.requested), func.sum(ProductOrder.requested - ProductOrder.received))\
        .join(ProductOrder, Product.productorders)\
        .group_by(Product.id)\
        .all()

    #print(str(products) + "\nKraj\n")

    productsResult = []
    #productsResult2 = []
    for i in range(0, len(products)):
        #temp2 = products2[i].productStatistics()
        #productsResult2.append(temp2)
        temp = {'name' : products[i][0], 'sold' : int(products[i][1]), 'waiting' : int(products[i][2])}
        #if temp["sold"] != 0:
        productsResult.append(temp)
    #print(str(productsResult) + "\nKraj1\n")
    #print(str(productsResult2) + "\nKraj2\n")
    database.session.commit()

    return jsonify(statistics = productsResult), 200


@application.route("/categoryStatistics", methods=["GET"])
@jwt_required()
def categoryStatistics():

    if not checkIfAdmin(get_jwt()):
        return jsonify(msg = "Missing Authorization Header"), 401

    categories = database.session.query(Category.name)\
        .join(Product, Category.products)\
        .outerjoin(ProductOrder)\
        .order_by(func.sum(ProductOrder.requested).desc(), Category.name)\
        .group_by(Category.id)\
        .all()
    #categories2 = Category.query.all()
    #categories2 = prepareCateogriesForSort(categories2)
    #categories2 = quickSortCategories(categories2)
    result = []
    for i in range(0, len(categories)):
        result.append(categories[i][0])
    print(str(categories) + "\nKraj1\n")
    #print(str(categories2) + "\nKraj2\n")

    return jsonify(statistics = result), 200



def checkIfAdmin(jwt):
    roles = jwt["roles"]
    for role in roles:
        if role == "admin":
            return True

    return False

def prepareCateogriesForSort(categories):
    for i in range(0, len(categories)):
        categories[i] = [categories[i], categories[i].numberOfSoldProducts()]
    return categories

def quickSortCategories(categories):
    low = 0
    high = len(categories) - 1
    stack = [[low, high]]

    while len(stack) != 0:
        positions = stack.pop()
        low = positions[0]
        high = positions[1]
        while low < high:
            categories,i = partitionQuickSortCategories(low, high, categories)
            if i + 1 < high:
                stack.append([i+1,high])
            high = i - 1
            #print(categories)


    return categories

def partitionQuickSortCategories(low, high, categories):
    i = low
    pivot = categories[high][1]
    pivotName : str = categories[high][0].name
    for j in range(low, high):
        if categories[j][1] > pivot or (categories[j][1] == pivot and categories[j][0].name < pivotName):
            temp = categories[i]
            categories[i] = categories[j]
            categories[j] = temp
            i += 1
    temp = categories[high]
    categories[high] = categories[i]
    categories[i] = temp
    return categories,i

if __name__ == "__main__":
    database.init_app(application)
    application.run(host="0.0.0.0", port="5004", debug=True)