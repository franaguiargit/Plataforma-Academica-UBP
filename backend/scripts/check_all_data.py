import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3

def check_all_data():
    """Verificar todos los datos en la base de datos"""
    conn = sqlite3.connect('plataforma_ubp.db')
    cursor = conn.cursor()
    
    try:
        print("=" * 50)
        print("USUARIOS:")
        cursor.execute("SELECT id, username, role FROM users")
        users = cursor.fetchall()
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}, Role: {user[2]}")
        
        print("\n" + "=" * 50)
        print("MATERIAS:")
        cursor.execute("SELECT id, title, description, price, created_at FROM subjects")
        subjects = cursor.fetchall()
        for subject in subjects:
            print(f"ID: {subject[0]}, Title: {subject[1]}, Price: ${subject[3]}")
            print(f"   Description: {subject[2]}")
            print(f"   Created: {subject[4]}")
            print()
        
        print("=" * 50)
        print("CONTENIDO:")
        cursor.execute("""
            SELECT c.id, c.title, c.description, c.content_type, c.subject_id, s.title as subject_name, c.created_at 
            FROM content c 
            LEFT JOIN subjects s ON c.subject_id = s.id
        """)
        content = cursor.fetchall()
        for item in content:
            print(f"ID: {item[0]}, Title: {item[1]}")
            print(f"   Subject: {item[5]} (ID: {item[4]})")
            print(f"   Type: {item[3]}")
            print(f"   Description: {item[2]}")
            print(f"   Created: {item[6]}")
            print()
        
        print("=" * 50)
        print("COMPRAS:")
        cursor.execute("""
            SELECT p.id, u.username, s.title, p.amount, p.created_at 
            FROM purchases p 
            LEFT JOIN users u ON p.user_id = u.id 
            LEFT JOIN subjects s ON p.subject_id = s.id
        """)
        purchases = cursor.fetchall()
        for purchase in purchases:
            print(f"ID: {purchase[0]}, User: {purchase[1]}")
            print(f"   Subject: {purchase[2]}")
            print(f"   Amount: ${purchase[3]}")
            print(f"   Date: {purchase[4]}")
            print()
            
        if not purchases:
            print("No hay compras registradas")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_all_data()