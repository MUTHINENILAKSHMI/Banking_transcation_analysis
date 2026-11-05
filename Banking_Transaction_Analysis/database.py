
import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="NewPassword@123",
        database="banking_tran_analysis"
    )

    return connection
