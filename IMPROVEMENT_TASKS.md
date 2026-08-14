# Improvement Tasks — Autonomous Multi-Agent Support Orchestration

Branch: `feature/multi-agent-orchestrator`
Context: This is a working LangGraph-based support pipeline (memory → intent → planner → decision → tool_executor → response). The tool-selection layer is already LLM-driven (planner) with rule-based gating (decision engine). The gap: the **graph topology itself is linear/fixed** — no conditional routing between nodes — which undercuts the "autonomous" framing at the architecture level. Tasks below are ordered by priority.

Give this whole file to your IDE agent as-is. Each task lists exact files, current state, target state, and acceptance checks. Do tasks in order — later tasks assume earlier ones are done.

---

## Task 1 (P0): Wire real conditional routing into the LangGraph graph

**Problem:** `ai_core/workflow/decision_engine.py` already has a `route_after_intent(state) -> str` method that returns `"ticket"` or `"knowledge"` based on `state.intent.intent.value`. It is never called by the graph — only referenced in `tests/test_decision_engine.py`. `ai_core/graph/builder.py` wires every node in a strict linear chain with `graph.add_edge(...)` only; there is no `graph.add_conditional_edges(...)` call anywhere in the codebase.

**Target:** Make the graph route dynamically based on intent/confidence instead of always walking all six nodes for every request.

**Steps:**
1. Open `apps/backend/ai_core/graph/builder.py`.
2. After the `intent` node, add a conditional edge instead of the current fixed `graph.add_edge("intent", "planner")`:
   ```python
   def route_after_intent(state: SupportState) -> str:
       if state.intent is None:
           return "planner"
       # High-confidence general queries can skip the planner/tool loop entirely
       if (
           state.intent.intent.value == "general_query"
           and state.intent.confidence > 0.85
       ):
           return "response"
       return "planner"

   graph.add_conditional_edges(
       "intent",
       route_after_intent,
       {"planner": "planner", "response": "response"},
   )
   ```
3. Remove the old `graph.add_edge("intent", "planner")` line (replaced by the conditional edges above).
4. Import `route_after_intent` from `DecisionEngine` if you'd rather reuse the existing method instead of writing a new one inline — either is fine, but prefer reusing `engine.route_after_intent` from `ai_core/workflow/decision_engine.py` since it already exists and is tested. If you reuse it, adapt its return values (`"ticket"` / `"knowledge"`) to match real node names, or extend it with a third branch for the skip-to-response case above.
5. Delete `route_after_intent` from `decision_engine.py` only if you fully replace it with the graph-level version — otherwise keep both in sync (graph routing should call into `DecisionEngine`, not duplicate the rule).

**Acceptance check:** Send a request with an obviously high-confidence general query (e.g. "what are your business hours?") and confirm via logs/trace that `planner`, `decision`, and `tool_executor` nodes were skipped. Existing `test_graph_execution.py` should still pass for a refund-intent message (full path).

---

## Task 2 (P1): Move workflow rules out of hardcoded constants into config

**Problem:** `apps/backend/ai_core/workflow/rules.py` hardcodes `escalation_threshold: float = 0.7`, `knowledge_confidence_threshold: float = 0.8`, and the intent-to-tool mappings as a frozen dataclass. Changing these requires a code change and redeploy.

**Steps:**
1. Open `apps/backend/app/core/config.py`.
2. Add these settings to the `Settings` class:
   ```python
   ESCALATION_THRESHOLD: float = 0.7
   KNOWLEDGE_CONFIDENCE_THRESHOLD: float = 0.8
   ```
3. Open `apps/backend/ai_core/workflow/rules.py` and change `WorkflowRules` to read from `settings` at construction time instead of hardcoding:
   ```python
   from app.core.config import settings

   @dataclass(frozen=True)
   class WorkflowRules:
       knowledge_intents: tuple[IntentType, ...] = (...)  # unchanged
       ticket_intents: tuple[IntentType, ...] = (...)      # unchanged
       escalation_threshold: float = settings.ESCALATION_THRESHOLD
       knowledge_confidence_threshold: float = settings.KNOWLEDGE_CONFIDENCE_THRESHOLD
       default_tone: str = "professional"
   ```
4. Add both new keys to `apps/backend/env.example` with their default values and a one-line comment explaining what they control.

**Acceptance check:** Changing `ESCALATION_THRESHOLD` in `.env` and restarting the app changes escalation behavior without touching `rules.py`. `tests/test_decision_engine.py` still passes.

---

## Task 3 (P1): Track and expose LLM-fallback rate in observability

**Problem:** `ai_core/planner/planner.py`, `ai_core/agents/response_agent.py`, and `ai_core/rag/pipeline.py` all silently fall back to non-LLM logic (`_fallback_plan`, string concatenation, canned message) when an LLM call throws. This is good resilience design, but it's invisible — there's no metric for how often it happens.

**Steps:**
1. Open `apps/backend/ai_core/workflow/execution_trace.py` and check what fields `WorkflowTrace` (in `ai_core/observability/models.py`) currently exposes. Add a new counter field, e.g. `llm_fallback_count: int = 0`, and a helper function `record_llm_fallback(state: SupportState, component: str) -> None` alongside the existing `increment_llm_calls` / `mark_documents_retrieved` helpers.
2. In `ai_core/planner/planner.py`, inside the `except Exception:` block in `PlannerAgent.run()`, you'll need access to `state` to record this — if `run()` doesn't currently take `state`, either pass it in from `planner_node` (in `ai_core/agents/planner.py`) or return a flag on `ExecutionPlan` (e.g. add `used_fallback: bool = False` to `ai_core/models/execution_plan.py`) and let the caller record it.
3. Do the same for `ResponseAgent.execute()`'s `except Exception as e:` block in `ai_core/agents/response_agent.py`, and for `RAGPipeline.ask()`'s `except Exception:` block in `ai_core/rag/pipeline.py` (this one will need a similar plumbing decision since `RAGPipeline` doesn't currently receive `state`).
4. Surface the aggregate fallback count in whatever endpoint/dashboard already reads `WorkflowTrace` (check `app/schemas/trace.py` and `app/routers/` for an existing trace/metrics endpoint — `app/services/analytics_service.py` looks like the right home for an aggregate view).

**Acceptance check:** Temporarily break the LLM call (bad API key) and confirm the fallback counter increments and is visible via the trace/analytics endpoint, without the request failing.

---

## Task 4 (P1): Add behavior-level tests for the decision engine and tool executor

**Problem:** `tests/test_graph_execution.py` only asserts the graph ran and produced *a* decision (`assert result.decision is not None`), not that it produced the *correct* one. The decision engine and tool executor are the core of the "intelligent orchestration" claim and currently have the thinnest behavioral coverage relative to their importance.

**Steps:**
1. Create `apps/backend/tests/test_decision_engine_behavior.py` with cases that construct a `SupportState` with a specific `IntentOutput` and assert on `DecisionResult.modified_plan.tool_calls`:
   - Given `intent="refund_intent"` equivalent (`IntentType.REFUND`) with `confidence=0.9` → assert the resulting plan includes a `ToolCall(tool="ticket", ...)`.
   - Given `intent=IntentType.TECHNICAL_ISSUE` with `confidence=0.5` (below `escalation_threshold`) → assert the plan includes both `"ticket"` and `"human_review"` tool calls.
   - Given `intent=IntentType.GENERAL` with `confidence=0.9` → assert `"ticket"` is NOT present, and that it appears in `DecisionResult.blocked_tools` if it was in the original plan.
2. Create `apps/backend/tests/test_tool_executor_behavior.py`:
   - Mock or stub `tool_registry` entries for `knowledge`, `ticket`, `human_review` and assert `ToolExecutor.execute_plan()` returns a dict keyed by tool name with the right values, and that a failing tool doesn't take down the others (there's already a try/except around `tool_executor.execute_plan(plan)` in `ai_core/agents/tool_executor.py` — write a test that a raised exception inside one tool's `execute()` is caught at the `tool_executor_node` level and doesn't propagate).
3. Use the existing test patterns in `tests/test_decision_engine.py` and `tests/test_ticket_tool.py` as your template for fixtures — don't invent a new test-setup style.

**Acceptance check:** `pytest apps/backend/tests/test_decision_engine_behavior.py apps/backend/tests/test_tool_executor_behavior.py` passes and each test fails if you comment out the relevant rule in `rules.py` or `decision_engine.py` (mutation-test it manually once to confirm the tests actually catch a broken rule).

---

## Task 5 (P2): Add a retrieval-quality smoke test for RAG

**Problem:** `ai_core/knowledge/retriever.py` and `ai_core/rag/pipeline.py` are real, working retrieval code against a live Chroma store (`apps/backend/chroma_db/`) — but there is no test asserting that a known question actually retrieves the right policy document from `apps/backend/knowledge_base/`.

**Steps:**
1. Create `apps/backend/tests/test_rag_retrieval_quality.py`.
2. For each file in `knowledge_base/` (`faq.md`, `refund_policy.md`, `shipping_policy.md`, `warrenty_policy.md`), write one test that asks a question clearly tied to that document (e.g. "How long do I have to request a refund?" → expect `refund_policy.md` content to appear in the top-3 retrieved chunks) and assert the retrieved `Document.page_content` or `Document.metadata` (check what metadata `ai_core/knowledge/loader.py` and `ai_core/knowledge/chunker.py` attach — likely a `source` field) matches the expected source file.
3. If chunk metadata doesn't currently include the source filename, add it in `ai_core/knowledge/loader.py` at ingestion time so tests (and future debugging) can trace a retrieved chunk back to its source doc.

**Acceptance check:** All four smoke tests pass against the existing `chroma_db/` store. If they don't, that's a real retrieval-quality bug worth knowing about now rather than after a demo.

---

## Task 6 (P2): Security/config pass

**Steps:**
1. Open `apps/backend/app/core/config.py` and confirm `DEBUG: bool = True` is NOT the effective default in a way that could ship to production — either make it read from `ENVIRONMENT` (e.g. `DEBUG = ENVIRONMENT == "development"`) or explicitly document that `.env` must override it in production.
2. Open `apps/backend/env.example` and confirm no real secret values are present (only placeholders like `GOOGLE_API_KEY=your-key-here`). Cross-check against `.gitignore` that `.env` itself (not `env.example`) is excluded from git.
3. Re-read `app/core/security.py` and `app/middleware/auth.py` given the commit history shows a password-verification bypass was fixed (`fix(Task7): Remove password verification bypass`) — confirm there's a regression test for this in `tests/` so it can't silently reappear. If not, add one asserting a wrong password is rejected.

**Acceptance check:** No secrets in any committed file; a test exists that fails if password verification is ever bypassed again.

---

## Task 7 (P3): Clean up root-level status file sprawl

**Problem:** Repo root has `PROJECT_STATUS.md`, `PROJECT_STATUS2.md`, `PROJECT_STATUS3.md`, and `PROJECT_TREE.md` alongside `README.md`. Multiple numbered status files read as in-progress scratch notes rather than intentional documentation, which undercuts the project's credibility for anyone reviewing it (professor, recruiter, patent reviewer).

**Steps:**
1. Read all three `PROJECT_STATUS*.md` files and merge anything still accurate into a single `PROJECT_STATUS.md` (or rename to `CHANGELOG.md` if the content is chronological).
2. Delete `PROJECT_STATUS2.md` and `PROJECT_STATUS3.md` after merging.
3. Confirm `PROJECT_TREE.md` is either auto-generated (add a comment noting how to regenerate it, e.g. `tree > PROJECT_TREE.md`) or delete it if `README.md` already documents structure well enough.
4. Update `README.md`'s architecture/tech-stack section to reflect what's actually implemented on this branch (LangGraph with the new conditional routing from Task 1, real RAG via Chroma, LLM-driven planner) rather than describing the older linear-pipeline design from the `feature/backend-foundation` branch.

**Acceptance check:** Repo root has one clear status doc, not three; README accurately describes the current branch's architecture.

---

## Suggested execution order for the IDE agent

Do Task 1 first and get it fully working and tested before moving on — it's the one change that meaningfully upgrades the "autonomous" claim, and later tasks (4, in particular) should test against the post-Task-1 graph shape, not the old linear one. Tasks 2, 3, 5, 6 can be done in any order after that. Task 7 last, since it documents the end state.
