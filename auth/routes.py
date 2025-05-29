import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('editor.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Please check your login details and try again.', 'error')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        next_page = request.args.get('next')

        if not next_page or next_page.startswith('/'):
            next_page = url_for('editor.dashboard')

        return redirect(next_page)

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('editor.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password = request.form.get('password')

        # Check if email already exists
        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email address already exists', 'error')
            return redirect(url_for('auth.register'))

        # Create new user
        new_user = User(
            email=email,
            full_name=full_name,
            a_password=generate_password_hash(password),
            created_date=datetime.datetime.utcnow()
        )

        db.session.add(new_user)
        db.session.commit()

        # Log in the new user
        login_user(new_user)

        return redirect(url_for('editor.dashboard'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name')

        if full_name:
            current_user.full_name = full_name
            db.session.commit()
            flash('Profile updated successfully', 'success')

        # Password change
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if current_password and new_password and confirm_password:
            if not current_user.check_password(current_password):
                flash('Current password is incorrect', 'error')
            elif new_password != confirm_password:
                flash('New passwords do not match', 'error')
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash('Password updated successfully', 'success')

        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')
