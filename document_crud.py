import datetime
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from models import db, Document, DocumentSection, DocumentCollaborator
from section_crud import create_section, get_section_hierarchy


class DocumentError(Exception):
    """Base exception for document operations"""
    pass


def get_document_types():
    """Return available document types"""
    return [
        {'id': 'academic', 'name': 'Academic Paper'},
        {'id': 'thesis', 'name': 'Thesis/Dissertation'},
        {'id': 'report', 'name': 'Technical Report'},
        {'id': 'article', 'name': 'Article'},
        {'id': 'book', 'name': 'Book'},
        {'id': 'presentation', 'name': 'Presentation'}
    ]


def get_document_template(doc_type):
    """Return the default template for a document type"""
    templates = {
        'academic': [
            {'title': 'Abstract', 'content': '', 'position': 1, 'children': []},
            {'title': 'Introduction', 'content': '', 'position': 2, 'children': []},
            {'title': 'Methods', 'content': '', 'position': 3, 'children': []},
            {'title': 'Results', 'content': '', 'position': 4, 'children': []},
            {'title': 'Discussion', 'content': '', 'position': 5, 'children': []},
            {'title': 'Conclusion', 'content': '', 'position': 6, 'children': []},
            {'title': 'References', 'content': '', 'position': 7, 'children': []}
        ],
        'thesis': [
            {'title': 'Abstract', 'content': '', 'position': 1, 'children': []},
            {'title': 'Acknowledgements', 'content': '', 'position': 2, 'children': []},
            {'title': 'Introduction', 'content': '', 'position': 3, 'children': []},
            {'title': 'Literature Review', 'content': '', 'position': 4, 'children': []},
            {'title': 'Methodology', 'content': '', 'position': 5, 'children': []},
            {'title': 'Results', 'content': '', 'position': 6, 'children': []},
            {'title': 'Discussion', 'content': '', 'position': 7, 'children': []},
            {'title': 'Conclusion', 'content': '', 'position': 8, 'children': []},
            {'title': 'Bibliography', 'content': '', 'position': 9, 'children': []},
            {'title': 'Appendices', 'content': '', 'position': 10, 'children': []}
        ],
        'report': [
            {'title': 'Executive Summary', 'content': '', 'position': 1, 'children': []},
            {'title': 'Introduction', 'content': '', 'position': 2, 'children': []},
            {'title': 'Background', 'content': '', 'position': 3, 'children': []},
            {'title': 'Methodology', 'content': '', 'position': 4, 'children': []},
            {'title': 'Findings', 'content': '', 'position': 5, 'children': []},
            {'title': 'Recommendations', 'content': '', 'position': 6, 'children': []},
            {'title': 'Conclusion', 'content': '', 'position': 7, 'children': []},
            {'title': 'References', 'content': '', 'position': 8, 'children': []}
        ],
        'article': [
            {'title': 'Headline', 'content': '', 'position': 1, 'children': []},
            {'title': 'Byline', 'content': '', 'position': 2, 'children': []},
            {'title': 'Introduction', 'content': '', 'position': 3, 'children': []},
            {'title': 'Body', 'content': '', 'position': 4, 'children': []},
            {'title': 'Conclusion', 'content': '', 'position': 5, 'children': []}
        ],
        'book': [
            {'title': 'Title Page', 'content': '', 'position': 1, 'children': []},
            {'title': 'Table of Contents', 'content': '', 'position': 2, 'children': []},
            {'title': 'Preface', 'content': '', 'position': 3, 'children': []},
            {'title': 'Chapter 1', 'content': '', 'position': 4, 'children': []},
            {'title': 'Chapter 2', 'content': '', 'position': 5, 'children': []},
            {'title': 'Chapter 3', 'content': '', 'position': 6, 'children': []},
            {'title': 'Bibliography', 'content': '', 'position': 7, 'children': []},
            {'title': 'Appendix', 'content': '', 'position': 8, 'children': []}
        ],
        'presentation': [
            {'title': 'Title Slide', 'content': '', 'position': 1, 'children': []},
            {'title': 'Agenda', 'content': '', 'position': 2, 'children': []},
            {'title': 'Introduction', 'content': '', 'position': 3, 'children': []},
            {'title': 'Main Content', 'content': '', 'position': 4, 'children': []},
            {'title': 'Conclusion', 'content': '', 'position': 5, 'children': []},
            {'title': 'Q&A', 'content': '', 'position': 6, 'children': []}
        ]
    }

    return templates.get(doc_type, [{'title': 'New Section', 'content': '', 'position': 1, 'children': []}])


def create_document(title, doc_type, user_id):
    """Create a new document with initial template structure"""
    try:
        # Create the document
        document = Document(
            title=title,
            document_type=doc_type,
            user_id=user_id,
            created_date=datetime.datetime.utcnow(),
            modified_date=datetime.datetime.utcnow(),
            status='draft'
        )
        db.session.add(document)
        db.session.flush()  # Get the document ID

        # Create sections from template
        template = get_document_template(doc_type)
        for section_data in template:
            create_section_from_template(document.id, section_data, None)

        db.session.commit()
        return document
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating document: {str(e)}")
        raise DocumentError(f"Failed to create document: {str(e)}")


def create_section_from_template(document_id, section_data, parent_id):
    """Recursively create sections from template"""
    # Create the current section
    section = create_section(
        document_id=document_id,
        title=section_data['title'],
        content=section_data['content'],
        position=section_data['position'],
        parent_id=parent_id
    )

    # Create child sections if any
    for idx, child_data in enumerate(section_data.get('children', []), 1):
        child_data['position'] = idx
        create_section_from_template(document_id, child_data, section.id)

    return section


def get_document(document_id):
    """Get document by ID"""
    try:
        document = Document.query.get(document_id)
        return document
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error retrieving document {document_id}: {str(e)}")
        raise DocumentError(f"Failed to retrieve document: {str(e)}")


def get_documents_by_user(user_id):
    """Get all documents owned by a user"""
    try:
        documents = Document.query.filter_by(user_id=user_id).all()
        return documents
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error retrieving documents for user {user_id}: {str(e)}")
        raise DocumentError(f"Failed to retrieve documents: {str(e)}")


def get_collaborative_documents(user_id):
    """Get documents where user is a collaborator"""
    try:
        collaborations = DocumentCollaborator.query.filter_by(user_id=user_id).all()
        document_ids = [collab.document_id for collab in collaborations]
        documents = Document.query.filter(Document.id.in_(document_ids)).all()
        return documents
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error retrieving collaborative documents for user {user_id}: {str(e)}")
        raise DocumentError(f"Failed to retrieve collaborative documents: {str(e)}")


def update_document(document_id, title=None, status=None):
    """Update document attributes"""
    try:
        document = Document.query.get(document_id)
        if not document:
            raise DocumentError(f"Document with ID {document_id} not found")

        if title is not None:
            document.title = title

        if status is not None:
            document.status = status

        document.modified_date = datetime.datetime.utcnow()
        db.session.commit()
        return document
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating document {document_id}: {str(e)}")
        raise DocumentError(f"Failed to update document: {str(e)}")


def delete_document(document_id):
    """Delete a document and all its sections"""
    try:
        document = Document.query.get(document_id)
        if not document:
            raise DocumentError(f"Document with ID {document_id} not found")

        db.session.delete(document)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise DocumentError(f"Failed to delete document: {str(e)}")


def add_collaborator(document_id, user_id, permission_level='view'):
    """Add a collaborator to a document"""
    try:
        # Check if already a collaborator
        existing = DocumentCollaborator.query.filter_by(
            document_id=document_id, user_id=user_id).first()

        if existing:
            # Update permission if different
            if existing.permission_level != permission_level:
                existing.permission_level = permission_level
                db.session.commit()
            return existing

        # Add new collaborator
        collaborator = DocumentCollaborator(
            document_id=document_id,
            user_id=user_id,
            permission_level=permission_level,
            added_at=datetime.datetime.utcnow()
        )

        # Update document collaboration field
        document = Document.query.get(document_id)
        document.collaboration_enabled = True
        document.last_collaboration = datetime.datetime.utcnow()

        db.session.add(collaborator)
        db.session.commit()
        return collaborator
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding collaborator to document {document_id}: {str(e)}")
        raise DocumentError(f"Failed to add collaborator: {str(e)}")


def remove_collaborator(document_id, user_id):
    """Remove a collaborator from a document"""
    try:
        collaborator = DocumentCollaborator.query.filter_by(
            document_id=document_id, user_id=user_id).first()

        if not collaborator:
            raise DocumentError(f"User {user_id} is not a collaborator on document {document_id}")

        db.session.delete(collaborator)

        # Check if any collaborators remain
        remaining = DocumentCollaborator.query.filter_by(document_id=document_id).count()
        if remaining == 0:
            document = Document.query.get(document_id)
            document.collaboration_enabled = False

        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error removing collaborator from document {document_id}: {str(e)}")
        raise DocumentError(f"Failed to remove collaborator: {str(e)}")


def get_document_structure(document_id):
    """Get the complete document structure with sections hierarchy"""
    try:
        document = Document.query.get(document_id)
        if not document:
            raise DocumentError(f"Document with ID {document_id} not found")

        # Get document sections organized in hierarchy
        sections = get_section_hierarchy(document_id)

        # Prepare document data
        document_data = {
            'id': document.id,
            'title': document.title,
            'document_type': document.document_type,
            'status': document.status,
            'created_date': document.created_date.isoformat(),
            'modified_date': document.modified_date.isoformat(),
            'owner_id': document.user_id,
            'collaboration_enabled': document.collaboration_enabled,
            'sections': sections
        }

        return document_data
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error retrieving document structure for {document_id}: {str(e)}")
        raise DocumentError(f"Failed to retrieve document structure: {str(e)}")
