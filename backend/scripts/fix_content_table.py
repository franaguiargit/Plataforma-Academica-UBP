import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3

def fix_content_table():
    """Crear tabla content con las columnas correctas"""
    conn = sqlite3.connect('plataforma_ubp.db')
    cursor = conn.cursor()
    
    try:
        # Crear tabla content
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                content_type VARCHAR(50) NOT NULL,
                subject_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subjects (id)
            )
        ''')
        
        conn.commit()
        print("Table 'content' created successfully!")
        
        # Verificar estructura
        cursor.execute("PRAGMA table_info(content)")
        columns = cursor.fetchall()
        print("Columns in content table:")
        for col in columns:
            print(f"  {col[1]} {col[2]}")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_content_table()