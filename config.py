import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:postgres@localhost/dash_editor'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Login configuration
    REMEMBER_COOKIE_DURATION = 30  # days

    # Upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size

    # AI Assistant configuration
    AI_API_KEY = os.environ.get('AI_API_KEY')
    AI_ENDPOINT = os.environ.get('AI_ENDPOINT')

    # Collaboration configuration
    MAX_COLLABORATORS = 10

# Configuration for the Academic Draft Generator

# Journal styles and their requirements
JOURNAL_STYLES = {
    "general_scientific": {
        "name": "General Scientific Journal",
        "max_words": 5000,
        "citation_style": "APA",
        "sections": [
            "Abstract", "Introduction", "Literature Review", "Methodology",
            "Results", "Discussion", "Conclusion", "References"
        ]
    },
    "nature": {
        "name": "Nature",
        "max_words": 3000,
        "citation_style": "Nature",
        "sections": [
            "Abstract", "Introduction", "Results", "Discussion",
            "Methods", "References"
        ]
    },
    "ieee": {
        "name": "IEEE Transactions",
        "max_words": 8000,
        "citation_style": "IEEE",
        "sections": [
            "Abstract", "Introduction", "Related Work", "Methodology",
            "Experiments", "Results", "Discussion", "Conclusion", "References"
        ]
    },
    "acm": {
        "name": "ACM Computing",
        "max_words": 7000,
        "citation_style": "ACM",
        "sections": [
            "Abstract", "Introduction", "Background", "Approach",
            "Implementation", "Evaluation", "Discussion", "Related Work",
            "Conclusion", "References"
        ]
    },
    "plos": {
        "name": "PLOS",
        "max_words": 6000,
        "citation_style": "Vancouver",
        "sections": [
            "Abstract", "Introduction", "Materials and Methods",
            "Results", "Discussion", "Conclusion", "References"
        ]
    },
    "humanities": {
        "name": "Humanities Journal",
        "max_words": 8000,
        "citation_style": "Chicago",
        "sections": [
            "Abstract", "Introduction", "Literature Review", "Analysis",
            "Discussion", "Conclusion", "Notes", "Bibliography"
        ]
    }
}
