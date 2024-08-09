import sqlite3

def setup_db():
    conn = sqlite3.connect('secure_db.sqlite')
    cursor = conn.cursor()

    # Create necessary tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        content TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        query TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS common_terms (
        user_id TEXT NOT NULL,
        term TEXT NOT NULL,
        PRIMARY KEY (user_id, term)
    )
    ''')

    conn.commit()
    conn.close()

def save_document(user_id, document_name, content):
    """Saves a document in the database without encryption."""
    conn = sqlite3.connect('secure_db.sqlite')
    cursor = conn.cursor()
    
    cursor.execute('INSERT INTO documents (user_id, document_name, content) VALUES (?, ?, ?)',
                   (user_id, document_name, content))
    conn.commit()
    conn.close()

def save_query(user_id, query, result):
    """Saves a user's query and the corresponding result in the database without encryption."""
    conn = sqlite3.connect('secure_db.sqlite')
    cursor = conn.cursor()
    
    cursor.execute('INSERT INTO queries (user_id, query, result) VALUES (?, ?, ?)',
                   (user_id, query, result))
    conn.commit()
    conn.close()

def save_search(user_id, query):
    """Saves a search query in the database for tracking trends."""
    conn = sqlite3.connect('secure_db.sqlite')
    cursor = conn.cursor()
    from datetime import datetime
    date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('INSERT INTO searches (user_id, query, date) VALUES (?, ?, ?)',
                   (user_id, query, date))
    conn.commit()
    conn.close()

def get_user_history(user_id):
    """Retrieves the user's query history and corresponding results without decryption."""
    conn = sqlite3.connect('secure_db.sqlite')
    cursor = conn.cursor()
    
    cursor.execute('SELECT query, result FROM queries WHERE user_id = ?', (user_id,))
    history = cursor.fetchall()
    
    conn.close()
    
    # Concatenate all history into a readable format
    concatenated_history = "\n".join([f"Query: {row[0]}\nResult: {row[1]}\n" for row in history])
    
    return concatenated_history

def get_document_count():
    """Returns the number of documents uploaded."""
    conn = sqlite3.connect('secure_db.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM documents')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_most_searched_queries():
    """Returns the most searched queries."""
    conn = sqlite3.connect('secure_db.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT query, COUNT(*) as count FROM queries GROUP BY query ORDER BY count DESC')
    queries = cursor.fetchall()
    conn.close()
    return queries

def get_document_types(user_id):
    """Returns the distribution of document types for the user."""
    conn = sqlite3.connect('secure_db.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT substr(document_name, -3) AS doc_type, COUNT(*) FROM documents WHERE user_id = ? GROUP BY doc_type', (user_id,))
    doc_types = cursor.fetchall()
    conn.close()
    return doc_types

def get_search_trends(user_id):
    """Returns the search trends over time for the user."""
    conn = sqlite3.connect('secure_db.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT date, COUNT(*) FROM searches WHERE user_id = ? GROUP BY date ORDER BY date', (user_id,))
    trends = cursor.fetchall()
    conn.close()
    return trends

def get_common_terms(user_id):
    """Fetches and returns the most common terms for the specified user."""
    conn = sqlite3.connect('secure_db.sqlite')
    cursor = conn.cursor()

    # Ensure the table exists before querying
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='common_terms';")
    if cursor.fetchone() is None:
        conn.close()
        raise Exception("Table 'common_terms' does not exist.")
    
    # Query to get common terms
    cursor.execute('SELECT term FROM common_terms WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    
    # Decode bytes to strings if necessary and join
    all_text = ' '.join([row[0].decode('utf-8') if isinstance(row[0], bytes) else row[0] for row in rows])
    
    conn.close()
    return all_text.split()  # Return as a list of terms