from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import sqlite3
import requests
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for sessions and flash messages

# Database helper functions
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('books.db')
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Google Books API function
def search_book_by_isbn(isbn):
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        response = requests.get(url)
        data = response.json()
        
        if data['totalItems'] > 0:
            book_info = data['items'][0]['volumeInfo']
            return {
                'isbn': isbn,
                'title': book_info.get('title', 'Unknown'),
                'author': ', '.join(book_info.get('authors', ['Unknown'])),
                'page_count': book_info.get('pageCount', 0),
                'average_rating': book_info.get('averageRating', 0.0),
                'thumbnail_url': book_info.get('imageLinks', {}).get('thumbnail', '')
            }
        return None
    except Exception as e:
        print(f"Error fetching book data: {e}")
        return None

# Routes
@app.route('/')
@login_required
def index():
    db = get_db()
    books = db.execute('''
        SELECT * FROM books WHERE user_id = ? ORDER BY added_at DESC
    ''', [session['user_id']]).fetchall()
    return render_template('index.html', books=books)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/add_book', methods=['POST'])
@login_required
def add_book():
    isbn = request.form['isbn']
    book_info = search_book_by_isbn(isbn)
    
    if book_info:
        db = get_db()
        try:
            db.execute('''
                INSERT INTO books (isbn, title, author, page_count, average_rating, 
                                 thumbnail_url, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (book_info['isbn'], book_info['title'], book_info['author'],
                 book_info['page_count'], book_info['average_rating'],
                 book_info['thumbnail_url'], session['user_id']))
            db.commit()
            flash('Book added successfully!')
        except sqlite3.IntegrityError:
            flash('You already have this book in your collection')
    else:
        flash('Book not found')
    return redirect(url_for('index'))

@app.route('/delete_book/<int:book_id>')
@login_required
def delete_book(book_id):
    db = get_db()
    db.execute('DELETE FROM books WHERE id = ? AND user_id = ?',
               (book_id, session['user_id']))
    db.commit()
    flash('Book deleted successfully')
    return redirect(url_for('index'))

# Initialize database
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

if __name__ == '__main__':
    if not os.path.exists('books.db'):
        init_db()
    app.run(debug=True)