from flask import Blueprint, jsonify, request, make_response
from auth.utils import token_required

logout_bp = Blueprint('logout', __name__)

@logout_bp.route('/', methods=['POST'])
@token_required
def logout(current_user):
    try:
        response = make_response(jsonify({'message': 'Logout Success', 'success': True}))
        response.delete_cookie('token', httponly=True, secure=True, samesite='Lax')
        
        return response, 200
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({'message': 'An error occurred.', 'success': False}), 500