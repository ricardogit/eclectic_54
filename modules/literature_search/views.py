# modules/literature_search/views.py

from flask import Blueprint, render_template
from flask_login import login_required
from flask import request, jsonify, current_app
from flask_login import current_user
from modules.literature_search.service import LiteratureSearchService

literature_bp = Blueprint('literature', __name__, url_prefix='/literature')

@literature_bp.route('/search')
@login_required
def search():
    """Render the literature search page."""
    return render_template('literature/search.html')


# Create service
literature_service = LiteratureSearchService()


@literature_bp.route('/api/search')
@login_required
def api_search_papers():
    """Search for papers."""
    query = request.args.get('query', '')
    source = request.args.get('source', 'all')
    max_results = int(request.args.get('max_results', 25))

    if not query:
        return jsonify({'error': 'Query is required'}), 400

    try:
        papers = literature_service.search_papers(
            query=query,
            source=source,
            max_results=max_results,
            user_id=current_user.id
        )

        return jsonify({
            'query': query,
            'source': source,
            'results': papers,
            'count': len(papers)
        })
    except Exception as e:
        current_app.logger.error(f"Error searching papers: {e}")
        return jsonify({'error': str(e)}), 500

# Add the rest of your API endpoints here
# ...
