# paint-tracker

Paint and stain shelf tracker with:

- **FastAPI** API
- **PostgreSQL-ready** SQLAlchemy persistence (set `DATABASE_URL`)
- **React + Vite** frontend

## Backend

```bash
cd /home/runner/work/paint-tracker/paint-tracker/backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

`DATABASE_URL` defaults to local SQLite for convenience. Set a PostgreSQL URL in production, for example:

```bash
export DATABASE_URL='postgresql+psycopg://user:password@localhost:5432/paint_tracker'
```

## Frontend

```bash
cd /home/runner/work/paint-tracker/paint-tracker/frontend
npm install
npm run dev
```

Optional API override:

```bash
export VITE_API_BASE_URL='http://localhost:8000/api'
```

## Included behavior

- Create paints with required `room`, `shelf_level`, `shelf_depth`
- Room suggestions while typing; new room names are saved automatically
- Search paints by room, color, and coordinates
- Edit existing paints from the list (✏️ button)
- Confirmation/decline controls use green check and red X buttons
