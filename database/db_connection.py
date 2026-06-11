import mysql.connector


class DBconnection:
    def __init__(self):
        self.connect()

    def connect(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="library",
            password="100526",
            database="library_db",
            port=3308
            )
        print("connect successfully")

    def get_connection(self):
        if not self.conn.is_connected():
            self.connect()
        return self.conn

    def create_db(self):
        conn = mysql.connector.connect(
            host="localhost",
            user="library",
            password="100526",
            port=3308
            )
        with conn.cursor() as cursor:
            cursor.execute(
                """CREATE DATABASE IF NOT EXISTS library_db
                    USE library_db"""
                    )
            conn.commit()

    def create_books_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS books (
                        id INT PRIMARY KEY AUTO_INCREMENT ,
                        title VARCHAR(50) NOT NULL ,
                        author VARCHAR(50) NOT NULL ,
                        genre ENUM('fiction', 'non-fiction', 'science', 'history', 'other') ,
                        is_available BOOLEAN DEFAULT TRUE ,
                        borrowed_by_member_id INT NOT NULL
                        )"""
                        )
            self.conn.commit()


    def create_members_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS members (
                        id INT PRIMARY KEY AUTO_INCREMENT ,
                        name VARCHAR(50) NOT NULL ,
                        email VARCHAR(50) UNIQUE NOT NULL ,
                        is_active BOOLEAN DEFAULT TRUE ,
                        total_borrows INT DEFAULT 0
                        )"""
                        )
            self.conn.commit()



DB = DBconnection()