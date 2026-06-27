# Todo App

A full stack todo application built with FastAPI, Supabase, and React.
Deployed on Google Cloud Run (backend) and Vercel (frontend).

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** Supabase (PostgreSQL)
- **Authentication:** Supabase Auth
- **Frontend:** React + Vite
- **Backend Deployment:** Google Cloud Run
- **Frontend Deployment:** Vercel

## Project Structure

```
TodoList/
├── backend/    → FastAPI Python backend
└── frontend/   → React + Vite frontend
```

## Backend Setup Locally

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your Supabase credentials:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
```

Start the server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

API docs available at: `http://localhost:8080/docs`

## Frontend Setup Locally

```bash
cd frontend
npm install
```

Copy `.env.example` to `.env` and set the backend URL:

```
VITE_API_URL=http://localhost:8080
```

Start the dev server:

```bash
npm run dev
```

App available at: `http://localhost:5173`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login user |
| POST | `/auth/logout` | Logout user |
| GET | `/auth/me` | Get current user |
| GET | `/todos/` | Get all todos |
| POST | `/todos/` | Create todo |
| PATCH | `/todos/{id}` | Update todo |
| PATCH | `/todos/{id}/complete` | Mark todo complete |
| DELETE | `/todos/{id}` | Delete todo |

## Supabase Tables

**todos** — `id, title, description, is_completed, user_id, created_at, updated_at`

**profiles** — `id, full_name, avatar_url, created_at`

Row Level Security is enabled on both tables.
