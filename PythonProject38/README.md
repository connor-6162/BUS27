# StudyApp (Uni-Focus) - Sprint 2 Full Prototype

This project is a runnable Flask prototype that covers:
- **S1 Manual task entry** (persisted in SQLite via SQLAlchemy)
- **S2 Urgency visualizer**: tasks due within 24h turn red (logic runs in backend `Task.is_urgent()`)
- **S3 Completion tracking**: mark done -> DB + UI update

## 1) Create venv & install
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

## 2) Create database (first time only)
```bash
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

## 3) Run
```bash
python app.py
```

Open: http://127.0.0.1:5000/
