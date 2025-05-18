DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS users;


CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    page_count INTEGER,
    average_rating FLOAT,
    thumbnail_url TEXT,  
    user_id INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    -- Ensure a user can't add the same ISBN twice
    UNIQUE(isbn, user_id)
);


CREATE INDEX idx_books_user_id ON books(user_id);
CREATE INDEX idx_books_isbn ON books(isbn);
CREATE INDEX idx_users_username ON users(username);


INSERT INTO users (username, password) VALUES 
('test_user', 'test_password'),
('admin', 'admin_password');


INSERT INTO books (isbn, title, author, page_count, average_rating, thumbnail_url, user_id) VALUES 
('9781449372620', 'Learning Python', 'Mark Lutz', 1648, 4.5, 'https://example.com/thumbnail1.jpg', 1),
('9780596516499', 'Python Programming', 'David Ascher', 1214, 4.0, 'https://example.com/thumbnail2.jpg', 1);