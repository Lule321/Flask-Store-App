from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property

database = SQLAlchemy()

class ProductOrder(database.Model):
    __tablename__ = "productorders"

    id = database.Column(database.Integer, primary_key=True)
    orderId = database.Column(database.Integer, database.ForeignKey("orders.id"), nullable = False)
    productId = database.Column(database.Integer, database.ForeignKey("products.id"), nullable = False)
    requested = database.Column(database.Integer)
    received = database.Column(database.Integer)
    price = database.Column(database.Float)
    date = database.Column(database.DateTime)
    product = database.relationship("Product", back_populates="productorders")

    order = database.relationship("Order", back_populates="productorders")

class ProductCategory(database.Model):
    __tablename__ = "productcategory"

    id = database.Column(database.Integer, primary_key=True)
    productId = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)
    categoryId = database.Column(database.Integer, database.ForeignKey("categories.id"), nullable=False)

class Category(database.Model):

    __tablename__ = "categories"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256))
    products = database.relationship("Product", secondary= ProductCategory.__table__, back_populates="categories")

    def numberOfSoldProducts(self):
        sold = 0
        for product in self.products:
            sold += product.productStatistics()["sold"]
        return sold

    def __repr__(self):
        return str(self.name)

class Product(database.Model):
    __tablename__ = "products"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256))
    quantity = database.Column(database.Integer)
    price = database.Column(database.Float)
    categories = database.relationship("Category", secondary=ProductCategory.__table__, back_populates = "products")
    productorders = database.relationship("ProductOrder", back_populates = "product")

    def __repr__(self):
        return str(self.name)

    def dictCustomer(self):
        dictionary = dict()
        categories = []
        for category in self.categories:
            categories.append(category.name)
        dictionary["categories"] = categories
        dictionary["id"] = self.id
        dictionary["name"] = self.name
        dictionary["price"] = self.price
        dictionary["quantity"] = self.quantity
        return dictionary

    def dictStatus(self):
        dictionary = dict()
        categories = []
        for category in self.categories:
            categories.append(category.name)
        dictionary["categories"] = categories
        dictionary["name"] = self.name
        #dictionary["price"] = self.price
        return dictionary

    def productStatistics(self):
        dictionary = dict()
        sold = 0
        waiting = 0
        for productorder in self.productorders:
            sold += productorder.requested
            waiting += productorder.requested - productorder.received

        dictionary["name"] = self.name
        dictionary["sold"] = sold
        dictionary["waiting"] = waiting

        return dictionary

class Order(database.Model):
    __tablename__ = "orders"

    id = database.Column(database.Integer, primary_key = True)
    date = database.Column(database.DateTime)
    status = database.Column(database.String(256))
    price = database.Column(database.Float)
    productorders = database.relationship("ProductOrder", back_populates="order")
    leftToComplete = database.Column(database.Integer)
    customerEmail = database.Column(database.String(256), nullable = False)
    #dodati remaining productorders

    def dictCustomer(self):
        dictionary = dict()
        products = []

        for productorder in self.productorders: #pretpostavka u jednoj porudzbi nema vise narucenih istih predmeta
            product = dict()
            product = productorder.product.dictStatus()
            product["requested"] = productorder.requested
            product["received"] = productorder.received
            product["price"] = productorder.price / productorder.requested
            products.append(product)
        dictionary["products"] = products
        dictionary["price"] = self.price
        dictionary["status"] = self.status
        dictionary["timestamp"] = self.date.isoformat()
        return dictionary

