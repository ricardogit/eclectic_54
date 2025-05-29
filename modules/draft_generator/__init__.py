# modules/draft_generator/__init__.py
# Blueprint initialization for the Academic Draft Generator

# from flask import Blueprint
#
# # Importing routes will also create the blueprint
# from modules.draft_generator.routes import draft_generator_bp, register_dash
#
# def init_app(app):
#     """
#     Initialize the draft generator module with the Flask app.
#     This function is called from the main app.py file.
#     """
#     # Register blueprint
#     app.register_blueprint(draft_generator_bp)
#
#     # Register Dash app
#     register_dash(app)
#
#     return app

# modules/draft_generator/__init__.py
# Blueprint initialization for the Draft Generator module

from flask import Blueprint

# Create blueprint
draft_generator_bp = Blueprint(
    'draft_generator',
    __name__,
    url_prefix='/draft-generator',
    template_folder='templates',
    static_folder='static',
    static_url_path='/draft-generator/static'
)

# Import routes to register them with the blueprint
from modules.draft_generator import routes