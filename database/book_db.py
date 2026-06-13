from db_connection import DB
from pydantic import BaseModel


class NewBook(BaseModel):
    title: str
    author: str
    genre: str

class UpdateBook(BaseModel):
    title: str | None = None
    author: str | None = None
    genre: str | None = None
    is_available: bool | None = None

class BooksDB:
    def __init__(self):
        self.conn = DB.get_connection()

    def create_book(self, new_book: NewBook):
        book_data = new_book.model_dump()
        values = [book_data["title"], book_data["author"], book_data["genre"]]
        with self.conn.cursor() as cursor:
            query = """INSERT INTO books (title, author, genre)
                                VALUES (%s, %s, %s)"""
            cursor.execute(query, values)
            self.conn.commit()

    def get_all_books(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM books")
            all_books = cursor.fetchall()
        return all_books

    def get_book_by_id(self, id: int):
        with self.conn.cursor(dictionary=True) as cursor:
            query = """SELECT * FROM books
                                WHERE id = %s"""
            cursor.execute(query, [id])
            book = cursor.fetchone()
            if not book:
                return None
            return book

    def update_book(self, book_id, update_data: UpdateBook):
        changes = update_data.model_dump(exclude_unset=True)
        columns = []
        values = []
        for key, value in changes.items():
            columns.append(f"{key} = %s")
            values.append(value)
        values.append(book_id)
        with self.conn.cursor() as cursor:
            query = f"""UPDATE books
                                SET {", ".join(columns)} WHERE id = %s"""
            cursor.execute(query, values)
            self.conn.commit()

    def set_available(self, book_id, val, member_id):
        with self.conn.cursor() as cursor:
            query = """UPDATE books
                                SET is_available = %s, borrowed_by_member_id = %s
                                WHERE id = %s"""
            cursor.execute(query, [val, member_id, book_id])
            self.conn.commit()

    def count_total_books(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM books")
            all_books = cursor.fetchone()
            return all_books[0] if all_books else 0

    def available_books(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM books WHERE is_available = TRUE")
            available_books = cursor.fetchone()
            return available_books[0] if available_books else 0

    def count_borrowed_books(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM books WHERE is_available = FALSE")
            borrowed_books = cursor.fetchone()
            return borrowed_books[0] if borrowed_books else 0

    def count_by_genre(self):
        with self.conn.cursor(dictionary=True) as cursor:
            query = """SELECT genre, COUNT(*) AS book_count 
                                FROM books 
                                GROUP BY genre 
                                ORDER BY book_count DESC"""
            cursor.execute(query)
            genre_count = cursor.fetchall()
        return genre_count

    def count_active_borrow_by_member(self, member_id):
        with self.conn.cursor() as cursor:
            query = """SELECT COUNT(*) FROM books 
                                WHERE borrowed_by_member_id = %s AND is_available = FALSE"""
            cursor.execute(query, [member_id])
            count_borrow = cursor.fetchone()
            return count_borrow[0] if count_borrow else 0