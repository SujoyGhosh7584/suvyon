# Suvyon Frontend

React + TypeScript + Vite app for the Suvyon AI workspace.

## Stack

- React 18 + TypeScript
- Vite
- React Router
- TanStack Query
- Tailwind CSS
- Axios
- React Markdown

## Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

App runs at [http://localhost:3000](http://localhost:3000).

Backend should be available at `http://127.0.0.1:8000` (CORS already allows localhost:3000).

## Screens

- Landing
- Login / Register
- Workspace picker
- Overview dashboard
- Chat (conversations + RAG knowledge base selector)
- Agents (create, configure tools, run)
- Knowledge bases + document upload
- Settings (profile + password)
