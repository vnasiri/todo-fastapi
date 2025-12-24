import uuid

from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.security import hash_password
from src.entities.todo import Priority, Todo
from src.entities.user import User


def get_user_data_factory(**kwargs):
    """Generates unique user data to prevent 'Unique Constraint' errors."""
    unique_id = uuid.uuid4().hex
    defaults = {
        "first_name": "Sarah",
        "last_name": "Doe",
        "username": f"user_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "Sec_urePas$sword123",
        "email_verified": True,
    }
    defaults.update(kwargs)
    return defaults


VALID_TODO = {
    "title": "Buy groceries",
    "description": "Milk, Bread, Eggs",
    "is_completed": False,
    "priority": Priority.Medium.value,
}

VALID_TODO_UPDATE = {
    "title": "Buy groceries and milk",
    "description": "Updated: Milk, Bread, Eggs, Cheese",
    "is_completed": True,
    "priority": Priority.High.value,
}


async def create_test_user(session: AsyncSession, **kwargs):
    user_data = get_user_data_factory(**kwargs)
    password = user_data.pop("password")
    user = User(**user_data, password_hash=hash_password(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def create_test_todo(session: AsyncSession):
    todo = Todo(**VALID_TODO)
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return todo
