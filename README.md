# Evolution Simulation (prototype)

Hex-grid agent simulation with genetics, food/starvation, trade/steal, and a
semantic language layer. Optional OpenAI calls for trait invention and language
adoption; without a key the sim runs in mock mode.

Design notes (broader vision): [`GeneralIdea.md`](GeneralIdea.md).

## Stack

- Python 3.11, Flask UI (`src/web_server.py` + canvas frontend)
- Optional: `openai` when `OPENAI_API_KEY` is set
- Docker / docker-compose

## Quick start (mock AI)

```bash
python -m venv venv
# Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/web_server.py
```

Open http://127.0.0.1:5000

CLI tick loop (no UI):

```bash
python src/main.py
```

## Real OpenAI mode

```bash
cp .env.example .env
# put OPENAI_API_KEY=sk-... in .env (never commit .env)
```

Docker:

```bash
docker compose up --build
```

Pass the key via compose env (see `docker-compose.yml`). UI shows `mockup testing` vs `real testing`.

## Layout

```
src/
  agent.py genetics.py grid.py engine.py language.py
  main.py web_server.py
  static/          # hex canvas UI
data/              # runtime agent JSON (gitignored)
```

## Security

API keys must come from the environment only. If a key was ever committed, revoke it in the OpenAI dashboard.
