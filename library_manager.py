import sqlite3
import streamlit as st

# Database file ka naam
DB_FILE = "library.db"

# Database connection establish karne ke liye function
def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Taaki hum row ke columns ko dictionary ke tarah access kar sakein
    return conn

# Database ko initialize karo, table agar exist nahi karti to create karo
def initialize_db():
    conn = get_connection()
    c = conn.cursor() # Cursor object banata hai jo SQL queries ko execute karne ke liye use hota hai.
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER,
            genre TEXT,
            read INTEGER
        )
    ''')
    conn.commit() # Database mein changes ko save karta hai taaki wo persist rahein
    conn.close() # Database connection ko close karta hai taaki resources free ho jaayein
    
    

# Database mein naya book add karne ke liye function
def add_book_db(title, author, year, genre, read):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO books (title, author, year, genre, read)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, author, year, genre, int(read)))
    conn.commit()
    conn.close()
    
    

# Database se book remove karne ke liye function (book id ke basis par)
def remove_book_db(book_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()

# Search query ke through books dhoondhne ka function
def search_books_db(query):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT * FROM books 
        WHERE LOWER(title) LIKE ? OR LOWER(author) LIKE ?
    ''', (f'%{query.lower()}%', f'%{query.lower()}%'))
    results = c.fetchall()
    conn.close()
    return results

# Saare books fetch karne ka function
def fetch_all_books_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM books')
    results = c.fetchall()
    conn.close()
    return results

# Library statistics ke liye function: total books aur kitne read hue hain
def get_statistics_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM books')
    total_books = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM books WHERE read = 1')
    read_books = c.fetchone()[0]
    conn.close()
    return total_books, read_books

# Streamlit par "Add Book" ka UI
def add_book():
    st.subheader("📖 Add a New Book")
    with st.form("add_book_form"):
        title = st.text_input("Enter the book title:")
        author = st.text_input("Enter the author:")
        year = st.number_input("Enter the publication year:", min_value=0, step=1)
        genre = st.text_input("Enter the genre:")
        read_status = st.checkbox("Have you read this book?")
        submitted = st.form_submit_button("📌 Add Book")
        if submitted:
            if title and author and genre:
                add_book_db(title, author, int(year), genre, read_status)
                st.success(f"✅ '{title}' added successfully!")
            else:
                st.error("⚠ Please fill in all fields before submitting.")

# Streamlit par "Remove Book" ka UI
def remove_book():
    st.subheader("🗑 Remove a Book")
    books = fetch_all_books_db()
    if books:
        # Har book ko ek descriptive label ke saath list karte hain
        options = {
            "Select a book": None
            }
        
        for book in books:
            label = f"{book['title']} by {book['author']} ({book['year']})"
            options[label] = book['id']
            
        selected = st.selectbox("Select a book to remove:", list(options.keys()))
        if selected != "Select a book" and st.button("❌ Remove Book"):
            book_id = options[selected]
            remove_book_db(book_id)
            st.success("🚮 Book removed successfully!")
    else:
        st.info("📭 Your library is empty. Add books first!")

# Streamlit par "Search Book" ka UI
def search_books():
    st.subheader("🔍 Search for a Book")
    search_query = st.text_input("Search by title or author:")
    if search_query:
        results = search_books_db(search_query)
        if results:
            st.write("### 📚 Search Results")
            for book in results:
                st.write(f"{book['title']} by {book['author']} ({book['year']}) - {book['genre']} - {'✅ Read' if book['read'] else '📖 Unread'}")
        else:
            st.warning("❌ No matching books found.")

# Streamlit par "Display All Books" ka UI
def display_books():
    st.subheader("📚 Your Book Collection")
    books = fetch_all_books_db()
    if not books:
        st.info("📭 Your library is empty. Add some books!")
    else:
        for book in books:
            st.write(f"{book['title']} by {book['author']} ({book['year']}) - {book['genre']} - {'✅ Read' if book['read'] else '📖 Unread'}")

# Streamlit par "Display Statistics" ka UI
def display_statistics():
    st.subheader("📊 Library Statistics")
    total_books, read_books = get_statistics_db()
    unread_books = total_books - read_books
    read_percentage = (read_books / total_books * 100) if total_books > 0 else 0
    st.metric("📚 Total Books", total_books)
    st.metric("✅ Books Read", read_books)
    st.metric("📖 Unread Books", unread_books)
    st.progress(read_percentage / 100)
    st.write(f"📈 Read Percentage: {read_percentage:.2f}%")

# Main function jo Streamlit UI ko manage karta hai
def main():
    st.title("📚 Personal Library Manager with Database")
    initialize_db()  # Database aur table create karo agar exist nahi karti

    menu = [
        "📖 Add a Book", 
        "🗑 Remove a Book", 
        "🔍 Search for a Book", 
        "📚 Display All Books", 
        "📊 Display Statistics", 
        "🚪 Exit"
    ]
    choice = st.sidebar.radio("📌 Navigation", menu)

    if choice == "📖 Add a Book":
        add_book()
    elif choice == "🗑 Remove a Book":
        remove_book()
    elif choice == "🔍 Search for a Book":
        search_books()
    elif choice == "📚 Display All Books":
        display_books()
    elif choice == "📊 Display Statistics":
        display_statistics()
    elif choice == "🚪 Exit":
        st.success("📁 Library saved to database. Goodbye! 👋")
        st.stop()

if __name__ == "__main__":
    main()
