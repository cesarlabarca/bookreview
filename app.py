import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB = "library.db"

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS books (
                bookid INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bookid INTEGER,
                finished TEXT,
                note TEXT,
                FOREIGN KEY (bookid) REFERENCES books (bookid)
            )""")

@app.route('/')
def index():
    conn = get_db_connection()
    # Counts
    total_read = conn.execute("SELECT COUNT(*) FROM activity WHERE finished = 'Yes'").fetchone()[0]
    total_library = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    
    # Recently Finished
    finished = conn.execute("""
        SELECT b.title, b.author, a.note FROM books b 
        JOIN activity a ON b.bookid = a.bookid 
        WHERE a.finished = 'Yes' ORDER BY a.id DESC LIMIT 5
    """).fetchall()
    
    # Want to Read (Books in library NOT in activity as 'Yes')
    want_to_read = conn.execute("""
        SELECT title, author FROM books 
        WHERE bookid NOT IN (SELECT bookid FROM activity WHERE finished = 'Yes')
    """).fetchall()
    
    conn.close()
    return render_template('index.html', total_read=total_read, total_library=total_library, 
                           finished=finished, want_to_read=want_to_read)

@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        # Collect all 4 pieces of data from the form
        title = request.form['title']
        author = request.form['author']
        published = request.form['published']
        pages = request.form['pages']
        
        conn = get_db_connection()
        # Update the SQL to include all columns
        conn.execute("""
            INSERT INTO books (title, author, published, pages) 
            VALUES (?, ?, ?, ?)
        """, (title, author, published, pages))
        
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_book.html')

@app.route('/add', methods=['GET', 'POST'])
def add_activity():
    conn = get_db_connection()
    if request.method == 'POST':
        book_id = request.form['book_id']
        note = request.form['note']
        conn.execute("INSERT INTO activity (bookid, finished, note) VALUES (?, 'Yes', ?)",
                    (book_id, note))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    books = conn.execute("SELECT bookid, title FROM books").fetchall()
    conn.close()
    return render_template('add.html', books=books)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)