from flask import Blueprint, jsonify, request
from models import User, db
from werkzeug.security import generate_password_hash

register_bp = Blueprint('register', __name__)

@register_bp.route('/create', methods=['POST'])
def register_user():
    try:
        user = request.get_json()
        username = user.get('username')
        password = user.get('password')
        email = user.get('email')

        if not username or not password or not email:
            return jsonify({'message': 'All fields must be filled.', 'success': False}), 400
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'message': 'Registration Failed.', 'success': False}), 409
        
        hashed_password = generate_password_hash(password)

        new_user = User(username=username, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User Registered Successfully!', 'success': True}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred.', 'success': False}), 500