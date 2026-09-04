from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """作为项目内所有 SQLAlchemy ORM 映射类的基类。"""
