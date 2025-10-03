# Technology Stack

## Backend

- **Framework**: FastAPI 0.100+
- **Language**: Python 3.9+
- **Data Processing**: pandas, numpy
- **Optimization**: OR-Tools (SCIP solver for MILP, CP-SAT solver for scheduling)
- **Server**: uvicorn

## Frontend

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **HTTP Client**: fetch API

## Data Layer

- CSV-based seed data (no database required for MVP)
- Files stored in `backend/data/seed/`

## Common Commands

### Backend

```bash
# Setup
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Run server
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Test
python -m pytest
```

### Frontend

```bash
# Setup
cd frontend
npm install

# Run dev server
npm run dev  # Runs on port 3000

# Build
npm run build
npm start
```

## Key Dependencies

- **ortools**: Mixed Integer Linear Programming (MILP) and Constraint Programming (CP-SAT) solvers
- **recharts**: Chart visualization library
- **fastapi**: Modern Python web framework
- **pandas**: Data manipulation and CSV handling
