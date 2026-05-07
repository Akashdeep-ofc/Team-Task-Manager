# Team Task Manager

A full-stack collaborative task management web application built with **FastAPI** and **React**. Supports project creation, team collaboration, task assignment, role-based access control, and a real-time project dashboard.

> Think of it as a simplified Trello/Asana — built from scratch.

---

## Live Demo

- **Frontend:** https://luminous-integrity-production-baaf.up.railway.app
- **Backend API Docs:** https://team-task-manager-production-16b1.up.railway.app

---

## Features

### Authentication
- Signup with username, email, and password
- Secure login with JWT-based authentication
- Protected routes — unauthenticated users are redirected to login

### Project Management
- Create projects (creator automatically becomes Admin)
- Admin and Member views — switch between projects you own vs projects you're a member of
- Delete projects (cascades to all tasks and memberships)

### Team Collaboration
- Admin can add members to a project by email
- Admin can remove members (their assigned tasks are automatically unassigned)
- Role-based access — Admin and Member roles enforced on both frontend and backend

### Task Management
- Create tasks with title, description, priority, due date, and status
- Assign tasks to project members
- Update task status: `To Do` → `In Progress` → `Done`
- Delete tasks (Admin only)
- Filter tasks by: All, By Status (Kanban view), Overdue, Per User

### Dashboard
- **Admin Dashboard:** Total tasks, tasks by status, tasks per user, overdue tasks
- **Member Dashboard:** Personal task summary — assigned tasks, status breakdown, overdue tasks

---

## Tech Stack

### Backend
| Tool | Purpose |
|---|---|
| FastAPI | REST API framework |
| SQLAlchemy | ORM for database interaction |
| PostgreSQL | Relational database |
| Pydantic | Data validation and serialization |
| JWT (python-jose) | Authentication tokens |
| Passlib + bcrypt | Password hashing |
| Uvicorn | ASGI server |

### Frontend
| Tool | Purpose |
|---|---|
| React 18 | UI library |
| React Router v6 | Client-side routing |
| Vite | Build tool and dev server |
| Vanilla CSS | Styling |

### Deployment
| Service | Purpose |
|---|---|
| Railway | Backend + Frontend hosting |
| Railway PostgreSQL | Managed database |

---

## Project Structure

```
team-task-manager/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── routes/
│   │   │           ├── user.py        # Auth + user routes
│   │   │           ├── project.py     # Project CRUD + member management
│   │   │           ├── task.py        # Task CRUD + assignment
│   │   │           └── dashboard.py   # Dashboard + filter routes
│   │   ├── core/
│   │   │   └── security.py            # JWT, password hashing
│   │   ├── db/
│   │   │   ├── base.py                # DeclarativeBase
│   │   │   └── session.py             # DB session + engine
│   │   ├── models/
│   │   │   └── models.py              # SQLAlchemy models
│   │   ├── schemas/
│   │   │   ├── user.py                # Pydantic schemas for User
│   │   │   ├── project.py             # Pydantic schemas for Project
│   │   │   └── task.py                # Pydantic schemas for Task
│   │   └── main.py                    # FastAPI app entry point
│   ├── requirements.txt
│   └── .env                           # Local environment variables (not committed)
│
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── Login.jsx
    │   │   ├── Signup.jsx
    │   │   ├── Projects.jsx           # Project list with Admin/Member toggle
    │   │   ├── ProjectDetail.jsx      # Kanban board + members panel
    │   │   └── Dashboard.jsx          # Project analytics
    │   ├── components/
    │   │   └── Navbar.jsx
    │   ├── api.js                     # All backend API calls
    │   ├── App.jsx                    # Routing
    │   └── index.css                  # Global styles
    ├── package.json
    └── .env                           # Local environment variables (not committed)
```

---

## Database Schema

```
users
  id, email, username, hashed_password

projects
  id, name, created_by (FK → users), created_at

project_members
  id, project_id (FK → projects), user_id (FK → users), role

tasks
  id, title, description, due_date, priority, status,
  project_id (FK → projects), assigned_to (FK → users), created_at
```

---

## API Overview

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/user` | Create account | Public |
| POST | `/user/token` | Login | Public |
| GET | `/user/project` | Get owned projects | Admin |
| POST | `/user/project` | Create project | Admin |
| DELETE | `/user/project/{id}` | Delete project | Admin |
| GET | `/user/project/{id}/members` | Get members | Admin |
| POST | `/user/project/{id}/add` | Add member | Admin |
| DELETE | `/user/project/{id}/members/{member_id}` | Remove member | Admin |
| GET | `/user/project/{id}/task` | Get tasks (with filters) | Admin + Member |
| POST | `/user/project/{id}/task` | Create task | Admin |
| PATCH | `/user/project/{id}/task/{task_id}` | Update task status | Admin + Member |
| DELETE | `/user/project/{id}/task/{task_id}` | Delete task | Admin |
| POST | `/user/project/{id}/task/{task_id}` | Assign task | Admin |
| GET | `/user/project/{id}/admin-dashboard-summary` | Admin dashboard | Admin |
| GET | `/user/project/{id}/member-dashboard-summary` | Member dashboard | Member |
| GET | `/user/member-projects` | Get projects as member | Member |

Full interactive API documentation available at `/docs` (Swagger UI).

---

## Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL

### Backend

```bash
# Clone the repo
git clone https://github.com/your-username/team-task-manager.git
cd team-task-manager/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Fill in your values (see Environment Variables section)

# Run the server
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### Frontend

```bash
cd team-task-manager/frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_BASE_URL=http://localhost:8000" > .env

# Start dev server
npm run dev
```

Frontend will be available at `http://localhost:5173`

---

## Environment Variables

### Backend `.env`
```
DATABASE_URL=postgresql://user:password@localhost:5432/taskmanager
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL=http://localhost:5173
```

### Frontend `.env`
```
VITE_BASE_URL=http://localhost:8000
```

---

## Deployment (Railway)

### Backend Service
1. Create a new service from your GitHub repo
2. Set **Root Directory** to `backend`
3. Set **Start Command** to:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Add environment variables in the **Variables** tab

### PostgreSQL
1. Add a new PostgreSQL database service in Railway
2. In your backend service variables, add:
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   ```

### Frontend Service
1. Create another service from the same repo
2. Set **Root Directory** to `frontend`
3. Set **Build Command** to:
   ```
   npm install && npm run build
   ```
4. Set **Start Command** to:
   ```
   npx serve -s dist -l $PORT
   ```
5. Add environment variable:
   ```
   VITE_BASE_URL=https://your-backend-url.up.railway.app
   ```

---

## Role-Based Access

| Action | Admin | Member |
|---|---|---|
| Create/Delete project | ✅ | ❌ |
| Add/Remove members | ✅ | ❌ |
| Create/Delete tasks | ✅ | ❌ |
| Assign tasks | ✅ | ❌ |
| View all tasks | ✅ | ❌ |
| View assigned tasks | ✅ | ✅ |
| Update task status | ✅ | ✅ (own tasks only) |
| Admin dashboard | ✅ | ❌ |
| Member dashboard | ❌ | ✅ |

---

## Author

Built as a full-stack coding assignment demonstrating REST API design, relational database modelling, JWT authentication, role-based access control, and React frontend development.
