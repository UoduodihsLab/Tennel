import asyncio

from app.constants.enum import UserRole
from app.db.models.user import UserModel
from app.db.register import connect_to_db, close_db_connection
from app.utils.security import hash_password


async def create_admin():
    await connect_to_db()
    username = input("Username: ")
    password = input("Password: ")
    hashed_password = hash_password(password)
    await UserModel(username=username, hashed_password=hashed_password, role=UserRole.ADMIN).save()
    print("Admin account created")
    await close_db_connection()


if __name__ == '__main__':
    asyncio.run(create_admin())
