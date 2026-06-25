# Dnext Support Chatbot Production Implementation Plan

## 1. Goal

Move the current prototype into a production-ready architecture that:

- replaces the Gradio UI with a React embeddable widget
- replaces local auth with JWT-based access from `dndev`
- replaces the Python monolith UI flow with REST APIs running on AWS
- replaces local ChromaDB with Amazon OpenSearch for vector retrieval
- replaces local SQLite with DynamoDB for operational data
- replaces local `docs_md/` storage with S3-based document ingestion

This document is based on the current repository implementation, not on a generic RAG template.

## 2. What Exists Today In The Repo

### Current architecture

- UI is Gradio and the app starts by launching a local web server in [`main.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/main.py:48).
- Login is a lightweight form asking for email and full name in [`app/ui_builder.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/app/ui_builder.py:55).
- User registration and access checks are handled in [`auth_service.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/auth_service.py:35).
- Users, conversations, admins, and retrieval traces are stored in SQLite in [`database.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/database.py:43).
- Source documents are read from `docs_md/` via [`config.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/config.py:17) and loaded in [`app/rag_engine.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/app/rag_engine.py:45).
- Chunking is separator-based only: documents must contain `****` style separators in [`src/chunker.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/src/chunker.py:21).
- Embeddings are generated with OpenAI and stored in local ChromaDB in [`src/embeddings.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/src/embeddings.py:11) and [`src/vector_store.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/src/vector_store.py:16).
- Retrieval already uses hybrid search: semantic + BM25 in [`app/rag_engine.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/app/rag_engine.py:165).
- Uploaded files are copied to local disk under `data/uploads` in [`app/message_handler.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/app/message_handler.py:304).

### Important current gaps before production

- No REST API yet. The UI and backend flow are still tightly coupled through Gradio.
- No real production auth yet. The widget must eventually rely on JWT verification, not `email + full name`.
- Admin bootstrap is insecure for production: default `admin/admin123` is created in [`main.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/main.py:32).
- Website scraping happens during request handling through `requests.get("https://www.dnext.io/")` in [`src/llm_handler.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/src/llm_handler.py:260). This should not stay in the hot path for production chat requests.
- Operational data model is still relational/SQLite oriented, while DynamoDB will need access-pattern-first design.
- No automated test suite is present in the repository right now.
- There is a naming mismatch in conversation classification:
  - classifier returns `CASUAL` or `ACTIONABLE` in [`src/llm_handler.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/src/llm_handler.py:25)
  - retrieval config expects `TECHNICAL` or `CASUAL` in [`src/retrieval_config.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/src/retrieval_config.py:82)
  - retrieval traces for text chats are saved only when type is `TECHNICAL` in [`app/message_handler.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/app/message_handler.py:159)

## 3. Recommended Target Production Architecture

### Frontend

- React widget embedded inside `dndev`
- Widget rendered only when host application already has a valid user token
- Widget calls backend REST API through HTTPS
- Optional later phase: support file upload through pre-signed S3 URLs

### Authentication

- Reuse the existing `dndev` identity system if it already issues JWTs
- Backend verifies JWT signature, issuer, audience, expiry, and user claims
- Recommended flow:
  - `dndev` logs the user in
  - host page passes token to widget
  - widget includes `Authorization: Bearer <jwt>` on every API call
  - API Gateway authorizer or Lambda authorizer validates token

### Backend

- API Gateway exposes the chatbot REST endpoints
- AWS Lambda runs request handling logic for chat, sessions, feedback, and admin-safe endpoints
- Shared service modules:
  - auth verification
  - chat orchestration
  - retrieval service
  - persistence service
  - prompt/template service

### Knowledge ingestion

- Source `.md` files stored in S3
- S3 upload event triggers ingestion pipeline
- Pipeline steps:
  1. fetch object from S3
  2. validate separator format
  3. split using the same `****` chunking logic
  4. generate embeddings
  5. write chunks + metadata into OpenSearch
  6. write ingestion status/manifest to DynamoDB

### Data stores

- Amazon OpenSearch:
  - vector index for semantic retrieval
  - optional keyword fields for hybrid retrieval
- DynamoDB:
  - users
  - chat sessions
  - conversation metadata
  - ingestion jobs / document manifests
  - feedback / audit status
- Amazon S3:
  - source markdown docs
  - uploaded user files if file upload remains in scope
  - large retrieval trace payloads if they exceed DynamoDB item size

### Observability and operations

- CloudWatch logs and dashboards
- request tracing
- alarms on Lambda errors, latency, throttling, and OpenSearch health
- Secrets Manager or SSM Parameter Store for secrets
- IaC using Terraform or AWS CDK
- CI/CD for `dev`, `staging`, and `prod`

## 4. Production Design Notes Specific To This Repo

### A. Keep the current chunking contract at first

Do not change chunking and retrieval behavior at the same time as infrastructure migration.

For phase 1:

- keep the separator-based chunking logic from [`src/chunker.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/src/chunker.py:54)
- keep metadata fields such as `document`, `section`, `chunk_index`, `keywords`
- keep hybrid retrieval behavior conceptually similar to [`app/rag_engine.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/app/rag_engine.py:165)

This reduces regression risk.

### B. Do not put all ingestion inside synchronous chat Lambdas

Chat API and document ingestion should be separate workloads.

- Chat request Lambda: synchronous, low latency
- Ingestion pipeline: asynchronous, retriable, allowed to take longer

If document volume is small, S3 event -> Lambda is enough.
If volume grows, use SQS and possibly Step Functions for retries and visibility.

### C. DynamoDB should not blindly mirror SQLite tables

The current SQLite schema in [`database.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/database.py:56) is useful for understanding the domain, but DynamoDB design must follow access patterns.

Suggested access patterns:

- get user profile by `user_id`
- get sessions by `user_id`
- get messages by `session_id`
- get recent conversations for admin filters
- get ingestion status by `document_id`
- get feedback by `session_id` or `message_id`

Important: retrieval traces can get large. Consider storing only summary metadata in DynamoDB and raw trace JSON in S3.

### D. Remove runtime website scraping from the answer path

The current request flow fetches `dnext.io` during generation in [`src/llm_handler.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/src/llm_handler.py:260).

Production recommendation:

- either ingest website content into the same knowledge pipeline
- or remove it entirely from the first production release

Do not rely on live scraping during user chat requests.

### E. Clarify phase-1 scope for uploads

The current prototype supports images, PDFs, and `.txt` uploads in chat.

For production, decide early:

- Option 1: text-only widget first release
- Option 2: keep uploads in scope and build signed S3 upload flow

Text-only first release is faster and much lower risk.

## 5. Workstreams And Owners

### Workstream 1: Architecture and scope

Owner: Dev lead + DevOps lead + you as business/RAG owner

- freeze phase-1 scope
- confirm auth source and JWT contract
- confirm traffic expectations
- confirm whether uploads are in phase 1
- confirm data retention and logging rules

### Workstream 2: Frontend widget

Owner: Frontend dev team

- build embeddable React widget
- integrate host token consumption
- connect to REST API
- handle loading, streaming/non-streaming answers, fallback, and error states

### Workstream 3: Backend API

Owner: Backend dev team

- extract business logic from Gradio-driven flow
- expose REST endpoints
- implement JWT verification
- implement session and conversation persistence
- implement response generation service

### Workstream 4: RAG and ingestion

Owner: Backend dev + AI/RAG owner

- port chunking logic exactly
- build S3-to-OpenSearch ingestion path
- migrate document metadata model
- validate retrieval quality against current prototype

### Workstream 5: Cloud platform and delivery

Owner: DevOps team

- provision AWS resources
- networking, IAM, secrets, encryption
- CI/CD
- monitoring, alarms, backups, rollback process

### Workstream 6: Acceptance and rollout

Owner: You + support stakeholders + QA + dev team

- define business test questions
- compare prototype vs staging answers
- sign off on accuracy, latency, and fallback behavior

## 6. Phased Implementation Plan

## Phase 0: Discovery and decisions

Duration: 3 to 5 working days

Deliverables:

- approved target architecture
- agreed phase-1 scope
- JWT integration specification
- document ownership list
- non-functional requirements

Tasks:

- decide whether to use API Gateway authorizer or custom verification in Lambda
- decide whether uploads are in or out for phase 1
- decide whether admin dashboard is rebuilt now or postponed
- decide whether OpenSearch hybrid search uses one index or separate vector + keyword fields

## Phase 1: Stabilize the prototype before migration

Duration: 3 to 5 working days

Goal:
reduce ambiguity before the AWS rewrite starts.

Tasks:

- fix the `ACTIONABLE` vs `TECHNICAL` naming mismatch
- remove default production credentials
- document exact prompt, retrieval, and fallback behavior
- define canonical chunk metadata schema
- export a golden test set of real user questions and expected answers

## Phase 2: Build the production backend foundation

Duration: 1 to 2 weeks

Tasks:

- create REST API contract
- create Lambda project structure
- implement JWT verification
- implement health endpoint and config management
- implement DynamoDB repositories
- implement OpenSearch client wrapper
- add structured logging and tracing

Suggested initial endpoints:

- `POST /chat/query`
- `GET /chat/sessions`
- `GET /chat/sessions/{sessionId}`
- `POST /chat/feedback`
- `GET /health`

Optional internal endpoints:

- `POST /ingestion/documents/reindex`
- `GET /ingestion/jobs/{jobId}`

## Phase 3: Build ingestion and indexing pipeline

Duration: 1 to 2 weeks

Tasks:

- create S3 bucket structure
- upload current `docs_md/*.md`
- implement document manifest format
- implement chunking validation
- generate embeddings
- write chunks to OpenSearch
- persist ingestion status
- build reindex command/process

Suggested S3 layout:

- `knowledge/raw/<document-name>.md`
- `knowledge/processed/<document-id>/manifest.json`
- `uploads/<env>/<yyyy>/<mm>/<dd>/...`
- `traces/<env>/<session-id>/...`

## Phase 4: Build the React widget

Duration: 1 to 2 weeks

Tasks:

- create embeddable widget package
- read host JWT
- show/hide widget based on token presence
- connect query input to API
- render citations/sources only if product wants them
- handle empty state, errors, loading, retry
- optionally support streaming if backend exposes it

## Phase 5: Staging validation and migration

Duration: 1 week

Tasks:

- deploy dev and staging
- ingest same knowledge base into staging
- run golden question set
- compare answer quality to current prototype
- load test basic concurrency
- security review
- rollback dry run

## Phase 6: Production rollout

Duration: 2 to 3 days

Tasks:

- prod infrastructure ready
- prod secrets ready
- prod docs ingested
- smoke tests complete
- limited internal release
- monitor logs and KPIs
- full rollout after signoff

## 7. Jira-Style Ticket Backlog

### Epic A: Production architecture and delivery

1. `ARCH-01` Define target architecture and phase-1 scope
   - Owner: Tech lead
   - Output: architecture diagram, ADR, scope decision log

2. `ARCH-02` Define API contract for widget/backend integration
   - Owner: Backend lead + frontend lead
   - Output: OpenAPI spec or equivalent

3. `ARCH-03` Define JWT trust model with `dndev`
   - Owner: Backend lead + auth owner
   - Output: issuer, audience, claims, JWKS/JWT verification rules

### Epic B: Security and auth

4. `SEC-01` Remove hardcoded default admin bootstrap from production path
   - Owner: Backend dev
   - Based on: [`main.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/main.py:32)

5. `SEC-02` Implement JWT validation middleware/authorizer
   - Owner: Backend dev
   - Output: validated identity context for every request

6. `SEC-03` Configure secrets management for OpenAI keys and app config
   - Owner: DevOps

7. `SEC-04` Define IAM least-privilege policies for Lambda, S3, DynamoDB, and OpenSearch
   - Owner: DevOps

### Epic C: Backend API

8. `BE-01` Extract chat orchestration from Gradio event handlers into reusable service layer
   - Owner: Backend dev
   - Based on: [`app/ui_builder.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/app/ui_builder.py:155)

9. `BE-02` Implement `POST /chat/query`
   - Owner: Backend dev

10. `BE-03` Implement sessions API
   - Owner: Backend dev

11. `BE-04` Implement conversation persistence in DynamoDB
   - Owner: Backend dev

12. `BE-05` Implement retrieval trace persistence strategy
   - Owner: Backend dev
   - Note: use S3 for large payloads if needed

13. `BE-06` Add structured logs, request IDs, and error taxonomy
   - Owner: Backend dev

### Epic D: RAG and ingestion

14. `RAG-01` Port separator-based chunking logic unchanged
   - Owner: Backend dev
   - Based on: [`src/chunker.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/src/chunker.py:54)

15. `RAG-02` Define OpenSearch index mapping for chunks and metadata
   - Owner: Backend dev + DevOps

16. `RAG-03` Implement S3-triggered ingestion pipeline
   - Owner: Backend dev

17. `RAG-04` Implement OpenSearch retrieval service with hybrid ranking
   - Owner: Backend dev
   - Based on: [`app/rag_engine.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/app/rag_engine.py:165)

18. `RAG-05` Build reindex/replay job for full corpus rebuild
   - Owner: Backend dev

19. `RAG-06` Remove runtime `dnext.io` scraping from hot path
   - Owner: Backend dev
   - Based on: [`src/llm_handler.py`](/C:/Users/DNEXT%20DHIA/dnext-support-chatbot/src/llm_handler.py:260)

20. `RAG-07` Fix conversation type naming mismatch (`ACTIONABLE` vs `TECHNICAL`)
   - Owner: Backend dev

### Epic E: Frontend widget

21. `FE-01` Create React embeddable widget shell
   - Owner: Frontend dev

22. `FE-02` Integrate host JWT into widget auth flow
   - Owner: Frontend dev

23. `FE-03` Implement chat UI and answer rendering
   - Owner: Frontend dev

24. `FE-04` Implement session history view
   - Owner: Frontend dev

25. `FE-05` Implement upload flow with pre-signed S3 URLs
   - Owner: Frontend dev
   - Only if uploads remain in scope

### Epic F: Platform and DevOps

26. `OPS-01` Provision AWS environments (`dev`, `staging`, `prod`)
   - Owner: DevOps

27. `OPS-02` Provision S3, DynamoDB, OpenSearch, API Gateway, Lambda
   - Owner: DevOps

28. `OPS-03` Build CI/CD pipelines
   - Owner: DevOps

29. `OPS-04` Configure monitoring, alarms, and dashboards
   - Owner: DevOps

30. `OPS-05` Define rollback and backup procedures
   - Owner: DevOps

### Epic G: QA and rollout

31. `QA-01` Build golden question set from real support use cases
   - Owner: You + support team

32. `QA-02` Define acceptance criteria for answer quality, latency, and fallback behavior
   - Owner: You + QA + product owner

33. `QA-03` Execute prototype vs staging answer comparison
   - Owner: QA + you

34. `REL-01` Run staging smoke test and go-live checklist
   - Owner: QA + DevOps + backend lead

## 8. Migration Plan

### Step 1: Freeze current logic

- identify current production-like behavior to preserve:
  - chunking
  - retrieval style
  - prompt style
  - fallback message
- capture 30 to 50 representative user questions

### Step 2: Migrate documents first, not users first

- upload current `docs_md/*.md` corpus to S3
- run ingestion into OpenSearch
- verify that retrieved chunks match the prototype closely

### Step 3: Build backend in parallel with widget

- backend team creates API and persistence
- frontend team builds widget against mock/staging API
- you validate business behavior on staging

### Step 4: Migrate operational data only if needed

Because this is still a POC, you may not need a full historical migration from SQLite to DynamoDB.

Recommended approach:

- keep old SQLite database archived
- migrate only if business requires old conversations in the new system
- otherwise start fresh in production and preserve old data as a reference export

### Step 5: Staging parity validation

- compare prototype answers and staging answers on the same question set
- test auth flow inside `dndev`
- test session history
- test no-result fallback
- test admin/observability basics

### Step 6: Controlled release

- release to internal users first
- monitor retrieval quality and latency
- enable broader rollout after 2 to 5 business days of stable metrics

## 9. What You Can Do Yourself Right Now

These are the highest-leverage tasks for your side as customer support / AI owner.

### Immediate actions

1. Build a golden dataset
   - collect 30 to 50 real support questions
   - add expected good answers
   - mark the source document that should support each answer

2. Clean and normalize the markdown knowledge base
   - verify every document still follows the `****` separator rule
   - remove duplicated or conflicting answers
   - identify document owners for each file

3. Define business fallback rules
   - when should the bot answer directly
   - when should it say "contact support"
   - which topics must never be guessed

4. Write the scope memo for phase 1
   - text-only or text + file uploads
   - internal users only or external clients too
   - languages supported
   - answer style and compliance rules

5. Ask the `dndev` team for auth integration inputs
   - sample JWT
   - token claims definition
   - issuer/audience values
   - JWKS or public key validation method
   - how the widget will receive the token

6. Ask DevOps for environment planning inputs
   - AWS account/environment structure
   - who manages IaC
   - naming conventions
   - secrets management standard
   - logging/monitoring standard

### Useful artifacts you can prepare

- FAQ / expected-answer spreadsheet
- knowledge base ownership list
- unsupported-question list
- rollout readiness checklist
- go-live acceptance checklist

## 10. What You Need From The Dev Team

- API design and implementation
- React widget implementation
- OpenSearch integration
- DynamoDB schema design
- prompt/config externalization
- staging environment for validation

## 11. What You Need From The DevOps Team

- AWS resource provisioning
- CI/CD
- secrets management
- IAM/security baselines
- monitoring and alarms
- deployment and rollback process

## 12. Coordination Model That Will Work Well

### Weekly structure

- 1 architecture/planning meeting per week
- 2 short implementation syncs per week
- 1 staging demo / validation session per week

### Decision owners

- You: business behavior, content quality, acceptance questions, fallback policy
- Frontend lead: widget UX and embedding
- Backend lead: API, orchestration, persistence, RAG service
- DevOps lead: AWS, security, CI/CD, monitoring

### Suggested execution rhythm

1. Week 1
   - finalize scope
   - gather auth inputs
   - prepare golden dataset
   - confirm target architecture

2. Week 2
   - backend skeleton
   - AWS environments
   - ingestion proof in OpenSearch

3. Week 3
   - widget connected to staging API
   - session persistence
   - document ingestion complete

4. Week 4
   - full staging validation
   - fixes from QA
   - go-live checklist

5. Week 5
   - controlled rollout
   - monitoring
   - post-launch improvements

## 13. Recommended First Release Scope

To reach production faster, the safest first release is:

- React widget embedded in `dndev`
- JWT auth based on existing platform login
- text-only chat
- S3 markdown ingestion
- OpenSearch retrieval
- DynamoDB for users/sessions/conversation metadata
- CloudWatch monitoring

Defer to phase 2 if possible:

- file uploads
- vision/PDF analysis
- admin dashboard redesign
- advanced analytics exports

## 14. Final Recommendation

Treat this as a controlled productization project, not just an infrastructure migration.

The fastest path is:

1. stabilize current logic
2. preserve chunking/retrieval behavior
3. separate backend API from the Gradio UI
4. build AWS ingestion and storage around that logic
5. validate answer quality before full rollout

If the team follows that order, you reduce the chance of changing UI, auth, storage, retrieval, and prompting all at the same time.
