import requests
from tqdm import tqdm

from src import config

TYPEFORM_API_BASE = "https://api.typeform.com"


class TypeformClient:
    """Client for the Typeform Responses API."""

    def __init__(self, token=None):
        self._token = token or config.TYPEFORM_TOKEN
        self._session = requests.Session()
        self._session.headers["Authorization"] = f"Bearer {self._token}"

    # ------------------------------------------------------------------
    # Responses
    # ------------------------------------------------------------------

    def get_responses(self, form_id, include_partial=True, page_size=1000):
        """Fetch all responses for a single form using cursor-based pagination.

        Args:
            form_id: The Typeform form ID.
            include_partial: If True, include partial (incomplete) and started responses.
            page_size: Items per request (max 1000).

        Returns:
            List of response dicts.
        """
        url = f"{TYPEFORM_API_BASE}/forms/{form_id}/responses"
        params = {"page_size": min(page_size, 1000)}

        # Use response_type instead of deprecated 'completed' param
        if include_partial:
            params["response_type"] = "started,partial,completed"
        else:
            params["response_type"] = "completed"

        all_responses = []
        expected_total = None

        pbar = tqdm(desc=f"Typeform {form_id}", unit="resp")

        while True:
            resp = self._session.get(url, params=params, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            # Capture total_items from first page for validation
            if expected_total is None:
                expected_total = data.get("total_items", 0)
                pbar.total = expected_total

            items = data.get("items", [])
            all_responses.extend(items)
            pbar.update(len(items))

            # If fewer items than page_size, we've reached the end
            if len(items) < params["page_size"]:
                break

            # Use the last response's token as the cursor for the next page
            last_token = items[-1].get("token")
            if not last_token:
                break
            params["before"] = last_token

        pbar.close()

        if expected_total and len(all_responses) != expected_total:
            print(f"  Warning: API reports {expected_total} total responses but we fetched {len(all_responses)}")

        return all_responses

    def get_all_responses(self, form_ids, include_partial=True):
        """Fetch responses for multiple forms.

        Args:
            form_ids: List of Typeform form IDs.
            include_partial: If True, include partial responses.

        Returns:
            Dict mapping form_id -> list of response dicts.
        """
        results = {}
        for form_id in form_ids:
            results[form_id] = self.get_responses(form_id, include_partial=include_partial)
        return results

    # ------------------------------------------------------------------
    # Email extraction helpers
    # ------------------------------------------------------------------

    @staticmethod
    def extract_email(response):
        """Try to extract an email address from a single Typeform response.

        Checks hidden fields first, then looks for email-type answers.

        Args:
            response: A single Typeform response dict.

        Returns:
            Email string or None.
        """
        # Check hidden fields (most common for pre-filled emails)
        hidden = response.get("hidden", {})
        for key in ("email", "e-mail", "Email", "EMAIL"):
            if key in hidden and hidden[key]:
                return hidden[key]

        # Check answer fields for email-type questions
        for answer in response.get("answers", []):
            if answer.get("type") == "email":
                return answer.get("email")

        return None

    @staticmethod
    def flatten_response(response, form_id=None):
        """Flatten a single Typeform response into a simple dict for tabular output.

        Args:
            response: A single Typeform response dict.
            form_id: Optional form ID to include in the output.

        Returns:
            Dict with response metadata and answers keyed by question ref/id.
        """
        row = {
            "response_id": response.get("response_id") or response.get("token"),
            "landed_at": response.get("landed_at"),
            "submitted_at": response.get("submitted_at"),
            "response_type": response.get("response_type"),
        }
        if form_id:
            row["form_id"] = form_id

        # Extract email
        row["email"] = TypeformClient.extract_email(response)

        # Add hidden fields
        for k, v in response.get("hidden", {}).items():
            row[f"hidden_{k}"] = v

        # Flatten answers by field ref or ID
        for answer in response.get("answers", []):
            field = answer.get("field", {})
            field_key = field.get("ref") or field.get("id", "unknown")
            answer_type = answer.get("type", "")

            if answer_type == "choice":
                choice = answer.get("choice", {})
                row[field_key] = choice.get("label") or choice.get("other")
            elif answer_type == "choices":
                choices = answer.get("choices", {})
                labels = choices.get("labels", [])
                other = choices.get("other")
                if other:
                    labels.append(other)
                row[field_key] = "; ".join(labels)
            elif answer_type in ("text", "email", "url", "file_url", "phone_number"):
                row[field_key] = answer.get(answer_type)
            elif answer_type in ("number", "boolean"):
                row[field_key] = answer.get(answer_type)
            elif answer_type == "date":
                row[field_key] = answer.get("date")
            else:
                row[field_key] = str(answer.get(answer_type, ""))

        return row
