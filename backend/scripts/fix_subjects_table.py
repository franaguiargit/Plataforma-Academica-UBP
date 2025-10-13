import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3

def fix_subjects_table():
    """Recrear tabla subjects con las columnas correctas"""
    conn = sqlite3.connect('plataforma_ubp.db')
    cursor = conn.cursor()
    
    try:
        # Eliminar tabla existente
        cursor.execute("DROP TABLE IF EXISTS subjects")
        
        # Crear tabla con todas las columnas necesarias
        cursor.execute('''
            CREATE TABLE subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        print("Table 'subjects' recreated successfully!")
        
        # Verificar estructura
        cursor.execute("PRAGMA table_info(subjects)")
        columns = cursor.fetchall()
        print("Columns in subjects table:")
        for col in columns:
            print(f"  {col[1]} {col[2]}")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_subjects_table()