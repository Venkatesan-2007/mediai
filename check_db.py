import sqlite3

db_path = r'g:\medi ai\backend\database\medi_ai.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('=== USERS ===')
try:
    cursor.execute('SELECT id, username FROM users')
    for row in cursor.fetchall():
        print(f'ID: {row[0]}, Username: {row[1]}')
except Exception as e:
    print(f'Error: {e}')

print()
print('=== BOOKS ===')
try:
    cursor.execute('SELECT id, user_id, filename FROM books')
    for row in cursor.fetchall():
        print(f'ID: {row[0]}, User: {row[1]}, File: {row[2]}')
except Exception as e:
    print(f'Error: {e}')

print()
print('=== CHUNKS TABLE ===')
try:
    cursor.execute('PRAGMA table_info(chunks)')
    print('Columns:')
    for row in cursor.fetchall():
        print(f'  {row[1]}: {row[2]}')
except Exception as e:
    print(f'Error: {e}')

conn.close()
