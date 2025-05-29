import datetime
from flask import current_app
from flask_socketio import emit, join_room, leave_room
from models import db, Document, DocumentSection, SectionLock, CollaborationSession
from sqlalchemy.exc import SQLAlchemyError


def init_socketio(socketio):
    """Initialize SocketIO event handlers"""

    @socketio.on('connect')
    def handle_connect():
        current_app.logger.info('Client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        current_app.logger.info('Client disconnected')
        # Handle any cleanup needed

    @socketio.on('join_document')
    def handle_join_document(data):
        """Handle a user joining a document session"""
        document_id = data.get('document_id')
        user_id = data.get('user_id')

        if not document_id or not user_id:
            emit('error', {'message': 'Missing document_id or user_id'})
            return

        try:
            # Create or update collaboration session
            session = CollaborationSession.query.filter_by(
                document_id=document_id, user_id=user_id, ended_at=None
            ).first()

            if not session:
                session = CollaborationSession(
                    document_id=document_id,
                    user_id=user_id,
                    started_at=datetime.datetime.utcnow()
                )
                db.session.add(session)

                # Update document collaboration timestamp
                document = Document.query.get(document_id)
                document.last_collaboration = datetime.datetime.utcnow()

                db.session.commit()

            # Join the document room
            room = f'document_{document_id}'
            join_room(room)

            # Notify others about the new user
            emit('user_joined', {
                'user_id': user_id,
                'timestamp': datetime.datetime.utcnow().isoformat()
            }, room=room, include_self=False)

            # Return current active users
            active_sessions = CollaborationSession.query.filter_by(
                document_id=document_id, ended_at=None
            ).all()

            active_users = []
            for session in active_sessions:
                user = session.user
                active_users.append({
                    'user_id': user.id,
                    'full_name': user.full_name,
                    'joined_at': session.started_at.isoformat()
                })

            emit('document_users', {'users': active_users})

        except SQLAlchemyError as e:
            current_app.logger.error(f"Error in join_document: {str(e)}")
            db.session.rollback()
            emit('error', {'message': 'Database error'})

    @socketio.on('leave_document')
    def handle_leave_document(data):
        """Handle a user leaving a document session"""
        document_id = data.get('document_id')
        user_id = data.get('user_id')

        if not document_id or not user_id:
            emit('error', {'message': 'Missing document_id or user_id'})
            return

        try:
            # Update collaboration session
            session = CollaborationSession.query.filter_by(
                document_id=document_id, user_id=user_id, ended_at=None
            ).first()

            if session:
                session.ended_at = datetime.datetime.utcnow()
                db.session.commit()

            # Leave the document room
            room = f'document_{document_id}'
            leave_room(room)

            # Notify others
            emit('user_left', {
                'user_id': user_id,
                'timestamp': datetime.datetime.utcnow().isoformat()
            }, room=room)

        except SQLAlchemyError as e:
            current_app.logger.error(f"Error in leave_document: {str(e)}")
            db.session.rollback()
            emit('error', {'message': 'Database error'})

    @socketio.on('section_edit')
    def handle_section_edit(data):
        """Handle real-time section edits"""
        document_id = data.get('document_id')
        section_id = data.get('section_id')
        user_id = data.get('user_id')
        content = data.get('content')
        cursor_position = data.get('cursor_position')

        if not all([document_id, section_id, user_id]):
            emit('error', {'message': 'Missing required data'})
            return

        try:
            # Check if user has a lock on this section
            lock = SectionLock.query.filter_by(section_id=section_id, user_id=user_id).first()
            if not lock:
                emit('error', {'message': 'You do not have a lock on this section'})
                return

            # Broadcast the edit to other users
            room = f'document_{document_id}'
            emit('section_update', {
                'section_id': section_id,
                'user_id': user_id,
                'content': content,
                'cursor_position': cursor_position,
                'timestamp': datetime.datetime.utcnow().isoformat()
            }, room=room, include_self=False)

        except Exception as e:
            current_app.logger.error(f"Error in section_edit: {str(e)}")
            emit('error', {'message': 'Error processing edit'})

    @socketio.on('section_lock')
    def handle_section_lock(data):
        """Handle section locking"""
        document_id = data.get('document_id')
        section_id = data.get('section_id')
        user_id = data.get('user_id')

        if not all([document_id, section_id, user_id]):
            emit('error', {'message': 'Missing required data'})
            return

        try:
            # Check for existing locks
            existing_lock = SectionLock.query.filter_by(section_id=section_id).first()

            if existing_lock and existing_lock.user_id != user_id:
                # Section is locked by another user
                emit('lock_denied', {
                    'section_id': section_id,
                    'locked_by': existing_lock.user_id,
                    'expires_at': existing_lock.expires_at.isoformat()
                })
                return

            # Create or update lock
            if existing_lock:
                # Extend lock
                existing_lock.expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
                lock = existing_lock
            else:
                # Create new lock
                lock = SectionLock(
                    section_id=section_id,
                    user_id=user_id,
                    locked_at=datetime.datetime.utcnow(),
                    expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
                )
                db.session.add(lock)

            db.session.commit()

            # Notify all users about the lock
            room = f'document_{document_id}'
            emit('section_locked', {
                'section_id': section_id,
                'user_id': user_id,
                'expires_at': lock.expires_at.isoformat()
            }, room=room)

        except SQLAlchemyError as e:
            current_app.logger.error(f"Error in section_lock: {str(e)}")
            db.session.rollback()
            emit('error', {'message': 'Database error'})

    @socketio.on('section_unlock')
    def handle_section_unlock(data):
        """Handle section unlocking"""
        document_id = data.get('document_id')
        section_id = data.get('section_id')
        user_id = data.get('user_id')

        if not all([document_id, section_id, user_id]):
            emit('error', {'message': 'Missing required data'})
            return

        try:
            # Find and remove lock
            lock = SectionLock.query.filter_by(section_id=section_id, user_id=user_id).first()

            if lock:
                db.session.delete(lock)
                db.session.commit()

                # Notify all users
                room = f'document_{document_id}'
                emit('section_unlocked', {
                    'section_id': section_id,
                    'user_id': user_id
                }, room=room)

        except SQLAlchemyError as e:
            current_app.logger.error(f"Error in section_unlock: {str(e)}")
            db.session.rollback()
            emit('error', {'message': 'Database error'})

    @socketio.on('chat_message')
    def handle_chat_message(data):
        """Handle chat messages between collaborators"""
        document_id = data.get('document_id')
        user_id = data.get('user_id')
        message = data.get('message')

        if not all([document_id, user_id, message]):
            emit('error', {'message': 'Missing required data'})
            return

        # Broadcast message to all users in the document
        room = f'document_{document_id}'
        emit('new_message', {
            'user_id': user_id,
            'message': message,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }, room=room)
