# migrations/add_literature_search_tables.py

"""
Add literature search tables to the database.
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# Revision identifiers
revision = 'xxxx'  # Replace with a unique identifier
down_revision = 'yyyy'  # Replace with previous migration identifier
branch_labels = None
depends_on = None


def upgrade():
    # Papers table
    op.create_table(
        'papers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('authors', sa.Text(), nullable=True),
        sa.Column('abstract', sa.Text(), nullable=True),
        sa.Column('doi', sa.String(100), nullable=True),
        sa.Column('url', sa.String(500), nullable=True),
        sa.Column('journal', sa.String(255), nullable=True),
        sa.Column('published_date', sa.DateTime(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('source_db', sa.String(100), nullable=True),
        sa.Column('paper_id', sa.String(100), nullable=True),
        sa.Column('full_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('doi')
    )
    op.create_index('idx_papers_doi', 'papers', ['doi'])
    op.create_index('idx_papers_source_paper_id', 'papers', ['source_db', 'paper_id'])

    # Citations table
    op.create_table(
        'citations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('paper_id', sa.Integer(), nullable=True),
        sa.Column('cited_paper_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['paper_id'], ['papers.id']),
        sa.ForeignKeyConstraint(['cited_paper_id'], ['papers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_citations_paper_id', 'citations', ['paper_id'])
    op.create_index('idx_citations_cited_paper_id', 'citations', ['cited_paper_id'])

    # Keywords table
    op.create_table(
        'keywords',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('keyword', sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('keyword')
    )
    op.create_index('idx_keywords_keyword', 'keywords', ['keyword'])

    # Collections table
    op.create_table(
        'collections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_collections_user_id', 'collections', ['user_id'])

    # Paper-Keywords association table
    op.create_table(
        'paper_keywords',
        sa.Column('paper_id', sa.Integer(), nullable=True),
        sa.Column('keyword_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['paper_id'], ['papers.id']),
        sa.ForeignKeyConstraint(['keyword_id'], ['keywords.id']),
        sa.UniqueConstraint('paper_id', 'keyword_id')
    )

    # Paper-Collections association table
    op.create_table(
        'paper_collections',
        sa.Column('paper_id', sa.Integer(), nullable=True),
        sa.Column('collection_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['paper_id'], ['papers.id']),
        sa.ForeignKeyConstraint(['collection_id'], ['collections.id']),
        sa.UniqueConstraint('paper_id', 'collection_id')
    )

    # Search queries table
    op.create_table(
        'search_queries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('query', sa.String(500), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('source_db', sa.String(100), nullable=True),
        sa.Column('results_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_search_queries_user_id', 'search_queries', ['user_id'])


def downgrade():
    op.drop_table('search_queries')
    op.drop_table('paper_collections')
    op.drop_table('paper_keywords')
    op.drop_table('collections')
    op.drop_table('keywords')
    op.drop_table('citations')
    op.drop_table('papers')

