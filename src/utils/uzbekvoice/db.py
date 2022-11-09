from datetime import datetime
from sqlalchemy import (
    create_engine,
    BigInteger,
    MetaData,
    Boolean,
    Column,
    String,
    insert,
    select,
    Table,
    update,
    DATETIME
)
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.sql import exists

from dotenv import load_dotenv, find_dotenv
from os import getenv

load_dotenv(find_dotenv())

engine = create_engine(getenv("DATABASE_URL"))
Base = declarative_base()
metadata_obj = MetaData()


class User(Base):
    __tablename__ = 'user_account'
    id = Column(BigInteger, primary_key=True)
    tg_id = Column(BigInteger, unique=True)
    under_investigation = Column(Boolean, default=False, nullable=False)
    offset_score = Column(BigInteger, default=0, nullable=False)
    karma = Column(BigInteger, default=0, nullable=False)
    correct_count = Column(BigInteger, default=0, nullable=False)
    error_count = Column(BigInteger, default=0, nullable=False)
    uuid = Column(String(40), unique=True)
    access_token = Column(String(40), unique=True)
    full_name = Column(String(300))
    phone_number = Column(String(30))
    sweatshirt_size = Column(String(5))
    gender = Column(String(20))
    accent_region = Column(String(100))
    year_of_birth = Column(String(50), nullable=True)
    native_language = Column(String(100))
    vote_streak_count = Column(BigInteger, nullable=True, default=0)
    is_banned = Column(Boolean, nullable=True, default=False)
    ban_reason = Column(String(300), nullable=True)
    banned_time = Column(DATETIME, nullable=True)
    last_validated_at = Column(DATETIME, nullable=True)


class Violations(Base):
    __tablename__ = 'user_violations'
    id = Column(BigInteger, primary_key=True)
    created_at = Column(DATETIME, nullable=False, server_default=func.now())
    type = Column(String(255))
    client_id = Column(String(36))


Base.metadata.create_all(engine)
user_table = Table('user_account', metadata_obj, autoload_with=engine)
violation_table = Table('user_violations', metadata_obj, autoload_with=engine)
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
            native_language=native_language,
        )

        conn.execute(create_user)
        session.commit()
        return uuid, access_token


def user_exists(tg_id):
    with engine.connect() as conn:
        q = session.query(exists().where(User.tg_id == tg_id)).scalar()
        return q


def user_banned(tg_id):
    with engine.connect() as conn:
        q = select(user_table).where(user_table.c.tg_id == tg_id)
        user = conn.execute(q).first()
        return user is not None and user.is_banned


def get_user(tg_id):
    with engine.connect() as conn:
        q = select(user_table).where(user_table.c.tg_id == tg_id)
        return conn.execute(q).first()


def add_user_violation(
        tg_id,
        violation_type
):
    with engine.connect() as conn:
        user = get_user(tg_id)
        conn.execute(
            insert(violation_table).values(
                type=violation_type,
                client_id=user.uuid
            )
        )
        session.commit()


def is_user_under_investigation(
        tg_id,
):
    with engine.connect() as conn:
        user = get_user(tg_id)
        return user.under_investigation


def increase_user_error_count(
        tg_id
):
    with engine.connect() as conn:
        q = update(user_table).where(user_table.c.tg_id == tg_id).values(
            error_count=user_table.c.error_count + 1,
            karma=user_table.c.karma - 1
        )
        conn.execute(q)
        session.commit()


def increase_user_correct_count(
        tg_id
):
    with engine.connect() as conn:
        q = update(user_table).where(user_table.c.tg_id == tg_id).values(
            correct_count=user_table.c.correct_count + 1,
            karma=user_table.c.karma + 1
        )
        conn.execute(q)
        session.commit()


def user_validated_now(
        tg_id,
):
    with engine.connect() as conn:
        q = update(user_table).where(user_table.c.tg_id == tg_id).values(
            last_validated_at=datetime.now()
        )
        conn.execute(q)
        session.commit()


def get_all_users():
    with engine.connect() as conn:
        q = select(user_table)
        return conn.execute(q).fetchall()


async def edit_profile(tg_id, age=None, lang=None, accent=None):
    with engine.connect() as conn:
        if age is not None:
            q = update(user_table).where(user_table.c.tg_id == tg_id).values(
                year_of_birth=age
            )
        elif lang is not None:
            q = update(user_table).where(user_table.c.tg_id == tg_id).values(
                native_language=lang
            )
        elif accent is not None:
            q = update(user_table).where(user_table.c.tg_id == tg_id).values(
                accent_region=accent
            )
        conn.execute(q)
        session.commit()