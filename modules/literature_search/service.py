# modules/literature_search/service.py

from typing import List, Dict, Any, Optional
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from models import db, Paper, Keyword, SearchQuery, Collection, paper_keywords, paper_collections
from modules.literature_search.api_clients import SearchClientFactory


class LiteratureSearchService:
    """Service for searching and managing scientific papers."""

    def __init__(self):
        self.search_factory = SearchClientFactory()

    def search_papers(self, query: str, source: str = 'all', max_results: int = 25,
                      user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for papers across specified sources.

        Args:
            query: The search query
            source: Which database to search ('all', 'arxiv', 'pubmed', etc.)
            max_results: Maximum number of results to return
            user_id: Optional user ID to associate with the search

        Returns:
            List of paper dictionaries
        """
        # Get the appropriate client
        client = self.search_factory.get_client(source)

        # Log the search query if user_id is provided
        if user_id:
            search_query = SearchQuery(
                query=query,
                user_id=user_id,
                source_db=source
            )
            db.session.add(search_query)
            db.session.commit()

        # Perform the search
        try:
            papers = client.search(query, max_results)

            # Update the search query with results count
            if user_id:
                search_query.results_count = len(papers)
                db.session.commit()

            return papers
        except Exception as e:
            # Log the error and re-raise
            print(f"Error searching {source}: {e}")
            if user_id:
                search_query.results_count = 0
                db.session.commit()
            raise

    def get_paper(self, paper_id: str, source: str) -> Dict[str, Any]:
        """
        Get details for a specific paper.

        Args:
            paper_id: The ID of the paper
            source: The source database

        Returns:
            Paper details dictionary
        """
        # Get the appropriate client
        client = self.search_factory.get_client(source)

        # Get the paper
        return client.get_paper(paper_id)

    def save_paper(self, paper_data: Dict[str, Any], user_id: int) -> Paper:
        """
        Save a paper to the database.

        Args:
            paper_data: Paper data dictionary
            user_id: User ID to associate with the paper

        Returns:
            Saved Paper object
        """
        # Check if paper already exists
        existing_paper = None
        if paper_data.get('doi'):
            existing_paper = Paper.query.filter_by(doi=paper_data['doi']).first()
        elif paper_data.get('paper_id') and paper_data.get('source_db'):
            existing_paper = Paper.query.filter_by(
                paper_id=paper_data['paper_id'],
                source_db=paper_data['source_db']
            ).first()

        if existing_paper:
            return existing_paper

        # Create new paper
        new_paper = Paper(
            title=paper_data['title'],
            authors=paper_data.get('authors', ''),
            abstract=paper_data.get('abstract', ''),
            doi=paper_data.get('doi'),
            url=paper_data.get('url'),
            journal=paper_data.get('journal', ''),
            published_date=paper_data.get('published_date'),
            year=paper_data.get('year'),
            source_db=paper_data.get('source_db', ''),
            paper_id=paper_data.get('paper_id', ''),
            full_text=paper_data.get('full_text')
        )

        # Add keywords if present
        if 'keywords' in paper_data and paper_data['keywords']:
            keywords = paper_data['keywords']
            if isinstance(keywords, str):
                keywords = [k.strip() for k in keywords.split(',')]

            for keyword_text in keywords:
                keyword = Keyword.query.filter_by(keyword=keyword_text).first()
                if not keyword:
                    keyword = Keyword(keyword=keyword_text)
                    db.session.add(keyword)
                new_paper.keywords.append(keyword)

        # Add categories as keywords if present (for arXiv papers)
        if 'categories' in paper_data and paper_data['categories']:
            for category in paper_data['categories']:
                keyword = Keyword.query.filter_by(keyword=category).first()
                if not keyword:
                    keyword = Keyword(keyword=category)
                    db.session.add(keyword)
                if keyword not in new_paper.keywords:
                    new_paper.keywords.append(keyword)

        # Save to database
        db.session.add(new_paper)
        try:
            db.session.commit()
            return new_paper
        except IntegrityError:
            db.session.rollback()
            # If there was an integrity error, the paper might have been added by another process
            # Try to find it again
            if paper_data.get('doi'):
                return Paper.query.filter_by(doi=paper_data['doi']).first()
            elif paper_data.get('paper_id') and paper_data.get('source_db'):
                return Paper.query.filter_by(
                    paper_id=paper_data['paper_id'],
                    source_db=paper_data['source_db']
                ).first()
            else:
                # If we can't find a unique identifier, just create a new entry
                new_paper = Paper(
                    title=paper_data['title'],
                    authors=paper_data.get('authors', ''),
                    abstract=paper_data.get('abstract', ''),
                    # Generate a unique DOI-like identifier
                    paper_id=f"local-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    source_db='local'
                )
                db.session.add(new_paper)
                db.session.commit()
                return new_paper

    def add_paper_to_collection(self, paper_id: int, collection_id: int) -> bool:
        """
        Add a paper to a collection.

        Args:
            paper_id: Paper ID
            collection_id: Collection ID

        Returns:
            True if successful, False otherwise
        """
        # Check if paper and collection exist
        paper = Paper.query.get(paper_id)
        collection = Collection.query.get(collection_id)

        if not paper or not collection:
            return False

        # Check if paper is already in collection
        if collection in paper.collections:
            return True

        # Add paper to collection
        paper.collections.append(collection)

        # Save to database
        try:
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    def remove_paper_from_collection(self, paper_id: int, collection_id: int) -> bool:
        """
        Remove a paper from a collection.

        Args:
            paper_id: Paper ID
            collection_id: Collection ID

        Returns:
            True if successful, False otherwise
        """
        # Check if paper and collection exist
        paper = Paper.query.get(paper_id)
        collection = Collection.query.get(collection_id)

        if not paper or not collection:
            return False

        # Check if paper is in collection
        if collection not in paper.collections:
            return True

        # Remove paper from collection
        paper.collections.remove(collection)

        # Save to database
        try:
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    def create_collection(self, name: str, description: str, user_id: int) -> Collection:
        """
        Create a new collection.

        Args:
            name: Collection name
            description: Collection description
            user_id: User ID to associate with the collection

        Returns:
            Created Collection object
        """
        # Create new collection
        collection = Collection(
            name=name,
            description=description,
            user_id=user_id
        )

        # Save to database
        db.session.add(collection)
        db.session.commit()

        return collection

    def get_user_collections(self, user_id: int) -> List[Collection]:
        """
        Get all collections for a user.

        Args:
            user_id: User ID

        Returns:
            List of Collection objects
        """
        return Collection.query.filter_by(user_id=user_id).all()

    def get_collection_papers(self, collection_id: int) -> List[Paper]:
        """
        Get all papers in a collection.

        Args:
            collection_id: Collection ID

        Returns:
            List of Paper objects
        """
        collection = Collection.query.get(collection_id)
        if not collection:
            return []

        # Query for papers in this collection using the association table
        papers = db.session.query(Paper). \
            join(paper_collections). \
            filter(paper_collections.c.collection_id == collection_id). \
            all()

        return papers

    def get_user_recent_searches(self, user_id: int, limit: int = 10) -> List[SearchQuery]:
        """
        Get recent searches for a user.

        Args:
            user_id: User ID
            limit: Maximum number of searches to return

        Returns:
            List of SearchQuery objects
        """
        # Fix the query access - use db.session.query instead of model.query
        return db.session.query(SearchQuery).filter(SearchQuery.user_id == user_id). \
            order_by(SearchQuery.created_at.desc()). \
            limit(limit). \
            all()
