from uuid import uuid4
from functools import wraps
from flask import session, jsonify


def create_uuid():
    return uuid4().hex


def require_auth(view_func):
    @wraps(view_func)
    def decorated_func(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401

        return view_func(*args, **kwargs)

    return decorated_func
