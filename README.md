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
│   ├── pull_data.ipynb     # Run this to pull all data
│   └── unify_users.ipynb   # Build unified user & anonymous lists
└── data/                   # Output JSON files (not committed)
```

## Output Files

### Raw Data (from `pull_data.ipynb`)

| File | Contents |
|---|---|
| `govocal_users.json` | All registered users (id, email, name, etc.) |
| `govocal_ideas.json` | All ideas/posts **and** survey responses (see note below) |
| `govocal_comments.json` | All comments (body, author, idea, etc.) |
| `govocal_reactions.json` | All likes/dislikes on ideas and comments |
| `typeform_{form_id}.json` | Responses for each Typeform form |

### Unified Data (from `unify_users.ipynb`)

| File | Contents |
|---|---|
| `unified_users.json` | Deduplicated list of all identified users across GoVocal and Typeform, matched by email |
| `anonymous_users.json` | Contributions (ideas, comments, survey responses) with no identifiable author |

## GoVocal Data Structure

> **Important:** The GoVocal API returns both real ideas and survey responses from the same `/ideas/` endpoint. Each record has a `type` field that distinguishes them.

The data spans three GoVocal projects:

| Project | Record Type | Description |
|---|---|---|
| Welcome to The South Carolina Forum! | `idea` | User-submitted ideas and proposals (~778 records) |
| The South Carolina Forum: Initial Survey | `survey` | Native GoVocal survey responses (~1,810 records) |
| The South Carolina Forum: Pre-Launch Survey | `survey` | Native GoVocal survey responses (~655 records) |

Key fields for distinguishing record types:
- **`type`**: `"idea"` for actual ideas, `"survey"` for survey responses
- **`author_id`**: Present for registered users, `null` for anonymous contributions. Most survey responses have a `null` author_id because survey respondents are typically anonymous.
- **`project_id`** / **`project_title`**: Identifies which project the record belongs to

## Unified User Matching

The `unify_users.ipynb` notebook matches users across GoVocal and Typeform by **normalized email address** (lowercased, trimmed). The process:

1. **Seed** from all GoVocal registered users (each has an email)
2. **Merge** Typeform respondents — if an email matches a GoVocal user, their records are linked; otherwise a new user entry is created
3. **Enrich** with GoVocal activity counts (ideas authored, comments, reactions)
4. **Collect anonymous contributions** — any idea/comment with `null` author_id, or Typeform response with no email

Each unified user record tracks which platforms they appear in (`sources`), cross-reference IDs (`govocal_user_id`, `typeform_response_ids`), and activity counts.
