from flask import Flask, request, jsonify, g, session
from flask_migrate import Migrate
from flask_cors import CORS
from functools import wraps
import datetime
import os

from config import config
from models import db, bcrypt, User, JournalEntry


app = Flask(__name__)
app.config.from_object(config[os.environ.get('FLASK_ENV', 'default')])


db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)


CORS(app, supports_credentials=True, origins=['http://localhost:3000'])

def login_required(f):
   
    @wraps(f)
    def decorated(*args, **kwargs):
       
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required. Please log in.'}), 401
        
       
        current_user = User.query.get(session['user_id'])
        if not current_user:
            session.clear()  
            return jsonify({'message': 'User not found. Please log in again.'}), 401
        
        g.current_user = current_user
        return f(*args, **kwargs)
    return decorated


@app.route('/api/auth/register', methods=['POST'])
def register():
   
    data = request.get_json()
    
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Username, email, and password are required'}), 400
    
    if not User.validate_email(data['email']):
        return jsonify({'message': 'Invalid email format'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 409
    
    try:
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
   
    data = request.get_json()
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password are required'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    
    session.permanent = True
    session['user_id'] = user.id
    session['username'] = user.username
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    
    return jsonify({'user': g.current_user.to_dict()}), 200


@app.route('/api/journal-entries', methods=['GET'])
@login_required
def get_journal_entries():
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if page < 1:
        return jsonify({'message': 'Page must be at least 1'}), 400
    if per_page < 1 or per_page > 100:
        return jsonify({'message': 'Per page must be between 1 and 100'}), 400
    
    paginated_entries = JournalEntry.query.filter_by(user_id=g.current_user.id)\
        .order_by(JournalEntry.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'data': [entry.to_dict() for entry in paginated_entries.items],
        'pagination': {
            'page': paginated_entries.page,
            'per_page': paginated_entries.per_page,
            'total_pages': paginated_entries.pages,
            'total_items': paginated_entries.total,
            'has_next': paginated_entries.has_next,
            'has_prev': paginated_entries.has_prev
        }
    }), 200

@app.route('/api/journal-entries', methods=['POST'])
@login_required
def create_journal_entry():
    
    data = request.get_json()
    
    if not data.get('title'):
        return jsonify({'message': 'Title is required'}), 400
    if not data.get('content'):
        return jsonify({'message': 'Content is required'}), 400
    
    try:
        entry = JournalEntry(
            title=data['title'],
            content=data['content'],
            mood=data.get('mood'),
            user_id=g.current_user.id
        )
        db.session.add(entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Journal entry created successfully',
            'data': entry.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create journal entry'}), 500

@app.route('/api/journal-entries/<int:entry_id>', methods=['GET'])
@login_required
def get_journal_entry(entry_id):
    
    entry = JournalEntry.query.get(entry_id)
    
    if not entry:
        return jsonify({'message': 'Journal entry not found'}), 404
    
    if entry.user_id != g.current_user.id:
        return jsonify({'message': 'Access denied'}), 403
    
    return jsonify({'data': entry.to_dict()}), 200

@app.route('/api/journal-entries/<int:entry_id>', methods=['PATCH'])
@login_required
def update_journal_entry(entry_id):
    """Update a specific journal entry"""
    entry = JournalEntry.query.get(entry_id)
    
    if not entry:
        return jsonify({'message': 'Journal entry not found'}), 404
    
    if entry.user_id != g.current_user.id:
        return jsonify({'message': 'Access denied'}), 403
    
    data = request.get_json()
    
    try:
        entry.update_from_dict(data)
        db.session.commit()
        
        return jsonify({
            'message': 'Journal entry updated successfully',
            'data': entry.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update journal entry'}), 500

@app.route('/api/journal-entries/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_journal_entry(entry_id):
    
    entry = JournalEntry.query.get(entry_id)
    
    if not entry:
        return jsonify({'message': 'Journal entry not found'}), 404
    
    if entry.user_id != g.current_user.id:
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        db.session.delete(entry)
        db.session.commit()
        
        return jsonify({'message': 'Journal entry deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete journal entry'}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)