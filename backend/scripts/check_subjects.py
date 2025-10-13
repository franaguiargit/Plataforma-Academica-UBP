import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3

def check_subjects():
    conn = sqlite3.connect('plataforma_ubp.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM subjects")
        subjects = cursor.fetchall()
        
        print("Subjects in database:")
        for subject in subjects:
            print(f"ID: {subject[0]}, Title: {subject[1]}, Description: {subject[2]}, Price: {subject[3]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_subjects()