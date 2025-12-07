import sqlalchemy as sq
from sqlalchemy.orm import  declarative_base, relationship

Base = declarative_base()

class Users(Base):
    __tablename__ = "users"

    id = sq.Column(sq.Integer, primary_key=True)
    login = sq.Column(sq.String(length=40), unique=True)

    def __str__(self):
        return f'User {self.id}: {self.login}'

class Words(Base):
    __tablename__ = "words"

    id = sq.Column(sq.Integer, primary_key=True)
    word = sq.Column(sq.String(length=40))
    user_id = sq.Column(sq.Integer, sq.ForeignKey("users.id"), nullable=False)

    users = relationship(Users, backref="words")

    def __str__(self):
        return f'Words {self.id}: {self.word}, {self.user_id}'

class Translations(Base):
    __tablename__ = "translations"

    id = sq.Column(sq.Integer, primary_key=True)
    trans = sq.Column(sq.String(length=40))
    word_id = sq.Column(sq.Integer, sq.ForeignKey("words.id"), nullable=False)

    words = relationship(Words, backref="translations")

    def __str__(self):
        return f'Translations {self.id}: {self.trans}, {self.word_id}'

class UserInfo(Base):
    __tablename__ = "user_info"

    id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=40) ,nullable=False)
    last_name = sq.Column(sq.String(length=40) ,nullable=False)
    telegram_id = sq.Column(sq.Integer, unique=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("users.id"), nullable=False)
    chat_id = sq.Column(sq.Integer, unique=True)
    user_step = sq.Column(sq.String(length=40))

    users = relationship(Users, backref="user_info")

    def __str__(self):
        return f'User Info {self.id}: {self.first_name} {self.last_name},{self.telegram_id}, {self.user_id}, {self.chat_id}, {self.user_step}'


def create_tables(engine):
    #Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

