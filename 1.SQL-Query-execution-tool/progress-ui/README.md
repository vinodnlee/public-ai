# Project Progress UI

Standalone dashboard to visualize task progress for **DeepAgent SQL Chat**, based on `PROJECT_PLAN.md`.

## Run

```bash
cd progress-ui
npm install
npm run dev
```

Open **http://localhost:5174**.

## Build

```bash
npm run build
npm run preview   # preview production build
```

## Data source

Task and phase data is defined in `src/data/projectPlan.ts`. Update that file when `PROJECT_PLAN.md` changes to keep the dashboard in sync.
