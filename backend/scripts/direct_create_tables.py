import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3

def create_users_table():
    """Crear tabla users directamente con SQL"""
    conn = sqlite3.connect('plataforma_ubp.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                full_name VARCHAR(255),
                hashed_password VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                role VARCHAR(255) DEFAULT 'student',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        print("Table 'users' created successfully!")
        
        # Verificar que se creó
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Existing tables: {[table[0] for table in tables]}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_users_table()