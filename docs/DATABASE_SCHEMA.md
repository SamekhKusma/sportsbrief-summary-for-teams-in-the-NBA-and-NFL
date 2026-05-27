# Database Schema

The MVP uses SQLite for local development. SQLAlchemy creates the tables automatically on backend startup.

## articles

Stores normalized article metadata. Full copyrighted article text is not stored.

| Column | Type | Description |
|---|---|---|
| id | integer | Primary key |
| league | string | NBA or NFL |
| team_name | string | Team name |
| title | string | Article title |
| source_name | string | Publisher or source name |
| source_url | string | Source URL |
| published_at | datetime | Article publish timestamp |
| description | text | Short description from provider or seed data |
| content_snippet | text | Short snippet from provider or seed data |
| article_hash | string | Hash used for duplicate removal |
| created_at | datetime | Insert timestamp |

## summaries

Stores generated briefs for audit and demo purposes.

| Column | Type | Description |
|---|---|---|
| id | integer | Primary key |
| team_name | string | Team name |
| league | string | NBA or NFL |
| summary_text | text | Team-level summary |
| topic_json | text | JSON list of topic cards |
| generated_at | datetime | Generation timestamp |
| article_ids | text | JSON list of source article IDs |
