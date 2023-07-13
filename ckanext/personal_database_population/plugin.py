from __future__ import annotations

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from werkzeug.datastructures import FileStorage
from io import BytesIO

from flask import Blueprint, request, jsonify

from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.ext.declarative import DeclarativeMeta
import json

import base64 
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
from Crypto.Random import get_random_bytes


# DEFINE THE DATABASE CREDENTIALS
# user_mysql = 'root'
# password_mysql = 'Matinovac5'
# host_mysql = '127.0.0.1'
# port_mysql = 3306
# database_mysql = 'articles'

#encryption function
def encrypt(data,key,iv):
        data = pad(data.encode(),16)
        cipher = AES.new(key.encode('utf-8'),AES.MODE_CBC,iv)
        return base64.b64encode(cipher.encrypt(data)),base64.b64encode(cipher.iv).decode('utf-8')

#dectyption function  
def decrypt(enc,key,iv):
        enc = base64.b64decode(enc)
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, base64.b64decode(iv))
        return unpad(cipher.decrypt(enc),16)

#function that return an engine connection for the database based on the system used
def connect_to_database(user_mysql, password_mysql, host_mysql, port_mysql, database_mysql, system):
    if system == "mysql":
        engine = create_engine(url="mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format( user_mysql, 
            password_mysql, host_mysql, port_mysql, database_mysql))
    elif system == "mariadb":
        engine = create_engine(url="mariadb+mariadbconnector://{0}:{1}@{2}:{3}/{4}".format( user_mysql, 
            password_mysql, host_mysql, port_mysql, database_mysql))
    return engine

#function that executes a query for a connection
def execute_query(engine, query):
    with engine.connect() as con:
        results = con.execute(text(query))
    return json.dumps([dict(r) for r in results])

#Flask blueprint for the new upload tab
upload_blueprint_endpoint = Blueprint("upload_endpoint", __name__)
@upload_blueprint_endpoint.route("/organization/<org_id>/upload") # URL of the new page
def upload_tab(org_id): # name of the function is used inside the endpoint name
    # organization is required inside template
    organization = toolkit.get_action("organization_show")({}, {"id": org_id})

    # render the upload_database.html template
    return toolkit.render("organization/upload_database.html", {
        "group_dict": organization,
        "group_type": organization["type"]
    })

#Flask blueprint for the error page
error_blueprint_endpoint = Blueprint("error_endpoint", __name__)
@error_blueprint_endpoint.route("/organization/<org_id>/error/<type>") # URL of the new page
def error_page(org_id,type): # name of the function is used inside the endpoint name
    # organization is required inside template
    organization = toolkit.get_action("organization_show")({}, {"id": org_id})

    # render the error.html template based on error
    if type == 'name':
        return toolkit.render("organization/error_name.html", {
            "group_dict": organization,
            "group_type": organization["type"]
        })
    elif type == 'query':
        return toolkit.render("organization/error_query.html", {
            "group_dict": organization,
            "group_type": organization["type"]
        })
    elif type == 'conn':
        return toolkit.render("organization/error_connection.html", {
            "group_dict": organization,
            "group_type": organization["type"]
        })

#Flask Blueprint for the javascript
upload_information_endpoint = Blueprint("upload_information", __name__)
@upload_information_endpoint.route('/<org_id>/upload/upload_information', methods=['POST'])
def upload_information(org_id):
    #arrays for queries
    queries = [] 
    results = []
    #encryption variables
    key = 'AAAAAAAAAAAAAAAA' #16 char for AES128
    iv =  get_random_bytes(16) #16 char for AES128
    #organization id
    organization = toolkit.get_action("organization_show")({}, {"id": org_id})
    #captured data from javascript
    data = request.get_json()
    #personal database connection information
    database_program = data["database_program"]
    username = data["username"]
    password, iv = encrypt(data["password"], key, iv)
    hostname = data["hostname"]
    port = data["port"]
    database = data["database"]
    #dataset and resource / resources information
    dataset_name = data["dataset_name"]
    dataset_description = data["dataset_description"]
    author_name = data["author_name"]
    author_email = data["author_email"]
    resource_names = data["resource_name"].split(",")
    description = data["description"]

    #verification of Dataset name format
    for character in dataset_name:
        if character.isupper() or character == " ":
            return jsonify({"url":toolkit.url_for("error_endpoint.error_page", org_id = org_id, type = 'name' ,_external=True), "error":True})
    #query execution based on the number of queries received from the javascript. If the connection cannot be made or the query is incorect it will render an error page.
    for i in range(1,10):
        name = "query" + str(i)
        if name in data:
            queries.append(data[name])
    try:
        connection = connect_to_database(username, decrypt(password,key,iv).decode("utf-8", "ignore"), hostname, port, database, database_program)
        for query in queries:
            result = execute_query(connection, query)
            results.append(result)
    except:
        return jsonify({"url":toolkit.url_for("error_endpoint.error_page", org_id = org_id, type = 'conn' ,_external=True), "error":True})
    #if there are no results received then it will render an error page.
    for query_result in results:
        if len(results) != len(queries) or query_result == "[]":
            return jsonify({"url":toolkit.url_for("error_endpoint.error_page", org_id = org_id, type = 'query' ,_external=True), "error":True})
    #if the number of names for the resources is bigger that the number of querie results than it will use the same name on all results and numerotate them.
    if len(results) > len(resource_names):
        resources_names = []
        for result_number in range(len(results)):
            resources_names.append( resource_names[0] + str(result_number+1))
        resource_names = resources_names

    #here is the process of uploading the data. First check if the dataset already exists 
    existing_datasets = toolkit.get_action('package_search')(None, {"fq": "name:" + dataset_name})
    #if it doesn't exist it will create a new one and collect its id.
    if existing_datasets["count"] == 0:
        dataset_dict = {
        'name': dataset_name,
        'author' : author_name,
        'author_email' : author_email,
        'maintainer' : author_name,
        'maintainer_email' : author_email,
        'notes' : dataset_description,
        'version' : 1.0,
        'owner_org': organization["id"]
        }
        created_dataset = toolkit.get_action('package_create')(None, dataset_dict)
        package_id = created_dataset["id"]
        #here it searches for all the resources to see if one exists
        for resource_name in resource_names:
            #search query for resources
            field_resource = 'name:resource_name'
            field_resource = field_resource.replace("resource_name",resource_name)
            search_query_resource = {'query':field_resource}
            #filename for the upload
            filename = resource_name + '.json'
            existing_resources = toolkit.get_action('resource_search')(None, search_query_resource)
            index = resource_names.index(resource_name)
            #if it doesn't exist it will create a new one with specified information. Else it will update the existing one 
            if existing_resources["count"] == 0:
                resource_dict = {
                    'package_id':package_id,
                    'description':description,
                    'name':resource_name,
                    'upload':  FileStorage(BytesIO(bytes(results[index], "utf8")), filename)
                }
                toolkit.get_action('resource_create')(None, resource_dict)
            else:
                found_resources = existing_resources["results"]
                for resource in  found_resources:
                    resource_id = resource["id"]
                resource_dict = {
                    'id':resource_id,
                    'upload':  FileStorage(BytesIO(bytes(results[index], "utf8")), filename)
                }
                if description != "":
                    resource_dict["description"] = description 
                toolkit.get_action('resource_patch')(None, resource_dict)
    else:
        #If the dataset exists it gets the packadge id and the version to update it and if the used entered any aditional data it will update with it.
        for dataset in existing_datasets["results"]:
            package_id = dataset["id"]
            version = dataset["version"]
            update_dict = {'id':package_id}
        if dataset_description != "":
            update_dict['notes'] = dataset_description
        if author_email != "":
            update_dict['author'] = author_name
            update_dict['maintainer'] = author_name
        if author_name != "":
            update_dict['author_email'] = author_email
            update_dict['maintainer_email'] = author_email
        if version is not None:
            update_dict['new_version'] = float(version) + 1
        else:
            update_dict['new_version'] = 2.0
        toolkit.get_action('package_patch')(None, update_dict)
        for resource_name in resource_names:
            #search query for resources
            field_resource = 'name:resource_name'
            field_resource = field_resource.replace("resource_name",resource_name)
            search_query_resource = {'query':field_resource}
            #filename for the upload
            filename = resource_name + '.json'
            existing_resources = toolkit.get_action('resource_search')(None, search_query_resource)
            index = resource_names.index(resource_name)
            existing_resources = toolkit.get_action('resource_search')(None, search_query_resource)
            if existing_resources["count"] == 0:
                resource_dict = {
                    'package_id':package_id,
                    'description':description,
                    'name':resource_name,
                    'upload':  FileStorage(BytesIO(bytes(results[index], "utf8")), filename)
                }
                toolkit.get_action('resource_create')(None, resource_dict)
            else:
                found_resources = existing_resources["results"]
                for resource in  found_resources:
                    resource_id = resource["id"]
                resource_dict = {
                    'id':resource_id,
                    'upload':  FileStorage(BytesIO(bytes(results[index], "utf8")), filename)
                }
                if description != "":
                    resource_dict["description"] = description 
                toolkit.get_action('resource_patch')(None, resource_dict)

    return jsonify({"queries":queries,"results":query_result,"error":False})

class PersonalDatabasePopulationPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource('assets', "personal_database_population")

    # IBlueprint
    def get_blueprint(self):
        return [upload_blueprint_endpoint, upload_information_endpoint, error_blueprint_endpoint]
