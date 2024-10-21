from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text  # Import text from SQLAlchemy
from app.config.database import engine, Base
from app.models.models import Roles

async def init_db():
    # Create all the database tables (schemas)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        async with session.begin():
            # Clear existing data
            await session.execute(text("TRUNCATE TABLE roles RESTART IDENTITY CASCADE;"))

            # Add default roles with specific IDs
            default_roles = [
                Roles(id=0, role_name="member"),
                Roles(id=1, role_name="admin")
            ]
            session.add_all(default_roles)
            await session.commit()
            print("Default roles added: member, admin")

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())