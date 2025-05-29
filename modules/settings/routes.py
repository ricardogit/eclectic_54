from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User, AIProvider, ScientificDatabase

# Create the blueprint
settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/')
@login_required
def settings_page():
    """Render the settings page."""
    return render_template('settings/settings.html', title="User Settings")

@settings_bp.route('/dashboard')
@login_required
def settings_dashboard():
    """Render the settings dashboard."""
    return render_template('settings/dashboard.html', title="Settings Dashboard")

# Test the URLs to ensure they're working
# You can add this to a debug route or run in a Flask shell:
# print(url_for('settings.settings_page'))  # Should print '/settings/'
# print(url_for('settings.settings_dashboard'))  # Should print '/settings/dashboard'

@settings_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Handle profile update form submission."""
    data = request.json

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    try:
        user = User.query.get(current_user.id)

        # Update user data
        if 'name' in data:
            user.full_name = data['name']

        # Email updates typically require verification
        # This is a simplified example
        if 'email' in data and data['email'] != user.email:
            # Check if email already exists
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'success': False, 'message': 'Email already in use'}), 409

            user.email = data['email']

        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully'})

    except Exception as e:
        current_app.logger.error(f"Error updating profile: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@settings_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Handle password change form submission."""
    data = request.json

    if not data or 'current_password' not in data or 'new_password' not in data:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        user = User.query.get(current_user.id)

        # Verify current password
        if not check_password_hash(user.password_hash, data['current_password']):
            return jsonify({'success': False, 'message': 'Current password is incorrect'}), 401

        # Check if new password meets requirements
        if len(data['new_password']) < 8:
            return jsonify({'success': False, 'message': 'Password must be at least 8 characters long'}), 400

        # Update password
        user.password_hash = generate_password_hash(data['new_password'])
        db.session.commit()

        return jsonify({'success': True, 'message': 'Password changed successfully'})

    except Exception as e:
        current_app.logger.error(f"Error changing password: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@settings_bp.route('/update-preferences', methods=['POST'])
@login_required
def update_preferences():
    """Handle user preferences update."""
    data = request.json

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    try:
        user = User.query.get(current_user.id)

        # Assuming user has a preferences JSON column or related table
        # This is a simplified example
        preferences = user.preferences if hasattr(user, 'preferences') else {}

        # Update preferences
        if 'theme' in data:
            preferences['theme'] = data['theme']

        if 'editor_preferences' in data:
            preferences['editor_preferences'] = data['editor_preferences']

        if 'citation_style' in data:
            preferences['citation_style'] = data['citation_style']

        # Save preferences
        user.preferences = preferences
        db.session.commit()

        return jsonify({'success': True, 'message': 'Preferences updated successfully'})

    except Exception as e:
        current_app.logger.error(f"Error updating preferences: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@settings_bp.route('/api-keys', methods=['GET'])
@login_required
def get_api_keys():
    """Get all API keys for the current user."""
    try:
        providers = AIProvider.query.filter_by(user_id=current_user.id).all()

        results = []
        for provider in providers:
            # Mask API key
            masked_key = f"{'*' * 20}{provider.api_key[-5:]}" if provider.api_key else ""

            results.append({
                'id': provider.id,
                'provider': provider.provider,
                'api_key': masked_key,
                'is_paid': provider.is_paid,
                'updated_at': provider.updated_at.strftime('%Y-%m-%d %H:%M:%S') if provider.updated_at else None
            })

        return jsonify(results)

    except Exception as e:
        current_app.logger.error(f"Error fetching API keys: {e}")
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/api-keys/<int:provider_id>', methods=['DELETE'])
@login_required
def delete_api_key(provider_id):
    """Delete an API key."""
    try:
        provider = AIProvider.query.get(provider_id)

        if not provider or provider.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'API key not found'}), 404

        db.session.delete(provider)
        db.session.commit()

        return jsonify({'success': True, 'message': 'API key deleted successfully'})

    except Exception as e:
        current_app.logger.error(f"Error deleting API key: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@settings_bp.route('/scientific-databases', methods=['GET'])
@login_required
def get_scientific_databases():
    """Get all scientific database configurations for the current user."""
    try:
        databases = ScientificDatabase.query.filter_by(user_id=current_user.id).all()

        results = []
        for db_config in databases:
            # Mask API key
            masked_key = f"{'*' * 20}{db_config.api_key[-5:]}" if db_config.api_key else ""

            results.append({
                'id': db_config.id,
                'database_name': db_config.database_name,
                'api_key': masked_key,
                'is_institutional': db_config.is_institutional,
                'institution': db_config.institution,
                'updated_at': db_config.updated_at.strftime('%Y-%m-%d %H:%M:%S') if db_config.updated_at else None
            })

        return jsonify(results)

    except Exception as e:
        current_app.logger.error(f"Error fetching scientific databases: {e}")
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/scientific-databases/<int:database_id>', methods=['DELETE'])
@login_required
def delete_scientific_database(database_id):
    """Delete a scientific database configuration."""
    try:
        db_config = ScientificDatabase.query.get(database_id)

        if not db_config or db_config.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Database configuration not found'}), 404

        db.session.delete(db_config)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Database configuration deleted successfully'})

    except Exception as e:
        current_app.logger.error(f"Error deleting database configuration: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
