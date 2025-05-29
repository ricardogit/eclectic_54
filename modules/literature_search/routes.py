from flask import Blueprint, request, jsonify, current_app, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from modules.literature_search.service import LiteratureSearchService
# Make sure to import the needed models
from models import db, Collection, SearchQuery, paper_collections

# Create Blueprint with correct prefix
literature_bp = Blueprint('literature', __name__, url_prefix='/literature')

# Create service
literature_service = LiteratureSearchService()


@literature_bp.route('/')
@login_required
def search():
    """Render the literature search page."""
    return render_template('literature/basic_search.html', title="Literature Search")


@literature_bp.route('/basic-search')
@login_required
def basic_search():
    """Simple search without Dash."""
    results = []
    query = request.args.get('query', '')
    source = request.args.get('source', 'all')
    year_from = request.args.get('year_from', '')
    year_to = request.args.get('year_to', '')

    if query:
        try:
            # Get search results
            results = literature_service.search_papers(
                query=query,
                source=source,
                max_results=25,
                user_id=current_user.id
            )

            # Apply year filter if specified
            if year_from or year_to:
                filtered_results = []
                for paper in results:
                    year = paper.get('year')
                    if year:
                        if year_from and year_to:
                            if int(year_from) <= year <= int(year_to):
                                filtered_results.append(paper)
                        elif year_from:
                            if int(year_from) <= year:
                                filtered_results.append(paper)
                        elif year_to:
                            if year <= int(year_to):
                                filtered_results.append(paper)
                results = filtered_results

        except Exception as e:
            current_app.logger.error(f"Error searching papers: {e}")
            flash(f"Error searching papers: {str(e)}", "danger")
            results = []

    # Get recent searches
    try:
        recent_searches = db.session.query(SearchQuery).filter(SearchQuery.user_id == current_user.id). \
            order_by(SearchQuery.created_at.desc()). \
            limit(5). \
            all()
    except Exception as e:
        current_app.logger.error(f"Error getting recent searches: {e}")
        recent_searches = []

    # Get user collections with paper counts
    try:
        collections = []
        collection_records = db.session.query(Collection).filter(Collection.user_id == current_user.id).all()

        for collection in collection_records:
            # Count papers in each collection
            paper_count = db.session.query(db.func.count(paper_collections.c.paper_id)). \
                              filter(paper_collections.c.collection_id == collection.id). \
                              scalar() or 0

            # Add to collections list with paper count
            collections.append({
                'id': collection.id,
                'name': collection.name,
                'description': collection.description,
                'paper_count': paper_count
            })
    except Exception as e:
        current_app.logger.error(f"Error getting collections: {e}")
        collections = []

    return render_template(
        'literature/basic_search.html',
        title="Literature Search",
        query=query,
        source=source,
        year_from=year_from,
        year_to=year_to,
        results=results,
        recent_searches=recent_searches,
        collections=collections
    )


# Add a route to get collection papers for the modal
@literature_bp.route('/api/collections/<int:collection_id>/papers')
@login_required
def get_collection_papers(collection_id):
    """Get papers in a collection."""
    try:
        papers = literature_service.get_collection_papers(collection_id)

        # Format papers for JSON response
        paper_list = []
        for paper in papers:
            paper_list.append({
                'id': paper.id,
                'title': paper.title,
                'authors': paper.authors,
                'journal': paper.journal,
                'year': paper.year,
                'doi': paper.doi,
                'url': paper.url
            })

        return jsonify(paper_list)
    except Exception as e:
        current_app.logger.error(f"Error getting collection papers: {e}")
        return jsonify({'error': str(e)}), 500

# Add this route with a different name to avoid conflict
@literature_bp.route('/submit-collection', methods=['POST'])
@login_required
def submit_collection_form():
    """Handle the collection creation form submission."""
    name = request.form.get('name')
    description = request.form.get('description', '')

    if not name:
        flash('Collection name is required', 'danger')
        return redirect(url_for('literature.basic_search'))

    try:
        # Create collection
        collection = literature_service.create_collection(
            name=name,
            description=description,
            user_id=current_user.id
        )

        flash(f'Collection "{collection.name}" created successfully', 'success')
    except Exception as e:
        current_app.logger.error(f"Error creating collection: {e}")
        flash(f'Error creating collection: {str(e)}', 'danger')

    return redirect(url_for('literature.basic_search'))


# Original API endpoints - keep these as they are
@literature_bp.route('/api/search', methods=['GET'])
@login_required
def search_papers():
    """Search for papers API endpoint."""
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


@literature_bp.route('/paper/<source>/<paper_id>')
@login_required
def view_paper(source, paper_id):
    """View paper details."""
    try:
        # Get paper details
        paper = literature_service.get_paper(paper_id, source)

        # Get user collections for adding to collection
        collections = db.session.query(Collection).filter(Collection.user_id == current_user.id).all()

        return render_template(
            'literature/paper_details.html',
            title=paper.get('title', 'Paper Details'),
            paper=paper,
            collections=collections
        )
    except Exception as e:
        current_app.logger.error(f"Error getting paper details: {e}")
        flash(f"Error getting paper details: {str(e)}", "danger")
        return redirect(url_for('literature.basic_search'))


@literature_bp.route('/api/save-paper', methods=['POST'])
@login_required
def api_save_paper():
    """API endpoint to save a paper."""
    data = request.json

    if not data or 'paper_id' not in data or 'source_db' not in data:
        return jsonify({'error': 'Paper data is required'}), 400

    try:
        # Get paper details
        paper_data = literature_service.get_paper(data['paper_id'], data['source_db'])

        # Save paper
        paper = literature_service.save_paper(paper_data, current_user.id)

        return jsonify({
            'message': 'Paper saved successfully',
            'paper_id': paper.id
        })
    except Exception as e:
        current_app.logger.error(f"Error saving paper: {e}")
        return jsonify({'error': str(e)}), 500


@literature_bp.route('/api/collections', methods=['GET'])
@login_required
def api_get_collections():
    """API endpoint to get user collections."""
    try:
        collections = db.session.query(Collection).filter(Collection.user_id == current_user.id).all()

        collection_list = []
        for collection in collections:
            collection_list.append({
                'id': collection.id,
                'name': collection.name,
                'description': collection.description
            })

        return jsonify(collection_list)
    except Exception as e:
        current_app.logger.error(f"Error getting collections: {e}")
        return jsonify({'error': str(e)}), 500


@literature_bp.route('/api/collections/<int:collection_id>/papers', methods=['POST'])
@login_required
def api_add_paper_to_collection(collection_id):
    """API endpoint to add a paper to a collection."""
    data = request.json

    if not data or 'paper_id' not in data or 'source' not in data:
        return jsonify({'error': 'Paper data is required'}), 400

    try:
        # Get paper details
        paper_data = literature_service.get_paper(data['paper_id'], data['source'])

        # Save paper to get ID
        paper = literature_service.save_paper(paper_data, current_user.id)

        # Add to collection
        success = literature_service.add_paper_to_collection(paper.id, collection_id)

        if success:
            return jsonify({'message': 'Paper added to collection successfully'})
        else:
            return jsonify({'error': 'Failed to add paper to collection'}), 400
    except Exception as e:
        current_app.logger.error(f"Error adding paper to collection: {e}")
        return jsonify({'error': str(e)}), 500


@literature_bp.route('/submit-paper-to-collection', methods=['POST'])
@login_required
def submit_paper_to_collection():
    """Handle the form submission for adding a paper to a collection."""
    paper_id = request.form.get('paper_id')
    source = request.form.get('source')
    collection_id = request.form.get('collection_id')

    if not paper_id or not source or not collection_id:
        flash('Missing required data', 'danger')
        return redirect(url_for('literature.basic_search'))

    try:
        # Get paper details
        paper_data = literature_service.get_paper(paper_id, source)

        # Save paper
        paper = literature_service.save_paper(paper_data, current_user.id)

        # Add to collection
        success = literature_service.add_paper_to_collection(paper.id, int(collection_id))

        if success:
            flash('Paper added to collection successfully', 'success')
        else:
            flash('Failed to add paper to collection', 'danger')

    except Exception as e:
        current_app.logger.error(f"Error adding paper to collection: {e}")
        flash(f'Error adding paper to collection: {str(e)}', 'danger')

    return redirect(url_for('literature.basic_search'))
