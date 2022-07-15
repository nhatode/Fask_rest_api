from dataclasses import field, fields
from flask import Flask, request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import  Marshmallow 
from datetime import timezone
from sqlalchemy.sql import func
import config
import os
from flask_jwt_extended import create_access_token , get_jwt_identity,jwt_required,JWTManager

##instantiate flask app
#app = Flask(__name__)

##set config
#app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///rest_dataset.db"
#app.config['SQLALCHEMY_TRACK_MODIFICATION']= False


#### Aditional code to create connection with MSSQL Database from other project

def create_app():
    """Create and configure the flask app"""
    flask_app = Flask(__name__, instance_relative_config=True)
    flask_app.secret_key = 'dummy_secret_key'
    """
    env = os.environ.get('FLASK_ENV')
    if env == 'DEV':
        config_obj = config.DevelopmentConfig()
    elif env == 'BETA':
        config_obj = config.BetaConfig()
    elif env == 'PROD':
        config_obj = config.ProductionConfig()
    else:
        config_obj = config.Config()
        """
    config_obj = config.DevelopmentConfig()
    flask_app.config.from_object(config_obj)

    return flask_app


app = create_app()
db = SQLAlchemy(app=app)
###########################################Code Finished#####################

## Instantiate database object
#db = SQLAlchemy(app)

## create Marshmallow object
ma = Marshmallow(app)

## Setup the flask-JWT-Extended extension 
app.config["JWT_SECRET_KEY"] = 'stonexJWT'  # need to move to secrete vault
jwt= JWTManager(app)

##create database
class restapi_dataset(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    url_resource = db.Column(db.String(100))
    vds_location = db.Column(db.String(100))
    group_name = db.Column(db.String(100))
    permissions = db.Column(db.String(100))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

    def __init__(self,url_resource,vds_location,group_name,permissions):
       self.url_resource=url_resource
       self.vds_location=vds_location
       self.group_name=group_name
       self.permissions = permissions
    
    def __repr__(self) -> str:
        return  {self.id} 

## create dataset schema
class restapi_dataset_schema(ma.Schema):
    class Meta:
        fields = ('id','url_resource','vds_location','group_name','permissions','date_created')


## Create instance of Schema
dataset_schema = restapi_dataset_schema(many=False)
datasets_schema = restapi_dataset_schema(many=True)

## Protect a route with JWT_Required, which will kick out request
## without valid JWT-Tocken

@app.route('/api/v1/accesscontrol/auth', methods=['POST'])
def auth():
    username = request.json.get("username",None)
    password = request.json.get("password",None)
    if username != 'admin' or password != 'admin123':
        return jsonify({"msg": "Bad username and password"}), 401

    access_token = create_access_token(identity=username) 
    return jsonify(access_token=access_token)


## Create Routes for rest Api
## POST routes
static_route = 'api/v1/accesscontrol/'

@app.route('/api/v1/accesscontrol/add', methods=['POST'] )
def add_dataset():

    try:
        
        url_resource = request.json['url_resource']
        vds_location = request.json['vds_location']
        group_name = request.json['group_name']
        permissions = request.json['permissions']

        new_dataset = restapi_dataset(url_resource=url_resource,vds_location=vds_location,group_name=group_name,permissions=permissions)
        #print(new_dataset)

        db.session.add(new_dataset)
        db.session.commit()
        return dataset_schema.jsonify(new_dataset)

    except Exception as e:
        print(e)
        return jsonify({"error": "Invalid dataset"})

## POST routes

@app.route('/api/v1/accesscontrol/getrecords', methods=['GET'])
def get_records():
    getrecords = restapi_dataset.query.all()
    result_set = datasets_schema.dump(getrecords)
    return jsonify(result_set)

 ## Retrive single record 
@app.route('/api/v1/accesscontrol/getrecords/<int:id>',methods=['GET'])
def get_single_record(id):
    get_single_record = restapi_dataset.query.get_or_404(int(id))
    single_set = dataset_schema.dump(get_single_record)
    return jsonify(single_set)

## update Specifice record
@app.route('/api/v1/accesscontrol/update/<int:id>', methods=['PUT'])
def update_record(id):
    update_specific_record = restapi_dataset.query.get_or_404(int(id))

    url_resource = request.json['url_resource']
    vds_location = request.json['vds_location']
    group_name = request.json['group_name']
    permissions = request.json['permissions']

    update_specific_record.url_resource = url_resource
    update_specific_record.vds_location = vds_location
    update_specific_record.group_name = group_name
    update_specific_record.permissions = permissions

    db.session.commit()

    return dataset_schema.jsonify(update_specific_record)

## Delete sepcifice Record
## Delete function is Protected by JWT Tocken a delete route to accidently deleted the dataset
@app.route('/api/v1/accesscontrol/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_record(id):
    current_user = get_jwt_identity()
    delete_specific_record = restapi_dataset.query.get_or_404(int(id))
    db.session.delete(delete_specific_record)
    db.session.commit()

    return jsonify({"Delete requested by": current_user,"Success" : "Given Record Deleted"})


if __name__ == '__main__':
    app.run(debug=True)