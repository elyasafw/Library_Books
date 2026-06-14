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

    def member_by_id(self, member_id):
        with self.conn.cursor(dictionary=True) as cursor:
            query = "SELECT * FROM members WHERE id = %s"
            cursor.execute(query, [member_id])
            member = cursor.fetchone()
            return member if member else None

    def update_member(self, member_id, update_data: UpdateMember):
        changes = update_data.model_dump(exclude_unset=True)
        columns = []
        values = []
        for key, value in changes.items():
            columns.append(f"{key} = %s")
            values.append(value)
        values.append(member_id)
        with self.conn.cursor() as cursor:
            query = f"""UPDATE members
                                SET {", ".join(columns)} WHERE id = %s"""
            cursor.execute(query, values)
            self.conn.commit()

    def deactivate_member(self, member_id):
        with self.conn.cursor() as cursor:
            query = """UPDATE members
                                SET is_active = FALSE
                                WHERE id = %s"""
            cursor.execute(query, [member_id])
            self.conn.commit()

    def activate_member(self, member_id):
        with self.conn.cursor() as cursor:
            query = """UPDATE members
                                SET is_active = TRUE
                                WHERE id = %s"""
            cursor.execute(query, [member_id])
            self.conn.commit()

    def increment_borrows(self, member_id):
        with self.conn.cursor() as cursor:
            query = """UPDATE members
                                SET total_borrows = total_borrows + 1
                                WHERE id = %s"""
            cursor.execute(query, [member_id])
            self.conn.commit()

    def count_active_members(self):
        with self.conn.cursor() as cursor:
            query = """SELECT COUNT(*) FROM members
                                WHERE is_active = TRUE"""
            cursor.execute(query)
            active_members = cursor.fetchone()
            return active_members[0] if active_members else 0

    def get_top_member(self):
        with self.conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM members ORDER BY total_borrows DESC LIMIT 1")
            top_member = cursor.fetchone()
            return top_member()