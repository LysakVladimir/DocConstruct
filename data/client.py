import datetime
import sqlalchemy

from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Client(SqlAlchemyBase):
    __tablename__ = "clients"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    patronymic = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    birth_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship("User")

    def __repr__(self):
        return f"{self.surname} {self.name} {self.patronymic}"
