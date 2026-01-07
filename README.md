# TalentScout – Hiring Assistant (Streamlit)

A conversational hiring assistant that collects candidate details and generates tailored technical questions based on the candidate’s declared tech stack.

## Features
- **Greeting & Purpose**: Introduces itself, explains scope, and supports end keywords.
- **Information Gathering**: Collects full name, email, phone, years of experience, desired positions, current location, and tech stack.
- **Tech Questions**: Generates 3–5 questions per key technology mentioned.
- **Context Handling**: Maintains chat history and uses prompts to target missing fields.
- **Fallback**: Clarifies on unclear inputs without deviating from purpose.
- **Privacy**: Stores to local JSONL only if the user consents; masks email/phone.
- **LLM Flexibility**: Works with OpenAI or any OpenAI-compatible endpoint (e.g., Ollama).

## Advanced Features
- **Multilingual support**: Auto-detect user language (when set to "auto") or force responses in English/Spanish/French/Hindi. The model is guided to answer in the selected language.
- **Sentiment analysis**: Per-user-message sentiment label (`positive`, `neutral`, `negative`) shown below each user turn.
- **Personalization (privacy-preserving)**: If the candidate provides an email, a hashed identifier is used to load prior session details and prefill missing fields, with a welcome-back notice.
- **UI enhancements**: Subtle styling and a sidebar progress indicator showing profile completion.
- **Performance controls**: Fast mode toggle, adjustable temperature, history window size, and max tokens for low-latency operation.

## Quickstart

### 1) Clone and setup
```bash
# Python 3.10+
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

### 2) Configure environment
Copy `.env.example` to `.env` (optional) and set:
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL` (default: `https://api.openai.com/v1`)
- `OPENAI_MODEL` (default: `gpt-4o-mini`)

For local LLMs via Ollama:
- `OPENAI_BASE_URL=http://localhost:11434/v1`
- `OPENAI_MODEL=llama3.1`

### 3) Run
```bash
streamlit run app.py
```
Open the local URL shown by Streamlit.

## Prompt Design
- **System Prompt** (`src/prompts.py: SYSTEM_PROMPT`): Governs scope, fields, end keywords, fallback, and privacy handling.
- **Assistant Greeting** (`ASSISTANT_GREETING`): Clear onboarding and termination instruction.
- **Profile-Aware Instructions** (`INSTRUCTIONS_WITH_PROFILE`): Injects partial candidate profile to drive targeted questions and completion of missing fields. The LLM is asked to produce 3–5 concise, practical questions per key technology.

## Data Handling & Privacy
- Local-only demo storage at `data/candidates.jsonl` via `src/storage.py`.
- Email and phone are masked before persistence.
- Consent gate in sidebar; no write without consent.
- Do not submit real sensitive data. Aligns with privacy best practices for demos.

### Personalization details
- The app computes a SHA-256 hash of the provided email (never stores raw email in the record key) and searches prior sessions for that hash to prefill missing fields.
- Persisted records always store masked email/phone in the `profile` section.

## Code Structure
- `app.py`: Streamlit UI and chat loop.
- `src/prompts.py`: Prompt templates.
- `src/llm_client.py`: OpenAI-compatible client wrapper.
- `src/storage.py`: Local JSONL persistence with masking and history lookup helpers.
- `src/utils.py`: Helpers (end keywords, parsing, normalization).
- `src/nlp.py`: Sentiment analysis and language detection utilities.
- `requirements.txt`: Dependencies.

## Challenges & Solutions
- **Context control**: Provided explicit profile JSON to model each turn; keeps it grounded and focused on missing fields and question generation.
- **Fallback & end detection**: Rule-based checks plus instructions prevent drift and ensure graceful exit.
- **Privacy**: Masking and consent before writes; avoids echoing sensitive values back.

## Performance Tuning
- **Fast mode**: Lowers temperature and max tokens to respond faster.
- **History window**: Limits how many recent turns are sent to the LLM (controls context size and latency).
- **Max tokens**: Caps the length of model outputs.
- **Temperature**: Adjusts response variability.

## Optional Enhancements
- **Sentiment analysis**: Add a second model call (or classifier) and log per turn sentiment.
- **Multilingual**: Detect language and switch prompt language; or select a multilingual model.
- **Personalization**: Load prior sessions by email hash and adapt questions.
- **UI polish**: Add sections, badges, and progress chips for collected fields.
- **Cloud deploy**: Streamlit Community Cloud or any PaaS; ensure env vars are set.

## Demo Tips
- Start with your name, target role, and years of experience.
- Provide a tech stack (e.g., "Python, Django, PostgreSQL, Docker").
- Change the response language in the sidebar or leave on auto to detect.
- Toggle Fast mode if latency is high.

## License
MIT (for assignment/demo purposes).
