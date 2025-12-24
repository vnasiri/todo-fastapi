from src.core.security import create_access_token
from src.entities.user import User


async def issue_test_token(user: User):
    return await create_access_token(
        payload={
            "user": {"sub": user.email, "user_id": str(user.id)},
        }
    )
