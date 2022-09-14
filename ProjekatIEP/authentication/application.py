from flask import Flask, request, jsonify, Response
from configuration import Configuration
from models import database, User, UserRole, Role
from email.utils import parseaddr
import re
import types
from sqlalchemy import and_

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)
#engine = create_engine(Configuration.SQLALCHEMY_DATABASE_URI)
#Session = sessionmaker(engine)

@application.route("/", methods=["GET"])
def index():
    return "Hello world!"

@application.route("/register", methods =["POST"])
def register():

    email = request.json.get("email", "")
    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    isCustomer = request.json.get("isCustomer", "")


    falseInfo = checkRegisterData(email = email, password = password, surname = surname, forename = forename, isCustomer= isCustomer)

    if falseInfo[0]:
        return jsonify(message=falseInfo[1]), 400


    newUser = User(email=email, password=password, forename=forename, surname=surname)
    database.session.add(newUser)
    database.session.commit()

    if (isCustomer == True):
        role: Role = Role.query.filter(Role.name == "customer").first()
    else:
        role: Role = Role.query.filter(Role.name == "warehouse").first()

    userrole = UserRole(
        roleId = role.id,
        userId = newUser.id
    )

    database.session.add(userrole)
    database.session.commit()
    
    return Response("", 200)

def checkRegisterData(email, password: str, forename, surname, isCustomer):
    if(len(forename) == 0):
        return [True,"Field forename is missing."]
    elif(len(surname) == 0):
        return [True, "Field surname is missing."]
    elif(len(email) == 0):
        return [True, "Field email is missing."]
    elif(len(password) == 0):
        return [True, "Field password is missing."]
    elif(not isinstance(isCustomer, bool)):
        return [True, "Field isCustomer is missing."]


    if not checkEmail(email):
        return [True, "Invalid email."]

    passwordCheck = [False, False, False] #kad je sve true znaci da ima sve potrebno
    if(len(password) >= 8):
        for i in range (0, len(password)):
            if password[i].isdigit():
                passwordCheck[0] = True
            elif password[i].isalpha():
                if password[i].islower():
                    passwordCheck[1] = True
                elif password[i].isupper():
                    passwordCheck[2] = True

    if(not (passwordCheck[0] and passwordCheck[1] and passwordCheck[2])):
        return [True, "Invalid password."]

    userExists = User.query.filter(User.email == email).first() is not None

    if userExists:
        return [True, "Email already exists."]

    return [False, ""]


def checkEmail(email: str):
    result = re.findall("^[a-zA-Z][a-zA-Z0-9\.]*@[a-zA-Z][a-zA-Z0-9]*\.[a-zA-Z0-9\.]*$", email)
    if len(result) == 1:
        previousChar = ''
        for i in range(0, len(email)):
            if(previousChar == '.' and email[i] == '.'):
                return False
            previousChar = email[i]

        if email[len(email) - 1] == "." or email[len(email) - 2] == ".":
            return False

        return True
    else:
        return False

#login si poceo
@application.route("/login", methods = ["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    falseInfo = checkLoginData(email, password)

    if falseInfo[0]:
        return jsonify(message=falseInfo[1]), 400

    user = falseInfo[2]

    additional_claims = {
        "forename": user.forename,
        "surname": user.surname,
        "roles": [str(role) for role in user.roles]
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additional_claims)
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additional_claims)

    return jsonify(accessToken = accessToken, refreshToken = refreshToken), 200

def checkLoginData(email, password):
    if len(email) == 0:
        return [True, "Field email is missing.", None]
    elif len(password) == 0:
        return [True, "Field password is missing.", None]

    if not checkEmail(email):
        return [True, "Invalid email.", None]

    user = User.query.filter(and_(User.email == email, User.password == password)).first()

    if user is None:
        return [True, "Invalid credentials.", None]

    return [False, "", user]

@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refresh_claims = get_jwt()
    additional_claims = {
        "forename": refresh_claims["forename"],
        "surname": refresh_claims["surname"],
        "roles": refresh_claims["roles"]
    }

    accessToken = create_access_token(identity= identity, additional_claims = additional_claims)

    return jsonify(accessToken = accessToken), 200

@application.route("/delete", methods = ["POST"])
@jwt_required()
def delete():
    claims = get_jwt()
    roles = claims["roles"]
    for role in roles:
        if role == "admin":
            email = request.json.get("email", "")

            falseInfo = checkDeleteData(email)

            if falseInfo[0]:
                return jsonify(message= falseInfo[1]), 400

            user = falseInfo[2]

            database.session.delete(user)
            database.session.commit()

            return Response("", 200)

    return jsonify(msg = "Missing Authorization Header"), 401

def checkDeleteData(email):

    if len(email) == 0:
        return [True, "Field email is missing.", None]

    if not checkEmail(email):
        return [True, "Invalid email.", None]

    user = User.query.filter(User.email == email).first()

    if user is None:
        return [True, "Unknown user.", None]

    return [False, "", user]


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5005)
