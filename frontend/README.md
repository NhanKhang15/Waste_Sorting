# Frontend

The frontend is a Vite + React + TypeScript dashboard for submitting waste queries and visualizing backend results.

## Features

- image upload and DSL query form
- SAHI toggle for sliced inference
- detection overlay canvas
- normalized DSL viewer
- token stream display
- semantic AST and formal parse tree visualization
- engine decision and confidence summary

## Setup

```powershell
cd frontend
npm install
Copy-Item .env.example .env
```

Default API target:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Development

```powershell
npm.cmd run dev
```

If PowerShell blocks `npm.ps1`, use `npm.cmd` instead of `npm`.

## Production build

```powershell
npm.cmd run build
```

## Lint

```powershell
npm.cmd run lint
```

## Notes

- Routes are lazy-loaded in `src/App.tsx`.
- The dashboard expects the backend `WasteFindResponse` shape from `/api/v1/waste/find`.
- `react-d3-tree` is used for both the semantic AST and formal ANTLR parse tree.
