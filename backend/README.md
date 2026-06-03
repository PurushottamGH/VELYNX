# Backend (FastAPI)

Quickstart

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest
```

Interactive terminal chat:

```bash
python -m backend.cli chat
```

Ask a one-off question:

```bash
python -m backend.cli chat --question "what is 2+3?"
```
