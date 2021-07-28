import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')
LOG_DATA = config['S3']['LOG_DATA']
ARN = config['IAM_ROLE']['ARN']
LOG_JSONPATH = config['S3']['LOG_JSONPATH']
SONG_DATA = config['S3']['SONG_DATA']

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users" 
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE IF NOT EXISTS staging_events (
    artist VARCHAR,
    auth VARCHAR,
    first_name VARCHAR(50),
    gender CHAR,
    iteminsession INTEGER ,
    last_name VARCHAR(50),
    length FLOAT ,
    level VARCHAR,
    location VARCHAR,
    method VARCHAR ,
    page VARCHAR,
    registration NUMERIC,
    session_id FLOAT,
    title VARCHAR,
    status INTEGER,
    ts BIGINT,
    user_agent VARCHAR,
    user_id INTEGER
    );
""")


staging_songs_table_create = ("""
CREATE TABLE staging_songs (
    num_songs INTEGER,
    artist_id VARCHAR,
    artist_latitude NUMERIC,
    artist_longitude NUMERIC,
    artist_location VARCHAR,
    artist_name VARCHAR,
    song_id VARCHAR,
    title VARCHAR ,
    duration NUMERIC,
    year INTEGER    
    );
""")

songplay_table_create = ("""
CREATE TABLE songplays (
    songplay_id INTEGER IDENTITY(0,1) PRIMARY KEY, 
    start_time TIMESTAMP, 
    user_id INTEGER, 
    level VARCHAR, 
    song_id VARCHAR, 
    artist_id VARCHAR, 
    session_id INTEGER, 
    location VARCHAR, 
    user_agent VARCHAR
)
""")

user_table_create = ("""
CREATE TABLE users (
    user_id INTEGER,
    first_name VARCHAR,
    last_name VARCHAR,
    gender VARCHAR,
    level VARCHAR
)
""")

song_table_create = ("""
CREATE TABLE songs (
    song_id VARCHAR,
    title VARCHAR,
    artist_id VARCHAR,
    year INTEGER,
    duration NUMERIC
)
""")

artist_table_create = ("""
CREATE TABLE artists (
    artist_id VARCHAR,
    name VARCHAR,
    location VARCHAR,
    latitude NUMERIC,
    longitude NUMERIC
)
""")

time_table_create = ("""
CREATE TABLE time (
    start_time TIMESTAMP,
    hour INTEGER,
    day INTEGER,
    week INTEGER,
    month INTEGER,
    year INTEGER,
    weekday VARCHAR
)
""")

# STAGING TABLES
#COPY staging_events FROM '{}'
#    credentials 'aws_iam_role={}'
#    json '{}' compupdate on region 'us-west-2';

staging_events_copy = ("""
COPY staging_events FROM '{}'
iam_role '{}'
FORMAT AS json '{}' compupdate on region 'us-west-2';
""").format(LOG_DATA,ARN,LOG_JSONPATH)


staging_songs_copy = ("""
COPY staging_songs FROM '{}'
    credentials 'aws_iam_role={}'
    json 'auto' compupdate on region 'us-west-2';
""").format(SONG_DATA,ARN)

# FINAL TABLES

songplay_table_insert = ("""
INSERT INTO songplays (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
SELECT DISTINCT 
    TIMESTAMP 'epoch' + st_ev.ts/1000 *INTERVAL '1 second' as start_time,
    st_ev.user_id,
    st_ev.level,
    st_so.song_id,
    st_so.artist_id,
    st_ev.session_id,
    st_ev.location,
    st_ev.user_agent
FROM staging_songs st_so
INNER JOIN staging_events st_ev
ON (st_so.title = st_ev.title AND st_ev.artist = st_so.artist_name)
AND st_ev.page = 'NextSong';
""")

user_table_insert = ("""
INSERT INTO users (user_id, first_name, last_name, gender, level)
SELECT DISTINCT
    user_id, first_name, last_name, gender, level
    FROM staging_events
    WHERE page = 'NextSong'
    AND user_id IS NOT NULL;
""")

song_table_insert = ("""
INSERT INTO songs (song_id, title, artist_id, year, duration)
SELECT DISTINCT
    song_id, title, artist_id, year, duration
    FROM staging_songs
    WHERE song_id IS NOT NULL;
""")

artist_table_insert = ("""
INSERT INTO artists (artist_id, name, location, latitude, longitude)
SELECT DISTINCT
    artist_id,
    artist_name,
    artist_location,
    artist_latitude,
    artist_longitude
    FROM staging_songs
    WHERE artist_id IS NOT NULL;
""")

time_table_insert = ("""
INSERT INTO time (start_time, hour, day, week, month, year, weekday)
SELECT DISTINCT
    TIMESTAMP 'epoch' + ts/1000 *INTERVAL '1 second' as start_time,
    EXTRACT(HOUR FROM start_time) AS hour,
    EXTRACT(DAY FROM start_time) AS day,
    EXTRACT(WEEKS FROM start_time) AS week,
    EXTRACT(MONTH FROM start_time) AS month,
    EXTRACT(YEAR FROM start_time) AS year,
    EXTRACT(weekday from start_time) AS weekday
FROM staging_events;
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
