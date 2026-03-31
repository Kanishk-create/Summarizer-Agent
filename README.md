# 📝 AI Text Summarizer Agent (Cloud Run + Gemini)

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run/?git_repo=https://github.com/Kanishk-create/Summarizer-Agent)

🚀 A production-ready AI agent that summarizes text and analyzes sentiment using Google ADK and Gemini 2.0 Flash — deployed on Cloud Run.

# 📝 Text Summarization Agent — ADK + Gemini on Cloud Run

A production-ready AI agent built with **Google Agent Development Kit (ADK)**
and **Gemini 2.0 Flash**, deployed as an HTTP service on **Google Cloud Run**.

The agent accepts any block of text and returns a concise summary, plus optional
sentiment classification — all via a simple REST API.

---

## Project Structure

```
summarizer_agent/           ← Cloud Run source root (deploy from here)
├── requirements.txt        ← Python dependencies (google-adk)
└── summarizer_agent/       ← ADK agent package
    ├── __init__.py
    ├── agent.py            ← Agent definition + tools
    └── .env                ← Credentials (never commit the real file)
```

> **Why this layout?**  
> ADK's built-in FastAPI server (`adk api_server`) automatically discovers
> `root_agent` from any Python package in the working directory.
> The outer `summarizer_agent/` folder is what you deploy; the inner one
> is the importable Python package.

---

## What the Agent Does

| Capability | Tool | Description |
|---|---|---|
| **Text summarization** | `summarize_text` | Condenses any text into N sentences (default 3) |
| **Sentiment classification** | `classify_sentiment` | Labels text POSITIVE / NEGATIVE / NEUTRAL |

The agent uses **Gemini 2.0 Flash** for inference and exposes both capabilities
through a single HTTP endpoint powered by ADK's built-in API server.

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10 or higher |
| Google Cloud SDK (`gcloud`) | Latest |
| Google Cloud project | With billing enabled |
| IAM roles | `roles/run.sourceDeveloper`, `roles/aiplatform.user`, `roles/iam.serviceAccountUser` |

---

## 1 — Local Development

### 1a. Clone & install

```bash
git clone <your-repo-url>
cd summarizer_agent

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 1b. Configure credentials

**Option A — Vertex AI (recommended):**
```bash
# Authenticate your local machine
gcloud auth application-default login

# Edit the .env file
cd summarizer_agent
nano .env
```

Set these values in `summarizer_agent/.env`:
```env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

**Option B — Gemini API key (quickest for local testing):**
```env
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your-api-key-from-aistudio
```

### 1c. Run locally

From the **outer** `summarizer_agent/` directory (the Cloud Run source root):

```bash
adk api_server
```

The agent is now running at `http://localhost:8000`.

---

## 2 — Calling the API

ADK's API server exposes a standard REST interface. All requests follow this pattern:

### Create a session

```bash
curl -X POST http://localhost:8000/apps/summarizer_agent/users/user-1/sessions \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response:
```json
{ "id": "abc123", "appName": "summarizer_agent", "userId": "user-1" }
```

### Send a summarization request

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "summarizer_agent",
    "userId": "user-1",
    "sessionId": "abc123",
    "newMessage": {
      "role": "user",
      "parts": [{
        "text": "Summarize this: Artificial intelligence is transforming every industry. From healthcare, where AI assists in diagnosing diseases, to finance, where algorithms detect fraud in milliseconds, the technology is becoming indispensable. However, concerns around bias, privacy, and job displacement remain significant challenges that researchers and policymakers must address together."
      }]
    }
  }'
```

### Example response

```json
{
  "candidates": [{
    "content": {
      "role": "model",
      "parts": [{
        "text": "**Summary:** AI is revolutionizing industries like healthcare and finance, but raises important concerns around bias, privacy, and employment.\n\n**Stats:** Original text — 52 words, 342 characters."
      }]
    }
  }]
}
```

### Request with sentiment + custom length

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "summarizer_agent",
    "userId": "user-1",
    "sessionId": "abc123",
    "newMessage": {
      "role": "user",
      "parts": [{
        "text": "Summarize in 2 sentences and tell me the sentiment: The product launch exceeded all expectations. Customers flooded social media with praise, sales hit record highs in the first 24 hours, and our support team reported almost zero complaints. The team is ecstatic."
      }]
    }
  }'
```

---

## 3 — Deploy to Cloud Run

### 3a. Enable required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  cloudbuild.googleapis.com
```

### 3b. Set your project

```bash
gcloud config set project YOUR_PROJECT_ID
```

### 3c. Deploy from source

From the **outer** `summarizer_agent/` directory:

```bash
gcloud run deploy summarizer-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_GENAI_USE_VERTEXAI=TRUE \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID \
  --set-env-vars GOOGLE_CLOUD_LOCATION=us-central1
```

> `--source .` triggers Cloud Run's **buildpack** auto-detection.  
> It finds `requirements.txt`, installs dependencies, and sets the entrypoint to
> `adk api_server` automatically — no Dockerfile needed.

After ~2 minutes you'll see:
```
Service [summarizer-agent] revision [summarizer-agent-00001] has been deployed
and is serving 100% of traffic.
Service URL: https://summarizer-agent-xxxxxxxxxx-uc.a.run.app
```

### 3d. Call the deployed agent

Replace `SERVICE_URL` with your actual Cloud Run URL:

```bash
SERVICE_URL="https://summarizer-agent-xxxxxxxxxx-uc.a.run.app"

# 1. Create a session
SESSION=$(curl -s -X POST "$SERVICE_URL/apps/summarizer_agent/users/user-1/sessions" \
  -H "Content-Type: application/json" -d '{}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "Session: $SESSION"

# 2. Run the agent
curl -X POST "$SERVICE_URL/run" \
  -H "Content-Type: application/json" \
  -d "{
    \"appName\": \"summarizer_agent\",
    \"userId\": \"user-1\",
    \"sessionId\": \"$SESSION\",
    \"newMessage\": {
      \"role\": \"user\",
      \"parts\": [{\"text\": \"Summarize: The James Webb Space Telescope has revealed thousands of galaxies never seen before, pushing the boundaries of our understanding of the early universe. Scientists are now able to study light from just 300 million years after the Big Bang.\"}]
    }
  }"
```

---

## 4 — ADK Dev UI (local only)

For interactive debugging and conversation testing:

```bash
adk web
```

Opens a browser UI at `http://localhost:8000` where you can chat with the agent,
inspect tool calls, and view session state in real time.

---

## Architecture

```
HTTP Client
    │
    ▼
Cloud Run Service
    │  (ADK built-in FastAPI server — adk api_server)
    ▼
summarizer_agent  ←── ADK Agent runtime
    │
    ├── Tool: summarize_text()     ← Python function (local)
    ├── Tool: classify_sentiment() ← Python function (local)
    │
    └── Gemini 2.0 Flash  ←── Vertex AI API
```

**Request flow:**
1. Client sends text via `POST /run`
2. ADK routes the message to `root_agent`
3. Gemini decides which tool(s) to call based on the instruction
4. Tools return structured metadata back to Gemini
5. Gemini synthesizes the final human-readable response
6. ADK returns the response as JSON

---

## Extending the Agent

To add a new capability, add a Python function and register it in `agent.py`:

```python
def extract_keywords(text: str, top_n: int = 5) -> dict:
    """Extract the top N keywords from the given text."""
    return {"status": "ready", "text": text, "top_n": top_n}

root_agent = Agent(
    ...
    tools=[summarize_text, classify_sentiment, extract_keywords],  # ← add here
)
```

No other changes needed — ADK and Gemini handle the rest.

---

## Cleanup

```bash
# Delete the Cloud Run service
gcloud run services delete summarizer-agent --region us-central1

# Delete the container image (optional)
gcloud artifacts repositories delete cloud-run-source-deploy \
  --location us-central1
```

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
