# Canvas Todo Dashboard

Production-ready minimal todo dashboard that pulls assignments from Canvas LMS and displays them in a clean SaaS-style UI.

## Tech Stack

- Frontend: React + Vite, Tailwind CSS, shadcn-style components
- Backend: Node.js + Express
- Deploy: Vercel (frontend), Render (backend)

## Folder Structure

```text
todo/
  backend/
    src/
      canvasService.js
      server.js
    .env.example
    package.json
  frontend/
    src/
      components/ui/
        card.jsx
        checkbox.jsx
      lib/
        utils.js
      App.jsx
      index.css
      main.jsx
    .env.example
    package.json
    vite.config.js
    jsconfig.json
  render.yaml
  README.md
```

## Backend Setup

```bash
cd backend
cp .env.example .env
```

Set `CANVAS_API_KEY` in `backend/.env`.

Run:

```bash
npm install
npm run dev
```

Backend endpoint:

- `GET /api/todos` - fetches courses + assignments from Canvas, filters null `due_at`, sorts by due date, and groups by course.

## Frontend Setup

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Set `VITE_API_BASE_URL` to your backend URL:

- local: `http://localhost:8080`
- production example: `https://canvas-todo-backend.onrender.com`

## Deployment

### Backend on Render

1. Push repo to GitHub.
2. In Render, create a **Web Service** from repo.
3. Configure:
   - Root directory: `backend`
   - Build command: `npm install`
   - Start command: `npm run start`
4. Add env vars:
   - `CANVAS_API_KEY` (required, secret)
   - `CANVAS_BASE_URL=https://canvas.instructure.com/api/v1` (optional)
5. Deploy and copy the service URL.

Optional: use included `render.yaml` for Blueprint deployment.

### Frontend on Vercel

1. Import repo in Vercel.
2. Set project root to `frontend`.
3. Add environment variable:
   - `VITE_API_BASE_URL=<your Render backend URL>`
4. Deploy.

## Notes

- Canvas API key never appears in frontend code.
- Completion toggles are local-only UI state (no persistence).
- UI is responsive and optimized for quick scanning of due dates.
