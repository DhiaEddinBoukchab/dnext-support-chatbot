# Dnext Support Chatbot API

API-only branch for the Dnext support chatbot. This branch is prepared for containerized review and keeps only the files required to build and run the FastAPI service.

## Runtime Stack

- FastAPI
- OpenAI chat + embeddings
- ChromaDB persistent vector store
- SQLite for users, sessions, and conversation traces
- Markdown knowledge base under `docs_md/`

## Repository Layout

- `api/` FastAPI interface layer: routes, schemas, and request dependencies
- `core/` runtime configuration
- `domain/` domain models shared across the app
- `infrastructure/` persistence adapters such as SQLite
- `services/` application services for auth and chat orchestration
- `rag/` retrieval, embeddings, vector store, session, and LLM helpers
- `docs_md/` indexed knowledge base documents
- `Dockerfile` production container entrypoint

Current high-level flow:

```text
api -> services -> rag
     -> infrastructure
     -> domain
     -> core
```

## Required Environment Variables

- `OPENAI_API_KEY`

Optional:

- `OPENAI_MODEL`
- `EMBEDDING_MODEL`
- `DOCS_FOLDER`
- `CHROMA_DB_PATH`
- `API_DB_PATH`
- `API_PORT`

## Run Locally

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Routes expect upstream identity headers:

```text
X-User-Email: user@example.com
X-User-Name: John Doe
```

Main endpoints:

- `GET /health`
- `POST /api/v1/chat/query`
- `GET /api/v1/chat/sessions`
- `GET /api/v1/chat/sessions/{session_id}`
- `POST /api/v1/knowledge/reindex`

## Build The Container

```bash
docker build -t dnext-support-chatbot .
```

```bash
docker run --rm -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  dnext-support-chatbot
```

## Notes For DevOps

- The image copies only the runtime packages, configuration, and `docs_md/`.
- If the Chroma store is empty on first startup, the app auto-indexes `docs_md/`.
- `chroma_db/` and `runtime_data/` are runtime directories and are not baked into the image.
- Local development data such as `.gradio/`, `data/`, and archived email folders is intentionally excluded from this branch.
- The service is ready for later replacement of local storage pieces such as ChromaDB or file-based docs with AWS-managed components.
