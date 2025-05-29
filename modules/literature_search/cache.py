# modules/literature_search/cache.py

import hashlib
import json
import os
import pickle
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple


class APICache:
    """Simple cache for API responses."""

    def __init__(self, cache_dir="./cache", timeout_seconds=3600):
        """
        Initialize the cache.

        Args:
            cache_dir: Directory to store cache files
            timeout_seconds: Time before cache entries expire
        """
        self.cache_dir = cache_dir
        self.timeout = timeout_seconds

        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """
        Generate a unique cache key for the API request.

        Args:
            endpoint: API endpoint
            params: Request parameters

        Returns:
            A unique hash for the request
        """
        # Sort params to ensure consistent hashing
        param_str = json.dumps(params, sort_keys=True)

        # Generate hash
        key = f"{endpoint}:{param_str}"
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> str:
        """
        Get the file path for a cache key.

        Args:
            key: Cache key

        Returns:
            Path to the cache file
        """
        return os.path.join(self.cache_dir, f"{key}.cache")

    def get(self, endpoint: str, params: Dict[str, Any]) -> Optional[Any]:
        """
        Get a cached response if available and not expired.

        Args:
            endpoint: API endpoint
            params: Request parameters

        Returns:
            Cached response or None if not found or expired
        """
        key = self._get_cache_key(endpoint, params)
        path = self._get_cache_path(key)

        # Check if cache file exists
        if not os.path.exists(path):
            return None

        try:
            # Load cache data
            with open(path, "rb") as f:
                timestamp, data = pickle.load(f)

            # Check if cache is expired
            if datetime.utcnow() - timestamp > timedelta(seconds=self.timeout):
                return None

            return data
        except Exception:
            # If there's any error reading the cache, return None
            return None

    def set(self, endpoint: str, params: Dict[str, Any], data: Any) -> None:
        """
        Cache a response.

        Args:
            endpoint: API endpoint
            params: Request parameters
            data: Response data to cache
        """
        key = self._get_cache_key(endpoint, params)
        path = self._get_cache_path(key)

        try:
            # Save cache data with timestamp
            with open(path, "wb") as f:
                pickle.dump((datetime.utcnow(), data), f)
        except Exception as e:
            # Log error but continue
            print(f"Error caching response: {e}")
            