import datetime
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from models import db, DocumentSection, SectionLock, SectionRevision


class SectionError(Exception):
    """Base exception for section operations"""
    pass


def create_section(document_id, title, content="", position=None, parent_id=None):
    """Create a new document section"""
    try:
        # If position not specified, place at the end
        if position is None:
            if parent_id:
                # Get highest position among siblings
                highest = DocumentSection.query.filter_by(
                    document_id=document_id, parent_id=parent_id
                ).order_by(DocumentSection.position.desc()).first()
            else:
                # Get highest position among root sections
                highest = DocumentSection.query.filter_by(
                    document_id=document_id, parent_id=None
                ).order_by(DocumentSection.position.desc()).first()

            position = 1 if highest is None else highest.position + 1

        # Create the section
        section = DocumentSection(
            title=title,
            content=content,
            position=position,
            document_id=document_id,
            parent_id=parent_id,
            created_date=datetime.datetime.utcnow(),
            modified_date=datetime.datetime.utcnow()
        )
        db.session.add(section)
        db.session.commit()
        return section
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating section: {str(e)}")
        raise SectionError(f"Failed to create section: {str(e)}")


def get_section(section_id):
    """Get section by ID"""
    try:
        section = DocumentSection.query.get(section_id)
        return section
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error retrieving section {section_id}: {str(e)}")
        raise SectionError(f"Failed to retrieve section: {str(e)}")


def get_sections_by_document(document_id):
    """Get all sections for a document"""
    try:
        sections = DocumentSection.query.filter_by(document_id=document_id).all()
        return sections
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error retrieving sections for document {document_id}: {str(e)}")
        raise SectionError(f"Failed to retrieve sections: {str(e)}")


def get_section_hierarchy(document_id):
    """Get sections organized in a hierarchical structure"""
    try:
        # Get root sections (no parent)
        root_sections = DocumentSection.query.filter_by(
            document_id=document_id, parent_id=None
        ).order_by(DocumentSection.position).all()

        # Build hierarchy
        sections = []
        for section in root_sections:
            sections.append(build_section_tree(section))

        return sections
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error retrieving section hierarchy for document {document_id}: {str(e)}")
        raise SectionError(f"Failed to retrieve section hierarchy: {str(e)}")


def build_section_tree(section):
    """Recursively build section tree"""
    section_data = {
        'id': section.id,
        'title': section.title,
        'position': section.position,
        'modified_date': section.modified_date.isoformat(),
        'children': []
    }

    # Add children if any
    for child in sorted(section.children, key=lambda x: x.position):
        section_data['children'].append(build_section_tree(child))

    return section_data


def update_section(section_id, title=None, content=None, position=None, user_id=None):
    """Update section attributes and create revision"""
    try:
        section = DocumentSection.query.get(section_id)
        if not section:
            raise SectionError(f"Section with ID {section_id} not found")

        # Create revision if content changed and user_id provided
        if content is not None and content != section.content and user_id is not None:
            revision = SectionRevision(
                section_id=section_id,
                user_id=user_id,
                content=section.content,  # Store the old content
                created_at=datetime.datetime.utcnow()
            )
            db.session.add(revision)

        # Update section attributes
        if title is not None:
            section.title = title

        if content is not None:
            section.content = content

        if position is not None:
            # Reorder siblings if position changed
            if position != section.position:
                reorder_sections(section.document_id, section.parent_id, section.id, position)
                section.position = position

        section.modified_date = datetime.datetime.utcnow()
        db.session.commit()
        return section
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating section {section_id}: {str(e)}")
        raise SectionError(f"Failed to update section: {str(e)}")


def reorder_sections(document_id, parent_id, section_id, new_position):
    """Reorder sections when a section's position changes"""
    if parent_id:
        # Reorder siblings with the same parent
        siblings = DocumentSection.query.filter_by(
            document_id=document_id, parent_id=parent_id
        ).order_by(DocumentSection.position).all()
    else:
        # Reorder root sections
        siblings = DocumentSection.query.filter_by(
            document_id=document_id, parent_id=None
        ).order_by(DocumentSection.position).all()

    # Remove the current section from the list
    siblings = [s for s in siblings if s.id != section_id]

    # Insert at new position
    new_position = max(1, min(new_position, len(siblings) + 1))
    siblings.insert(new_position - 1, None)  # Placeholder

    # Update positions
    for i, sibling in enumerate(siblings, 1):
        if sibling:  # Skip placeholder
            sibling.position = i


def delete_section(section_id):
    """Delete a section and all its children"""
    try:
        section = DocumentSection.query.get(section_id)
        if not section:
            raise SectionError(f"Section with ID {section_id} not found")

        # Get siblings for reordering
        if section.parent_id:
            siblings = DocumentSection.query.filter_by(
                document_id=section.document_id, parent_id=section.parent_id
            ).filter(DocumentSection.id != section_id).order_by(DocumentSection.position).all()
        else:
            siblings = DocumentSection.query.filter_by(
                document_id=section.document_id, parent_id=None
            ).filter(DocumentSection.id != section_id).order_by(DocumentSection.position).all()

        # Delete the section (cascades to children)
        db.session.delete(section)

        # Reorder remaining siblings
        for i, sibling in enumerate(siblings, 1):
            sibling.position = i

        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting section {section_id}: {str(e)}")
        raise SectionError(f"Failed to delete section: {str(e)}")


def move_section(section_id, new_parent_id=None, new_position=None):
    """Move a section to a new parent and/or position"""
    try:
        section = DocumentSection.query.get(section_id)
        if not section:
            raise SectionError(f"Section with ID {section_id} not found")

        old_parent_id = section.parent_id

        # Check if new parent is valid (not itself or its descendant)
        if new_parent_id is not None and new_parent_id != old_parent_id:
            if new_parent_id == section_id:
                raise SectionError("Cannot make a section its own parent")

            # Check if new parent is a descendant
            parent = DocumentSection.query.get(new_parent_id)
            if parent:
                current_parent_id = parent.parent_id
                while current_parent_id:
                    if current_parent_id == section_id:
                        raise SectionError("Cannot make a section a child of its descendant")
                    current_parent = DocumentSection.query.get(current_parent_id)
                    current_parent_id = current_parent.parent_id if current_parent else None

        # Update parent and reorder sections
        if new_parent_id is not None and new_parent_id != old_parent_id:
            # Remove from old parent's children ordering
            if old_parent_id:
                old_siblings = DocumentSection.query.filter_by(
                    document_id=section.document_id, parent_id=old_parent_id
                ).filter(DocumentSection.id != section_id).order_by(DocumentSection.position).all()
                # Reorder old siblings
                for i, sibling in enumerate(old_siblings, 1):
                    sibling.position = i
            else:
                old_siblings = DocumentSection.query.filter_by(
                    document_id=section.document_id, parent_id=None
                ).filter(DocumentSection.id != section_id).order_by(DocumentSection.position).all()
                # Reorder old siblings
                for i, sibling in enumerate(old_siblings, 1):
                    sibling.position = i

            # Update parent
            section.parent_id = new_parent_id

            # Determine new position
            if new_position is None:
                if new_parent_id:
                    highest = DocumentSection.query.filter_by(
                        document_id=section.document_id, parent_id=new_parent_id
                    ).order_by(DocumentSection.position.desc()).first()
                else:
                    highest = DocumentSection.query.filter_by(
                        document_id=section.document_id, parent_id=None
                    ).order_by(DocumentSection.position.desc()).first()

                new_position = 1 if highest is None else highest.position + 1

        # Update position if specified
        if new_position is not None:
            if new_parent_id == old_parent_id:
                # Same parent, just reorder
                reorder_sections(section.document_id, section.parent_id, section.id, new_position)
            else:
                # New parent, insert at position
                if new_parent_id:
                    new_siblings = DocumentSection.query.filter_by(
                        document_id=section.document_id, parent_id=new_parent_id
                    ).order_by(DocumentSection.position).all()
                else:
                    new_siblings = DocumentSection.query.filter_by(
                        document_id=section.document_id, parent_id=None
                    ).order_by(DocumentSection.position).all()

                # Insert at new position
                new_position = max(1, min(new_position, len(new_siblings) + 1))
                section.position = new_position

                # Shift other positions
                for sibling in new_siblings:
                    if sibling.position >= new_position:
                        sibling.position += 1

        section.modified_date = datetime.datetime.utcnow()
        db.session.commit()
        return section
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error moving section {section_id}: {str(e)}")
        raise SectionError(f"Failed to move section: {str(e)}")


def lock_section(section_id, user_id, duration_minutes=15):
    """Lock a section for editing by a user"""
    try:
        # Clear any expired locks
        clear_expired_locks()

        # Check for existing lock
        existing_lock = SectionLock.query.filter_by(section_id=section_id).first()
        if existing_lock:
            if existing_lock.user_id != user_id:
                raise SectionError(
                    f"Section is already locked by another user until {existing_lock.expires_at.isoformat()}"
                )
            # Extend existing lock
            existing_lock.expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=duration_minutes)
            db.session.commit()
            return existing_lock

        # Create new lock
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=duration_minutes)
        lock = SectionLock(
            section_id=section_id,
            user_id=user_id,
            locked_at=datetime.datetime.utcnow(),
            expires_at=expires_at
        )
        db.session.add(lock)
        db.session.commit()
        return lock
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error locking section {section_id}: {str(e)}")
        raise SectionError(f"Failed to lock section: {str(e)}")


def unlock_section(section_id, user_id):
    """Release a lock on a section"""
    try:
        lock = SectionLock.query.filter_by(section_id=section_id, user_id=user_id).first()
        if lock:
            db.session.delete(lock)
            db.session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error unlocking section {section_id}: {str(e)}")
        raise SectionError(f"Failed to unlock section: {str(e)}")


def clear_expired_locks():
    """Remove all expired locks"""
    try:
        now = datetime.datetime.utcnow()
        expired_locks = SectionLock.query.filter(SectionLock.expires_at < now).all()
        for lock in expired_locks:
            db.session.delete(lock)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error clearing expired locks: {str(e)}")


def get_section_revisions(section_id):
    """Get revision history for a section"""
    try:
        revisions = SectionRevision.query.filter_by(section_id=section_id).order_by(
            SectionRevision.created_at.desc()).all()
        return revisions
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error retrieving revisions for section {section_id}: {str(e)}")
        raise SectionError(f"Failed to retrieve section revisions: {str(e)}")
