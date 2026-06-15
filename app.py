import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit
from models import db, User, Announcement, ChatMessage

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Qwertyu-fer'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conference.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connect our models architecture
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Register Blueprints from our routes package to fix the routing BuildError
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.user import user_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

# State tracking definitions
meeting_state = {
    'active': False,
    'mic_enabled': True,
    'cam_enabled': True
}

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the system platform.', 'warning')
        return redirect(url_for('auth.login'))
        
    users_list = User.query.all()
    announcements_list = Announcement.query.order_by(Announcement.id.desc()).all()
    chat_history_list = ChatMessage.query.order_by(ChatMessage.id.asc()).all()
    
    return render_template(
        'dashboard.html',
        users=users_list,
        announcements=announcements_list,
        chat_history=chat_history_list,
        meeting_state=meeting_state
    )

# --- WebSocket Infrastructure Hooks ---

@socketio.on('send_global_msg')
def handle_global_message(data):
    user_email = session.get('email', 'Anonymous Employee')
    message_text = data.get('message', '').strip()
    if message_text:
        new_msg = ChatMessage(email=user_email, message=message_text)
        db.session.add(new_msg)
        db.session.commit()
        emit('receive_global_msg', {'email': user_email, 'message': message_text}, broadcast=True)

@socketio.on('toggle_meeting')
def handle_meeting_toggle(data):
    if session.get('role') == 'admin':
        meeting_state['active'] = data.get('status', False)
        emit('meeting_status_changed', {'active': meeting_state['active']}, broadcast=True)

@socketio.on('permission_control')
def handle_permission_control(data):
    if session.get('role') == 'admin':
        perm_type = data.get('type')
        is_enabled = data.get('enabled', True)
        if perm_type == 'mic':
            meeting_state['mic_enabled'] = is_enabled
        elif perm_type == 'cam':
            meeting_state['cam_enabled'] = is_enabled
        emit('permission_updated', {'type': perm_type, 'enabled': is_enabled}, broadcast=True)

# Cold Start Hooks
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Enforce administrative default record seeding
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(email='admin@company.org', role='admin', otp='000000')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("\n[DB SUCCESS] Admin seeded: admin@company.org / admin123\n")

    socketio.run(app, debug=True, port=5000)