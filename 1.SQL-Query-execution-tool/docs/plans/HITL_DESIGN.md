# Human-in-the-Loop (HITL): Approve SQL Before Execution

**Status:** Design (B.1) — no code yet.  
**Goal:** Pause before executing SQL; user approves, rejects, or edits; then resume.

---

## 1. Current Flow

- **Supervisor** (built with `create_deep_agent`) has tools (`get_schema_context`, skills) and one subagent: **sql-executor**.
- **sql-executor** exposes a single tool: `execute_sql_query(nl_query, sql)`.
  - The subagent’s LLM produces SQL and calls this tool.
  - The tool calls `execute_sql` (in `src/tools/execute_sql.py`), which runs the query on the adapter and emits events (TOOL_CALL, SQL, EXECUTING, RESULT/ERROR).
- So today: “plan SQL” and “execute SQL” happen in one step inside the subagent tool. There is no pause for human approval.

---

## 2. Interrupt Point

We need to **split “plan SQL” from “execute SQL”** and insert an **interrupt** between them.

- **Before interrupt:** We have a proposed SQL (and the original natural-language query).
- **After interrupt:** User responds with approve / reject / edit (and optionally `edited_sql`).
- **Resume:** Graph continues: either execute the (possibly edited) SQL, or handle reject (e.g. return to supervisor or end with a message).

Because the current graph is built by `create_deep_agent` (from the deepagents library), we have two implementation approaches:

| Approach | Description | Pros / Cons |
|----------|-------------|-------------|
| **A. Custom graph** | Replace or wrap the supervisor/sql-executor flow with a LangGraph `StateGraph` that has an explicit “propose_sql” node and an “execute_sql” node, with `interrupt_before` (or `interrupt_after`) on the execute node. | Full control; clear state at interrupt. Requires building/maintaining our own graph and possibly duplicating some supervisor logic. |
| **B. Interrupt inside tool** | Keep `create_deep_agent` but change the sql-executor tool so it does not execute immediately: it returns “proposed SQL” and the graph is configured to interrupt after that tool (if the library supports it). On resume, a second tool or node runs the approved SQL. | Minimal change to graph structure if the library supports interrupt after a tool node. Depends on deepagents/LangGraph API. |

**Recommendation:** Prefer **Approach A** if we need guaranteed control over interrupt state and resume payload; use **Approach B** only if the existing graph can be configured with `interrupt_after` on the subagent’s tool node and we can pass the user’s decision into the state on resume.

---

## 3. State at Interrupt

When the graph pauses for approval, we must persist and expose:

- **thread_id** — LangGraph thread (from checkpointer); required to resume.
- **session_id** — Our chat session (for history and API correlation).
- **proposed_sql** — The SQL string to approve, reject, or edit.
- **nl_query** — Original user question (for re-execution and context).

Optional for product/UX:

- **dialect** — Database dialect (for display/editing hints).

This state is stored in the **checkpointer** (Redis or memory) so that when the client calls the resume API, we can load the same thread and inject the user’s decision.

---

## 4. SSE: `interrupt` Event

The stream that the frontend consumes (e.g. `GET /api/chat/stream/{stream_id}`) should emit a new event type when the graph is waiting for approval:

- **Event type:** `interrupt` (add to `EventType` in `src/agent/events.py`).
- **Payload (e.g. in `content` or a dedicated field):** At least `proposed_sql`, and optionally `thread_id`, `nl_query`, so the UI can show an approval card and later call the approve API with the right identifiers.

The client should treat `interrupt` as “stream is paused; show approval UI; do not expect more events until the user approves/rejects and the resume request is sent.”

---

## 5. Resume API

- **Endpoint:** `POST /api/chat/approve` (or `POST /api/chat/resume`).
- **Request body:**
  - `thread_id` (required) — So we can resume the correct graph state.
  - `session_id` (required) — For auth/history.
  - `action` (required): `"approve"` | `"reject"` | `"edit"`.
  - `edited_sql` (optional) — Required when `action == "edit"`; ignored otherwise.
- **Behaviour:**
  - Load thread state from checkpointer.
  - Inject the user’s decision (and, if edit, the new SQL) into state.
  - Resume the graph (e.g. `graph.invoke(..., config={"configurable": {"thread_id": thread_id}})`
  - Either:
    - Return 200 with a new `stream_id` and the client opens a new SSE to that stream, or
    - Same stream: response might indicate “resumed” and the client keeps listening to the existing stream for execute/result/done events (depends on how we implement streaming on resume).

**Recommendation:** Document in this design that we will choose one of “new stream on resume” vs “same stream continues” and implement consistently (B.2/B.3).

---

## 6. Graph Flow (Target)

High-level target flow:

1. User sends message → **Supervisor** (and optionally sql-executor) produces a **proposed SQL** (no execution yet).
2. Graph hits **interrupt** with state `{ thread_id, session_id, proposed_sql, nl_query }`.
3. SSE emits **interrupt** event; frontend shows approval card.
4. User approves / rejects / edits → **POST /api/chat/approve** with `thread_id`, `session_id`, `action`, optional `edited_sql`.
5. Backend resumes graph with the decision in state.
6. **Execute node** runs (approved or edited) SQL, or **reject path** returns a message without executing.
7. Result (or reject message) is streamed back; stream ends with **done**.

---

## 7. Dependencies

- **A.5 (Redis checkpointer):** For production, thread state must survive across requests; Redis checkpointer is required so that resume from another HTTP request sees the same state. In-memory checkpointer is acceptable for single-process dev only.
- **LangGraph:** Use `interrupt_before` / `interrupt_after` or in-node `interrupt()` and resume via `invoke` with the same `thread_id` and updated state (or a dedicated “human input” channel).

---

## 8. Implementation Order (Phase B)

| Step | Task | Notes |
|------|------|--------|
| B.1 | Design doc | This document. |
| B.2 | Graph change + SSE `interrupt` | Implement interrupt point and emit `interrupt` in stream. TDD: test stream yields interrupt event. |
| B.3 | `POST /api/chat/approve` | Request/response, resume graph, optional new stream. TDD: test approve/resume. |
| B.4 | Frontend approval UI | Handle `interrupt`, show card, call approve API, resume stream. |

---

## 9. Open Points

- **Same stream vs new stream on resume:** Decide and document in B.2/B.3.
- **Reject behaviour:** Whether to loop back to supervisor for a new plan or simply end with a message.
- **Edit:** Validation (e.g. SELECT-only) and who does it (backend vs frontend).
