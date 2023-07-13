[![Tests](https://github.com/TudicEdward/ckanext-personal_database_population/workflows/Tests/badge.svg?branch=main)](https://github.com/TudicEdward/ckanext-personal_database_population/actions)

# ckanext-personal_database_population

The purpose of the extension is to offer a simple way for organizations that want to upload data from a personal database to also manipulate what data to upload with the help of SQL queries.

Demo:

Once the extension is installed, if the user is logged in and has admin or editor role for an organization he will have available the "Upload" navigation tab.

![Alt text](https://github.com/TudicEdward/ckanext-personal_database_population/blob/master/upload%20tab.png)

After selecting the "Upload" Tab a form page will be loaded.

form page components:
-database program selection
-database connection information
-dataset and resource information
-query / queries input for the data to be uploaded

![Alt text](https://github.com/TudicEdward/ckanext-personal_database_population/blob/master/part1.png)

![Alt text](https://github.com/TudicEdward/ckanext-personal_database_population/blob/master/part2.png)

Execution process:

-verify data is correct (names) (if format is incorrect load error page)
-connect to the database with the connection information (if data is incorrect load error page)
-request data with the query / queries (if queries are incorrect (results are empty) load error page)
-verify if dataset exists:
	-if it doesn't exist it will create with specified information
	-if it exists it will upload the version and the specified information
verify if resource exists:
	-if resource doesn't exist inside dataset it will create it and upload the results
	-if the resource exists it will upload the information 
Note1: If in the "Resource Name" is given a list of names separated by ',' it will put the names for each query. Otherwise it will use the same name and numerotate.
Note2: Add button will create up to 9 query fields.

After "Submit" button is pressed the extension will load the page containing the newly uploaded data.

## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.9 and earlier | not tested    |
| 2.10            | yes           |

## Installation

To install ckanext-personal_database_population:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com/TudicEdward/ckanext-personal_database_population.git
    cd ckanext-personal_database_population
    pip install -e .
	pip install -r requirements.txt

3. Add `personal_database_population` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload

## Developer installation

To install ckanext-personal_database_population for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/TudicEdward/ckanext-personal_database_population.git
    cd ckanext-personal_database_population
    python setup.py develop
    pip install -r requirements.txt

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
