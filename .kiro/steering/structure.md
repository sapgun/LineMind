# Project Structure

## Root Directory Layout

```
linemind-mvp/
├── backend/              # FastAPI backend services
├── frontend/             # Next.js frontend application
├── data/                 # Seed data and test datasets
├── docs/                 # Documentation and screenshots
├── .git/                 # Git repository
└── README.md             # Project overview
```

## Backend Structure

```
backend/
├── app.py                # FastAPI application entry point
├── data_loader.py        # CSV loading and validation
├── forecast.py           # Forecasting module (SimpleForecaster)
├── optimizer.py          # Production mix optimization (StubOptimizer, MilpOptimizer)
├── scheduler.py          # Workforce scheduling (StubScheduler, CpsatScheduler)
├── requirements.txt      # Python dependencies
└── data/
    └── seed/             # CSV seed data files
        ├── production_history.csv
        ├── lines.csv
        ├── workers.csv
        └── cost_params.csv
```

## Frontend Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx      # Home dashboard (main entry point)
│   │   └── layout.tsx    # Root layout
│   └── components/
│       ├── ForecastPage.tsx   # Forecasting UI
│       ├── OptimizePage.tsx   # Mix optimization UI
│       └── SchedulePage.tsx   # Scheduling UI
├── package.json          # Node dependencies
└── tailwind.config.js    # Tailwind CSS configuration
```

## Key Files

### Backend Core Modules

- **app.py**: Defines all API endpoints (`/health`, `/api/data/status`, `/api/forecast/run`, `/api/mix/optimize`, `/api/schedule/run`)
- **data_loader.py**: Central data access layer with CSV validation
- **forecast.py**: Moving average forecasting algorithm
- **optimizer.py**: MILP-based production mix optimization using OR-Tools
- **scheduler.py**: CP-SAT-based workforce scheduling using OR-Tools

### Frontend Pages

- **page.tsx**: Main dashboard with navigation to all features
- **ForecastPage.tsx**: Forecast execution and line chart visualization
- **OptimizePage.tsx**: Optimization execution with pie/bar charts and KPI cards
- **SchedulePage.tsx**: Schedule execution with table view and KPI cards

## Data Flow

1. CSV files → DataLoader → Backend modules
2. Backend API endpoints → Frontend fetch calls
3. Frontend state management → Recharts visualization

## Module Organization

Each backend module follows a class-based design:
- `__init__`: Initialize dependencies (DataLoader, other modules)
- `run_*`: Main execution method that returns standardized response format
- Helper methods: Algorithm-specific logic

Standard response format:
```python
{
    "status": "success" | "error",
    "data": {...},  # Module-specific results
    "message": "...",  # Optional error message
    "suggestion": "..."  # Optional error resolution hint
}
```
