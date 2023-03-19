import json
from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
import pickle
from dotenv import load_dotenv
import os
from cuidGen import generator





load_dotenv() #load environment variables


app = Flask(__name__)


# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://'+os.getenv("MYSQL_USERNAME")+ ':' + os.getenv("MYSQL_PASSWORD") + '@localhost/homey_db'
# 
config_type = os.getenv('CONFIG_TYPE', default='config.DevelopmentConfig')
app.config.from_object(config_type)


db = SQLAlchemy(app)

from models import User, UserSavedProperty, Property, PropertyType

engine = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo = True)
# metadata = MetaData()
inspector = sa.inspect(engine)

if not inspector.has_table("User"):
    with app.app_context():
        db.drop_all()
        db.create_all()
        app.logger.info('Initialized the database!')

else:
    app.logger.info('Database already contains the User table.')

Session = sessionmaker(bind = engine)
session = Session()



# routes


### CRUD FOR USER

@app.route("/createUser", methods=["POST"])
def createUser():
    # data = json.loads('{"name": "hello", "email": "hello@gmail.com", "password": "1234"}')
    data = request.get_json() #get json payload from the post req
    uniqueId = generator()
    new_row = User(id=uniqueId, name=data['name'], email=data['email'], password=data['password'])
    db.session.add(new_row)
    db.session.commit()
    result_json = json.dumps(f'User {uniqueId} Created')
    response = Response(result_json, content_type='application/json')

    return response

@app.route("/getUser", methods=["GET"])
def getUser():
    args = request.args
    user_id = args.get('id')
    if request.method == 'GET':
        user = db.session.query(User).filter_by(id = user_id)
        if user.first() is None:
            result_json = json.dumps(f"Account with userID {user_id} does not exist")
            response = Response(result_json, content_type='application/json')
            return response

        
        else:
            acc = user[0]
            accout = acc.as_dict()
            result = json.dumps(accout)
            response = Response(result, content_type='application/json')
            return response





@app.route("/deleteUser/<user_id>", methods=["DELETE"])
def deleteUser(user_id):
    if request.method == 'DELETE':
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            result_json = json.dumps(f"Account with userID {user_id} does not exist")
            response = Response(result_json, content_type='application/json')
            return response

        
        else:
            db.session.delete(user)
            db.session.commit()

            result_json = json.dumps(f"Account with userID {user_id} has been deleted")
            response = Response(result_json, content_type='application/json')
            return response

        
    else: 
        return Response(json.dumps("method not allowed"), content_type='application/json')

    
@app.route("/updateUser/<user_id>", methods=["PATCH"])
def updateUser(user_id): 
    if request.method =="PATCH":
        request_params = request.get_json()
        user = db.session.query(User).filter_by(id = user_id)
        acc = user[0]

        for key,value in request_params.items():
            setattr(acc, key, value)


        # acc.name = data['name']
        # acc.email = data['email']
        # acc.password = data['password']



        db.session.commit()

        if user.first() is None:
            return "invalid user id, you shouldn't be here"
        else:
            return Response(json.dumps("Account successfully updated!"), content_type='application/json')
    else: 
        return Response(json.dumps("update failed"), content_type='application/json')
    

## CRUD FOR PROPERTY

@app.route("/createProperty", methods=["POST"])
def createProperty():
    # data = json.loads('{"id": "1", "clusterId": "1", "type": "rent"}')
    data = request.get_json() #get json payload from the post req
    print(data)
    if "type" not in data:
        new_row = Property(id=data['id'], clusterId=data['clusterId'], type=PropertyType.RENT)
    else:
        new_row = Property(id=data['id'], clusterId=data['clusterId'], type=data["type"])
    db.session.add(new_row)
    db.session.commit()

    return Response(json.dumps("Property created!"), content_type='application/json')

@app.route("/getProperty", methods=["GET"])
def getProperty():
    args=request.args
    prop_id=args.get("prop_id")
    if request.method == 'GET':
        property = db.session.query(Property).filter_by(id = prop_id)

        if property.first() is None:
            return Response(json.dumps(f"Property with PropID {prop_id} does not exist"), content_type='application/json')
        
        else:

            prop = property[0]
            propout = prop.as_dict()

            return Response(json.dumps(propout), content_type='application/json')

@app.route("/deleteProperty/<int:prop_id>", methods=["DELETE"])
def deleteProperty(prop_id):
    if request.method == 'DELETE':
        property = Property.query.filter_by(id=str(prop_id)).first()
        if property is None:
            return Response(json.dumps(f"Property with Property_ID {prop_id} does not exist"), content_type='application/json')
        
        else:
            db.session.delete(property)
            db.session.commit()

            return Response(json.dumps(f"Property with id {prop_id} has been deleted"), content_type='application/json')
        
    else: 
        return Response(json.dumps("method not allowed"), content_type='application/json')

@app.route("/updateProperty/<prop_id>", methods=["PATCH"])
def updateProperty(prop_id): 
    if request.method =="PATCH":
        property = db.session.query(Property).filter_by(id = prop_id)
        prop = property[0]
        request_params = request.get_json()

        for key,value in request_params.items():
            setattr(prop, key, value)

        db.session.commit()

        if property.first() is None:
            return Response(json.dumps(f"Property with property_id {prop_id} does not exist"), content_type='application/json')
        else:
            return Response(json.dumps("Property successfully updated"), content_type='application/json')
    else: 
        return Response(json.dumps("Update Failed"), content_type='application/json')


## CRUD FOR USP

#this requires user to be logged in!
@app.route("/createUSP/<user_id>", methods=["POST"])
def createUserSavedProperty(user_id):
    # data = json.loads({"userID" : "1","propertyId" : "1", "property": {"id": "12", "clusterId": "1", "type": "rent"}})
    data = request.get_json()
    user = db.session.query(User).filter_by(id = user_id)
    user = user[0]
    # print(user)
    pickledProperty = pickle.dumps(data["property"])
    new_row = UserSavedProperty(userID=data["userID"], propertyId=data["propertyId"], property=pickledProperty)
    propSaved = pickle.loads(user.propertySaved)
    propSaved.append(new_row.as_dict()['property'])
    user.propertySaved = pickle.dumps(propSaved)
    db.session.add(new_row)
    db.session.commit()
    return Response(json.dumps("usp created"), content_type='application/json')

# depracated, use view user method to get propertySaved
# @app.route("/viewUSP/<user_id>", methods=["GET"])
# def viewUSP(user_id):
#     if request.method == 'GET':
#         usp = db.session.query(UserSavedProperty).filter_by(userID = user_id).all()
#         if len(usp)==0:
#             return f"User with userID {user_id} has no saved listings"
        
#         else:
#             listout = []
#             for savedListing in usp:
#                 listout.append(savedListing.as_dict())
#             return json.dumps({"result": listout})

# this requires login!
@app.route("/deleteUSP/<user_id>/<prop_id>", methods=["DELETE"])
def deleteUSP(user_id,prop_id):
    if request.method == 'DELETE':
        usp = UserSavedProperty.query.filter_by(userID = user_id, propertyId=prop_id).first()
        user = User.query.filter_by(id=user_id).first()
        if usp is None:
            return Response(json.dumps("USP does not exist"), content_type='application/json')
        
        else:
            propSaved = pickle.loads(user.propertySaved)
            print(propSaved)
            for prop in propSaved:
                if prop['id']==prop_id:
                    propSaved.remove(prop)
            # del propSaved[prop_id]
            print(propSaved)
            user.propertySaved = pickle.dumps(propSaved)
            db.session.delete(usp)
            db.session.commit()

            return Response(json.dumps("USP has been deleted"), content_type='application/json')
        
    else: 
        return Response(json.dumps("method not allowed"), content_type='application/json')
    

# if __name__ == "__main__":
#     app.app_context().push()
#     db.create_all()
#     app.run(host='0.0.0.0', debug=True)



#1) Check if user and property exists
#1.1) If user doesn't exists, exit (NOT_FOUND)
#1.2) if property doesn't exists, create new Property 
#2) if both property and user exists, create a new UserSavedProperty
#3) return all UserSavedProperty with matching userID