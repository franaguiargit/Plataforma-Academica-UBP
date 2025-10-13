import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3

def fix_purchases_table():
    """Recrear tabla purchases con las columnas correctas"""
    conn = sqlite3.connect('plataforma_ubp.db')
    cursor = conn.cursor()
    
    try:
        # Eliminar tabla existente
        cursor.execute("DROP TABLE IF EXISTS purchases")
        
        # Crear tabla con todas las columnas necesarias
        cursor.execute('''
            CREATE TABLE purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (subject_id) REFERENCES subjects (id)
            )
        ''')
        
        conn.commit()
        print("Table 'purchases' recreated successfully!")
        
        # Verificar estructura
        cursor.execute("PRAGMA table_info(purchases)")
        columns = cursor.fetchall()
        print("Columns in purchases table:")
        for col in columns:
            print(f"  {col[1]} {col[2]}")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_purchases_table()