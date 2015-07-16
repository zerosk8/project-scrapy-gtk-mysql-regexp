******************************
Database
******************************

It is needed a database server to run the application, "MySQL Server" preferable.

- Database Server name: 'localhost'
- Database name: 'WallhavenGallery'
- Database user name: 'wallhaven_user'
- Database password for user name: 'wallhaven'
- Database table name: 'Image'

If you have not access to a database within these specifications then just follow one of these steps:

1. Run "database_configuration.sql" file from prompt in your database server. This file contains several "SQL" sentences which perform:
    - 'WallhavenGallery' database creation.
    - 'wallhaven_user' user creation, with 'wallhaven' password and access to 'WallhavenGallery' database.
    - 'Image' database table creation, inner 'WallhavenGallery' database.

e.g.: In a GNU/Linux based O.S., using "bash" prompt and "MySQL Server", script can be executed as follows:
        
        $ > mysql -u root -p < "<local_path_to_sql_file>/database_configuration.sql"

2. Edit database connection configuration, so your own database, database user, databae table, etc... can be used instead. To do this
just modify values associated to variables in lines from 97 to 101 from file "main_wallhaven.py" in "Wallhaven" directory.

******************************
Execution
******************************

Application file is found in "Wallhaven" directory.

e.g.: In a GNU/Linux based O.S., using "bash" prompt application run as follows:
        
        $ > python ./Wallhaven/main_wallhaven.py

IMPORTANT: ONLY ONE SEARCH PER APPLICATION EXECUTION IS ALLOWED DUE TO DIFFICULTIES IN CRAWLING THE SAME SPIDER WITH ONE REACTOR RUNNING.
IN ORDER TO PERFORM A NEW SEARCH, APPLICATION MUST BE CLOSED AND OPENED.

