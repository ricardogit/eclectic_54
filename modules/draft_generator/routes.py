# # modules/draft_generator/routes.py
# # Routes for the Academic Draft Generator
#
# from flask import render_template, jsonify, request, Blueprint
# from flask_login import login_required, current_user
# from dash import Dash
# import dash_bootstrap_components as dbc
#
# from modules.draft_generator.layout import create_draft_generator_layout
# from modules.draft_generator.callbacks import register_draft_generator_callbacks
# from modules.draft_generator.utils import get_user_ai_providers, fetch_arxiv_papers, call_ai_api, generate_prompt
#
# # Create blueprint
# draft_generator_bp = Blueprint('draft_generator', __name__,
#                               url_prefix='/draft-generator',
#                               template_folder='templates',
#                               static_folder='static')
#
# # Create Dash app instance (will be initialized when register_dash is called)
# dash_app = None
#
# @draft_generator_bp.route('/')
# @login_required
# def index():
#     """Main page for the draft generator."""
#     return render_template('draft_generator/index.html')
#
# # API endpoints for the JavaScript version
# @draft_generator_bp.route('/api/providers')
# @login_required
# def get_providers():
#     """API endpoint to get AI providers."""
#     user_id = current_user.id
#     providers = get_user_ai_providers(user_id)
#
#     return jsonify({
#         'providers': [{'name': name, 'paid': config.get('is_paid', False)}
#                      for name, config in providers.items()]
#     })
#
# @draft_generator_bp.route('/api/models')
# @login_required
# def get_models():
#     """API endpoint to get models for a provider."""
#     provider = request.args.get('provider')
#     if not provider:
#         return jsonify({'error': 'Provider not specified'}), 400
#
#     # Dictionary of available models
#     models = {
#         "openai": [
#             {"name": "gpt-3.5-turbo", "label": "GPT-3.5 Turbo",
#              "description": "Good balance of quality and speed",
#              "capabilities": ["Academic writing", "Structured content", "Citations integration"]},
#             {"name": "gpt-4", "label": "GPT-4",
#              "description": "Highest quality, more nuanced understanding",
#              "capabilities": ["Complex reasoning", "Advanced academic writing", "Better literature review"]}
#         ],
#         "anthropic": [
#             {"name": "claude-3-opus", "label": "Claude 3 Opus",
#              "description": "Anthropic's flagship model for complex tasks",
#              "capabilities": ["Academic writing", "Deep analysis", "Literature reviews"]},
#             {"name": "claude-3-sonnet", "label": "Claude 3 Sonnet",
#              "description": "Balanced performance and speed",
#              "capabilities": ["Academic writing", "Research summaries", "Citations"]}
#         ],
#         "gemini": [
#             {"name": "gemini-pro", "label": "Gemini Pro",
#              "description": "Google's advanced language model",
#              "capabilities": ["Academic writing", "Research analysis", "Citations"]}
#         ]
#     }
#
#     return jsonify({
#         'models': models.get(provider.lower(), [])
#     })
#
# @draft_generator_bp.route('/api/papers')
# @login_required
# def get_papers():
#     """API endpoint to fetch papers from arXiv."""
#     topic = request.args.get('topic')
#     if not topic:
#         return jsonify({'error': 'Topic not specified'}), 400
#
#     try:
#         papers = fetch_arxiv_papers(topic, max_results=15)
#         return jsonify({'papers': papers})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#
# @draft_generator_bp.route('/api/generate', methods=['POST'])
# @login_required
# def generate_draft():
#     """API endpoint to generate a paper draft."""
#     data = request.json
#
#     if not data:
#         return jsonify({'error': 'No data provided'}), 400
#
#     theme = data.get('theme')
#     journal_style = data.get('journal_style', 'general_scientific')
#     provider = data.get('provider')
#     model = data.get('model')
#     selected_papers = data.get('papers', [])
#
#     if not theme:
#         return jsonify({'error': 'Research topic not specified'}), 400
#
#     if not provider or not model:
#         return jsonify({'error': 'AI provider and model must be specified'}), 400
#
#     try:
#         # Generate prompt
#         prompt = generate_prompt(theme, journal_style, selected_papers)
#
#         # Call AI API
#         draft = call_ai_api(provider, model, prompt)
#
#         return jsonify({
#             'success': True,
#             'draft': draft
#         })
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#
# def register_dash(flask_app):
#     """
#     Register Dash app with the Flask app.
#     This is called from __init__.py when the blueprint is registered.
#     """
#     global dash_app
#
#     # Create Dash app
#     dash_app = Dash(
#         __name__,
#         server=flask_app,
#         url_base_pathname='/draft-generator/dash/',
#         external_stylesheets=[dbc.themes.BOOTSTRAP]
#     )
#
#     # Set up layout
#     dash_app.layout = create_draft_generator_layout()
#
#     # Register callbacks
#     register_draft_generator_callbacks(dash_app)
#
#     return dash_app


# modules/draft_generator/routes.py
# Routes for the Academic Draft Generator

from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from modules.draft_generator import draft_generator_bp
from modules.draft_generator.utils import get_user_ai_providers, fetch_arxiv_papers, call_ai_api, generate_prompt

# Main page route - serve the HTML template
@draft_generator_bp.route('/')
@login_required
def index():
    return render_template('draft_generator/index.html')

# API endpoint for getting available AI providers
@draft_generator_bp.route('/api/providers')
@login_required
def get_providers():
    user_id = current_user.id
    providers = get_user_ai_providers(user_id)

    return jsonify({
        'providers': [{'name': name, 'paid': config.get('is_paid', False)}
                     for name, config in providers.items()]
    })

# API endpoint for getting available models for a provider
@draft_generator_bp.route('/api/models')
@login_required
def get_models():
    provider = request.args.get('provider')
    if not provider:
        return jsonify({'error': 'Provider not specified'}), 400

    # Dictionary of available models
    models = {
        "openai": [
            {"name": "gpt-3.5-turbo", "label": "GPT-3.5 Turbo",
             "description": "Good balance of quality and speed",
             "capabilities": ["Academic writing", "Structured content", "Citations integration"]},
            {"name": "gpt-4", "label": "GPT-4",
             "description": "Highest quality, more nuanced understanding",
             "capabilities": ["Complex reasoning", "Advanced academic writing", "Better literature review"]}
        ],
        "anthropic": [
            {"name": "claude-3-opus", "label": "Claude 3 Opus",
             "description": "Anthropic's flagship model for complex tasks",
             "capabilities": ["Academic writing", "Deep analysis", "Literature reviews"]},
            {"name": "claude-3-sonnet", "label": "Claude 3 Sonnet",
             "description": "Balanced performance and speed",
             "capabilities": ["Academic writing", "Research summaries", "Citations"]}
        ],
        "gemini": [
            {"name": "gemini-pro", "label": "Gemini Pro",
             "description": "Google's advanced language model",
             "capabilities": ["Academic writing", "Research analysis", "Citations"]}
        ]
    }

    return jsonify({
        'models': models.get(provider.lower(), [])
    })

# API endpoint for fetching related papers
@draft_generator_bp.route('/api/papers')
@login_required
def get_papers():
    topic = request.args.get('topic')
    if not topic:
        return jsonify({'error': 'Topic not specified'}), 400

    try:
        papers = fetch_arxiv_papers(topic, max_results=15)
        return jsonify({'papers': papers})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API endpoint for generating paper draft
@draft_generator_bp.route('/api/generate', methods=['POST'])
@login_required
def generate_draft():
    data = request.json

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    theme = data.get('theme')
    journal_style = data.get('journal_style', 'general_scientific')
    provider = data.get('provider')
    model = data.get('model')
    selected_papers = data.get('papers', [])

    if not theme:
        return jsonify({'error': 'Research topic not specified'}), 400

    if not provider or not model:
        return jsonify({'error': 'AI provider and model must be specified'}), 400

    try:
        # Generate prompt
        prompt = generate_prompt(theme, journal_style, selected_papers)

        # Call AI API
        draft = call_ai_api(provider, model, prompt)

        return jsonify({
            'success': True,
            'draft': draft
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
