/**
 * Project plan data derived from PROJECT_PLAN.md for the progress dashboard.
 */

export type TaskStatus = 'done' | 'partial' | 'todo';

export interface Task {
  id: string;
  description: string;
  status: TaskStatus;
  files?: string;
  notes?: string;
}

export interface Phase {
  id: string;
  title: string;
  goal?: string;
  tasks: Task[];
  deliverable?: string;
}

export interface ArchitectureRow {
  layer: string;
  components: string;
  status: 'done' | 'partial' | 'todo';
}

export interface ProgressLogEntry {
  date: string;
  task: string;
  commit: string;
}

export interface ComponentStatus {
  component: string;
  path: string;
  notes?: string;
}

// --- Part I: Phases 1–4 ---

export const phase1: Phase = {
  id: 'phase1',
  title: 'Phase 1: UI Foundation (P0)',
  goal: 'Build the React frontend so users can interact with the chat API.',
  tasks: [
    { id: '1.1', description: 'Scaffold Vite + React + TypeScript project', status: 'done', files: 'ui/package.json, vite.config.ts, index.html, tsconfig.json' },
    { id: '1.2', description: 'Add Tailwind CSS', status: 'done', files: 'package.json, tailwind.config.js, postcss.config.js, index.css' },
    { id: '1.3', description: 'Define AgentEvent types', status: 'done', files: 'ui/src/types/agent.ts' },
    { id: '1.4', description: 'Implement chat API client', status: 'done', files: 'ui/src/api/chatApi.ts' },
    { id: '1.5', description: 'Implement useChat hook', status: 'done', files: 'ui/src/hooks/useChat.ts' },
    { id: '1.6', description: 'Build ChatWindow component', status: 'done', files: 'ui/src/components/chat/ChatWindow.tsx' },
    { id: '1.7', description: 'Build ChatInput component', status: 'done', files: 'ui/src/components/chat/ChatInput.tsx' },
    { id: '1.8', description: 'Build AssistantMessage component', status: 'done', files: 'ui/src/components/chat/AssistantMessage.tsx' },
    { id: '1.9', description: 'Build ThinkingIndicator', status: 'done', files: 'ui/src/components/chat/ThinkingIndicator.tsx' },
    { id: '1.10', description: 'Build SqlBlock (syntax highlight)', status: 'done', files: 'ui/src/components/chat/SqlBlock.tsx' },
    { id: '1.11', description: 'Build ResultTable', status: 'done', files: 'ui/src/components/chat/ResultTable.tsx' },
    { id: '1.12', description: 'Assemble App layout', status: 'done', files: 'ui/src/App.tsx, main.tsx' },
    { id: '1.13', description: 'Configure Vite proxy', status: 'done', files: 'ui/vite.config.ts' },
  ],
  deliverable: 'End-to-end flow: User types query → EventSource receives SSE → UI renders thinking/sql/result/token/done.',
};

export const phase2: Phase = {
  id: 'phase2',
  title: 'Phase 2: Configuration & Documentation (P1)',
  goal: 'Make the project easy to run and understand.',
  tasks: [
    { id: '2.1', description: 'Add .env.example', status: 'done', files: 'api/.env.example' },
    { id: '2.2', description: 'Write README', status: 'done', files: 'README.md' },
  ],
};

export const phase3: Phase = {
  id: 'phase3',
  title: 'Phase 3: Testing (P2)',
  goal: 'Add regression safety and confidence for future changes.',
  tasks: [
    { id: '3.1', description: 'Pytest setup', status: 'done', files: 'api/pytest.ini, api/conftest.py' },
    { id: '3.2', description: 'Test CodeAct tool', status: 'done', files: 'api/tests/test_codeact_tool.py' },
    { id: '3.3', description: 'Test DatabaseAdapter', status: 'done', files: 'api/tests/test_db_adapters.py' },
    { id: '3.4', description: 'Test SemanticLayer', status: 'done', files: 'api/tests/test_semantic_layer.py' },
    { id: '3.5', description: 'Test API routes', status: 'done', files: 'api/tests/test_routes.py' },
  ],
};

export const phase4: Phase = {
  id: 'phase4',
  title: 'Phase 4: Polish & Extensions (P3)',
  goal: 'Optional enhancements from PROMPT.md extension prompts.',
  tasks: [
    { id: '4.1', description: 'JWT authentication', status: 'done', notes: 'Auth middleware for API' },
    { id: '4.2', description: 'CSV export', status: 'done', notes: 'Download button in ResultTable' },
    { id: '4.3', description: 'Schema browser', status: 'done', notes: 'Sidebar showing tables/columns' },
    { id: '4.4', description: 'Chart UI', status: 'done', notes: 'Bar/line chart when result has numeric columns' },
  ],
};

// --- Part II: Phases A–D ---

export const phaseA: Phase = {
  id: 'phaseA',
  title: 'Phase A: Skill Registry + Redis Checkpointer',
  goal: 'Extensible skill registration and persistent checkpointer for HITL.',
  tasks: [
    { id: 'A.1', description: 'Add enabled_skills and related config to settings.py', status: 'done' },
    { id: 'A.2', description: 'Create api/src/skills/ with skill registry', status: 'done' },
    { id: 'A.3', description: 'Implement one built-in skill (e.g. export_result_csv) and register it', status: 'done' },
    { id: 'A.4', description: 'Wire enabled skills into deepagent_builder.py', status: 'done' },
    { id: 'A.5', description: 'Add Redis checkpointer and config', status: 'done' },
  ],
  deliverable: 'Agent can use configurable extra tools; graph state can persist in Redis.',
};

export const phaseB: Phase = {
  id: 'phaseB',
  title: 'Phase B: Human-in-the-Loop (Approve SQL Before Execution)',
  goal: 'Pause before executing SQL; user approves, rejects, or edits; then resume.',
  tasks: [
    { id: 'B.1', description: 'Design interrupt point: split plan SQL vs execute SQL', status: 'done' },
    { id: 'B.2', description: 'Implement graph change + emit interrupt payload in SSE', status: 'done' },
    { id: 'B.3', description: 'Add POST /api/chat/approve (or /resume)', status: 'done' },
    { id: 'B.4', description: 'Frontend: handle interrupt, SQL approval card, approve API, resume stream', status: 'done' },
  ],
  deliverable: 'User sees proposed SQL and can approve, reject, or edit before execution.',
};

export const phaseC: Phase = {
  id: 'phaseC',
  title: 'Phase C: SKILL.md Loader + Agent Calls MCP Tools',
  goal: 'Load Cursor/Codex SKILL.md into context; agent can call external MCP tools.',
  tasks: [
    { id: 'C.1', description: 'Add skill_loader.py — scan dirs for **/SKILL.md, parse', status: 'done' },
    { id: 'C.2', description: 'Inject selected SKILL.md into supervisor system prompt', status: 'done' },
    { id: 'C.3', description: 'Add api/src/mcp/ client: connect to MCP, fetch tools, convert to LangChain BaseTool', status: 'done' },
    { id: 'C.4', description: 'Config MCP_SERVERS; wire MCP tools into deepagent_builder.py', status: 'done' },
  ],
  deliverable: 'Agent has skill docs in prompt and can call external MCP tools.',
};

export const phaseD: Phase = {
  id: 'phaseD',
  title: 'Phase D: Expose App as MCP Server',
  goal: 'This app exposes a natural language → SQL → result tool via MCP.',
  tasks: [
    { id: 'D.1', description: 'Add MCP server (e.g. FastMCP) with tool query_database(question)', status: 'done' },
    { id: 'D.2', description: 'Mount MCP server on FastAPI and add config MCP_SERVER_*', status: 'done' },
    { id: 'D.3', description: 'Document MCP server usage and auth in README', status: 'done' },
  ],
  deliverable: 'External MCP clients can call this app to run NL→SQL queries.',
};

export const partIPhases: Phase[] = [phase1, phase2, phase3, phase4];
export const partIIPhases: Phase[] = [phaseA, phaseB, phaseC, phaseD];

// --- Architecture overview ---

export const architectureRows: ArchitectureRow[] = [
  { layer: 'UI Layer', components: 'React + EventSource, FastAPI API Gateway, Redis Session', status: 'partial' },
  { layer: 'DeepAgent Layer', components: 'Orchestrator, LLM Backend, Agent Memory, Tool Registry', status: 'done' },
  { layer: 'CodeAct Tool Layer', components: 'CodeAct Agent, SQL Query Builder, Semantic Layer, DatabaseAdapter', status: 'done' },
  { layer: 'Database Layer', components: 'PostgreSQL, Redis Cache, Bootstrap Scripts', status: 'done' },
];

// --- Completed components (Current Status) ---

export const completedComponents: ComponentStatus[] = [
  { component: 'API entry point', path: 'api/main.py', notes: 'FastAPI app, CORS, lifespan' },
  { component: 'Config', path: 'api/src/config/settings.py', notes: 'Pydantic BaseSettings' },
  { component: 'Database adapters', path: 'api/src/db/adapters/', notes: 'base, postgres, mysql, sqlite, factory' },
  { component: 'Semantic layer', path: 'api/src/semantic/', notes: 'models, registry, layer' },
  { component: 'Redis cache', path: 'api/src/cache/redis_client.py', notes: 'Result cache + session history' },
  { component: 'Agent core', path: 'api/src/agent/', notes: 'events, codeact_tool, deep_agent' },
  { component: 'API routes', path: 'api/src/api/routes/', notes: 'chat, health, schema' },
  { component: 'Schemas', path: 'api/src/api/schemas.py', notes: 'ChatRequest, ChatInitResponse' },
  { component: 'DB bootstrap', path: 'db/postgress/', notes: '00–09 SQL scripts' },
  { component: 'Docker deploy', path: 'deploy/', notes: 'docker-compose, Dockerfiles, nginx' },
];

// --- Progress log (Part I + Part II) ---

export const progressLogPartI: ProgressLogEntry[] = [
  { date: '2025-02-19', task: '1.1 + 1.2: Scaffold Vite+React+TS, Tailwind, Vite proxy', commit: 'd5e5819' },
  { date: '2025-02-19', task: '1.3: AgentEvent types', commit: '93364af' },
  { date: '2025-02-19', task: '1.4: Chat API client', commit: 'ef8ee54' },
  { date: '2025-02-19', task: '1.5: useChat hook', commit: '7e1c0c8' },
  { date: '2025-02-19', task: '1.6–1.12: Chat components + App layout', commit: '3474cc7' },
  { date: '2025-02-19', task: '2.1: .env.example', commit: '8980755' },
  { date: '2025-02-19', task: '2.2: README.md', commit: '799352e' },
  { date: '2025-02-19', task: '3.1–3.5: Pytest setup + tests', commit: '7801a86' },
  { date: '2025-02-19', task: '4.2: CSV export on ResultTable', commit: 'b8f5aba' },
  { date: '2025-02-19', task: '4.3: Schema browser sidebar', commit: '516e2bb' },
  { date: '2025-02-19', task: '4.4: Chart UI', commit: '43b368c' },
  { date: '2025-02-19', task: '4.1: JWT authentication', commit: '5e3a770' },
];

export const progressLogPartII: ProgressLogEntry[] = [
  { date: '2026-02-19', task: 'A.1: Settings for skills', commit: '3d3bbbe' },
  { date: '2026-02-19', task: 'A.2: Skill registry', commit: '2cc569f' },
  { date: '2026-02-19', task: 'A.3: Built-in skill (e.g. export_result_csv)', commit: '0f7e2ff' },
  { date: '2026-02-19', task: 'A.4: Wire skills into builder', commit: '8fd21e5' },
  { date: '2026-02-19', task: 'A.5: Redis checkpointer', commit: '18c519b' },
  { date: '2026-02-19', task: 'B.1: HITL design doc', commit: '16e9f2b' },
  { date: '2026-02-19', task: 'B.2: Interrupt in graph + SSE', commit: 'd6e00ec' },
  { date: '2026-02-19', task: 'B.3: POST /api/chat/approve', commit: '66f3c98' },
  { date: '2026-02-19', task: 'B.4: Frontend approval UI', commit: '4687387' },
  { date: '2026-02-19', task: 'C.1: skill_loader.py', commit: '6440fa2' },
  { date: '2026-02-19', task: 'C.2: Inject SKILL.md into prompt', commit: '94a9643' },
  { date: '2026-02-19', task: 'C.3: MCP client + tool conversion', commit: '7e70f7e' },
  { date: '2026-02-19', task: 'C.4: Wire MCP tools into builder', commit: 'dd3c3bd' },
  { date: '2026-02-19', task: 'D.1–D.3: MCP server + mount + docs', commit: 'e0be60d' },
];
