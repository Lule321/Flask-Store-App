from flask import Flask
from configuration import Configuration
from redis import Redis
from models import database, Product, Category, ProductCategory, ProductOrder, Order
import time
from sqlalchemy import and_

application = Flask(__name__)
application.config.from_object(Configuration)
TIME_FOR_WAITING = 10

#@application.route("/", methods = ["GET"])
#def index():
#    return "Daemon index!"



if __name__ == "__main__":
    database.init_app(application)
    #application.run(host="localhost", port="5002", debug=True)
    with Redis(host=Configuration.REDIS_HOST) as redis:
        with application.app_context() as context:
            while True:
                updatedProduct = redis.lpop(Configuration.REDIS_PRODUCTS_LIST)
                while updatedProduct is not None:
                    updatedProduct = updatedProduct.decode("utf-8")
                    #print(updatedProduct)

                    updatedProductSplit = updatedProduct.split(",")
                    categoriesList = updatedProductSplit[0].split("|")

                    product: Product = Product.query.filter(Product.name==updatedProductSplit[1]).first()

                    #Posle ubaci kad postoji produkt koji je trazen
                    if product is not None:
                        categoriesOfProduct = product.categories
                        if len(categoriesList) == len(categoriesOfProduct):
                            i = len(categoriesOfProduct)
                            for category in categoriesOfProduct:
                                for category2 in categoriesList:
                                    if category.name == category2:
                                        i -=1
                                        break

                            if i == 0:
                                database.session.commit()
                                print(f"1.Product name - {product.name} \t Product price - {product.price} \t Product quantity - {product.quantity}")
                                product.price = ((product.price * product.quantity + int(updatedProductSplit[2]) * float(updatedProductSplit[3]))/(product.quantity + int(updatedProductSplit[2])))

                                database.session.commit()
                                print(
                                    f"2.Product name - {product.name} \t Product price - {product.price} \t Product quantity - {product.quantity}")
                                #product.quantity += int(updatedProductSplit[2])
                                quantity: int = product.quantity + int(updatedProductSplit[2])
                                print(quantity)
                                checkForMoreProductOrders: bool = True

                                while(checkForMoreProductOrders):

                                    productOrder: ProductOrder = ProductOrder.query.filter(and_(ProductOrder.requested > ProductOrder.received, ProductOrder.productId == product.id)).order_by(ProductOrder.date.asc()).first()
                                    if productOrder is not None:
                                        if quantity >= productOrder.requested - productOrder.received:
                                            #product.quantity >= productOrder.requested - productOrder.received:
                                            #product.quantity -= productOrder.requested - productOrder.received
                                            quantity -= productOrder.requested - productOrder.received
                                            productOrder.received = productOrder.requested
                                            order : Order = productOrder.order
                                            order.leftToComplete -= 1
                                            if order.leftToComplete == 0:
                                                order.status = "COMPLETE"
                                            if quantity == 0:
                                                #product.quantity == 0:
                                                checkForMoreProductOrders = False
                                            #database.session.commit()
                                        else:
                                            productOrder.received += quantity
                                            #productOrder.received += product.quantity
                                            quantity = 0
                                            #product.quantity = 0
                                            checkForMoreProductOrders = False
                                            #database.session.commit()
                                        database.session.commit()
                                    else:
                                        checkForMoreProductOrders = False
                                product.quantity = quantity
                                print(
                                    f"3.Product name - {product.name} \t Product price - {product.price} \t Product quantity - {product.quantity}")
                                database.session.commit()

                                # posle provera narudzbina

                    else:
                        product = Product(name=updatedProductSplit[1], quantity= int(updatedProductSplit[2]), price = float(updatedProductSplit[3]))
                        database.session.add(product)
                        database.session.commit()

                        categories = []
                        for categoryStr in categoriesList:
                            category = Category.query.filter(Category.name==categoryStr).first()
                            if category is None:
                                category = Category(name=categoryStr)
                                database.session.add(category)
                                database.session.commit()
                            categories.append(category)

                        productCategories = []
                        for category in categories:
                            productCategory = ProductCategory(productId = product.id, categoryId = category.id)
                            productCategories.append(productCategory)

                        database.session.add_all(productCategories)
                        database.session.commit()



                    updatedProduct = redis.lpop(Configuration.REDIS_PRODUCTS_LIST)

                #time.sleep(TIME_FOR_WAITING)
"""
from flask import Flask
from configuration import Configuration
from redis import Redis
from models import database, Product, Category, ProductCategory, ProductOrder, Order
import time
from sqlalchemy import and_

application = Flask(__name__)
application.config.from_object(Configuration)
TIME_FOR_WAITING = 10

#@application.route("/", methods = ["GET"])
#def index():
#    return "Daemon index!"



if __name__ == "__main__":
    database.init_app(application)
    #application.run(host="localhost", port="5002", debug=True)
    with Redis(host=Configuration.REDIS_HOST) as redis:
        with application.app_context() as context:
            while True:
                #updatedProduct = redis.lpop(Configuration.REDIS_PRODUCTS_LIST)
                updatedProducts = redis.lrange(Configuration.REDIS_PRODUCTS_LIST, 0, -1)
                if updatedProducts is not None:
                    for updatedProduct in updatedProducts:
                #while updatedProduct is not None:
                        updatedProduct = updatedProduct.decode("utf-8")
                        #print(updatedProduct)

                        updatedProductSplit = updatedProduct.split(",")
                        categoriesList = updatedProductSplit[0].split("|")

                        product: Product = Product.query.filter(Product.name==updatedProductSplit[1]).first()

                        #Posle ubaci kad postoji produkt koji je trazen
                        if product is not None:
                            categoriesOfProduct = product.categories
                            if len(categoriesList) == len(categoriesOfProduct):
                                i = len(categoriesOfProduct)
                                for category in categoriesOfProduct:
                                    for category2 in categoriesList:
                                        if category.name == category2:
                                            i -=1
                                            break

                                if i == 0:
                                    database.session.commit()
                                    print(f"1.Product name - {product.name} \t Product price - {product.price} \t Product quantity - {product.quantity}")
                                    product.price = ((product.price * product.quantity + int(updatedProductSplit[2]) * float(updatedProductSplit[3]))/(product.quantity + int(updatedProductSplit[2])))

                                    database.session.commit()
                                    print(
                                        f"2.Product name - {product.name} \t Product price - {product.price} \t Product quantity - {product.quantity}")
                                    #product.quantity += int(updatedProductSplit[2])
                                    quantity: int = product.quantity + int(updatedProductSplit[2])
                                    print(quantity)
                                    checkForMoreProductOrders: bool = True

                                    while(checkForMoreProductOrders):

                                        productOrder: ProductOrder = ProductOrder.query.filter(and_(ProductOrder.requested > ProductOrder.received, ProductOrder.productId == product.id)).order_by(ProductOrder.date.asc()).first()
                                        if productOrder is not None:
                                            if quantity >= productOrder.requested - productOrder.received:
                                                #product.quantity >= productOrder.requested - productOrder.received:
                                                #product.quantity -= productOrder.requested - productOrder.received
                                                quantity -= productOrder.requested - productOrder.received
                                                productOrder.received = productOrder.requested
                                                order : Order = productOrder.order
                                                order.leftToComplete -= 1
                                                if order.leftToComplete == 0:
                                                    order.status = "COMPLETE"
                                                if quantity == 0:
                                                    #product.quantity == 0:
                                                    checkForMoreProductOrders = False
                                                #database.session.commit()
                                            else:
                                                productOrder.received += quantity
                                                #productOrder.received += product.quantity
                                                quantity = 0
                                                #product.quantity = 0
                                                checkForMoreProductOrders = False
                                                #database.session.commit()
                                            database.session.commit()
                                        else:
                                            checkForMoreProductOrders = False
                                    product.quantity = quantity
                                    print(
                                        f"3.Product name - {product.name} \t Product price - {product.price} \t Product quantity - {product.quantity}")
                                    database.session.commit()

                                    # posle provera narudzbina

                        else:
                            product = Product(name=updatedProductSplit[1], quantity= int(updatedProductSplit[2]), price = float(updatedProductSplit[3]))
                            database.session.add(product)
                            database.session.commit()

                            categories = []
                            for categoryStr in categoriesList:
                                category = Category.query.filter(Category.name==categoryStr).first()
                                if category is None:
                                    category = Category(name=categoryStr)
                                    database.session.add(category)
                                    database.session.commit()
                                categories.append(category)

                            productCategories = []
                            for category in categories:
                                productCategory = ProductCategory(productId = product.id, categoryId = category.id)
                                productCategories.append(productCategory)

                            database.session.add_all(productCategories)
                            database.session.commit()


                    for updatedProduct in updatedProducts:
                        redis.lpop(Configuration.REDIS_PRODUCTS_LIST)
                    #updatedProduct = redis.lpop(Configuration.REDIS_PRODUCTS_LIST)

                #time.sleep(TIME_FOR_WAITING)
"""


