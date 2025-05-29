# modules/literature_search/config.py

"""Configuration for the literature search module."""


class LiteratureSearchConfig:
    # API configuration
    PUBMED_EMAIL = "your-email@example.com"
    PUBMED_TOOL = "your-app-name"

    # Results configuration
    DEFAULT_MAX_RESULTS = 25

    # Cache configuration
    CACHE_ENABLED = True
    CACHE_TIMEOUT = 3600  # 1 hour
    CACHE_DIR = "./cache/literature_search"
    