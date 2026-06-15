from flask import Blueprint, request, redirect, url_for, flash, session
from models import db, User, Announcement

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    def wrap(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Access denied. Administrators only.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@admin_bp.route('/user/create', methods=['POST'])
@admin_required
def create_user():
    email = request.form.get('email')
    password = request.form.get('password')
    
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('An employee profile with that email already exists.', 'warning')
        return redirect(url_for('dashboard'))
    
    new_user = User(email=email, role='user')
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    flash(f'Successfully created employee profile for {email}.', 'success')
    return redirect(url_for('dashboard'))

@admin_bp.route('/user/delete/<int:id>')
@admin_required
def delete_user(id):
    user_to_delete = User.query.get_or_404(id)
    
    if user_to_delete.role == 'admin':
        flash('Administrative profiles cannot be removed.', 'danger')
        return redirect(url_for('dashboard'))
        
    db.session.delete(user_to_delete)
    db.session.commit()
    
    flash('Employee profile removed successfully.', 'info')
    return redirect(url_for('dashboard'))

@admin_bp.route('/announcement/create', methods=['POST'])
@admin_required
def create_announcement():
    title = request.form.get('title')
    content = request.form.get('content')
    
    new_announcement = Announcement(title=title, content=content)
    db.session.add(new_announcement)
    db.session.commit()
    
    flash('New board announcement broadcasted successfully.', 'success')
    return redirect(url_for('dashboard'))