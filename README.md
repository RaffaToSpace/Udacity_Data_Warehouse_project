# Data Warehouse project
## Project purpose
As stated in the project overview, the purpose of this project is to move the data of a hypothetical music streaming app, called Sparkify, from two directories of JSON files on Amazon S3, to a database on Amazon Redshift.  
The data is made of two kind of JSON files: 
- user activity logs;
- song metadata.

For the purpose of this project, I have built a ETL pipeline that extracts the data on S3 and transfers it into two tables (one per JSON file type), then transfers the data into a series of dimensional tables, according to a predefined database schema, as defined by the project instructions.
## Database schema
From the project description:
**Fact Table**

_songplays_ - records in event data associated with song plays i.e. records with page NextSong  
``
songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent
``  

**Dimension Tables**

_users_ - users in the app  
``
user_id, first_name, last_name, gender, level``  
_songs_ - songs in music database  
``song_id, title, artist_id, year, duration``  
_artists_ - artists in music database  
``artist_id, name, location, lattitude, longitude``  
_time_ - timestamps of records in songplays broken down into specific units  
``start_time, hour, day, week, month, year, weekday``

**Staging Tables**
These tables work as containers for the data in the JSON files, and are hence structured to match their shape. _staging events_ is structured to contain the data from the user activity logs, whereas _staging songs_ the songs metadata.


## Project structure
### Cluster start-up: _cluster commands.ipynb_
The first step in the project is to initiate the Redshift cluster, and to create the necessary IAM role to perform the required operations. The necessary parameters are stored in the configuration file dwh.cfg (a dummy is present on the repository, which can be used as a template to be filled by the user). 
The script also contains the necessary commands to delete the cluster, and a trouble-shooting tool that queries the error log of the cluster, in case on the ETL operations returns an error.

### SQL commands library: _sql_queries.py_
This script contains the necessary SQL query text to create and drop the tables in the schema, to copy the data from the S3 container and transfer it into the tables.

### DB tables creation: _create_tables.py_
When run, this script runs the queries necessary to drop the tables if already present, and create them.

### Data transfer and DB population: _etl.py_
When run, this script runs the queries necessary to copy the data from the S3 container into the staging tables, 

## Running instructions
1. open dwh.cfg and fill in with the relevant details in the "AWS" and "DWH" section. Refer to the [Amazon Redshift](https://aws.amazon.com/redshift/getting-started/?p=rs&bttn=hero&exp=b) guide.
2. Run the cells in _cluster commands.ipynb_, up until "Loading SQL interface".
3. Copy the Endpoint and role ARN information printed on screen by the notebook. Paste them in the in the dwh.cfg file, the Endpoint as "HOST" in the "Cluster" section, and the role ARN in the "IAM_ROLE" as "ARN".
4. In terminal, navigate to the project folder and run, in order:  
``python create_tables.py``  
``python etl.py``  

5. The last command might take some time to run. If it results in an error connected with the runnign of the queries, navigate to the "SQL errors diagnostics" section in _cluster commands.ipynb_, and run the commands to access the error log table, which may contain important information regarding the error that has occurred.
6. If required, delete the cluster by running the command in the "Delete cluster" section in  _cluster commands.ipynb_.