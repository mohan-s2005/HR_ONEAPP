from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models import db, User
import random

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['email'] = user.email
            session['role'] = user.role
            
            flash('Welcome back to HR Oneapp!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password credentials.', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            otp_code = str(random.randint(100000, 999999))
            user.otp = otp_code
            db.session.commit()
            
            print(f"\n[DEVELOPER SIMULATOR] Reset OTP token for {email}: {otp_code}\n")
            
            flash('A secure validation token has been updated on your user profile.', 'info')
            return redirect(url_for('auth.reset_password'))
        else:
            flash('No matching registered account found with that email.', 'danger')
            
    return render_template('forgot_password.html')

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        otp_entered = request.form.get('otp')
        new_password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.otp == otp_entered and otp_entered is not None:
            user.set_password(new_password)
            user.otp = None
            db.session.commit()
            flash('Your account credentials have been reset successfully. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid identification verification code or user match.', 'danger')
            
    return render_template('reset_password.html')