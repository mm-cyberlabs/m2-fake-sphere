"""
Authentication Routes

Simple authentication endpoints for the WebUI.
In a production environment, this would integrate with proper authentication systems.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import jwt
import uuid

auth_bp = Blueprint('auth', __name__)

# Simple user store (in production, this would be a proper user database)
USERS = {
    'admin': {
        'id': 'user_001',
        'username': 'admin',
        'password': 'admin123',  # In production, this would be hashed
        'role': 'administrator',
        'permissions': ['read', 'write', 'admin']
    },
    'operator': {
        'id': 'user_002',
        'username': 'operator',
        'password': 'op123',
        'role': 'operator',
        'permissions': ['read', 'write']
    },
    'viewer': {
        'id': 'user_003',
        'username': 'viewer',
        'password': 'view123',
        'role': 'viewer',
        'permissions': ['read']
    }
}

# Secret key for JWT (in production, this should be in environment variables)
JWT_SECRET = 'fake-sphere-jwt-secret-dev'

# Active sessions
ACTIVE_SESSIONS = {}


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No credentials provided'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    # Validate credentials
    user = USERS.get(username)
    if not user or user['password'] != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate JWT token
    payload = {
        'user_id': user['id'],
        'username': user['username'],
        'role': user['role'],
        'permissions': user['permissions'],
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=8)  # Token expires in 8 hours
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    
    # Store session
    session_id = str(uuid.uuid4())
    ACTIVE_SESSIONS[session_id] = {
        'user_id': user['id'],
        'username': user['username'],
        'created_at': datetime.utcnow().isoformat(),
        'last_activity': datetime.utcnow().isoformat(),
        'token': token
    }
    
    return jsonify({
        'success': True,
        'token': token,
        'session_id': session_id,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'permissions': user['permissions']
        },
        'expires_at': (datetime.utcnow() + timedelta(hours=8)).isoformat()
    })


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user and invalidate session."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    
    # Find and remove session
    session_to_remove = None
    for session_id, session_data in ACTIVE_SESSIONS.items():
        if session_data['token'] == token:
            session_to_remove = session_id
            break
    
    if session_to_remove:
        del ACTIVE_SESSIONS[session_to_remove]
    
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })


@auth_bp.route('/verify', methods=['GET'])
def verify_token():
    """Verify JWT token and return user info."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        
        # Update last activity
        for session_data in ACTIVE_SESSIONS.values():
            if session_data['token'] == token:
                session_data['last_activity'] = datetime.utcnow().isoformat()
                break
        
        return jsonify({
            'valid': True,
            'user': {
                'id': payload['user_id'],
                'username': payload['username'],
                'role': payload['role'],
                'permissions': payload['permissions']
            },
            'expires_at': datetime.fromtimestamp(payload['exp']).isoformat()
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh JWT token."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    old_token = auth_header.split(' ')[1]
    
    try:
        # Decode without verification to get user info (even if expired)
        payload = jwt.decode(old_token, JWT_SECRET, algorithms=['HS256'], options={"verify_exp": False})
        
        # Generate new token
        new_payload = {
            'user_id': payload['user_id'],
            'username': payload['username'],
            'role': payload['role'],
            'permissions': payload['permissions'],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=8)
        }
        
        new_token = jwt.encode(new_payload, JWT_SECRET, algorithm='HS256')
        
        # Update session
        for session_data in ACTIVE_SESSIONS.values():
            if session_data['token'] == old_token:
                session_data['token'] = new_token
                session_data['last_activity'] = datetime.utcnow().isoformat()
                break
        
        return jsonify({
            'success': True,
            'token': new_token,
            'expires_at': (datetime.utcnow() + timedelta(hours=8)).isoformat()
        })
        
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401


@auth_bp.route('/sessions', methods=['GET'])
def get_active_sessions():
    """Get active sessions (admin only)."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        
        # Check if user has admin permissions
        if 'admin' not in payload.get('permissions', []):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Return sanitized session data
        sessions = []
        for session_id, session_data in ACTIVE_SESSIONS.items():
            sessions.append({
                'session_id': session_id,
                'username': session_data['username'],
                'created_at': session_data['created_at'],
                'last_activity': session_data['last_activity']
            })
        
        return jsonify({
            'sessions': sessions,
            'total_active': len(sessions)
        })
        
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401


@auth_bp.route('/sessions/<session_id>', methods=['DELETE'])
def terminate_session(session_id):
    """Terminate a specific session (admin only)."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        
        # Check if user has admin permissions
        if 'admin' not in payload.get('permissions', []):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        if session_id not in ACTIVE_SESSIONS:
            return jsonify({'error': 'Session not found'}), 404
        
        del ACTIVE_SESSIONS[session_id]
        
        return jsonify({
            'success': True,
            'message': f'Session {session_id} terminated'
        })
        
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401


@auth_bp.route('/users', methods=['GET'])
def get_users():
    """Get list of users (admin only)."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        
        # Check if user has admin permissions
        if 'admin' not in payload.get('permissions', []):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Return sanitized user data
        users = []
        for user_data in USERS.values():
            users.append({
                'id': user_data['id'],
                'username': user_data['username'],
                'role': user_data['role'],
                'permissions': user_data['permissions']
            })
        
        return jsonify({
            'users': users,
            'total': len(users)
        })
        
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401


@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get current user profile."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        
        return jsonify({
            'user': {
                'id': payload['user_id'],
                'username': payload['username'],
                'role': payload['role'],
                'permissions': payload['permissions']
            },
            'session_info': {
                'issued_at': datetime.fromtimestamp(payload['iat']).isoformat(),
                'expires_at': datetime.fromtimestamp(payload['exp']).isoformat()
            }
        })
        
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401