from flask import Blueprint, jsonify, request, current_app, abort
from flask_login import login_required, current_user
import openai
import requests
import os
import datetime
from models import db, User, Document, DocumentSection

api_bp = Blueprint('api', __name__)


# AI Assistant endpoints
@api_bp.route('/ai/analyze', methods=['POST'])
@login_required
def ai_analyze():
    """Analyze document content and provide suggestions"""
    data = request.json
    text = data.get('text', '')
    analysis_type = data.get('type', 'grammar')

    try:
        # Use AI API for analysis
        api_key = current_app.config['AI_API_KEY']

        if not api_key:
            return jsonify({
                'success': False,
                'error': 'AI API key not configured'
            }), 500

        openai.api_key = api_key

        prompts = {
            'grammar': f"Check the following text for grammar and spelling issues and suggest corrections:\n\n{text}",
            'rewrite': f"Rewrite the following text to improve clarity and flow:\n\n{text}",
            'expand': f"Expand on the following text with additional details and examples:\n\n{text}",
            'simplify': f"Simplify the following text to make it more accessible:\n\n{text}",
            'academic': f"Revise the following text to match academic writing standards:\n\n{text}"
        }

        prompt = prompts.get(analysis_type, prompts['grammar'])

        # Use OpenAI API for analysis
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an academic writing assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )

        result = response.choices[0].message.content

        return jsonify({
            'success': True,
            'result': result,
            'type': analysis_type
        })

    except Exception as e:
        current_app.logger.error(f"AI analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/ai/suggest', methods=['POST'])
@login_required
def ai_suggest():
    """Generate suggestions for document sections"""
    data = request.json
    section_type = data.get('section_type', '')
    document_type = data.get('document_type', '')
    context = data.get('context', '')

    try:
        # Use AI API for suggestions
        api_key = current_app.config['AI_API_KEY']

        if not api_key:
            return jsonify({
                'success': False,
                'error': 'AI API key not configured'
            }), 500

        openai.api_key = api_key

        prompt = f"""Generate a detailed outline for a {section_type} section in a {document_type} document.

Context about the document:
{context}

Please provide a structured outline with key points that should be included in this section."""

        # Use OpenAI API for suggestions
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an academic writing assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )

        result = response.choices[0].message.content

        return jsonify({
            'success': True,
            'result': result,
            'section_type': section_type
        })

    except Exception as e:
        current_app.logger.error(f"AI suggestion error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Analysis endpoints
@api_bp.route('/analysis/document/<int:document_id>', methods=['GET'])
@login_required
def analyze_document(document_id):
    """Analyze document structure and content"""
    document = Document.query.get_or_404(document_id)

    # Check if user is owner or collaborator
    is_owner = document.user_id == current_user.id
    is_collaborator = any(c.user_id == current_user.id for c in document.collaborators)

    if not is_owner and not is_collaborator:
        abort(403)  # Forbidden

    # Get all sections
    sections = DocumentSection.query.filter_by(document_id=document_id).all()

    # Basic analysis
    total_words = 0
    section_counts = {}
    word_counts = {}
    readability_scores = {}

    for section in sections:
        # Count words
        words = len(section.content.split()) if section.content else 0
        total_words += words
        word_counts[section.title] = words

        # Count sections by type
        section_type = section.title
        section_counts[section_type] = section_counts.get(section_type, 0) + 1

        # Simple readability score (placeholder)
        # In a real app, use more sophisticated metrics like Flesch-Kincaid
        avg_word_length = sum(len(w) for w in section.content.split()) / max(words, 1) if section.content else 0
        readability_scores[section.title] = min(100, max(0, 100 - (avg_word_length - 4) * 10))

    # Get expected structure based on document type
    from document_crud import get_document_template
    expected_template = get_document_template(document.document_type)
    expected_sections = [section['title'] for section in expected_template]

    # Check which expected sections are missing
    current_sections = [section.title for section in sections]
    missing_sections = [s for s in expected_sections if s not in current_sections]

    # Calculate completeness percentage
    completeness = (len(expected_sections) - len(missing_sections)) / len(expected_sections) * 100

    analysis_result = {
        'total_words': total_words,
        'section_counts': section_counts,
        'word_counts': word_counts,
        'readability_scores': readability_scores,
        'missing_sections': missing_sections,
        'completeness': completeness,
        'expected_sections': expected_sections
    }

    return jsonify({
        'success': True,
        'analysis': analysis_result
    })


# User search for collaboration
@api_bp.route('/users/search', methods=['GET'])
@login_required
def search_users():
    """Search for users by email or name for collaboration"""
    query = request.args.get('q', '')

    if not query or len(query) < 3:
        return jsonify({
            'success': False,
            'error': 'Search query must be at least 3 characters'
        }), 400

    users = User.query.filter(
        (User.email.ilike(f'%{query}%') | User.full_name.ilike(f'%{query}%')) &
        (User.id != current_user.id)  # Exclude current user
    ).limit(10).all()

    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'full_name': user.full_name,
            'email': user.email
        })

    return jsonify({
        'success': True,
        'users': user_list
    })
