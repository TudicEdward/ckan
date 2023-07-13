/*
  This javascript has the purpose of collecting infromation from the Ckan Upload Tab. 
  The first function "get_query_form_information" collects the inputs and other browser informations
    fetches the python function from the plugin, after that function is done it will return a json that will 
    determine if the upload was succesfull or an error if the input was incorect and based on this information
    it will render eather an error page or the created / updated dataset.
  The second function "add_query_field" is used by the browser in order to add multiple queries fields and 
    request from the database multiple data to upload.
*/ 

ckan.module("personal_database_population-module", function ($, _) {
  "use strict";
  return {
    options: {
      debug: false,
    },
    
    initialize: function () {
      get_query_form_information();
      add_query_field();
    },
  };
});

async function get_query_form_information() {
  let id = "form_query?"

  var database_program = document.forms["upload_from_personal_database"]["database_program"].value;
  var username = document.forms["upload_from_personal_database"]["connection_username"].value;
  var password = document.forms["upload_from_personal_database"]["connection_password"].value;
  var hostname = document.forms["upload_from_personal_database"]["connection_hostname"].value;
  var port = document.forms["upload_from_personal_database"]["connection_port"].value;
  var database = document.forms["upload_from_personal_database"]["connection_database"].value;
  
  var dataset_name = document.forms["upload_from_personal_database"]["dataset_name"].value;
  var dataset_description = document.forms["upload_from_personal_database"]["dataset_description"].value;
  var author_name = document.forms["upload_from_personal_database"]["author_name"].value;
  var author_email = document.forms["upload_from_personal_database"]["author_email"].value;
  var resource_name = document.forms["upload_from_personal_database"]["resource_name"].value;
  var description = document.forms["upload_from_personal_database"]["resource_description"].value;

  const url = String(window.location.href)
  const search_string = 'organization'
  const index_location = url.indexOf(search_string) + search_string.length 
  const upload_url = url.substring(url.indexOf(search_string))
  const new_url = url.slice(index_location)
  const string = new_url.concat( '/upload_information')
  const dictionary={"database_program":database_program,"username":username,"password":password,"hostname":hostname,"port":port,"database":database,"dataset_name":dataset_name,"dataset_description":dataset_description,"author_name":author_name,"author_email":author_email,"resource_name":resource_name,"description":description}

  for (let j =1; j < 10 ; j++)
  {
    let new_id = id.replace('?',j)
    var input_query = document.getElementById(new_id);
    if (input_query != null)
    {
      var query = document.forms["upload_from_personal_database"][new_id].value;
      var name = "query" + j;
      dictionary[name] =query;
    }
  }
  
  console.log("connection user: ",username);
  console.log("connection pass: ",password);
  console.log("connection host: ",hostname);
  console.log("connection port: ",port);
  console.log("connection database: ",database);

  console.log("Dataset name is: ",dataset_name);
  console.log("Author name is: ",author_name);
  console.log("Author email is: ",author_email);
  console.log("Resource name is: ",resource_name);
  console.log("Resource description is: ",description);
  console.log("Query is: ",query)

  try{
  const response = await fetch(string, {
        method: 'POST',
        headers: {'Accept': 'application/json','Content-Type': 'application/json'},
        body: JSON.stringify(dictionary)
      })
  const data = await response.text()
  console.log(data)
  var response_data = JSON.parse(data);
  if (response_data["error"] == true){
    window.location = response_data["url"];
  }
  else if (response_data["error"] == false){
    window.location.assign(url.replace(upload_url,"dataset/"+dataset_name));
  }
  }
  catch (error) {
    console.error("Error:", error);
  }
}

function add_query_field(){
  var formfield = document.getElementById('upload_from_personal_database');
  let id = "form_query1"
  for (let i = 2 ; i < 10 ; i++){
    let new_id = id.replace('1',i)
    var query = document.getElementById(new_id);
    var lastquery = document.getElementById('form_query9');
    if (lastquery != null)
    {
      console.log("The query limit has been reached!");
      break;
    }
    if (query == null)
      {
      var newField = document.createElement('input');
      newField.setAttribute('type','text');
      newField.setAttribute('name',new_id);
      newField.setAttribute('id',new_id);
      newField.setAttribute('class','custom_form_input');
      newField.setAttribute('placeholder','Query for the upload');
      newField.required = true;
      formfield.appendChild(newField);
      break;
      }
  }  
}



