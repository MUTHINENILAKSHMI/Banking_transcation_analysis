
from database import get_connection

try:
    conn = get_connection()

    if conn.is_connected():
        print("MySQL Database Connected Successfully!")

    conn.close()

except Exception as e:
    print("Connection Error:", e)
