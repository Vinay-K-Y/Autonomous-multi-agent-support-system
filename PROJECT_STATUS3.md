# Project Status 3: Complete Architecture & File Documentation

## Overview
Autonomous Multi-Agent Support System - A LangGraph-based multi-agent system for customer support automation with observability/tracing capabilities.

## Complete Project Structure

```
apps/backend/
├── ai_core/              # Core AI/agent system
│   ├── __init__.py       # Empty init file
│   ├── agents/           # Agent implementations
│   ├── graph/            # LangGraph workflow
│   ├── observability/    # Tracing system
│   ├── tools/            # Tool system
│   ├── workflow/         # Decision engine
│   ├── state/            # State management
│   ├── models/           # Pydantic models
│   ├── planner/          # Planning agent
│   ├── llm/              # LLM integration
│   ├── memory/           # Conversation memory
│   ├── knowledge/        # RAG/knowledge
│   ├── rag/              # RAG pipeline
│   ├── prompts/          # LLM prompts
│   ├── integrations/     # External integrations
│   └── orchestrator/     # Workflow orchestration
├── app/                  # FastAPI application
│   ├── main.py           # FastAPI app entry point
│   ├── core/             # Core configuration
│   ├── middleware/       # HTTP middleware
│   ├── models/           # API models
│   ├── routers/          # API routes
│   └── services/         # Business logic services
├── api/                  # API layer (empty)
├── tests/                # Test suite
├── scripts/              # Utility scripts
├── knowledge_base/      # Knowledge documents
├── chroma_db/           # Vector database storage
└── pyproject.toml       # Python dependencies
```

---

## DETAILED FILE-BY-FILE DOCUMENTATION

### ROOT LEVEL FILES

**`.env.example`** - Environment variables template (empty)

**`.gitignore`** - Git ignore patterns

**`README.md`** - Project documentation

**`PROJECT_STATUS.md`** - Previous project status documentation

**`PROJECT_STATUS2.md`** - Previous project status documentation

**`PROJECT_STATUS3.md`** - This file - complete architecture documentation

---

## AI_CORE MODULE

### `ai_core/__init__.py`
Empty init file for the ai_core package.

---

### AI_CORE/AGENTS - Agent Implementations

#### `ai_core/agents/__init__.py`
Empty init file.

#### `ai_core/agents/base_agent.py`
**Purpose**: Abstract base class for all agents
**Key Components**:
- `BaseAgent` abstract class with `async execute(state: SupportState) -> SupportState` method
- All agents inherit from this base class

#### `ai_core/agents/intent_agent.py`
**Purpose**: Detects user intent using LLM
**Key Components**:
- `IntentAgent` class inheriting from BaseAgent
- Uses LLM to classify customer messages into intent types
- Returns `IntentOutput` with intent, confidence, and reasoning
- Traces execution with timing and LLM call tracking
- **Traced**: `@traced("intent")` decorator on node

#### `ai_core/agents/planner.py`
**Purpose**: Creates execution plans for tool calls
**Key Components**:
- `PlannerAgent` class (not inheriting from BaseAgent)
- `async run(query: str)` method returns `ExecutionPlan`
- Uses LLM to decide which tools to call
- Has fallback planning if LLM unavailable
- **Traced**: `@traced("planner")` decorator on node

#### `ai_core/agents/decision.py`
**Purpose**: Evaluates and approves execution plans
**Key Components**:
- `decision_node` async function (not a class)
- Uses `DecisionEngine` to evaluate plans
- Currently auto-approves all plans
- Sets `state.decision` with approval status
- **Traced**: `@traced("decision")` decorator on node

#### `ai_core/agents/tool_executor.py`
**Purpose**: Executes tools from approved plans
**Key Components**:
- `tool_executor_node` async function
- Checks if plan exists and is approved
- Uses `ToolExecutor.execute_plan()` to run tools
- Stores results in `state.tool_results`
- **Traced**: `@traced("tool_executor")` decorator on node

#### `ai_core/agents/knowledge_agent.py`
**Purpose**: Retrieves knowledge from knowledge base
**Key Components**:
- `KnowledgeAgent` class inheriting from BaseAgent
- Simple keyword-based knowledge retrieval (refund → refund policy)
- Returns `KnowledgeOutput` with answer and sources
- Tracks document retrieval count
- **Traced**: `@traced("knowledge")` decorator on node

#### `ai_core/agents/ticket_agent.py`
**Purpose**: Creates support tickets when needed
**Key Components**:
- `TicketAgent` class inheriting from BaseAgent
- Checks if intent requires ticket (refund, technical_issue)
- Uses `tool_executor.execute("ticket")` to create tickets
- Returns `TicketOutput` with ticket_id
- **Traced**: `@traced("ticket")` decorator on node

#### `ai_core/agents/response_agent.py`
**Purpose**: Generates final response to customer
**Key Components**:
- `ResponseAgent` class inheriting from BaseAgent
- Combines results from knowledge, ticket, and memory tools
- Handles blocked decisions from decision engine
- Updates conversation history with user/assistant messages
- Returns `ResponseOutput` with response, tone, and follow-up actions
- **Traced**: `@traced("response")` decorator on node
- **Workflow Finalization**: Calls `state._tracer.finish_workflow()` after execution

#### `ai_core/agents/memory_agent.py`
**Purpose**: Loads conversation history into state
**Key Components**:
- `MemoryAgent` class (not inheriting from BaseAgent)
- `async run(state: SupportState)` method
- Uses `tool_executor.execute("memory")` to retrieve history
- Sets `state.conversation_history`
- **Not traced**: Sync node in graph

#### `ai_core/agents/human_review_agent.py`
**Purpose**: Determines if human review is needed
**Key Components**:
- `HumanReviewAgent` class inheriting from BaseAgent
- Checks intent confidence (< 0.70 triggers review)
- Sets `state.human_review` with required status and reason
- **Not traced**: Sync node in graph

---

### AI_CORE/GRAPH - LangGraph Workflow

#### `ai_core/graph/__init__.py`
**Exports**: `support_graph`, `invoke_sync`

#### `ai_core/graph/builder.py`
**Purpose**: Builds and compiles the LangGraph workflow
**Key Components**:
- `StateGraph(SupportState)` - LangGraph graph definition
- `_run_async()` - Helper to run async functions in sync context
- Sync wrapper functions for all async nodes:
  - `memory_node`, `intent_node_sync`, `planner_node_sync`
  - `decision_node_sync`, `tool_executor_node_sync`
  - `knowledge_node_sync`, `ticket_node_sync`
  - `human_review_node_sync`, `response_node_sync`
- Graph edges: `START → memory → intent → planner → decision → tool_executor → response → END`
- `SupportGraphWrapper` class wraps compiled graph for sync/async invocation
- `support_graph` - Main graph instance
- `invoke_sync()` - Sync invocation helper

#### `ai_core/graph/nodes.py`
**Purpose**: Defines async node functions for the graph
**Key Components**:
- Agent instances: `intent_agent`, `knowledge_agent`, `ticket_agent`, `human_review_agent`, `response_agent`
- Async node functions with `@traced` decorators:
  - `@traced("intent")` - `intent_node()`
  - `@traced("knowledge")` - `knowledge_node()`
  - `@traced("ticket")` - `ticket_node()`
  - `@traced("response")` - `response_node()` (with workflow finalization)
- `human_review_node()` - No tracing decorator

#### `ai_core/graph/router.py`
**Purpose**: Routing function for graph navigation
**Key Components**:
- `route_after_intent(state)` - Uses DecisionEngine to route after intent detection
- Currently routes to "ticket" or "knowledge" based on intent

---

### AI_CORE/OBSERVABILITY - Tracing System

#### `ai_core/observability/__init__.py`
Empty init file.

#### `ai_core/observability/tracer.py`
**Purpose**: Workflow and agent execution tracing
**Key Components**:
- `WorkflowTracer` class:
  - `__init__()` - Creates workflow with unique ID and start time
  - `start_agent(name, summary)` - Starts tracing an agent
  - `finish_agent(output)` - Finishes agent trace, calculates duration
  - `fail_agent(error)` - Marks agent as failed with error
  - `finish_workflow()` - Finishes workflow, calculates total duration
- Stores traces in `WorkflowTrace` model

#### `ai_core/observability/decorators.py`
**Purpose**: `@traced` decorator for automatic agent tracing
**Key Components**:
- `@traced(agent_name)` decorator:
  - Creates tracer if not exists on state
  - Attaches tracer to `state._tracer`
  - Calls `tracer.start_agent()` before execution
  - Calls `tracer.finish_agent()` after successful execution
  - Calls `tracer.fail_agent()` on exception
  - Attaches trace to `state.trace`

#### `ai_core/observability/models.py`
**Purpose**: Pydantic models for tracing data
**Key Components**:
- `AgentTrace` model:
  - `agent` - Agent name
  - `started_at`, `finished_at` - Timestamps
  - `duration_ms` - Execution duration
  - `status` - "running", "completed", or "failed"
  - `input_summary`, `output_summary` - Execution summaries
  - `error` - Error message if failed
- `WorkflowTrace` model:
  - `workflow_id` - Unique workflow identifier
  - `traces` - List of AgentTrace objects
  - `started_at`, `finished_at` - Workflow timestamps
  - `total_duration_ms` - Total workflow duration

---

### AI_CORE/TOOLS - Tool System

#### `ai_core/tools/__init__.py`
**Purpose**: Registers all tools in the tool registry
**Key Components**:
- Imports: `tool_registry`, all tool classes
- Registers: `KnowledgeTool()`, `TicketTool()`, `MemoryTool()`, `HumanReviewTool()`

#### `ai_core/tools/base_tool.py`
**Purpose**: Abstract base class for all tools
**Key Components**:
- `BaseTool` abstract class:
  - `name: str` - Tool name
  - `description: str` - Tool description
  - `execute(**kwargs)` - Abstract execute method

#### `ai_core/tools/executor.py`
**Purpose**: Executes tools and execution plans
**Key Components**:
- `ToolExecutor` class:
  - `execute(tool_name, **kwargs)` - Executes single tool with parameter normalization
  - `execute_plan(plan)` - Executes all tools in an ExecutionPlan
- Parameter normalization: maps `query` → `question`, `conversation_id` → `conversation`
- `tool_executor` - Global instance

#### `ai_core/tools/registry.py`
**Purpose**: Central registry for tool management
**Key Components**:
- `ToolRegistry` class:
  - `register(tool)` - Registers a tool by name
  - `get(name)` - Retrieves a tool by name
  - `list_tools()` - Returns list of tool names
- `tool_registry` - Global instance

#### `ai_core/tools/knowledge_tool.py`
**Purpose**: Knowledge base search tool
**Key Components**:
- `KnowledgeTool` class inheriting from BaseTool
- `name = "knowledge"`
- Uses `RAGPipeline` for knowledge retrieval
- `execute(question, conversation)` - Returns answer from RAG pipeline

#### `ai_core/tools/ticket_tool.py`
**Purpose**: Support ticket creation tool
**Key Components**:
- `TicketTool` class inheriting from BaseTool
- `name = "ticket"`
- `execute(priority, summary, description)` - Creates ticket with UUID
- Returns `TicketOutput` or dict with ticket details

#### `ai_core/tools/memory_tool.py`
**Purpose**: Conversation history retrieval tool
**Key Components**:
- `MemoryTool` class inheriting from BaseTool
- `name = "memory"`
- `execute(conversation_id)` - Returns formatted conversation history

#### `ai_core/tools/human_review_tool.py`
**Purpose**: Human review escalation tool
**Key Components**:
- `HumanReviewTool` class inheriting from BaseTool
- `name = "human_review"`
- `execute(required, reason)` - Returns `HumanReview` object

---

### AI_CORE/WORKFLOW - Decision Engine & Routing

#### `ai_core/workflow/__init__.py`
**Exports**: `DecisionEngine`, `WORKFLOW_RULES`, `WorkflowRules`, execution trace functions

#### `ai_core/workflow/decision_engine.py`
**Purpose**: Decision engine for workflow routing and approval
**Key Components**:
- `DecisionEngine` class:
  - `route_after_intent(state)` - Routes to "ticket" or "knowledge" based on intent
  - `should_retrieve_knowledge(state)` - Determines if knowledge retrieval needed
  - `should_create_ticket(state)` - Determines if ticket creation needed
  - `should_escalate(state)` - Determines if human escalation needed (confidence < threshold)
  - `evaluate(state)` - Evaluates execution plan (currently auto-approves)
  - `record_agent()` - Records agent execution in metadata
  - `track_knowledge()` - Tracks document retrieval count
  - `track_llm_call()` - Tracks LLM API call count

#### `ai_core/workflow/rules.py`
**Purpose**: Workflow routing configuration
**Key Components**:
- `WorkflowRules` dataclass:
  - `knowledge_intents` - Tuple of intents requiring knowledge
  - `ticket_intents` - Tuple of intents requiring tickets
  - `escalation_threshold` - Confidence threshold for escalation (0.7)
  - `knowledge_confidence_threshold` - Knowledge confidence threshold (0.8)
  - `default_tone` - Default response tone ("professional")
- `WORKFLOW_RULES` - Global frozen instance

#### `ai_core/workflow/execution_trace.py`
**Purpose**: Execution tracking and metrics
**Key Components**:
- `start_agent_timer()` - Returns perf_counter timestamp
- `record_agent_execution(state, agent_name, started_at, details, extra)` - Records agent timing and metadata
- `increment_llm_calls(state, count)` - Increments LLM call counter
- `mark_documents_retrieved(state, count)` - Records document retrieval count
- `finalize_processing_time(state, started_at)` - Finalizes total processing time

#### `ai_core/workflow/router.py`
Empty file (placeholder for future routing logic).

---

### AI_CORE/STATE - State Management

#### `ai_core/state/__init__.py`
**Exports**: SupportState

#### `ai_core/state/support_state.py`
**Purpose**: Central state object flowing through the workflow
**Key Components**:
- `SupportState` Pydantic BaseModel:
  - `request: CustomerRequest` - User input
  - `metadata: ProcessingMetadata` - Execution metadata
  - `intent: IntentOutput | None` - Detected intent
  - `knowledge: KnowledgeOutput | None` - Retrieved knowledge
  - `response: ResponseOutput | None` - Generated response
  - `ticket: TicketOutput | None` - Created ticket
  - `human_review: HumanReview` - Human review status
  - `workflow: WorkflowContext` - Workflow context
  - `trace: WorkflowTrace | None` - Execution trace
  - `conversation_history: str` - Conversation context
  - `execution_plan: ExecutionPlan | None` - Planner output
  - `decision: DecisionResult | None` - Decision engine output
  - `tool_results: dict` - Tool execution results

---

### AI_CORE/MODELS - Pydantic Data Models

#### `ai_core/models/__init__.py`
Empty init file.

#### `ai_core/models/customer_request.py`
**Purpose**: Customer request input model
**Key Components**:
- `CustomerRequest` BaseModel:
  - `message: str` - Customer's support message
  - `customer_id: str | None` - Customer identifier
  - `conversation_id: str` - Conversation identifier (auto-generated UUID)
  - `language: str` - Message language (default "en")
  - `attachments: list[str]` - File attachments
  - `channel: str` - Communication channel (default "web")
  - `metadata: dict` - Additional metadata

#### `ai_core/models/intent.py`
**Purpose**: Intent classification model
**Key Components**:
- `IntentType` enum: `REFUND`, `TECHNICAL_ISSUE`, `BILLING`, `DELIVERY`, `ACCOUNT`, `GENERAL`, `OTHER`
- `IntentOutput` BaseModel:
  - `intent: IntentType` - Detected intent
  - `confidence: float` - Confidence score (0-1)
  - `reasoning: str` - Explanation of intent choice

#### `ai_core/models/knowledge.py`
**Purpose**: Knowledge retrieval output model
**Key Components**:
- `KnowledgeSource` BaseModel:
  - `title: str` - Document title
  - `source: str` - Document source
  - `confidence: float` - Source confidence
- `KnowledgeOutput` BaseModel:
  - `answer: str` - Knowledge answer
  - `sources: list[KnowledgeSource]` - Source documents
  - `confidence: float` - Overall confidence

#### `ai_core/models/ticket.py`
**Purpose**: Ticket creation output model
**Key Components**:
- `TicketOutput` BaseModel:
  - `ticket_required: bool` - Whether ticket was created
  - `ticket_id: str | None` - Ticket identifier
  - `priority: str` - Ticket priority
  - `assigned_team: str | None` - Assigned team

#### `ai_core/models/response.py`
**Purpose**: Response generation output model
**Key Components**:
- `ResponseOutput` BaseModel:
  - `response: str` - Generated response text
  - `tone: str` - Response tone (default "professional")
  - `follow_up_actions: list[str]` - Suggested follow-up actions
  - `confidence: float` - Response confidence

#### `ai_core/models/human_review.py`
**Purpose**: Human review status model
**Key Components**:
- `HumanReview` BaseModel:
  - `required: bool` - Whether human review is needed
  - `reason: str | None` - Reason for review
  - `reviewer: str | None` - Assigned reviewer
  - `approved: bool | None` - Review approval status

#### `ai_core/models/metadata.py`
**Purpose**: Processing metadata model
**Key Components**:
- `ProcessingMetadata` BaseModel:
  - `request_id: str` - Request identifier
  - `started_at: datetime` - Request start time
  - `processing_time_ms: float` - Total processing time
  - `llm_provider: str` - LLM provider used
  - `llm_model: str` - LLM model used
  - `workflow_version: str` - Workflow version
  - `routing_reasons: list[str]` - Routing decision reasons
  - `agent_timings: dict[str, float]` - Agent execution timings
  - `retrieved_documents: int` - Number of documents retrieved
  - `llm_call_count: int` - Number of LLM API calls
  - `execution_trace: dict` - Execution trace data
  - `planner_reasoning: str` - Planner reasoning
  - `decision_reasoning: str` - Decision reasoning
  - `blocked_tools: list[str]` - Blocked tools list

#### `ai_core/models/execution_plan.py`
**Purpose**: Execution plan model from planner
**Key Components**:
- `ExecutionPlan` BaseModel:
  - `reasoning: str` - Plan reasoning
  - `tool_calls: list[ToolCall]` - List of tool calls to execute

#### `ai_core/models/tool_call.py`
**Purpose**: Individual tool call model
**Key Components**:
- `ToolCall` BaseModel:
  - `tool: str` - Tool name
  - `parameters: dict[str, Any]` - Tool parameters

#### `ai_core/models/decision.py`
**Purpose**: Decision engine output model
**Key Components**:
- `DecisionResult` BaseModel:
  - `approved: bool` - Whether plan is approved
  - `reasoning: str` - Decision reasoning
  - `modified_plan: ExecutionPlan | None` - Modified plan if any
  - `blocked_tools: list[str]` - List of blocked tools

#### `ai_core/models/workflow.py`
**Purpose**: Workflow context model
**Key Components**:
- `WorkflowContext` BaseModel:
  - `current_agent: str | None` - Currently executing agent
  - `completed_agents: list[str]` - List of completed agents
  - `next_agent: str | None` - Next agent to execute
  - `retry_count: int` - Number of retries
  - `status: str` - Workflow status (default "running")

---

### AI_CORE/PLANNER - Planning Agent

#### `ai_core/planner/__init__.py`
Empty init file.

#### `ai_core/planner/planner.py`
**Purpose**: Planner agent for tool selection
**Key Components**:
- `PlannerAgent` class:
  - `async run(query: str)` - Returns `ExecutionPlan`
  - Uses LLM to generate structured execution plan
  - Has fallback planning if LLM unavailable
  - Fallback logic: keyword-based tool selection (refund → ticket, etc.)

#### `ai_core/planner/planner_prompt.py`
**Purpose**: LLM prompt for planning agent
**Key Components**:
- `PLANNER_PROMPT` - ChatPromptTemplate:
  - Instructs LLM to decide which tools to execute (not answer customer)
  - Lists available tools: knowledge, ticket, memory, human_review
  - Returns structured output only

---

### AI_CORE/LLM - LLM Integration

#### `ai_core/llm/__init__.py`
Empty init file.

#### `ai_core/llm/base.py`
**Purpose**: Abstract base class for LLM providers
**Key Components**:
- `BaseLLMProvider` abstract class:
  - `async generate_structured(prompt, output_schema, variables)` - Generate structured output
  - `async generate(prompt)` - Generate plain text output

#### `ai_core/llm/factory.py`
**Purpose**: Factory for creating LLM provider instances
**Key Components**:
- `LLMFactory` class:
  - `create()` - Creates provider based on `settings.LLM_PROVIDER`
  - Currently supports "gemini" only

#### `ai_core/llm/gemini.py`
**Purpose**: Google Gemini LLM provider implementation
**Key Components**:
- `GeminiProvider` class inheriting from BaseLLMProvider:
  - Uses `ChatGoogleGenerativeAI` from langchain-google-genai
  - `async generate(prompt)` - Plain text generation with error handling
  - `async generate_structured(prompt, output_schema, variables)` - Structured output with schema validation

#### `ai_core/llm/service.py`
**Purpose**: LLM service layer
**Key Components**:
- `LLMService` class:
  - `__init__()` - Creates provider via LLMFactory
  - `get()` - Returns provider's model
  - `async generate_structured()` - Delegates to provider with fallback logic
- Fallback logic: Returns default IntentOutput if LLM unavailable
- `llm_service` - Global instance

#### `ai_core/llm/client.py`
**Purpose**: Simple LLM client for direct usage
**Key Components**:
- `LLMClient` class:
  - `async ask(prompt)` - Simple question-answering with error handling
- `llm_client` - Global instance

#### `ai_core/llm/models.py`
Empty file (placeholder for future LLM models).

---

### AI_CORE/MEMORY - Conversation Memory

#### `ai_core/memory/__init__.py`
Empty init file.

#### `ai_core/memory/models.py`
**Purpose**: Memory data models
**Key Components**:
- `ConversationMessage` BaseModel:
  - `role: Literal["system", "user", "assistant"]` - Message role
  - `content: str` - Message content
  - `timestamp: datetime` - Message timestamp
- `ConversationHistory` BaseModel:
  - `conversation_id: str` - Conversation identifier
  - `messages: list[ConversationMessage]` - List of messages

#### `ai_core/memory/memory_store.py`
**Purpose**: In-memory storage for conversations
**Key Components**:
- `MemoryStore` class:
  - `_store: dict[str, ConversationHistory]` - In-memory storage
  - `get(conversation_id)` - Gets or creates conversation history
  - `add_message(conversation_id, message)` - Adds message to history
  - `clear(conversation_id)` - Clears conversation history
- Note: Can be replaced with Redis/PostgreSQL/MongoDB

#### `ai_core/memory/conversation_manager.py`
**Purpose**: High-level conversation management interface
**Key Components**:
- `ConversationManager` class:
  - `add_user_message(conversation_id, message)` - Adds user message
  - `add_assistant_message(conversation_id, message)` - Adds assistant message
  - `history(conversation_id)` - Gets conversation history
  - `formatted_history(conversation_id)` - Gets formatted string history
  - `clear(conversation_id)` - Clears conversation
- `conversation_manager` - Global instance

#### `ai_core/memory/summarizer.py`
**Purpose**: Conversation summarization (future component)
**Key Components**:
- `ConversationSummarizer` class:
  - `summarize(history)` - Currently returns history unchanged
- Note: Will summarize long conversations before context limit

---

### AI_CORE/KNOWLEDGE - RAG Knowledge Base

#### `ai_core/knowledge/__init__.py`
Empty init file.

#### `ai_core/knowledge/loader.py`
**Purpose**: Loads knowledge base documents
**Key Components**:
- `KnowledgeLoader` class:
  - `__init__(knowledge_path)` - Sets knowledge base path (default "knowledge_base")
  - `load()` - Loads all markdown files using TextLoader
  - Returns `list[Document]` from langchain

#### `ai_core/knowledge/chunker.py`
**Purpose**: Splits documents into chunks
**Key Components**:
- `KnowledgeChunker` class:
  - `__init__(chunk_size, chunk_overlap)` - Configures chunking (default 500/100)
  - `split(documents)` - Splits documents using RecursiveCharacterTextSplitter
  - Returns `list[Document]` chunks

#### `ai_core/knowledge/embeddings.py`
**Purpose**: Embedding service for vectorization
**Key Components**:
- `EmbeddingService` class:
  - Uses `GoogleGenerativeAIEmbeddings` with "models/gemini-embedding-2"
  - `get()` - Returns embeddings instance
- Requires `settings.GOOGLE_API_KEY`

#### `ai_core/knowledge/vector_store.py`
**Purpose**: Vector database management
**Key Components**:
- `VectorStoreService` class:
  - `build(documents, embeddings)` - Creates Chroma vector store from documents
  - `load(embeddings)` - Loads existing Chroma store from disk
  - Uses Chroma with persist_directory="chroma_db"

#### `ai_core/knowledge/retriever.py`
**Purpose**: Document retrieval from vector store
**Key Components**:
- `RetrieverService` class:
  - `__init__(vector_store)` - Creates retriever with k=3
  - `retrieve(query)` - Retrieves top-k documents
  - `search(query)` - Alias for retrieve

#### `ai_core/knowledge/service.py`
**Purpose**: Singleton knowledge service
**Key Components**:
- `KnowledgeService` class (singleton pattern):
  - `__new__()` - Ensures single instance
  - `__init__()` - Loads and indexes knowledge base once
  - `search(query)` - Searches knowledge base
- Initialization flow: loader → chunker → embeddings → vector_store → retriever
- `knowledge_service` - Global singleton instance

#### `ai_core/knowledge/instance.py`
**Purpose**: Knowledge service instance export
**Key Components**:
- `knowledge_service` - Global instance of KnowledgeService

---

### AI_CORE/RAG - RAG Pipeline

#### `ai_core/rag/__init__.py`
Empty init file.

#### `ai_core/rag/pipeline.py`
**Purpose**: Complete RAG pipeline for question answering
**Key Components**:
- `RAGPipeline` class:
  - `__init__()` - Initializes loader, chunker, embeddings, vector_store, retriever, LLM
  - `search(query)` - Retrieves relevant documents
  - `ask(question, conversation)` - Generates answer using RAG
  - `get_context(query)` - Gets formatted context from documents
- Uses RAG_PROMPT for LLM generation

#### `ai_core/rag/prompt.py`
**Purpose**: RAG prompt template
**Key Components**:
- `RAG_PROMPT` - Prompt template:
  - Instructs LLM to use conversation history and knowledge base
  - Handles pronoun references to previous context
  - Instructs not to invent information

---

### AI_CORE/PROMPTS - LLM Prompts

#### `ai_core/prompts/__init__.py`
Empty init file.

#### `ai_core/prompts/intent_prompt.py`
**Purpose**: Intent classification prompt
**Key Components**:
- `intent_prompt` - ChatPromptTemplate:
  - System message: Intent classification instructions
  - Lists all possible intents
  - Instructs JSON-only output
  - Human message: Customer message

#### `ai_core/prompts/rag_prompt.py`
**Purpose**: RAG question-answering prompt
**Key Components**:
- `RAG_PROMPT` - String template:
  - Instructs to use provided knowledge only
  - Handles conversation history for context
  - Provides fallback message if answer not found

#### `ai_core/prompts/knowledge_prompt.py`
Empty file (placeholder for future knowledge prompts).

#### `ai_core/prompts/response_prompt.py`
Empty file (placeholder for future response prompts).

---

### AI_CORE/INTEGRATIONS - External Integrations

#### `ai_core/integrations/__init__.py`
Empty init file.

#### `ai_core/integrations/jira_client.py`
**Purpose**: Jira integration for ticket creation
**Key Components**:
- `JiraClient` class:
  - `create_ticket(summary, description, priority)` - Creates mock Jira ticket
  - Returns dict with ticket_id, summary, priority, status
- Note: Currently mock, will communicate with real Jira REST API

---

### AI_CORE/ORCHESTRATOR - Workflow Orchestration

#### `ai_core/orchestrator/__init__.py`
Empty init file.

#### `ai_core/orchestrator/agent_registry.py`
**Purpose**: Registry for agent instances
**Key Components**:
- `AgentRegistry` class:
  - `__init__()` - Creates agent instances: intent, knowledge, ticket, human_review, response
  - `get(name)` - Retrieves agent by name
- Note: Orchestrator asks registry for agents instead of creating them

#### `ai_core/orchestrator/orchestrator.py`
**Purpose**: Main workflow orchestrator
**Key Components**:
- `SupportOrchestrator` class:
  - `__init__()` - Creates AgentRegistry and WorkflowRouter
  - `async run(state)` - Executes linear workflow: intent → knowledge → ticket → human_review → response
  - Updates workflow context with current/completed agents
- Note: Does not contain business logic, only coordination

#### `ai_core/orchestrator/workflow_router.py`
**Purpose**: Workflow routing based on intent
**Key Components**:
- `WorkflowRouter` class:
  - `get_workflow(state)` - Returns workflow list based on intent
  - Default workflow: intent → knowledge → response
  - Refund workflow: knowledge → ticket → human_review → response
  - Return workflow: knowledge → ticket → response
  - Technical workflow: knowledge → ticket → response
  - FAQ workflow: knowledge → response

---

## APP MODULE - FastAPI Application

### APP/MAIN - Application Entry Point

#### `app/main.py`
**Purpose**: FastAPI application setup
**Key Components**:
- Creates FastAPI app with title and version from settings
- Includes health router
- Adds request logging middleware
- Includes chat router
- Root endpoint returns LLM provider and model info

---

### APP/CORE - Core Configuration

#### `app/core/__init__.py`
Empty init file.

#### `app/core/config.py`
**Purpose**: Application configuration
**Key Components**:
- `Settings` class inheriting from BaseSettings:
  - `APP_NAME`, `APP_VERSION` - App metadata
  - `ENVIRONMENT`, `DEBUG` - Environment settings
  - `LLM_PROVIDER` - LLM provider (default "gemini")
  - `GOOGLE_API_KEY` - Google API key
  - `MODEL_NAME` - LLM model name (note: duplicate definition)
  - `TEMPERATURE` - LLM temperature
  - `MAX_TOKENS` - Max tokens
  - Loads from .env file
- `settings` - Global instance

#### `app/core/logging.py`
**Purpose**: Logging configuration
**Key Components**:
- `setup_logging()` function:
  - Configures logging at INFO level
  - Sets format: timestamp | level | name | message
  - Outputs to stdout

#### `app/core/constants.py`
Empty file (placeholder for constants).

---

### APP/MIDDLEWARE - HTTP Middleware

#### `app/middleware/__init__.py`
Empty init file.

#### `app/middleware/request_logger.py`
**Purpose**: HTTP request logging middleware
**Key Components**:
- `log_requests(request, call_next)` async function:
  - Records request start time
  - Calls next middleware/route
  - Calculates duration
  - Logs method, path, and duration

---

### APP/MODELS - API Models

#### `app/models/__init__.py`
Empty init file.

#### `app/models/chat.py`
**Purpose**: Chat API request/response models
**Key Components**:
- `ChatRequest` BaseModel:
  - `message: str` - User message
- `ChatResponse` BaseModel:
  - `intent: str` - Detected intent
  - `confidence: float` - Intent confidence
  - `ticket_required: bool` - Whether ticket was created
  - `ticket_id: str | None` - Ticket ID
  - `response: str` - Generated response
  - `escalation_required: bool` - Whether human review needed

---

### APP/ROUTERS - API Routes

#### `app/routers/__init__.py`
Empty init file.

#### `app/routers/chat.py`
**Purpose**: Chat endpoint
**Key Components**:
- `router` - APIRouter with prefix "/chat" and tag "Chat"
- `@router.post("")` - POST /chat endpoint:
  - Accepts ChatRequest
  - Calls ChatService.process()
  - Returns ChatResponse with intent, confidence, ticket info, response, escalation status

#### `app/routers/health.py`
**Purpose**: Health check endpoint
**Key Components**:
- `router` - APIRouter
- `@router.get("/health")` - GET /health endpoint:
  - Returns status, service name, and version

---

### APP/SERVICES - Business Logic Services

#### `app/services/__init__.py`
Empty init file.

#### `app/services/chat_service.py`
**Purpose**: Chat business logic service
**Key Components**:
- `ChatService` class:
  - `__init__()` - Creates SupportOrchestrator
  - `async process(message, customer_id, conversation_id)` - Processes chat message:
    - Creates SupportState with CustomerRequest and ProcessingMetadata
    - Calls orchestrator.run(state)
    - Returns updated SupportState

---

## API MODULE

### API/__INIT__.PY
Empty init file (placeholder for future API layer).

---

## SCRIPTS - Utility Scripts

### SCRIPTS/__INIT__.PY
Empty init file.

#### `scripts/ingest.py`
**Purpose**: Knowledge base ingestion script
**Key Components**:
- Loads documents using KnowledgeLoader
- Chunks documents using KnowledgeChunker
- Creates embeddings using EmbeddingService
- Builds vector store using VectorStoreService
- Prints success message

#### `scripts/test_memory_chat.py`
**Purpose**: Interactive RAG chat testing script
**Key Components**:
- Creates RAGPipeline instance
- Interactive loop:
  - Gets user input
  - Calls rag.ask() with conversation history
  - Prints response
  - Updates conversation history
  - Exits on "exit" or "quit"

---

## TESTS - Test Suite

### TESTS/__INIT__.PY
Empty init file.

#### Graph Execution Tests

**`tests/test_graph.py`**
- Tests graph compilation
- Asserts support_graph is not None

**`tests/test_graph_execution.py`**
- Tests async graph execution
- Creates SupportState with customer request
- Calls support_graph.ainvoke()
- Asserts execution_plan, decision, tool_results exist

**`tests/test_planner_graph.py`**
- Tests planner in graph context
- Creates SupportState with refund request
- Calls support_graph.invoke()
- Asserts execution_plan has tool_calls
- Asserts tool_results populated

#### Decision Engine Tests

**`tests/test_decision_engine.py`**
- Tests decision engine routing logic:
  - `test_decision_engine_retrieves_knowledge_for_refund_requests()` - Asserts knowledge retrieval for refunds
  - `test_decision_engine_creates_tickets_for_refund_requests()` - Asserts ticket creation for refunds
  - `test_decision_engine_escalates_low_confidence_requests()` - Asserts escalation for low confidence
  - `test_decision_engine_routes_refunds_to_ticket_flow()` - Asserts routing to ticket flow

#### Observability Tests

**`tests/test_observability.py`**
- Tests workflow tracing
- Executes graph
- Asserts trace exists with traces and duration
- Prints agent execution timings

#### Tool Tests

**`tests/test_tool_executor.py`**
- Tests tool registry and memory tool
- Asserts ticket tool execution
- Asserts memory tool returns string

**`tests/test_ticket_tool.py`**
- Tests ticket tool directly
- Asserts ticket_id starts with "TKT-"
- Asserts status is "OPEN"

**`tests/test_execute_plan.py`**
- Tests execution of multi-tool plans
- Creates ExecutionPlan with ticket and memory calls
- Asserts both tools executed

#### Planner Tests

**`tests/test_planner.py`**
- Tests planner agent
- Calls planner.run() with refund query
- Asserts plan has tool_calls

#### Memory Tests

**`tests/test_memory_store.py`**
- Tests in-memory storage
- Adds message to conversation
- Asserts message stored correctly

**`tests/test_conversation_manager.py`**
- Tests conversation manager
- Adds user and assistant messages
- Asserts formatted history contains both

**`tests/test_memory_integration.py`**
- Tests memory integration
- Clears conversation, adds messages
- Asserts history contains expected content

#### Knowledge/RAG Tests

**`tests/test_loader.py`**
- Tests knowledge loader
- Asserts at least 3 documents loaded
- Prints document content

**`tests/test_chunker.py`**
- Tests document chunking
- Loads and chunks documents
- Asserts chunks generated
- Prints chunk count and first chunk

**`tests/test_embeddings.py`**
- Tests embedding generation
- Generates embedding for query
- Asserts vector length > 0
- Prints vector sample

**`tests/test_vector_store.py`**
- Tests vector store creation
- Builds store from chunks
- Asserts store created

**`tests/test_retriever.py`**
- Tests document retrieval
- Builds complete pipeline
- Retrieves documents for query
- Asserts results returned

**`tests/test_knowledge_service.py`**
- Tests knowledge service
- Searches for cancellation query
- Asserts results returned

**`tests/test_instance.py`**
- Tests knowledge service instance
- Searches for refund
- Asserts documents retrieved

**`tests/test_singleton.py`**
- Tests singleton pattern
- Creates two KnowledgeService instances
- Asserts they are the same instance

**`tests/test_rag.py`**
- Tests RAG pipeline search
- Searches for refund query
- Asserts documents retrieved

**`tests/test_rag_answer.py`**
- Tests RAG answer generation
- Asks refund question
- Asserts answer generated

#### LLM Tests

**`tests/test_factory.py`**
- Tests LLM factory
- Creates provider
- Prints provider type

**`tests/test_gemini.py`**
- Tests Gemini provider
- Generates response with word count constraint
- Prints response

**`tests/test_llm.py`**
- Tests LLM client
- Asks capital of India
- Prints response

#### Utility Tests

**`tests/list_models.py`**
- Lists available Google models
- Requires API key

**`tests/test_file.py`**
- Tests intent agent end-to-end
- Creates SupportState with refund request
- Executes IntentAgent
- Prints full state JSON

---

## CONFIGURATION FILES

### `.env`
Environment variables (not in git):
- GOOGLE_API_KEY
- LLM_PROVIDER
- MODEL_NAME
- TEMPERATURE
- etc.

### `pyproject.toml`
Python project configuration with dependencies.

### `.python-version`
Python version specification.

---

## DATA DIRECTORIES

### `knowledge_base/`
Markdown files containing knowledge base documents for RAG.

### `chroma_db/`
Chroma vector database storage directory (persisted).

---

## SUMMARY

This project implements a multi-agent customer support system with:
- **9 agents**: Intent, Planner, Decision, Tool Executor, Knowledge, Ticket, Response, Memory, Human Review
- **LangGraph workflow**: Linear execution with tracing
- **Observability**: Complete workflow and agent tracing with @traced decorators
- **RAG system**: Knowledge retrieval with Chroma vector store
- **Tool system**: Extensible tool registry with 4 tools (knowledge, ticket, memory, human_review)
- **Decision engine**: Routing and approval logic with configurable rules
- **FastAPI application**: REST API with chat and health endpoints
- **Comprehensive tests**: 28 test files covering all components

## Core Architecture

### 1. State Management (SupportState)
**File**: `ai_core/state/support_state.py`

The central state object that flows through the entire workflow:

```python
class SupportState(BaseModel):
    request: CustomerRequest           # User input
    metadata: ProcessingMetadata       # Execution metadata
    intent: Optional[IntentOutput]     # Detected intent
    knowledge: Optional[KnowledgeOutput]  # Retrieved knowledge
    response: Optional[ResponseOutput]   # Generated response
    ticket: Optional[TicketOutput]    # Created ticket
    human_review: HumanReview         # Human review status
    workflow: WorkflowContext         # Workflow context
    trace: WorkflowTrace | None        # Execution trace
    conversation_history: str          # Conversation context
    execution_plan: ExecutionPlan | None  # Planner output
    decision: DecisionResult | None   # Decision engine output
    tool_results: dict                # Tool execution results
```

### 2. Agent System
**Base Class**: `ai_core/agents/base_agent.py`

All agents inherit from `BaseAgent` with a single abstract method:
```python
async def execute(self, state: SupportState) -> SupportState
```

#### Agent Implementations

**Intent Agent** (`ai_core/agents/intent_agent.py`)
- Detects user intent using LLM
- Returns structured IntentOutput with confidence score
- Traces with `@traced("intent")`

**Planner Agent** (`ai_core/planner/planner.py`)
- Analyzes user query and creates execution plan
- Determines which tools to call and in what order
- Has fallback planning if LLM unavailable
- Traces with `@traced("planner")`

**Decision Engine** (`ai_core/agents/decision.py`)
- Evaluates execution plan for safety/approval
- Can modify or block tool execution
- Currently auto-approves all plans
- Traces with `@traced("decision")`

**Tool Executor** (`ai_core/agents/tool_executor.py`)
- Executes tools from the approved plan
- Uses ToolExecutor to run registered tools
- Stores results in state.tool_results
- Traces with `@traced("tool_executor")`

**Knowledge Agent** (`ai_core/agents/knowledge_agent.py`)
- Retrieves relevant knowledge from RAG system
- Returns structured KnowledgeOutput
- Traces with `@traced("knowledge")`

**Ticket Agent** (`ai_core/agents/ticket_agent.py`)
- Creates support tickets when needed
- Returns TicketOutput with ticket_id
- Traces with `@traced("ticket")`

**Response Agent** (`ai_core/agents/response_agent.py`)
- Generates final response to user
- Combines results from all tools
- Updates conversation history
- Traces with `@traced("response")`

**Memory Agent** (`ai_core/agents/memory_agent.py`)
- Manages conversation context
- Retrieves conversation history
- No tracing decorator (sync node)

**Human Review Agent** (`ai_core/agents/human_review_agent.py`)
- Handles escalation to human reviewers
- Manages human review workflow
- No tracing decorator (sync node)

### 3. Graph/Workflow System
**File**: `ai_core/graph/builder.py`

Uses LangGraph's StateGraph for workflow orchestration:

#### Workflow Graph
```
START → memory → intent → planner → decision → tool_executor → response → END
```

#### Node Definitions
All async nodes have sync wrappers for LangGraph compatibility:

```python
# Async nodes (with @traced decorators)
- intent_node (nodes.py)
- planner_node (planner.py)
- decision_node (decision.py)
- tool_executor_node (tool_executor.py)
- knowledge_node (nodes.py)
- ticket_node (nodes.py)
- response_node (nodes.py)

# Sync nodes
- memory_node (memory_agent.py)
- human_review_node (nodes.py)
```

#### Graph Execution
```python
graph = StateGraph(SupportState)
graph.add_node("memory", memory_node)
graph.add_node("intent", intent_node_sync)
graph.add_node("planner", planner_node_sync)
graph.add_node("decision", decision_node_sync)
graph.add_node("tool_executor", tool_executor_node_sync)
graph.add_node("knowledge", knowledge_node_sync)
graph.add_node("ticket", ticket_node_sync)
graph.add_node("human_review", human_review_node_sync)
graph.add_node("response", response_node_sync)

# Edges define the workflow sequence
graph.add_edge(START, "memory")
graph.add_edge("memory", "intent")
graph.add_edge("intent", "planner")
graph.add_edge("planner", "decision")
graph.add_edge("decision", "tool_executor")
graph.add_edge("tool_executor", "response")
graph.add_edge("response", END)
```

#### SupportGraphWrapper
Wraps the compiled graph to handle both sync and async invocation:
```python
support_graph = SupportGraphWrapper(compiled_graph)

# Sync invocation
result = support_graph.invoke(state)

# Async invocation
result = await support_graph.ainvoke(state)
```

### 4. Observability/Tracing System
**Files**: `ai_core/observability/`

#### Tracer (`tracer.py`)
`WorkflowTracer` class tracks agent execution:
- Generates unique workflow_id
- Records agent start/finish times
- Calculates duration in milliseconds
- Tracks agent status (completed/failed)
- Captures errors and output summaries

#### Decorator (`decorators.py`)
`@traced(agent_name)` decorator for automatic tracing:
```python
@traced("intent")
async def intent_node(state: SupportState) -> SupportState:
    # Automatically:
    # 1. Creates tracer if not exists
    # 2. Starts agent trace
    # 3. Executes function
    # 4. Finishes agent trace
    # 5. Attaches trace to state.trace
```

#### Models (`models.py`)
Pydantic models for tracing:
- `WorkflowTrace`: Top-level workflow execution data
- `AgentTrace`: Individual agent execution data

#### Workflow Finalization
In `response_node`, after execution:
```python
if hasattr(state, "_tracer"):
    state._tracer.finish_workflow()
    state.trace = state._tracer.workflow
```

### 5. Tool System
**Files**: `ai_core/tools/`

#### Tool Registry (`registry.py`)
Central registry for all available tools:
```python
tool_registry = {
    "knowledge": KnowledgeTool,
    "ticket": TicketTool,
    "memory": MemoryTool,
    "human_review": HumanReviewTool,
}
```

#### Tool Executor (`executor.py`)
`ToolExecutor` class executes tools:
- Normalizes parameter names (e.g., query → question)
- Handles parameter mapping
- Executes single tools or entire plans
- Returns structured results

#### Available Tools
- **KnowledgeTool**: RAG-based knowledge retrieval
- **TicketTool**: Support ticket creation
- **MemoryTool**: Conversation history retrieval
- **HumanReviewTool**: Human review escalation

### 6. Decision Engine
**File**: `ai_core/workflow/decision_engine.py`

`DecisionEngine` class handles routing and approval:
- `route_after_intent()`: Routes based on intent type
- `should_retrieve_knowledge()`: Determines if knowledge needed
- `should_create_ticket()`: Determines if ticket needed
- `should_escalate()`: Determines if human review needed
- `evaluate()`: Approves/modifies execution plans
- Helper methods for tracking metrics

#### Workflow Rules (`workflow/rules.py`)
Defines routing thresholds and intent categories:
- `escalation_threshold`: Confidence threshold for escalation
- `knowledge_intents`: Intents requiring knowledge retrieval
- `ticket_intents`: Intents requiring ticket creation

### 7. Execution Tracing
**File**: `ai_core/workflow/execution_trace.py`

Tracks execution metrics:
- `increment_llm_calls()`: Counts LLM API calls
- `mark_documents_retrieved()`: Tracks RAG document retrieval
- `record_agent_execution()`: Records agent execution with timing
- `start_agent_timer()`: Starts timing for agent execution

## Data Flow

### Request Lifecycle
1. **Input**: CustomerRequest with message and conversation_id
2. **Memory Node**: Retrieves conversation history
3. **Intent Node**: Detects user intent and confidence
4. **Planner Node**: Creates execution plan with tool calls
5. **Decision Node**: Evaluates and approves/modifies plan
6. **Tool Executor Node**: Executes approved tools (knowledge, ticket, memory)
7. **Response Node**: Generates final response from tool results
8. **Output**: SupportState with response and trace

### State Transformation
```
Initial State:
- request: CustomerRequest
- metadata: ProcessingMetadata (empty)
- Other fields: None/defaults

After Memory:
- conversation_history: Populated from memory

After Intent:
- intent: IntentOutput (intent, confidence)
- metadata: Updated with routing reasons

After Planner:
- execution_plan: ExecutionPlan (tool_calls, reasoning)
- metadata: Updated with planner reasoning

After Decision:
- decision: DecisionResult (approved, reasoning, modified_plan)
- metadata: Updated with decision reasoning

After Tool Executor:
- tool_results: dict {tool_name: result}
- metadata: Updated with routing reasons

After Response:
- response: ResponseOutput (response, tone, confidence)
- trace: WorkflowTrace (complete execution trace)
```

## Key Design Patterns

### 1. Agent Pattern
Each agent is a self-contained unit that:
- Inherits from BaseAgent
- Implements async execute() method
- Takes SupportState as input/output
- Can be traced with @traced decorator

### 2. State Pattern
SupportState is the single source of truth:
- Immutable (Pydantic BaseModel)
- Flows through all agents
- Accumulates results
- Carries execution metadata

### 3. Graph Pattern
LangGraph provides:
- Declarative workflow definition
- Automatic state propagation
- Sync/async execution support
- Visualizable execution graph

### 4. Decorator Pattern
@traced decorator provides:
- Non-intrusive tracing
- Automatic error handling
- Consistent tracing across agents
- Workflow finalization

### 5. Registry Pattern
Tool registry provides:
- Centralized tool management
- Dynamic tool discovery
- Type-safe tool access
- Easy tool addition/removal

## Current Implementation Status

### ✅ Completed
- All async nodes have @traced decorators
- Workflow finalization in response_node
- Decision and tool_executor converted to async
- Sync wrappers for LangGraph compatibility
- Complete agent system
- Tool execution system
- Decision engine with routing logic
- Observability/tracing system

### 🔄 Workflow
Current linear workflow:
```
memory → intent → planner → decision → tool_executor → response
```

Knowledge and ticket nodes exist but are not currently in the main workflow graph. They are executed via the tool_executor based on the planner's execution plan.

### 📊 Observability
Every agent execution is traced with:
- Agent name
- Start/finish timestamps
- Duration in milliseconds
- Status (completed/failed)
- Input/output summaries
- Error details (if failed)

Workflow trace includes:
- Unique workflow_id
- Overall start/finish times
- Total duration
- List of all agent traces

## Usage Example

```python
from ai_core.graph.builder import support_graph
from ai_core.state.support_state import SupportState
from ai_core.models.customer_request import CustomerRequest

# Create initial state
state = SupportState(
    request=CustomerRequest(
        message="I need a refund for my order",
        conversation_id="conv_123"
    ),
    metadata=ProcessingMetadata()
)

# Execute workflow
result = support_graph.invoke(state)

# Access results
print(result.response.response)
print(result.trace)  # Complete execution trace
```

## Technical Stack
- **Framework**: LangGraph for workflow orchestration
- **State Management**: Pydantic for type-safe state
- **Async**: asyncio for async agent execution
- **LLM**: Structured output generation
- **RAG**: Knowledge retrieval system
- **Tracing**: Custom observability system

## File Locations Reference

### Core Workflow
- Graph definition: `ai_core/graph/builder.py`
- Node implementations: `ai_core/graph/nodes.py`
- State definition: `ai_core/state/support_state.py`

### Agents
- Intent: `ai_core/agents/intent_agent.py`
- Planner: `ai_core/planner/planner.py`
- Decision: `ai_core/agents/decision.py`
- Tool Executor: `ai_core/agents/tool_executor.py`
- Knowledge: `ai_core/agents/knowledge_agent.py`
- Ticket: `ai_core/agents/ticket_agent.py`
- Response: `ai_core/agents/response_agent.py`
- Memory: `ai_core/agents/memory_agent.py`
- Human Review: `ai_core/agents/human_review_agent.py`

### Observability
- Tracer: `ai_core/observability/tracer.py`
- Decorator: `ai_core/observability/decorators.py`
- Models: `ai_core/observability/models.py`

### Tools
- Executor: `ai_core/tools/executor.py`
- Registry: `ai_core/tools/registry.py`
- Tool implementations: `ai_core/tools/*.py`

### Workflow
- Decision Engine: `ai_core/workflow/decision_engine.py`
- Rules: `ai_core/workflow/rules.py`
- Execution Trace: `ai_core/workflow/execution_trace.py`

### Models
- All Pydantic models: `ai_core/models/*.py`
