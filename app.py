import os
from flask import Flask, g, redirect, url_for, render_template
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO
from config import Config
from models import db, User
import dash
from dash import Dash
import dash_bootstrap_components as dbc

# Initialize extensions
login_manager = LoginManager()
socketio = SocketIO()
dash_app = None  # Will be initialized in create_app


def create_app(config_class=Config):
    # Create and configure the Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize database
    db.init_app(app)

    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Initialize SocketIO for real-time collaboration
    socketio.init_app(app, cors_allowed_origins="*")

    # Register blueprints
    from auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    from editor.routes import editor_bp
    app.register_blueprint(editor_bp)

    from api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Register Draft Generator blueprint
    from modules.draft_generator import draft_generator_bp
    app.register_blueprint(draft_generator_bp)

    # Register Literature Search blueprint with the correct URL prefix
    from modules.literature_search.routes import literature_bp
    app.register_blueprint(literature_bp, url_prefix='/literature')

    # Register Settings module
    from modules.settings import init_settings_module
    init_settings_module(app)

    # REMOVED DUPLICATE INITIALIZATION HERE

    # Root route - redirect to appropriate page
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('editor.dashboard'))
        else:
            return redirect(url_for('auth.login'))

    # Initialize Dash app for literature search
    global dash_app
    dash_app = Dash(
        name='literature_dashboard',  # Added a name to avoid conflicts
        server=app,
        url_base_pathname='/dash/literature/',
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True
    )

    # Import and set the Dash layout
    from modules.literature_search.dash_ui import literature_layout, register_callbacks
    dash_app.layout = literature_layout

    # Register callbacks
    register_callbacks(dash_app)

    # Create a function to inject Dash assets into the Flask template
    @app.context_processor
    def inject_dash_assets():
        return {'dash_url': '/dash/literature/'}

    # User loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app


# Create template directories if they don't exist
def ensure_template_dirs():
    template_dir = os.path.join('templates', 'literature')
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)

    # Create the search.html template if it doesn't exist
    search_template = os.path.join(template_dir, 'search.html')
    if not os.path.exists(search_template):
        with open(search_template, 'w') as f:
            f.write('''{% extends "base.html" %}

{% block title %}Literature Search{% endblock %}

{% block styles %}
<!-- Load Dash CSS assets -->
<link rel="stylesheet" href="{{ dash_url }}assets/dash_bootstrap.css">
{% endblock %}

{% block content %}
<div class="container-fluid mt-4">
    <h1 class="mb-4">Scientific Literature Search</h1>

    <!-- This div will be populated by Dash -->
    <div id="dash-container">
        <iframe 
            src="{{ dash_url }}" 
            frameborder="0" 
            style="width: 100%; height: 800px; border: none;"
            title="Literature Search"
        ></iframe>
    </div>
</div>
{% endblock %}

{% block scripts %}
<!-- Load Dash JS assets -->
<script src="{{ dash_url }}assets/dash_renderer.js"></script>
{% endblock %}''')


# Create settings templates if they don't exist
def ensure_settings_templates():
    template_dir = os.path.join('templates', 'settings')
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)

    settings_template = os.path.join(template_dir, 'settings.html')
    dashboard_template = os.path.join(template_dir, 'dashboard.html')

    # Create settings.html if it doesn't exist
    if not os.path.exists(settings_template):
        with open(settings_template, 'w') as f:
            f.write('''{% extends "base.html" %}

{% block title %}Settings{% endblock %}

{% block content %}
<div class="container-fluid mt-4">
    <div class="row">
        <div class="col-md-3">
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Settings</h5>
                </div>
                <div class="card-body">
                    <ul class="nav flex-column nav-pills">
                        <li class="nav-item">
                            <a class="nav-link active" href="{{ url_for('settings.settings_page') }}">
                                <i class="fa fa-user"></i> Profile
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('settings.settings_dashboard') }}">
                                <i class="fa fa-sliders"></i> Advanced Settings
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('literature.search') }}">
                                <i class="fa fa-search"></i> Literature Search
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('auth.profile') }}">
                                <i class="fa fa-arrow-left"></i> Back to Profile
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col-md-9">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0">User Settings</h4>
                </div>
                <div class="card-body">
                    <div class="alert alert-info">
                        <i class="fa fa-info-circle"></i> For advanced settings including AI providers and scientific databases, please visit the <a href="{{ url_for('settings.settings_dashboard') }}" class="alert-link">Advanced Settings Dashboard</a>.
                    </div>

                    <h5 class="mb-3">Profile Settings</h5>
                    <form id="profile-form" method="post" action="{{ url_for('settings.update_profile') }}">
                        <div class="mb-3">
                            <label for="name" class="form-label">Full Name</label>
                            <input type="text" class="form-control" id="name" name="name" value="{{ current_user.full_name }}">
                        </div>
                        <div class="mb-3">
                            <label for="email" class="form-label">Email Address</label>
                            <input type="email" class="form-control" id="email" name="email" value="{{ current_user.email }}">
                        </div>
                        <button type="submit" class="btn btn-primary">Update Profile</button>
                    </form>

                    <hr class="my-4">

                    <h5 class="mb-3">Change Password</h5>
                    <form id="password-form" method="post" action="{{ url_for('settings.change_password') }}">
                        <div class="mb-3">
                            <label for="current-password" class="form-label">Current Password</label>
                            <input type="password" class="form-control" id="current-password" name="current_password">
                        </div>
                        <div class="mb-3">
                            <label for="new-password" class="form-label">New Password</label>
                            <input type="password" class="form-control" id="new-password" name="new_password">
                        </div>
                        <div class="mb-3">
                            <label for="confirm-password" class="form-label">Confirm New Password</label>
                            <input type="password" class="form-control" id="confirm-password" name="confirm_password">
                        </div>
                        <button type="submit" class="btn btn-primary">Change Password</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
{{ super() }}
<script>
    // Add your settings page JavaScript here
</script>
{% endblock %}''')

    # Create dashboard.html if it doesn't exist
    if not os.path.exists(dashboard_template):
        with open(dashboard_template, 'w') as f:
            f.write('''{% extends "base.html" %}

{% block title %}Settings Dashboard{% endblock %}

{% block styles %}
{{ super() }}
<!-- Load Dash CSS assets -->
<link rel="stylesheet" href="{{ url_for('settings.settings_dashboard') }}/assets/dash_bootstrap.css">
<style>
    .settings-container iframe {
        width: 100%;
        height: 800px;
        border: none;
    }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid mt-4">
    <div class="row">
        <div class="col-md-3">
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Settings</h5>
                </div>
                <div class="card-body">
                    <ul class="nav flex-column nav-pills">
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('settings.settings_page') }}">
                                <i class="fa fa-user"></i> Profile
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link active" href="{{ url_for('settings.settings_dashboard') }}">
                                <i class="fa fa-sliders"></i> Advanced Settings
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('literature.search') }}">
                                <i class="fa fa-search"></i> Literature Search
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('auth.profile') }}">
                                <i class="fa fa-arrow-left"></i> Back to Profile
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="col-md-9">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0">Advanced Settings Dashboard</h4>
                </div>
                <div class="card-body p-0">
                    <!-- This div will be populated by Dash -->
                    <div class="settings-container">
                        <iframe 
                            src="{{ url_for('settings.settings_dashboard') }}/" 
                            frameborder="0" 
                            title="Settings Dashboard"
                        ></iframe>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
{{ super() }}
<!-- Load Dash JS assets -->
<script src="{{ url_for('settings.settings_dashboard') }}/assets/dash_renderer.js"></script>
{% endblock %}''')


if __name__ == '__main__':
    ensure_template_dirs()
    ensure_settings_templates()  # Add this to create settings templates
    app = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)), allow_unsafe_werkzeug=True)
