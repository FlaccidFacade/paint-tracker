# paint-tracker

Paint and stain shelf tracker with:

- **FastAPI** API
- **SQLite** auto-configured database (no setup required)
- **React + Vite** frontend bundled into the Python package
- **Self-updating** – checks PyPI for new versions on every start

---

## 🚀 One-click install on Raspberry Pi Zero 2 W

Run this single command on the Pi (requires Python 3.11+ and internet access):

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/FlaccidFacade/paint-tracker/main/scripts/install_pi.sh)
```

The script will:
1. Install `paint-tracker` from PyPI.
2. Create and enable a **systemd service** that starts automatically on every boot.
3. Open port 8000 in the firewall (if ufw is active).
4. Print the local URL where the UI is reachable (e.g. `http://raspberrypi.local:8000`).

After installation, the tracker is accessible from any device on your network.

---

## 📦 Install from PyPI (any machine)

```bash
pip install paint-tracker
paint-tracker
```

On first launch Paint Tracker will:
- Check PyPI for a newer version and prompt you to upgrade.
- Auto-create the SQLite database at `~/.local/share/paint-tracker/paint_tracker.db`.
- Start the web server on `http://0.0.0.0:8000`.

### CLI options

```
paint-tracker --help

  --host HOST            Bind host (default: 0.0.0.0)
  --port PORT            Bind port (default: 8000)
  --no-update-check      Skip the PyPI update check on startup
```

---

## 🔧 Development setup

### Backend

```bash
cd backend
pip install -r requirements.txt
pip install -e ..          # install paint_tracker package in editable mode
uvicorn paint_tracker.main:app --reload
```

`DATABASE_URL` defaults to `~/.local/share/paint-tracker/paint_tracker.db`. Override for PostgreSQL:

```bash
export DATABASE_URL='postgresql+psycopg://user:password@localhost:5432/paint_tracker'
```

Run tests:

```bash
cd backend
pytest
```

### Frontend (standalone dev server)

```bash
cd frontend
npm install
npm run dev
```

Optional API override:

```bash
export VITE_API_BASE_URL='http://localhost:8000/api'
```

---

## 📤 Publishing to PyPI

Build the frontend, bundle it into the Python package, and publish in one step:

```bash
pip install build twine
bash scripts/build_and_publish.sh          # publish to PyPI
bash scripts/build_and_publish.sh --test   # publish to TestPyPI
```

---

## Included behaviour

- Create paints with required `room`, `shelf_level`, `shelf_depth`
- Room suggestions while typing; new room names are saved automatically
- Search paints by room, color, and coordinates
- Edit existing paints from the list (✏️ button)
- Confirmation/decline controls use green check and red X buttons
