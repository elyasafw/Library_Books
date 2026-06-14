import mysql.connector
from logs.logs_config import logger


class DBconnection:
    def __init__(self):
        self.create_db()
        self.conn = None
        self.connect()

    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="library",
                password="100526",
                database="library_db",
                port=3308,
            )
            logger.info("Connected successfully to library_db")
        except mysql.connector.Error as e:
            logger.error(f"Connection failed: {e}")
            raise e

    def get_connection(self):
        if self.conn is None or not self.conn.is_connected():
            self.connect()
        return self.conn

    def create_db(self):
        conn = mysql.connector.connect(
            host="localhost", user="library", password="100526", port=3308
        )
        with conn.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS library_db")
        conn.close()

    def create_members_table(self):
        with self.get_connection().cursor() as cursor:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS members (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        name VARCHAR(50) NOT NULL,
                        email VARCHAR(50) UNIQUE NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        total_borrows INT DEFAULT 0
                        )"""
            )
            self.conn.commit()
            logger.info("Members table ready")

    def create_books_table(self):
        with self.get_connection().cursor() as cursor:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS books (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        title VARCHAR(50) NOT NULL,
                        author VARCHAR(50) NOT NULL,
                        genre ENUM('fiction', 'non-fiction', 'science', 'history', 'other'),
                        is_available BOOLEAN DEFAULT TRUE,
                        borrowed_by_member_id INT NULL,
                        FOREIGN KEY (borrowed_by_member_id) REFERENCES members(id) ON DELETE SET NULL
                        )"""
            )
            self.conn.commit()
            logger.info("Books table ready")


    def close_connection(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()
            logger.info("Main database connection closed")



DB = DBconnection()