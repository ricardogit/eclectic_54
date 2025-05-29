from flask import Blueprint
import dash
from dash import Dash
import dash_bootstrap_components as dbc
from flask_login import login_required

# Import the blueprint and UI components
from .routes import settings_bp  # Import settings_bp from routes
from .dash_ui import create_settings_layout, register_settings_callbacks

# Create the settings dashboard
settings_dash_app = None


def init_settings_module(app, server=None):
    """
    Initialize the settings module with Flask and Dash applications

    Args:
        app: The Flask app
        server: The Flask server (optional, defaults to app)
    """
    # Initialize the Dash app for settings
    global settings_dash_app

    if not server:
        server = app

    # Create the Dash app with the correct path
    settings_dash_app = Dash(
        name='settings_dashboard',  # Use name as keyword argument
        server=server,
        url_base_pathname='/settings/dashboard/',
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True
    )

    # Set the layout as a function - this is the key fix
    # It ensures the layout is created dynamically for each request
    settings_dash_app.layout = create_settings_layout()

    # Register callbacks
    register_callbacks(settings_dash_app)

    # IMPORTANT: REMOVE the route definition from here
    # The route should only be defined in routes.py, not both places

    # Register the blueprint with the app
    app.register_blueprint(settings_bp)

    return settings_bp


def register_callbacks(app):
    """
    Wrapper function to register callbacks safely

    Args:
        app: The Dash app
    """
    # Import within the function to avoid circular imports
    from .dash_ui import register_settings_callbacks

    # Register the callbacks
    register_settings_callbacks(app)
