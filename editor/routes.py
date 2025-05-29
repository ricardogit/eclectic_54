from flask import Blueprint, render_template, redirect, url_for, request, jsonify, abort
from flask_login import login_required, current_user
from models import db, Document, DocumentSection, DocumentCollaborator, SectionLock
from document_crud import (
    get_document, get_documents_by_user, get_document_types,
    create_document, update_document, delete_document,
    add_collaborator, remove_collaborator, get_document_structure,
    get_collaborative_documents
)
from section_crud import (
    get_section, get_sections_by_document, create_section,
    update_section, delete_section, move_section,
    lock_section, unlock_section, get_section_revisions
)

editor_bp = Blueprint('editor', __name__)


# Dashboard - List all documents
@editor_bp.route('/dashboard')
@login_required
def dashboard():
    owned_documents = get_documents_by_user(current_user.id)
    collaborative_documents = get_collaborative_documents(current_user.id)

    return render_template(
        'editor/dashboard.html',
        owned_documents=owned_documents,
        collaborative_documents=collaborative_documents
    )


# Create a new document
@editor_bp.route('/documents/new', methods=['GET', 'POST'])
@login_required
def new_document():
    if request.method == 'POST':
        title = request.form.get('title')
        document_type = request.form.get('document_type')

        if not title or not document_type:
            return render_template(
                'editor/new_document.html',
                document_types=get_document_types(),
                error="Title and document type are required"
            )

        document = create_document(title, document_type, current_user.id)
        return redirect(url_for('editor.edit_document', document_id=document.id))

    return render_template(
        'editor/new_document.html',
        document_types=get_document_types()
    )


# Edit document
@editor_bp.route('/documents/<int:document_id>/edit')
@login_required
def edit_document(document_id):
    document = get_document(document_id)

    # Check if user is owner or collaborator
    is_owner = document.user_id == current_user.id
    is_collaborator = DocumentCollaborator.query.filter_by(
        document_id=document_id, user_id=current_user.id
    ).first() is not None

    if not is_owner and not is_collaborator:
        abort(403)  # Forbidden

    document_structure = get_document_structure(document_id)

    return render_template(
        'editor/editor.html',
        document=document,
        structure=document_structure,
        is_owner=is_owner,
        is_collaborator=is_collaborator
    )


# API Routes for AJAX operations
@editor_bp.route('/api/documents/<int:document_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_document(document_id):
    document = get_document(document_id)

    # Check ownership
    if document.user_id != current_user.id:
        abort(403)  # Forbidden

    if request.method == 'GET':
        return jsonify(get_document_structure(document_id))

    elif request.method == 'PUT':
        data = request.json
        updated = update_document(
            document_id,
            title=data.get('title'),
            status=data.get('status')
        )
        return jsonify({
            'success': True,
            'document': {
                'id': updated.id,
                'title': updated.title,
                'status': updated.status,
                'modified_date': updated.modified_date.isoformat()
            }
        })

    elif request.method == 'DELETE':
        delete_document(document_id)
        return jsonify({'success': True})


@editor_bp.route('/api/documents/<int:document_id>/sections', methods=['GET', 'POST'])
@login_required
def api_document_sections(document_id):
    document = get_document(document_id)

    # Check if user is owner or collaborator with edit permission
    is_owner = document.user_id == current_user.id
    collaborator = DocumentCollaborator.query.filter_by(
        document_id=document_id, user_id=current_user.id
    ).first()
    can_edit = is_owner or (collaborator and collaborator.permission_level == 'edit')

    if not is_owner and not collaborator:
        abort(403)  # Forbidden

    if request.method == 'GET':
        return jsonify({
            'sections': get_section_hierarchy(document_id)
        })

    elif request.method == 'POST':
        if not can_edit:
            abort(403)  # Forbidden

        data = request.json
        section = create_section(
            document_id=document_id,
            title=data.get('title', 'New Section'),
            content=data.get('content', ''),
            position=data.get('position'),
            parent_id=data.get('parent_id')
        )

        return jsonify({
            'success': True,
            'section': {
                'id': section.id,
                'title': section.title,
                'position': section.position,
                'parent_id': section.parent_id,
                'modified_date': section.modified_date.isoformat()
            }
        })


@editor_bp.route('/api/sections/<int:section_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_section(section_id):
    section = get_section(section_id)
    document = get_document(section.document_id)

    # Check if user is owner or collaborator with edit permission
    is_owner = document.user_id == current_user.id
    collaborator = DocumentCollaborator.query.filter_by(
        document_id=document.id, user_id=current_user.id
    ).first()
    can_edit = is_owner or (collaborator and collaborator.permission_level == 'edit')

    if not is_owner and not collaborator:
        abort(403)  # Forbidden

    if request.method == 'GET':
        return jsonify({
            'id': section.id,
            'title': section.title,
            'content': section.content,
            'position': section.position,
            'parent_id': section.parent_id,
            'document_id': section.document_id,
            'modified_date': section.modified_date.isoformat()
        })

    elif request.method == 'PUT':
        if not can_edit:
            abort(403)  # Forbidden

        data = request.json
        updated = update_section(
            section_id=section_id,
            title=data.get('title'),
            content=data.get('content'),
            position=data.get('position'),
            user_id=current_user.id
        )

        return jsonify({
            'success': True,
            'section': {
                'id': updated.id,
                'title': updated.title,
                'content': updated.content,
                'position': updated.position,
                'parent_id': updated.parent_id,
                'modified_date': updated.modified_date.isoformat()
            }
        })

    elif request.method == 'DELETE':
        if not can_edit:
            abort(403)  # Forbidden

        delete_section(section_id)
        return jsonify({'success': True})


@editor_bp.route('/api/sections/<int:section_id>/move', methods=['POST'])
@login_required
def api_move_section(section_id):
    section = get_section(section_id)
    document = get_document(section.document_id)

    # Check if user is owner or collaborator with edit permission
    is_owner = document.user_id == current_user.id
    collaborator = DocumentCollaborator.query.filter_by(
        document_id=document.id, user_id=current_user.id
    ).first()
    can_edit = is_owner or (collaborator and collaborator.permission_level == 'edit')

    if not can_edit:
        abort(403)  # Forbidden

    data = request.json
    moved = move_section(
        section_id=section_id,
        new_parent_id=data.get('parent_id'),
        new_position=data.get('position')
    )

    return jsonify({
        'success': True,
        'section': {
            'id': moved.id,
            'title': moved.title,
            'position': moved.position,
            'parent_id': moved.parent_id,
            'modified_date': moved.modified_date.isoformat()
        }
    })


@editor_bp.route('/api/sections/<int:section_id>/lock', methods=['POST'])
@login_required
def api_lock_section(section_id):
    section = get_section(section_id)
    document = get_document(section.document_id)

    # Check if user is owner or collaborator
    is_owner = document.user_id == current_user.id
    collaborator = DocumentCollaborator.query.filter_by(
        document_id=document.id, user_id=current_user.id
    ).first()

    if not is_owner and not collaborator:
        abort(403)  # Forbidden

    try:
        data = request.json
        duration = data.get('duration_minutes', 15)
        lock = lock_section(section_id, current_user.id, duration)

        return jsonify({
            'success': True,
            'lock': {
                'section_id': lock.section_id,
                'user_id': lock.user_id,
                'locked_at': lock.locked_at.isoformat(),
                'expires_at': lock.expires_at.isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 409  # Conflict


@editor_bp.route('/api/sections/<int:section_id>/unlock', methods=['POST'])
@login_required
def api_unlock_section(section_id):
    unlock_section(section_id, current_user.id)
    return jsonify({'success': True})


@editor_bp.route('/api/sections/<int:section_id>/revisions', methods=['GET'])
@login_required
def api_section_revisions(section_id):
    section = get_section(section_id)
    document = get_document(section.document_id)

    # Check if user is owner or collaborator
    is_owner = document.user_id == current_user.id
    collaborator = DocumentCollaborator.query.filter_by(
        document_id=document.id, user_id=current_user.id
    ).first()

    if not is_owner and not collaborator:
        abort(403)  # Forbidden

    revisions = get_section_revisions(section_id)
    revision_data = []

    for rev in revisions:
        revision_data.append({
            'id': rev.id,
            'section_id': rev.section_id,
            'user_id': rev.user_id,
            'content': rev.content,
            'created_at': rev.created_at.isoformat()
        })

    return jsonify({
        'revisions': revision_data
    })


@editor_bp.route('/api/documents/<int:document_id>/collaborators', methods=['GET', 'POST', 'DELETE'])
@login_required
def api_document_collaborators(document_id):
    document = get_document(document_id)

    # Check ownership for modification
    if document.user_id != current_user.id and request.method != 'GET':
        abort(403)  # Forbidden

    if request.method == 'GET':
        # Check if user is owner or collaborator
        is_owner = document.user_id == current_user.id
        is_collaborator = DocumentCollaborator.query.filter_by(
            document_id=document_id, user_id=current_user.id
        ).first() is not None

        if not is_owner and not is_collaborator:
            abort(403)  # Forbidden

        collaborators = DocumentCollaborator.query.filter_by(document_id=document_id).all()
        collaborator_data = []

        for collab in collaborators:
            user = collab.user
            collaborator_data.append({
                'id': collab.id,
                'user_id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'permission_level': collab.permission_level,
                'added_at': collab.added_at.isoformat()
            })

        return jsonify({
            'collaborators': collaborator_data
        })

    elif request.method == 'POST':
        data = request.json
        email = data.get('email')
        permission_level = data.get('permission_level', 'view')

        # Find user by email
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        # Add collaborator
        collaborator = add_collaborator(document_id, user.id, permission_level)

        return jsonify({
            'success': True,
            'collaborator': {
                'id': collaborator.id,
                'user_id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'permission_level': collaborator.permission_level,
                'added_at': collaborator.added_at.isoformat()
            }
        })

    elif request.method == 'DELETE':
        data = request.json
        user_id = data.get('user_id')

        # Remove collaborator
        remove_collaborator(document_id, user_id)

        return jsonify({
            'success': True
        })

@editor_bp.route('/draft_generator')
@login_required
def draft_generator():
    """Simple route for the Academic Draft Generator."""
    return render_template('draft_generator/index.html')