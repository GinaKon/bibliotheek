from flask import Flask, request, session, jsonify
from models import db, Users, Books, Borrowed_Books
from config import Config
from flask_bcrypt import Bcrypt
from utils import create_uuid, require_auth
import re
from functools import wraps
import secrets
from datetime import datetime
import os


admin_api_key = secrets.token_hex(32)
# print(admin_api_key)


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
bcrypt = Bcrypt(app)


with app.app_context():
    db.create_all()


def require_admin_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401

        token = auth_header.split(' ')[1]
        if token != admin_api_key:
            return jsonify({'error': 'Unauthorized'}), 401

        return f(*args, **kwargs)

    return decorated_function


def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#\$%\^&\*]', password):
        return False
    return True


@app.route('/register', methods=["POST"])
def add_user():
    try:
        email = request.json['email']
        password = request.json['password']

        is_user_existent = Users.query.filter_by(email=email).first() is not None

        if is_user_existent:
            return jsonify({'error': 'User already registered'}), 418

        encrypted_password = bcrypt.generate_password_hash(password)
        new_user = Users(id=create_uuid(),
                         email=email,
                         password=encrypted_password)
        db.session.add(new_user)
        db.session.commit()

        session["user_id"] = new_user.id

        return jsonify({
              'id': new_user.id,
              'email': new_user.email
            }), 201
    except KeyError:
        return jsonify({'error': 'Invalid request'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/login', methods=["POST"])
def user_login():
    try:
        email = request.json['email']
        password = request.json['password']

        user = Users.query.filter_by(email=email).first()

        if user is None:
            return jsonify({'error': 'Unauthorized'}), 401

        if not bcrypt.check_password_hash(user.password, password):
            return jsonify({'error': 'Unauthorized'}), 401

        session['user_id'] = user.id
        # print(session.get('user_id'))

        return jsonify({
            'id': user.id,
            'email': user.email
        }), 200
    except KeyError:
        return jsonify({'error': 'Invalid request'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/@current_user', methods=["GET"])
@require_auth
def get_current_user():
    try:
        user_authenticated_id = session.get('user_id')

        user = Users.query.filter_by(id=user_authenticated_id).first()
        return jsonify({
            'id': user.id,
            'email': user.email
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/books', methods=['POST'])
@require_admin_auth
def create_books():
    try:
        books_data = request.json.get('books', [])
        created_books = []

        for book in books_data:
            title = book.get('title')
            author = book.get('author')
            edition = book.get('edition')
            publisher = book.get('publisher')
            isbn = book.get('isbn')
            genre = book.get('genre')
            page_count = book.get('page_count')
            language = book.get('language')
            publication_year = book.get('publication_year')

            if not (title and author and isbn):
                return jsonify({'error': 'Invalid or incomplete book data'}), 400

            if Books.query.filter_by(isbn=isbn).first():
                return jsonify({'error': f"Book with ISBN {isbn} already exists."}), 400

            new_book = Books(
                id=create_uuid(),
                title=title,
                author=author,
                edition=edition,
                publisher=publisher,
                isbn=isbn,
                genre=genre,
                page_count=page_count,
                language=language,
                publication_year=publication_year,
                added_at=datetime.utcnow()
            )
            db.session.add(new_book)
            created_books.append({
                'isbn': new_book.isbn,
                'added_at': new_book.added_at
            })

        db.session.commit()
        return jsonify(created_books), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/books', methods=['GET'])
@require_auth
def list_books():
    try:
        page = request.args.get('page', 0, type=int)
        per_page = 10

        books_query = Books.query.order_by(Books.isbn.desc()).paginate(page, per_page, False)
        books = books_query.items

        books_list = [{
            'title': book.title,
            'author': book.author,
            'edition': book.edition,
            'publisher': book.publisher,
            'isbn': book.isbn,
            'genre': book.genre,
            'page_count': book.page_count,
            'language': book.language,
            'publication_year': book.publication_year,
            'added_at': book.added_at,
            'updated_at': book.updated_at
        } for book in books]

        return jsonify({
            'total_pages': books_query.pages,
            'page': page,
            'books': books_list
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/books/<isbn>', methods=['PUT'])
@require_admin_auth
def update_book(isbn):
    try:
        book_data = request.json
        book = Books.query.filter_by(isbn=isbn).first()

        if not book:
            return jsonify({'error': 'Book not found'}), 400

        book.title = book_data.get('title', book.title)
        book.author = book_data.get('author', book.author)
        book.edition = book_data.get('edition', book.edition)
        book.publisher = book_data.get('publisher', book.publisher)
        book.genre = book_data.get('genre', book.genre)
        book.page_count = book_data.get('page_count', book.page_count)
        book.language = book_data.get('language', book.language)
        book.publication_year = book_data.get('publication_year', book.publication_year)
        book.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'isbn': book.isbn,
            'updated_at': book.updated_at
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/books/<isbn>', methods=['DELETE'])
@require_admin_auth
def delete_book(isbn):
    try:
        book = Books.query.filter_by(isbn=isbn).first()

        if not book:
            return jsonify({'error': 'Book not found'}), 400

        db.session.delete(book)
        db.session.commit()

        return '', 204

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/borrow', methods=["POST"])
def borrow_book():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session['user_id']
    isbn = request.json.get("isbn")

    if not isbn:
        return jsonify({"error": "ISBN is required"}), 400

    book = Books.query.filter_by(isbn=isbn).first()
    if not book:
        return jsonify({"error": "Book not found"}), 400

    borrowed_book = Borrowed_Books.query.filter_by(isbn=isbn, returned_at=None).first()
    if borrowed_book:
        return jsonify({"error": "Book is already borrowed"}), 400

    borrowed_count = Borrowed_Books.query.filter_by(user_id=user_id, returned_at=None).count()
    if borrowed_count >= 2:
        return jsonify({"error": "You cannot borrow more than 2 books at a time"}), 400

    borrowed_entry = Borrowed_Books(
        user_id=user_id,
        isbn=isbn,
        borrowed_at=datetime.utcnow(),
        returned_at=None
    )
    db.session.add(borrowed_entry)
    db.session.commit()

    return jsonify({
        "isbn": isbn,
        "borrowed_at": borrowed_entry.borrowed_at.isoformat()
    }), 200


@app.route('/return/<isbn>', methods=["DELETE"])
def return_book(isbn):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session['user_id']

    borrowed_entry = Borrowed_Books.query.filter_by(isbn=isbn, user_id=user_id, returned_at=None).first()
    if not borrowed_entry:
        return jsonify({"error": "This book was not borrowed by you"}), 400

    borrowed_entry.returned_at = datetime.utcnow()
    db.session.commit()

    return '', 204


@app.route('/borrowed', methods=["GET"])
def list_borrowed_books():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session['user_id']
    borrowed_books = Borrowed_Books.query.filter_by(user_id=user_id).all()

    response_books = []
    for entry in borrowed_books:
        response_books.append({
            "isbn": entry.isbn,
            "borrowed_at": entry.borrowed_at.isoformat(),
            "returned_at": entry.returned_at.isoformat() if entry.returned_at else None
        })

    return jsonify({"books": response_books}), 200


if __name__ == '__main__':
    port = int(os.environ.get('API_LISTENING_PORT', 8080)) 
    app.run(debug=True, host='0.0.0.0', port=port) 