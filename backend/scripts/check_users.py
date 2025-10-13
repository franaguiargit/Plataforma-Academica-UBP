import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3

def check_users():
    conn = sqlite3.connect('plataforma_ubp.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, username, email, role, is_active FROM users")
        users = cursor.fetchall()
        
        print("Users in database:")
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Role: {user[3]}, Active: {user[4]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_users()