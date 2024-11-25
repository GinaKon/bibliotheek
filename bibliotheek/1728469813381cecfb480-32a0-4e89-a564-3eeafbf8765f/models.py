from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(255), primary_key=True, unique=True)
    username = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))
    roled = db.Column(db.String(255))
    created_at = db.Column(db.String(255))

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "roled": self.roled,
            "created_at": self.created_at
        }


class Books(db.Model):
    __tablename__ = "books"
    id = db.Column(db.String(255), primary_key=True, unique=True)
    title = db.Column(db.String(255))
    author = db.Column(db.String(255))
    publication_date = db.Column(db.String(255))
    genre = db.Column(db.String(255))
    available = db.Column(db.String(255))


    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "publication_date": self.publication_date,
            "genre": self.genre,
            "available": self.available
        }


class Borrowed_Books(db.Model):
    __tablename__ = "borrowedbooks"
    id = db.Column(db.String(255), primary_key=True, unique=True)
    user_id = db.Column(db.String(255))
    book_id = db.Column(db.String(255))
    borrowed_at = db.Column(db.String(255))
    returned_at = db.Column(db.String(255))

    def serialize(self):
        return {

            'id': self.id,
            'user_id': self.user_id,
            "book_id" : self.book_id,
            "borrowed_at": self.borrowed_at,
            "returned_at": self.returned_at
        }
