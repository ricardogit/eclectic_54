import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, func, Table
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
from sqlalchemy.types import TypeDecorator, TEXT

# Initialize SQLAlchemy
db = SQLAlchemy()

# Custom JSON type for storing preferences
class JSONType(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            return '{}'
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return {}
        return json.loads(value)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    full_name = Column(Text, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    a_password = Column(Text, nullable=False)
    created_date = Column(DateTime, default=func.current_timestamp())
    # Add these new fields
    preferences = db.Column(JSONType, default=lambda: {
        'theme': 'light',
        'editor_preferences': ['autosave', 'spellcheck', 'wordcount'],
        'citation_style': 'apa'
    })


    # Relationships
    documents = relationship('Document', back_populates='owner')
    collaborations = relationship('DocumentCollaborator', back_populates='user')
    collections = relationship('Collection', back_populates='user')

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.a_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.a_password, password)

    # Add properties for easy access to preferences
    @property
    def theme(self):
        return self.preferences.get('theme', 'light')

    @property
    def editor_preferences(self):
        return self.preferences.get('editor_preferences', ['autosave', 'spellcheck', 'wordcount'])

    @property
    def citation_style(self):
        return self.preferences.get('citation_style', 'apa')


class Document(db.Model):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(20), default='draft')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Collaboration fields
    collaboration_enabled = Column(Boolean, default=False)
    last_collaboration = Column(DateTime)

    # Relationships
    owner = relationship('User', back_populates='documents')
    sections = relationship('DocumentSection', back_populates='document',
                            cascade='all, delete-orphan')
    collaborators = relationship('DocumentCollaborator', back_populates='document',
                                 cascade='all, delete-orphan')
    sessions = relationship('CollaborationSession', back_populates='document',
                            cascade='all, delete-orphan')


class DocumentSection(db.Model):
    __tablename__ = 'document_sections'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    position = Column(Integer, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                           nullable=False)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('document_sections.id'))

    # Relationships
    document = relationship('Document', back_populates='sections')
    children = relationship('DocumentSection',
                            backref=db.backref('parent', remote_side=[id]),
                            cascade='all, delete-orphan')
    locks = relationship('SectionLock', back_populates='section',
                         cascade='all, delete-orphan')
    revisions = relationship('SectionRevision', back_populates='section',
                             cascade='all, delete-orphan')


class DocumentCollaborator(db.Model):
    __tablename__ = 'document_collaborators'

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id'))
    permission_level = Column(String(20), default='view')  # view, comment, edit
    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="collaborators")
    user = relationship("User", back_populates="collaborations")

    def __repr__(self):
        return f"<DocumentCollaborator(document_id={self.document_id}, user_id={self.user_id})>"


class SectionLock(db.Model):
    __tablename__ = 'section_locks'

    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey('document_sections.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    locked_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    # Relationships
    section = relationship('DocumentSection', back_populates='locks')
    user = relationship('User')


class SectionRevision(db.Model):
    __tablename__ = 'section_revisions'

    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey('document_sections.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    section = relationship('DocumentSection', back_populates='revisions')
    user = relationship('User')


class CollaborationSession(db.Model):
    __tablename__ = 'collaboration_sessions'

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)

    # Relationships
    document = relationship('Document', back_populates='sessions')
    user = relationship('User')

# If you're using SQLAlchemy with your models like this:
# db = SQLAlchemy()
# class User(db.Model, UserMixin):
#    ...

# Paper Search models
class Paper(db.Model):
    """Model for scientific papers."""
    __tablename__ = 'papers'

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    authors = Column(Text)
    abstract = Column(Text)
    doi = Column(String(100), index=True, unique=True)
    url = Column(String(500))
    journal = Column(String(255))
    published_date = Column(DateTime)
    year = Column(Integer)
    source_db = Column(String(100))  # arxiv, pubmed, scopus, etc.
    paper_id = Column(String(100))  # ID in the original database
    full_text = Column(Text)  # If we have the full text

    # Relationships - FIX HERE: Specify which foreign key to use
    citations = relationship('Citation', back_populates='paper', foreign_keys='Citation.paper_id')
    # Add reverse relationship for papers that cite this paper
    cited_by = relationship('Citation', foreign_keys='Citation.cited_paper_id')
    keywords = relationship('Keyword', secondary='paper_keywords')
    collections = relationship('Collection', secondary='paper_collections')

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Paper {self.title[:30]}...>"


class Citation(db.Model):
    """Model for paper citations."""
    __tablename__ = 'citations'

    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, ForeignKey('papers.id'))
    cited_paper_id = Column(Integer, ForeignKey('papers.id'))

    # Relationship
    paper = relationship('Paper', foreign_keys=[paper_id], back_populates='citations')
    cited_paper = relationship('Paper', foreign_keys=[cited_paper_id], back_populates='cited_by')


class Keyword(db.Model):
    """Model for paper keywords."""
    __tablename__ = 'keywords'

    id = Column(Integer, primary_key=True)
    keyword = Column(String(100), index=True, unique=True)

    def __repr__(self):
        return f"<Keyword {self.keyword}>"


# Association table for papers and keywords
paper_keywords = Table('paper_keywords', db.metadata,
                       Column('paper_id', Integer, ForeignKey('papers.id')),
                       Column('keyword_id', Integer, ForeignKey('keywords.id'))
                       )


class Collection(db.Model):
    """Model for paper collections/projects."""
    __tablename__ = 'collections'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))

    # Relationships
    user = relationship('User', back_populates='collections')

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Collection {self.name}>"


# Association table for papers and collections
paper_collections = Table('paper_collections', db.metadata,
                          Column('paper_id', Integer, ForeignKey('papers.id')),
                          Column('collection_id', Integer, ForeignKey('collections.id'))
                          )


class SearchQuery(db.Model):
    """Model to store search history."""
    __tablename__ = 'search_queries'

    id = Column(Integer, primary_key=True)
    query = Column(String(500), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    source_db = Column(String(100))  # 'all', 'arxiv', 'pubmed', etc.
    results_count = Column(Integer, default=0)

    # Relationship
    user = relationship('User')

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SearchQuery {self.query}>"

from datetime import datetime

# Add these classes to your models.py file

class AIProvider(db.Model):
    __tablename__ = 'ai_providers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider = db.Column(db.String(50), nullable=False)
    api_key = db.Column(db.String(255), nullable=False)  # Store encrypted in production
    is_paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('ai_providers', lazy=True))

    def __repr__(self):
        return f'<AIProvider {self.provider}>'


class ScientificDatabase(db.Model):
    __tablename__ = 'scientific_databases'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    database_name = db.Column(db.String(50), nullable=False)
    api_key = db.Column(db.String(255), nullable=False)  # Store encrypted in production
    is_institutional = db.Column(db.Boolean, default=False)
    institution = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('scientific_databases', lazy=True))

    def __repr__(self):
        return f'<ScientificDatabase {self.database_name}>'
