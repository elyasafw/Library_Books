from db_connection import DB
from pydantic import BaseModel, EmailStr, ValidationError


class NewMember(BaseModel):
    name: str
    email: EmailStr


class UpdateMember(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


class MemberDB:
    def __init__(self):
        self.conn = DB.get_connection()

    def create_member(self, new_member: NewMember):
        try:
            member_data = new_member.model_dump()
            values = [member_data["name"], member_data["email"]]
            with self.conn.cursor() as cursor:
                query = """INSERT INTO members (name, email)
                                    VALUES (%s, %s)"""
                cursor.execute(query, [values])
                self.conn.commit()
        except ValidationError as e:
            raise e

    def get_all_members(self):
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM members")
            all_members = cursor.fetchall()
            return all_members