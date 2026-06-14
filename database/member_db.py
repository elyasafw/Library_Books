from .db_connection import DB
from logs.logs_config import logger


class MemberDB:

    def create_member(self, member_data):
            values = [member_data["name"], member_data["email"]]
            with DB.get_connection().cursor() as cursor:
                query = """INSERT INTO members (name, email)
                                    VALUES (%s, %s)"""
                cursor.execute(query, values)
                if cursor.rowcount > 0:
                    DB.get_connection().commit()
                    logger.info(f"Member {member_data["name"]} created successfully")
                    return member_data
            logger.error(f"Member not create..")
            return

    def get_all_members(self):
        with DB.get_connection().cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM members")
            all_members = cursor.fetchall()
            if cursor.rowcount > 0:
                logger.info("Getting all members list")
                return all_members
            logger.warning("Table members is empty")
            return

    def get_member_by_id(self, member_id):
        with DB.get_connection().cursor(dictionary=True) as cursor:
            query = "SELECT * FROM members WHERE id = %s"
            cursor.execute(query, [member_id])
            member = cursor.fetchone()
            if member:
                logger.info(f"Getting member ID: {member_id}")
                return member
            logger.warning(f"Member ID: {member_id} does not exists")
            return None

    def update_member(self, member_id, update_data):
        columns = []
        values = []
        for key, value in update_data.items():
            columns.append(f"{key} = %s")
            values.append(value)
        values.append(member_id)
        with DB.get_connection().cursor() as cursor:
            query = f"""UPDATE members
                                SET {", ".join(columns)} WHERE id = %s"""
            cursor.execute(query, values)
            is_update = cursor.rowcount > 0
            DB.get_connection().commit()
            if is_update:
                logger.info(f"Member ID: {member_id} updated successfully")
                return update_data
            logger.warning("Member updated failed.. ID not found / no changes")
            return None

    def deactivate_member(self, member_id):
        with DB.get_connection().cursor() as cursor:
            query = """UPDATE members
                                SET is_active = FALSE
                                WHERE id = %s"""
            cursor.execute(query, [member_id])
            is_deactivate = cursor.rowcount
            DB.get_connection().commit()
            if is_deactivate:
                logger.info(f"Member ID: {member_id} deactivated successfully")
                return is_deactivate
            logger.warning(f"Member ID: {member_id} does not exists")
            return None

    def activate_member(self, member_id):
        with DB.get_connection().cursor() as cursor:
            query = """UPDATE members
                                SET is_active = TRUE
                                WHERE id = %s"""
            cursor.execute(query, [member_id])
            is_activate = cursor.rowcount
            DB.get_connection().commit()
            if is_activate:
                logger.info(f"Member ID: {member_id} activate successfully")
                return is_activate
            logger.warning(f"Member ID: {member_id} does not exists")
            return None

    def increment_borrows(self, member_id):
        with DB.get_connection().cursor() as cursor:
            query = """UPDATE members
                                SET total_borrows = total_borrows + 1
                                WHERE id = %s"""
            cursor.execute(query, [member_id])
            is_increment = cursor.rowcount
            DB.get_connection().commit()
            if is_increment:
                logger.info(f"Borrows of member ID: {member_id} updated")
                return is_increment
            logger.warning(f"Member ID: {member_id} does not exists")
            return None

    def count_active_members(self):
        with DB.get_connection().cursor() as cursor:
            query = """SELECT COUNT(*) FROM members
                                WHERE is_active = TRUE"""
            cursor.execute(query)
            active_members = cursor.fetchone()
            logger.info("Getting count of active members")
            return active_members[0] if active_members else 0

    def get_top_member(self):
        with DB.get_connection().cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM members ORDER BY total_borrows DESC LIMIT 1")
            top_member = cursor.fetchone()
            if top_member:
                logger.info("Getting the top member borrows")
                return top_member
            logger.warning("Table members is empty")