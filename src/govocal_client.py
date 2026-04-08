import time

import requests
from tqdm import tqdm

from src import config


class GoVocalClient:
    """Client for the GoVocal public REST API (v2)."""

    MAX_PAGE_SIZE = 24  # API-enforced maximum

    def __init__(self, base_url=None, client_id=None, client_secret=None):
        self.base_url = (base_url or config.GOVOCAL_BASE_URL).rstrip("/")
        self._client_id = client_id or config.GOVOCAL_CLIENT_ID
        self._client_secret = client_secret or config.GOVOCAL_CLIENT_SECRET
        self._jwt = None
        self._jwt_obtained_at = 0.0
        self._session = requests.Session()

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate(self):
        """Obtain a JWT token. Tokens expire after 24 h."""
        resp = self._session.post(
            f"{self.base_url}/api/v2/authenticate",
            json={
                "auth": {
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                }
            },
            timeout=30,
        )
        resp.raise_for_status()
        self._jwt = resp.json()["jwt"]
        self._jwt_obtained_at = time.time()
        self._session.headers["Authorization"] = f"Bearer {self._jwt}"

    def _ensure_auth(self):
        """Re-authenticate if we don't have a token or it's older than 23 h."""
        if self._jwt is None or (time.time() - self._jwt_obtained_at) > 23 * 3600:
            self.authenticate()

    # ------------------------------------------------------------------
    # Generic paginated GET
    # ------------------------------------------------------------------

    def _get_paginated(self, endpoint, key, params=None, label=None):
        """Fetch all pages from a paginated GoVocal endpoint.

        Args:
            endpoint: API path, e.g. "/api/v2/users/"
            key: JSON key that holds the list of items (e.g. "users")
            params: Extra query params dict
            label: tqdm progress bar label

        Returns:
            List of all item dicts across all pages.
        """
        self._ensure_auth()
        params = dict(params or {})
        params["page_size"] = self.MAX_PAGE_SIZE
        params["page_number"] = 1

        url = f"{self.base_url}{endpoint}"
        all_items = []
        total_pages = None
        pbar = None

        while True:
            resp = self._session.get(url, params=params, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            items = data.get(key, [])
            all_items.extend(items)

            meta = data.get("meta", {})
            total_pages = meta.get("total_pages", 1)

            if pbar is None and total_pages > 1:
                pbar = tqdm(total=total_pages, desc=label or endpoint, unit="page")
                pbar.update(1)
            elif pbar is not None:
                pbar.update(1)

            if params["page_number"] >= total_pages:
                break
            params["page_number"] += 1

        if pbar is not None:
            pbar.close()

        return all_items

    # ------------------------------------------------------------------
    # Public data-fetching methods
    # ------------------------------------------------------------------

    def get_users(self, **kwargs):
        """Fetch all users."""
        return self._get_paginated("/api/v2/users/", "users", params=kwargs, label="Users")

    def get_ideas(self, **kwargs):
        """Fetch all ideas/posts."""
        return self._get_paginated("/api/v2/ideas/", "ideas", params=kwargs, label="Ideas")

    def get_comments(self, **kwargs):
        """Fetch all comments."""
        return self._get_paginated("/api/v2/comments/", "comments", params=kwargs, label="Comments")

    def get_reactions(self, **kwargs):
        """Fetch all reactions (likes/dislikes on ideas and comments)."""
        return self._get_paginated("/api/v2/reactions", "reactions", params=kwargs, label="Reactions")

    def get_projects(self, **kwargs):
        """Fetch all projects."""
        return self._get_paginated("/api/v2/projects/", "projects", params=kwargs, label="Projects")
