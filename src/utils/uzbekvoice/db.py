from sqlalchemy import (
    create_engine,
    Table,
    MetaData,
    Column,
    BigInteger,
    Integer,
    String,
    insert,
    select
)

from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.sql import exists
from os import getenv

Base = declarative_base()


engine = create_engine(getenv("DATABASE_URL"))

metadata_obj = MetaData()


class User(Base):
    __tablename__ = 'user_account'
    id = Column(BigInteger, primary_key=True)
    tg_id = Column(BigInteger, unique=True)
    uuid = Column(String(40), unique=True)
    access_token = Column(String(40), unique=True)
    full_name = Column(String(300))
    phone_number = Column(String(30))
    sweatshirt_size = Column(String(5))
    gender = Column(String(20))
    accent_region = Column(String(100))
    year_of_birth = Column(Integer)
    native_language = Column(String(100))


Base.metadata.create_all(engine)

user_table = Table('user_account', metadata_obj, autoload_with=engine)
session = Session(engine)


async def write_user(
        tg_id,
        uuid,
        access_token,
        full_name,
        phone_number,
        gender,
        accent_region,
        year_of_birth,
        native_language
):
    with engine.connect() as conn:
        create_user = insert(user_table).values(
            tg_id=tg_id,
            uuid=uuid,
            access_token=access_token,
            full_name=full_name,
            phone_number=phone_number,
            gender=gender,
            accent_region=accent_region,
            year_of_birth=year_of_birth,
            native_language=native_language
        )
        conn.execute(create_user)
        session.commit()
        return uuid, access_token


def user_exists(tg_id):
    with engine.connect() as conn:
        q = session.query(exists().where(User.tg_id == tg_id)).scalar()
        return q


def get_user(tg_id):
    with engine.connect() as conn:
        q = select(user_table).where(user_table.c.tg_id == tg_id)
        return conn.execute(q).first()

