from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import MetaData

# URL avec le driver 'postgresql+asyncpg'
DATABASE_URL = "postgresql+asyncpg://followup_user:followup_password@localhost:5432/followup_db"

NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)

# Moteur asynchrone
engine = create_async_engine(DATABASE_URL, echo=True)

# Factory de sessions asynchrones
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dépendance pour FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session