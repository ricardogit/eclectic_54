# modules/literature_search/api_clients.py (update)
import requests
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import time
from typing import List, Dict, Any, Optional, Union

# Add these imports at the top
from modules.literature_search.cache import APICache
from modules.literature_search.config import LiteratureSearchConfig


# Update the BaseSearchClient class
class BaseSearchClient:
    """Base class for scientific database search clients."""

    def __init__(self):
        self.name = "base"
        self.cache = APICache(
            cache_dir=LiteratureSearchConfig.CACHE_DIR,
            timeout_seconds=LiteratureSearchConfig.CACHE_TIMEOUT
        ) if LiteratureSearchConfig.CACHE_ENABLED else None

    def search(self, query: str, max_results: int = 25) -> List[Dict[str, Any]]:
        """Search for papers matching query."""
        raise NotImplementedError("Subclasses must implement search method")

    def get_paper(self, paper_id: str) -> Dict[str, Any]:
        """Get details for a specific paper."""
        raise NotImplementedError("Subclasses must implement get_paper method")

    def format_paper(self, paper_data: Any) -> Dict[str, Any]:
        """Format paper data to a standard structure."""
        raise NotImplementedError("Subclasses must implement format_paper method")


class ArxivClient(BaseSearchClient):
    """Client for searching arXiv."""

    def __init__(self):
        super().__init__()
        self.name = "arxiv"
        self.base_url = "http://export.arxiv.org/api/query"

    def search(self, query: str, max_results: int = 25) -> List[Dict[str, Any]]:
        """Search for papers on arXiv."""
        try:
            # Encode query parameters
            params = {
                'search_query': query,
                'max_results': max_results,
                'sortBy': 'relevance'
            }

            # Send request to arXiv API
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.content)

            # Extract papers
            papers = []

            # Define namespace mapping (arXiv uses Atom)
            ns = {'atom': 'http://www.w3.org/2005/Atom',
                  'arxiv': 'http://arxiv.org/schemas/atom'}

            # Find all entries
            for entry in root.findall('.//atom:entry', ns):
                try:
                    paper = self.format_paper(entry, ns)
                    papers.append(paper)
                except Exception as e:
                    print(f"Error formatting arXiv paper: {e}")
                    # Continue with next paper
                    continue

            return papers
        except ET.ParseError as e:
            print(f"Error parsing arXiv XML: {e}")
            return []
        except requests.RequestException as e:
            print(f"Error connecting to arXiv API: {e}")
            return []
        except Exception as e:
            print(f"Error searching arxiv: {e}")
            return []

    def get_paper(self, paper_id: str) -> Dict[str, Any]:
        """Get a specific paper from arXiv."""
        # Encode query parameters
        params = {
            'id_list': paper_id
        }

        # Send request to arXiv API
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()

        # Parse XML response
        root = ET.fromstring(response.content)

        # Define namespace mapping
        ns = {'atom': 'http://www.w3.org/2005/Atom',
              'arxiv': 'http://arxiv.org/schemas/atom'}

        # Find entry
        entry = root.find('.//atom:entry', ns)
        if entry is None:
            raise ValueError(f"Paper with ID {paper_id} not found")

        return self.format_paper(entry, ns)

    def format_paper(self, entry: ET.Element, ns: Dict[str, str]) -> Dict[str, Any]:
        """Format arXiv paper data to standard structure."""
        # Extract basic information with error handling
        title_elem = entry.find('./atom:title', ns)
        title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Unknown Title"

        summary_elem = entry.find('./atom:summary', ns)
        summary = summary_elem.text.strip() if summary_elem is not None and summary_elem.text else ""

        # Extract authors with error handling
        authors = []
        for author_elem in entry.findall('./atom:author', ns):
            name_elem = author_elem.find('./atom:name', ns)
            if name_elem is not None and name_elem.text:
                authors.append(name_elem.text.strip())

        # Extract link with error handling
        url = None
        links = entry.findall('./atom:link', ns)
        for link in links:
            if link.get('rel') == 'alternate':
                url = link.get('href')
                break

        # Extract arXiv ID and categories with error handling
        arxiv_id_elem = entry.find('./arxiv:id', ns)
        arxiv_id = arxiv_id_elem.text.strip() if arxiv_id_elem is not None and arxiv_id_elem.text else None

        categories = []
        for category in entry.findall('./arxiv:category', ns):
            cat_term = category.get('term')
            if cat_term:
                categories.append(cat_term)

        # Extract published date with error handling
        published_date = None
        year = None
        published_elem = entry.find('./atom:published', ns)
        if published_elem is not None and published_elem.text:
            try:
                published_str = published_elem.text.strip()
                published_date = datetime.strptime(published_str, '%Y-%m-%dT%H:%M:%SZ')
                year = published_date.year
            except (ValueError, TypeError):
                # If date parsing fails, use current date
                published_date = datetime.utcnow()
                year = published_date.year

        # Create formatted paper with safe defaults
        paper = {
            'title': title,
            'authors': ', '.join(authors) if authors else "Unknown Authors",
            'abstract': summary,
            'doi': None,  # arXiv doesn't provide DOI directly
            'url': url,
            'journal': 'arXiv',
            'published_date': published_date,
            'year': year,
            'source_db': 'arxiv',
            'paper_id': arxiv_id,
            'categories': categories,
            'full_text': None  # We don't get full text from the API
        }

        return paper

class PubMedClient(BaseSearchClient):
    """Client for searching PubMed."""

    def __init__(self, email: str = "app@example.com", tool: str = "literature_search"):
        super().__init__()
        self.name = "pubmed"
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = email
        self.tool = tool

    def search(self, query: str, max_results: int = 25) -> List[Dict[str, Any]]:
        """Search for papers on PubMed."""
        # First, use esearch to get paper IDs
        search_url = f"{self.base_url}/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'sort': 'relevance',
            'retmode': 'json',
            'email': self.email,
            'tool': self.tool
        }

        response = requests.get(search_url, params=params)
        response.raise_for_status()
        search_data = response.json()

        # Extract paper IDs
        paper_ids = search_data['esearchresult']['idlist']

        if not paper_ids:
            return []

        # Next, use efetch to get paper details
        papers = []

        # Fetch in batches to avoid large requests
        batch_size = 50
        for i in range(0, len(paper_ids), batch_size):
            batch_ids = paper_ids[i:i + batch_size]

            fetch_url = f"{self.base_url}/efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': ','.join(batch_ids),
                'retmode': 'xml',
                'email': self.email,
                'tool': self.tool
            }

            response = requests.get(fetch_url, params=params)
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.content)

            # Extract papers
            for article in root.findall('.//PubmedArticle'):
                paper = self.format_paper(article)
                papers.append(paper)

            # Be nice to the API
            time.sleep(0.34)  # NCBI allows 3 requests per second

        return papers

    def get_paper(self, paper_id: str) -> Dict[str, Any]:
        """Get a specific paper from PubMed."""
        fetch_url = f"{self.base_url}/efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': paper_id,
            'retmode': 'xml',
            'email': self.email,
            'tool': self.tool
        }

        response = requests.get(fetch_url, params=params)
        response.raise_for_status()

        # Parse XML response
        root = ET.fromstring(response.content)

        # Find article
        article = root.find('.//PubmedArticle')
        if article is None:
            raise ValueError(f"Paper with ID {paper_id} not found")

        return self.format_paper(article)

    def format_paper(self, article: ET.Element) -> Dict[str, Any]:
        """Format PubMed paper data to standard structure."""
        # Extract basic information
        try:
            title_elem = article.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else "No title"

            # Extract abstract
            abstract_parts = article.findall('.//AbstractText')
            abstract = ''
            for part in abstract_parts:
                label = part.get('Label')
                if label:
                    abstract += f"{label}: {part.text}\n"
                else:
                    abstract += f"{part.text}\n"

            # Extract authors
            authors = []
            author_list = article.find('.//AuthorList')
            if author_list is not None:
                for author in author_list.findall('.//Author'):
                    last_name = author.find('./LastName')
                    fore_name = author.find('./ForeName')
                    initials = author.find('./Initials')

                    name_parts = []
                    if last_name is not None and last_name.text:
                        name_parts.append(last_name.text)
                    if fore_name is not None and fore_name.text:
                        name_parts.append(fore_name.text)
                    elif initials is not None and initials.text:
                        name_parts.append(initials.text)

                    if name_parts:
                        authors.append(' '.join(name_parts))

            # Extract journal info
            journal_elem = article.find('.//Journal/Title')
            journal = journal_elem.text if journal_elem is not None else "Unknown Journal"

            # Extract published date
            published_date = None
            year = None

            pub_date = article.find('.//PubDate')
            if pub_date is not None:
                year_elem = pub_date.find('./Year')
                if year_elem is not None and year_elem.text:
                    year = int(year_elem.text)

                month_elem = pub_date.find('./Month')
                month = month_elem.text if month_elem is not None else '01'

                day_elem = pub_date.find('./Day')
                day = day_elem.text if day_elem is not None else '01'

                # Try to parse the date
                try:
                    if month.isdigit() and day.isdigit():
                        published_date = datetime(int(year), int(month), int(day))
                    else:
                        # Handle month as text
                        month_dict = {
                            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                        }
                        month_num = month_dict.get(month[:3], 1)
                        published_date = datetime(int(year), month_num, int(day))
                except (ValueError, TypeError):
                    # If we can't parse the date, use a default
                    if year:
                        published_date = datetime(int(year), 1, 1)

            # Extract DOI
            doi = None
            article_id_list = article.find('.//ArticleIdList')
            if article_id_list is not None:
                for article_id in article_id_list.findall('.//ArticleId'):
                    if article_id.get('IdType') == 'doi':
                        doi = article_id.text
                        break

            # Extract PubMed ID
            pmid = None
            if article_id_list is not None:
                for article_id in article_id_list.findall('.//ArticleId'):
                    if article_id.get('IdType') == 'pubmed':
                        pmid = article_id.text
                        break

            # Create URL
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None

            # Create formatted paper
            paper = {
                'title': title,
                'authors': ', '.join(authors),
                'abstract': abstract.strip(),
                'doi': doi,
                'url': url,
                'journal': journal,
                'published_date': published_date,
                'year': year,
                'source_db': 'pubmed',
                'paper_id': pmid,
                'full_text': None  # We don't get full text from the API
            }

            return paper

        except Exception as e:
            # If there's an error parsing, return a minimal paper with error info
            return {
                'title': 'Error parsing paper',
                'authors': '',
                'abstract': f'Error parsing paper: {str(e)}',
                'doi': None,
                'url': None,
                'journal': 'Error',
                'published_date': None,
                'year': None,
                'source_db': 'pubmed',
                'paper_id': article.get('uid', 'unknown'),
                'full_text': None
            }


class SearchClientFactory:
    """Factory for creating search clients."""

    @staticmethod
    def get_client(source: str) -> BaseSearchClient:
        """Get a search client for the specified source."""
        if source == 'arxiv':
            return ArxivClient()
        elif source == 'pubmed':
            return PubMedClient()
        elif source == 'all':
            return MultiSourceClient()
        else:
            raise ValueError(f"Unsupported source: {source}")


class MultiSourceClient(BaseSearchClient):
    """Client that searches multiple sources."""

    def __init__(self):
        super().__init__()
        self.name = "all"
        self.clients = [
            ArxivClient(),
            PubMedClient()
        ]

    def search(self, query: str, max_results: int = 25) -> List[Dict[str, Any]]:
        """Search for papers across all sources."""
        # Distribute max_results across clients
        per_client = max(5, max_results // len(self.clients))

        all_papers = []
        for client in self.clients:
            try:
                papers = client.search(query, per_client)
                all_papers.extend(papers)
            except Exception as e:
                print(f"Error searching {client.name}: {e}")

        # Sort by relevance (assuming more recent papers are more relevant)
        all_papers.sort(key=lambda p: p.get('published_date', datetime.min), reverse=True)

        # Return up to max_results
        return all_papers[:max_results]

    def get_paper(self, paper_id: str) -> Dict[str, Any]:
        """Get a paper by ID."""
        # Paper ID should include source prefix, e.g., 'arxiv:1234.5678'
        parts = paper_id.split(':', 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid paper ID format: {paper_id}, expected format: 'source:id'")

        source, id_part = parts

        for client in self.clients:
            if client.name == source:
                return client.get_paper(id_part)

        raise ValueError(f"Unsupported source: {source}")
