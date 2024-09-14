from flask import Flask, Blueprint
from models import  db

database_bp = Blueprint('database', __name__)


@database_bp.route('/create', methods=['POST'])
def create_database():
    db.create_all()
    return 'Database created'