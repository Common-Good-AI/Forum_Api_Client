# Forum API Client

Pull and aggregate user activity data from **GoVocal** and **Typeform** into unified CSV datasets for analysis.

## Quick Start

### 1. Set up your environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .example.env .env
```

Edit `.env` and fill in your API credentials:

| Variable | Where to find it |
|---|---|
| `GOVOCAL_BASE_URL` | Your GoVocal platform URL (e.g. `https://participate.scforum.org`) |
| `GOVOCAL_CLIENT_ID` | GoVocal Admin → Tools → Public API Access |
| `GOVOCAL_CLIENT_SECRET` | GoVocal Admin → Tools → Public API Access |
| `TYPEFORM_TOKEN` | [Typeform Account Settings → Personal Tokens](https://admin.typeform.com/account#/section/tokens) |

### 3. Run the notebook

Open `notebooks/pull_data.ipynb` in VS Code or Jupyter and run each cell in order (Shift+Enter).

The notebook will:
1. Connect to GoVocal and Typeform APIs
2. Pull all users, ideas, comments, and reactions from GoVocal
3. Pull all responses from your specified Typeform forms
4. Save everything as JSON files in `data/`

## Project Structure

```
├── .env                    # Your API credentials (not committed)
├── .example.env            # Template for .env
├── requirements.txt        # Python dependencies
├── src/
│   ├── config.py           # Loads and validates credentials
│   ├── govocal_client.py   # GoVocal API client (auth, pagination)
│   └── typeform_client.py  # Typeform API client (auth, pagination)
├── notebooks/
│   └── pull_data.ipynb     # Run this to pull all data
└── data/                   # Output JSON files (not committed)
```

## Output Files

After running the notebook, you'll find these JSON files in `data/`:

| File | Contents |
|---|---|
| `govocal_users.json` | All registered users (id, email, name, etc.) |
| `govocal_ideas.json` | All ideas/posts (title, body, author, project, etc.) |
| `govocal_comments.json` | All comments (body, author, idea, etc.) |
| `govocal_reactions.json` | All likes/dislikes on ideas and comments |
| `typeform_{form_id}.json` | Responses for each Typeform form |

Users across platforms can be linked by **email address**.
