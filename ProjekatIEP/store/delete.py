from configuration import Configuration
from flask import Flask
from models import database, Product, ProductOrder, ProductCategory, Order, Category


application = Flask(__name__)

application.config.from_object(Configuration)
database.init_app(application)
with application.app_context():
    ProductOrder.query.delete()
    ProductCategory.query.delete()

    database.session.commit()

    Product.query.delete()
    Order.query.delete()
    Category.query.delete()

    database.session.commit()

    database.engine.execute("ALTER TABLE products AUTO_INCREMENT=1")
    database.engine.execute("ALTER TABLE categories AUTO_INCREMENT=1")
    database.engine.execute("ALTER TABLE orders AUTO_INCREMENT=1")
    database.engine.execute("ALTER TABLE productorders AUTO_INCREMENT=1")
    database.engine.execute("ALTER TABLE productcategory AUTO_INCREMENT=1")

    database.session.commit()
