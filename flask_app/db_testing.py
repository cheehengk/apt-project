import mysql.connector

# Establish a connection to the MySQL database
cnx = mysql.connector.connect(
    user='root',
    password='apt_mini_proj_230523',
    host='34.133.20.184',
    database='data_schema'
)

# Create a cursor object to execute SQL queries
cursor = cnx.cursor()

# Define the INSERT statement
insert_query = "INSERT INTO data (ID, PDF_URL, VIDEO_URL, CONVERSION_TASK_ID, TIME_CREATED, TIME_COMPLETED, STATUS) " \
               "VALUES (%s, %s, %s, %s, %s, %s, %s)"

# Data to be inserted
data = [
    ('00001', 'testing.com', None, 'something', 'some time',  None, 'RECEIVED')
]

# Execute the INSERT statement for each data item
cursor.executemany(insert_query, data)

# Commit the changes to the database
cnx.commit()

# Close the cursor and the connection
cursor.close()
cnx.close()
