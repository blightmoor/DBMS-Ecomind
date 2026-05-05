# EcoMind

Build sustainability like a product, not a spreadsheet.

EcoMind is a full-stack carbon intelligence platform for teams that want to track emissions, understand patterns, and take action with confidence.

## What EcoMind Does

- Captures real-world emission records across workflows
- Turns raw inputs into clear sustainability insights
- Provides AI-assisted recommendations for practical reductions
- Preserves traceability with auditable activity logs

## Features

- Role-based authentication and protected routes
- Emission data entry, storage, and analysis
- AI Insights and Recommendations modules
- Audit Logs for accountability and compliance
- Sustainability dashboards for progress tracking
- Admin area for organization and user management

## Tech Stack

- Frontend: SvelteKit + Tailwind CSS
- Backend: FastAPI (Python)
- Database: MySQL
- AI Layer: Python-based analytics and recommendation logic

## Screenshots

### Home
![Home Page](other/HomePage.png)

### Emissions
![Emission Page](other/EmissionPage.png)

## Project Structure

```text
DBMS_EcoMind/
|- backend/                     FastAPI services and DB scripts
|  |- main.py                   Backend entry point
|  |- check_structure.py        Database/schema checks
|  |- probe_emission_records_sql.py
|  \- insertValues/             Data insertion scripts
|- frontend/                    SvelteKit application
|  |- package.json
|  |- src/                      Routes, stores, and UI components
|  \- static/
|- other/                       Images and assets
\- README.md
```

## Quick Start

1. Clone the repo.
2. Configure your MySQL connection values for the backend.
3. Start the backend:

```bash
cd backend
uvicorn main:app --reload
```

4. Start the frontend:

```bash
cd frontend
npm install
npm run dev
```

5. Open the local frontend URL shown in the terminal.

## Vision

EcoMind is designed to make sustainability work measurable, explainable, and continuous, so teams can move from periodic reporting to everyday climate-aware decisions.
