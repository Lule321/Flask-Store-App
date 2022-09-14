from flask import Flask, jsonify, request
from configuration import Configuration
from store.models import database, Product, Category, Order, ProductOrder
from flask_jwt_extended import JWTManager, get_jwt, jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy import func, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
import time

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

SLEEP_TIME_FOR_TESTS = 1

@application.route("/", methods = ["GET"])
def index():
    return "Customer index!"

@application.route("/search", methods = ["GET"])
@jwt_required()
def search():

    #time.sleep(SLEEP_TIME_FOR_TESTS)


    if not checkIfCustomer(get_jwt()):
        return jsonify(msg = "Missing Authorization Header"), 401
    productName = request.args.get("name", "")
    categoryName = request.args.get("category", "")

    productName = "%" + productName + "%"
    categoryName = "%" + categoryName + "%"
    #products = Product.query.filter(Product.name.like(productName)).all()
    #database.session.begin()
    #database.session.expire_all()

    #if database.session.is_active:
    #    database.session.close()
    #engine = create_engine(Configuration.SQLALCHEMY_DATABASE_URI)
    #session = Session(engine)
    #session.begin()
    #session.close()

    productsAndCategories = database.session.query(Product, Category)\
        .join(Category, Product.categories)\
        .filter(and_(Product.name.like(productName), Category.name.like(categoryName)))\
        .all()

    productsList = []
    categoriesList = []
    for productAndCategory in productsAndCategories:
        if productAndCategory[0].dictCustomer() not in productsList:
            productsList.append(productAndCategory[0].dictCustomer())
            #database.session.expire(productAndCategory[0])
        if productAndCategory[1].name not in categoriesList:
            categoriesList.append(productAndCategory[1].name)
            #database.session.expire(productAndCategory[1])
    #database.session.commit()
    #database.session.expire_all()
    #database.session.close()
    #print(f"{time.time()}:productsList = {productsList}\n categoriesList = {categoriesList}\n\nKraj")
    return jsonify(categories=categoriesList, products = productsList), 200

@application.route("/order", methods=["POST"])
@jwt_required()
def order():

    if not checkIfCustomer(get_jwt()):
        return jsonify(msg = "Missing Authorization Header"), 401

    listOfProducts = request.json.get("requests", None)

    orderItems = extractProductsFromListOfProducts(listOfProducts)

    if orderItems[0]:
        return jsonify(message = orderItems[1]), 400

    orderItems = orderItems[2]

    newOrder: Order = Order()

    newOrder.date = datetime.now()
    newOrder.status = "PENDING"
    newOrder.price = 0
    newOrder.customerEmail = get_jwt_identity()
    database.session.add(newOrder)
    database.session.commit()



    orderPrice = 0
    uncompleted: int = 0
    productOrders = []
    for orderItem in orderItems:
        product : Product = orderItem[0]
        quantity: int = orderItem[1]
        newProductOrder: ProductOrder = ProductOrder()
        newProductOrder.productId = product.id
        newProductOrder.orderId = newOrder.id
        newProductOrder.requested = quantity
        newProductOrder.price = product.price * quantity
        newProductOrder.date = newOrder.date
        orderPrice += newProductOrder.price

        if product.quantity >= newProductOrder.requested:
            newProductOrder.received = newProductOrder.requested
            product.quantity -= newProductOrder.requested
            #database.session.commit()
        else:
            uncompleted += 1
            newProductOrder.received = product.quantity
            product.quantity = 0
            #database.session.commit()

        productOrders.append(newProductOrder)


    newOrder.price = orderPrice
    newOrder.leftToComplete = uncompleted
    if uncompleted == 0:
        newOrder.status = "COMPLETE"

    for orderItem in orderItems:
        product: Product = orderItem[0]
        #print(f"Product name - {product.name} \t Product price - {product.price} \t Product quantity - {product.quantity}")
    database.session.add_all(productOrders)
    database.session.commit()


    return jsonify(id = newOrder.id), 200

@application.route("/status", methods = ["GET"])
@jwt_required()
def status():

    if not checkIfCustomer(get_jwt()):
        return jsonify(msg = "Missing Authorization Header"), 401

    customerEmail : str = get_jwt_identity()

    #database.session.commit()
    #database.session.begin()
    orders = Order.query.filter(Order.customerEmail == customerEmail).all()

    for i in range (0, len(orders)):
        orders[i] = orders[i].dictCustomer()

    database.session.commit()
    return jsonify(orders = orders), 200

def checkIfCustomer(jwt):
    roles = jwt["roles"]
    for role in roles:
        if role == "customer":
            return True
    return False

def extractProductsFromListOfProducts(listOfProducts):
    orderItems = []
    i: int = 0
    if listOfProducts == None:
        return [True, "Field requests is missing.", None]
    for productItem in listOfProducts:
        keys = productItem.keys()
        if "id" not in keys:
            return [True, f"Product id is missing for request number {i}.", None]
        elif "quantity" not in keys:
            return [True, f"Product quantity is missing for request number {i}.", None]
        elif not isinstance(productItem["id"], int) or productItem["id"] <= 0:
            return [True, f"Invalid product id for request number {i}.", None]
        elif not isinstance(productItem["quantity"], int) or productItem["quantity"] <= 0:
            return [True, f"Invalid product quantity for request number {i}.", None]



        product = Product.query.filter(Product.id == productItem["id"]).first()
        if product == None:
            return [True, f"Invalid product for request number {i}.", None]
        orderItems.append([product, productItem["quantity"]])
        i += 1

    return [False, "", orderItems]

@application.route("/sqlTrial", methods = ["GET"])
def sqlTrial():
    categoriesList = request.args.get("categories", "")
    productName = request.args.get("product", "")
    categoriesList = categoriesList.split(",")
    queryResult = database.session.query(Product, func.count(Category.name)).join(Category, Product.categories).filter(and_(Category.name.in_(categoriesList), Product.name == productName)).group_by(Product.id).all()
    #print(queryResult)

    return str(len(queryResult)), 200

if __name__ == "__main__":
    database.init_app(application)
    application.run(host="127.0.0.1", port="5003", debug = True)