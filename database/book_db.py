from db_connection import DB
from pydantic import BaseModel
from logs.logs_config import logger


class NewBook(BaseModel):
    title: str
    author: str
    genre: str

class UpdateBook(BaseModel):
    title: str | None = None
    author: str | None = None
    genre: str | None = None

class BooksDB:
    def __init__(self):
        DB.get_connection()

    def create_book(self, new_book: NewBook):
        book_data = new_book.model_dump()
        values = [book_data["title"], book_data["author"], book_data["genre"]]
        with DB.get_connection().cursor() as cursor:
            query = """INSERT INTO books (title, author, genre)
                                VALUES (%s, %s, %s)"""
            cursor.execute(query, values)
            cursor.fetchone()
            book_create = cursor.rowcount > 0
            self.DB.get_connection().commit()
            if book_create:
                logger.info(f"Book {book_data["title"]} created successful")
                return book_data
            logger.warning("Book not create..")
            return

    def get_all_books(self):
        with DB.get_connection().cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM books")
            all_books = cursor.fetchall()
            if cursor.rowcount > 0:
                logger.info("Getting all books list")
                return all_books
            logger.warning("Table books is empty")
            return

    def get_book_by_id(self, book_id: int):
        with DB.get_connection().cursor(dictionary=True) as cursor:
            query = """SELECT * FROM books
                                WHERE id = %s"""
            cursor.execute(query, [book_id])
            book = cursor.fetchone()
            if book:
                logger.info(f"Getting book ID:{book_id}")
                return book
            logger.warning(f"Book ID: {book_id} does not exists")
            return None

    def update_book(self, book_id, update_data: UpdateBook):
        changes = update_data.model_dump(exclude_unset=True)
        if not changes:
            logger.warning("Book data update is empty..  No changes")
            return
        columns = []
        values = []
        for key, value in changes.items():
            columns.append(f"{key} = %s")
            values.append(value)
        values.append(book_id)
        with DB.get_connection().cursor() as cursor:
            query = f"""UPDATE books
                                SET {", ".join(columns)} WHERE id = %s"""
            cursor.execute(query, values)
            is_update = cursor.rowcount > 0
            DB.get_connection().commit()
            if is_update:
                logger.info(f"Book ID: {book_id} updated successfully")
                return changes
            logger.warning("Book updated field.. ID not found / no changes")
            return None

    def set_available(self, book_id, val, member_id):
        with DB.get_connection().cursor() as cursor:
            query = """UPDATE books
                                SET is_available = %s, borrowed_by_member_id = %s
                                WHERE id = %s"""
            cursor.execute(query, [val, member_id, book_id])
            is_update = cursor.rowcount > 0
            DB.get_connection().commit()
            if is_update:
                logger.info(f"Book ID: {book_id} update, available: {val}")
                return is_update
            logger.warning(f"Book ID: {book_id} does not exists")
            return is_update

    def count_total_books(self):
        with DB.get_connection().cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM books")
            all_books = cursor.fetchone()
            return all_books[0] if all_books else 0

    def available_books(self):
        with DB.get_connection().cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM books WHERE is_available = TRUE")
            available_books = cursor.fetchone()
            return available_books[0] if available_books else 0

    def count_borrowed_books(self):
        with DB.get_connection().cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM books WHERE is_available = FALSE")
            borrowed_books = cursor.fetchone()
            return borrowed_books[0] if borrowed_books else 0

    def count_by_genre(self):
        with DB.get_connection().cursor(dictionary=True) as cursor:
            query = """SELECT genre, COUNT(*) AS book_count 
                                FROM books 
                                GROUP BY genre 
                                ORDER BY book_count DESC"""
            cursor.execute(query)
            genre_count = cursor.fetchall()
        if genre_count:
            logger.info("Getting count of all books genres")
            return genre_count
        logger.warning("Table books is empty")

    def count_active_borrow_by_member(self, member_id):
        with DB.get_connection().cursor() as cursor:
            query = """SELECT COUNT(*) FROM books 
                                WHERE borrowed_by_member_id = %s AND is_available = FALSE"""
            cursor.execute(query, [member_id])
            count_borrow = cursor.fetchone()
            return count_borrow[0] if count_borrow else 0