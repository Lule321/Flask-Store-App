from flask import Flask
from configuration import Configuration
from redis import Redis
from models import database, Product, Category, ProductCategory, ProductOrder, Order
import time
from sqlalchemy import and_
from sqlalchemy import func

application = Flask(__name__)
application.config.from_object(Configuration)
TIME_FOR_WAITING = 10

# @application.route("/", methods = ["GET"])
# def index():
#    return "Daemon index!"


if __name__ == "__main__":
    database.init_app(application)
    # application.run(host="localhost", port="5002", debug=True)
    while True:
        try:
            #engine = database.engine()
            #engine.execute("UNLOCK TABLES")
            with Redis(host=Configuration.REDIS_HOST) as redis:
                with application.app_context() as context:
                    while True:
                        #if gotInfo:
                        #    redis.rpush(Configuration.REDIS_UPDATED, "ok")
                        #    gotInfo = False
                        updatedProducts = redis.blpop(Configuration.REDIS_PRODUCTS_LIST)
                        updatedProducts = updatedProducts[1]
                        if updatedProducts is not None:
                        #    gotInfo = True
                            #engine.execute("LOCK TABLES products WRITE, categories WRITE, orders WRITE")
                            updatedProducts = updatedProducts.decode("utf-8")
                            updatedProducts = updatedProducts.split("\n")
                            updatedProducts = updatedProducts[:-1]
                            for updatedProduct in updatedProducts:
                                # updatedProduct = updatedProduct.decode("utf-8")
                                # print(updatedProduct)

                                updatedProductSplit = updatedProduct.split(",")
                                categoriesList = updatedProductSplit[0].split("|")

                                #product: Product = Product.query.filter(Product.name == updatedProductSplit[1]).first()
                                queryResult = database.session.query(Product, func.count(Category.name))\
                                    .join(Product, Category.products)\
                                    .filter(and_(Product.name == updatedProductSplit[1], Category.name.in_(categoriesList)))\
                                    .group_by(Product.id)\
                                    .all()


                                product: Product = None
                                #print(str(queryResultTest))
                                if len(queryResult) != 0 and len(queryResult[0]) == 2 and queryResult[0][1] == len(categoriesList):
                                    product = queryResult[0][0]

                                #print(queryResult)
                                # Posle ubaci kad postoji produkt koji je trazen
                                if product is not None:

                                        database.session.commit()
                                        #print(
                                        #    f"1.Product name - {product.name} \t Product price - {product.price} \t Product quantity - {product.quantity}")
                                        product.price = ((product.price * product.quantity + int(
                                            updatedProductSplit[2]) * float(updatedProductSplit[3])) / (
                                                                     product.quantity + int(updatedProductSplit[2])))

                                        database.session.commit()
                                        #print(
                                        #    f"2.Product name - {product.name} \t Product price - {product.price} \t Product quantity - {product.quantity}")
                                        # product.quantity += int(updatedProductSplit[2])
                                        quantity: int = product.quantity + int(updatedProductSplit[2])
                                        #print(quantity)
                                        checkForMoreProductOrders: bool = True

                                        while (checkForMoreProductOrders):

                                            productOrder: ProductOrder = ProductOrder.query.filter(
                                                and_(ProductOrder.requested > ProductOrder.received,
                                                     ProductOrder.productId == product.id)).order_by(
                                                ProductOrder.date.asc()).first()
                                            if productOrder is not None:
                                                if quantity >= productOrder.requested - productOrder.received:
                                                    # product.quantity >= productOrder.requested - productOrder.received:
                                                    # product.quantity -= productOrder.requested - productOrder.received
                                                    quantity -= productOrder.requested - productOrder.received
                                                    productOrder.received = productOrder.requested
                                                    order: Order = productOrder.order
                                                    order.leftToComplete -= 1
                                                    if order.leftToComplete == 0:
                                                        order.status = "COMPLETE"
                                                    if quantity == 0:
                                                        # product.quantity == 0:
                                                        checkForMoreProductOrders = False
                                                    # database.session.commit()
                                                else:
                                                    productOrder.received += quantity
                                                    # productOrder.received += product.quantity
                                                    quantity = 0
                                                    # product.quantity = 0
                                                    checkForMoreProductOrders = False
                                                    # database.session.commit()
                                                database.session.commit()
                                            else:
                                                checkForMoreProductOrders = False
                                        product.quantity = quantity
                                        #print(
                                        #    f"3.Product name - {product.name} \t Product price - {product.price} \t Product quantity - {product.quantity}")
                                        database.session.commit()

                                        # posle provera narudzbina

                                elif len(queryResult) == 0 and Product.query.filter(Product.name == updatedProductSplit[1]).first() == None:
                                    product = Product(name=updatedProductSplit[1], quantity=int(updatedProductSplit[2]),
                                                      price=float(updatedProductSplit[3]))
                                    database.session.add(product)
                                    database.session.commit()

                                    categories = []
                                    for categoryStr in categoriesList:
                                        category = Category.query.filter(Category.name == categoryStr).first()
                                        if category is None:
                                            category = Category(name=categoryStr)
                                            database.session.add(category)
                                            database.session.commit()
                                        categories.append(category)

                                    productCategories = []
                                    for category in categories:
                                        productCategory = ProductCategory(productId=product.id, categoryId=category.id)
                                        productCategories.append(productCategory)

                                    database.session.add_all(productCategories)
                                    database.session.commit()
                            #print(str(time.time()) + ":" + str(updatedProducts) + "\n\nKraj")
                            redis.rpush(Configuration.REDIS_UPDATED,"ok")
        except Exception as exception:
            print(exception)

                    # updatedProduct = redis.lpop(Configuration.REDIS_PRODUCTS_LIST)

                # time.sleep(TIME_FOR_WAITING)

