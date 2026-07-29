# Project File Tree

Autonomous Multi-Agent Support System - Complete file structure with detailed descriptions

```
Autonomous-multi-agent-support-system/
├── README.md
├── PROJECT_STATUS.md
├── PROJECT_STATUS2.md
├── PROJECT_STATUS3.md
├── PROJECT_TREE.md
├── .gitignore
├── pyproject.toml
├── uv.lock
├── .python-version
├── .env
│
├── apps/
│   └── backend/
│       ├── main.py                          # Entry point for uvicorn server
│       ├── pyproject.toml                   # Python dependencies and project config
│       ├── uv.lock                          # UV lock file for dependencies
│       ├── .python-version                  # Python version specification
│       ├── .env                             # Environment variables
│       │
│       ├── ai_core/                         # Core AI/ML agent system
│       │   ├── __init__.py
│       │   │
│       │   ├── agents/                      # AI Agent implementations
│       │   │   ├── __init__.py
│       │   │   ├── base_agent.py            # Abstract base class for all agents
│       │   │   ├── intent_agent.py         # Classifies customer intent (refund, technical, etc.)
│       │   │   ├── knowledge_agent.py      # Retrieves knowledge from RAG system
│       │   │   ├── ticket_agent.py         # Creates support tickets when needed
│       │   │   ├── response_agent.py       # Generates final response using LLM
│       │   │   ├── memory_agent.py         # Loads conversation history
│       │   │   ├── human_review_agent.py   # Handles human escalation
│       │   │   ├── planner.py              # Planner agent node function
│       │   │   ├── decision.py             # Decision engine node function
│       │   │   └── tool_executor.py        # Tool executor node function
│       │   │
│       │   ├── graph/                       # LangGraph workflow orchestration
│       │   │   ├── __init__.py             # Exports support_graph and invoke_sync
│       │   │   ├── builder.py              # Builds the LangGraph state machine
│       │   │   ├── nodes.py                # Node functions for the graph
│       │   │   └── router.py               # Conditional routing logic
│       │   │
│       │   ├── observability/               # Tracing and monitoring
│       │   │   ├── __init__.py
│       │   │   ├── tracer.py               # Workflow tracer implementation
│       │   │   ├── decorators.py           # @traced decorator for agent tracing
│       │   │   └── models.py               # Tracing data models
│       │   │
│       │   ├── tools/                       # Tool implementations
│       │   │   ├── __init__.py             # Registers all tools on import
│       │   │   ├── base_tool.py            # Abstract base class for tools
│       │   │   ├── executor.py             # Tool executor with registry
│       │   │   ├── registry.py             # Tool registry for registration
│       │   │   ├── knowledge_tool.py       # RAG knowledge retrieval tool
│       │   │   ├── ticket_tool.py          # Ticket creation tool
│       │   │   ├── memory_tool.py          # Conversation history tool
│       │   │   └── human_review_tool.py    # Human escalation tool
│       │   │
│       │   ├── workflow/                    # Workflow orchestration
│       │   │   ├── __init__.py
│       │   │   ├── decision_engine.py     # Decision logic for workflow routing
│       │   │   ├── rules.py                # Workflow rules and thresholds
│       │   │   ├── execution_trace.py      # Execution tracking utilities
│       │   │   └── router.py               # Workflow routing logic
│       │   │
│       │   ├── state/                       # State management
│       │   │   ├── __init__.py             # Exports SupportState
│       │   │   └── support_state.py        # Main workflow state model
│       │   │
│       │   ├── models/                      # Pydantic data models
│       │   │   ├── __init__.py
│       │   │   ├── customer_request.py     # Customer request input model
│       │   │   ├── intent.py              # Intent classification model
│       │   │   ├── knowledge.py            # Knowledge retrieval output model
│       │   │   ├── ticket.py               # Ticket creation output model
│       │   │   ├── response.py             # Response generation output model
│       │   │   ├── human_review.py        # Human review status model
│       │   │   ├── metadata.py            # Processing metadata model
│       │   │   ├── execution_plan.py       # Planner execution plan model
│       │   │   ├── tool_call.py            # Tool call specification model
│       │   │   ├── decision.py             # Decision result model
│       │   │   └── workflow.py             # Workflow context model
│       │   │
│       │   ├── planner/                     # Planning agent
│       │   │   ├── __init__.py
│       │   │   ├── planner.py              # Planner agent implementation
│       │   │   └── planner_prompt.py       # Planner LLM prompt
│       │   │
│       │   ├── llm/                         # LLM integration
│       │   │   ├── __init__.py
│       │   │   ├── base.py                 # Abstract LLM provider interface
│       │   │   ├── factory.py              # LLM provider factory
│       │   │   ├── gemini.py               # Google Gemini provider
│       │   │   ├── service.py              # LLM service singleton
│       │   │   ├── client.py               # LLM client utilities
│       │   │   └── models.py               # LLM-related models
│       │   │
│       │   ├── memory/                      # Conversation memory
│       │   │   ├── __init__.py
│       │   │   ├── models.py               # Memory data models
│       │   │   ├── memory_store.py         # In-memory conversation storage
│       │   │   ├── conversation_manager.py # High-level conversation API
│       │   │   └── summarizer.py          # Conversation summarization
│       │   │
│       │   ├── knowledge/                   # Knowledge base management
│       │   │   ├── __init__.py
│       │   │   ├── loader.py               # Document loader from files
│       │   │   ├── chunker.py              # Text chunking for embeddings
│       │   │   ├── embeddings.py           # Embedding generation service
│       │   │   ├── vector_store.py         # Vector store (ChromaDB) wrapper
│       │   │   ├── retriever.py            # Similarity search retriever
│       │   │   ├── service.py             # Knowledge service singleton
│       │   │   └── instance.py            # Knowledge instance management
│       │   │
│       │   ├── rag/                         # RAG pipeline
│       │   │   ├── __init__.py
│       │   │   ├── pipeline.py             # RAG retrieval-augmented generation
│       │   │   └── prompt.py               # RAG prompt template
│       │   │
│       │   ├── prompts/                     # LLM prompts
│       │   │   ├── __init__.py
│       │   │   ├── intent_prompt.py        # Intent classification prompt
│       │   │   ├── response_prompt.py      # Response generation prompt
│       │   │   └── rag_prompt.py           # RAG prompt template
│       │   │
│       │   ├── integrations/                # External integrations
│       │   │   ├── __init__.py
│       │   │   └── jira_client.py          # Jira integration client
│       │   │
│       │   ├── orchestrator/                # Agent orchestration
│       │   │   ├── __init__.py
│       │   │   ├── agent_registry.py       # Agent registration
│       │   │   ├── orchestrator.py         # Main orchestrator
│       │   │   └── workflow_router.py      # Workflow routing
│       │   │
│       │   └── models/                      # Additional models
│       │       ├── __init__.py
│       │       ├── workflow.py             # Workflow context
│       │       ├── decision.py             # Decision results
│       │       └── execution_plan.py       # Execution plans
│       │
│       ├── app/                             # FastAPI application layer
│       │   ├── __init__.py
│       │   ├── main.py                     # FastAPI app initialization
│       │   │
│       │   ├── core/                       # Core application config
│       │   │   ├── __init__.py
│       │   │   ├── config.py               # Settings and environment config
│       │   │   ├── constants.py            # Application constants
│       │   │   └── logging.py              # Logging configuration
│       │   │
│       │   ├── dependencies/                # Dependency injection
│       │   │   └── __init__.py
│       │   │
│       │   ├── middleware/                  # FastAPI middleware
│       │   │   ├── __init__.py
│       │   │   └── request_logger.py       # Request logging middleware
│       │   │
│       │   ├── models/                      # API models
│       │   │   ├── __init__.py
│       │   │   └── chat.py                 # Chat-related models
│       │   │
│       │   ├── routers/                     # API route handlers
│       │   │   ├── __init__.py
│       │   │   ├── health.py               # Health check endpoint
│       │   │   └── support.py              # Support request endpoint
│       │   │
│       │   ├── schemas/                     # Pydantic schemas
│       │   │   ├── __init__.py
│       │   │   ├── request.py              # Request schemas
│       │   │   ├── response.py             # Response schemas
│       │   │   ├── conversation.py         # Conversation schemas
│       │   │   ├── metrics.py              # Metrics schemas
│       │   │   ├── trace.py                # Trace schemas
│       │   │   └── workflow.py             # Workflow schemas
│       │   │
│       │   └── services/                    # Business logic services
│       │       ├── __init__.py
│       │       ├── support_service.py      # Support request processing
│       │       ├── workflow_executor.py    # Workflow execution wrapper
│       │       ├── conversation_service.py # Conversation management
│       │       ├── chat_service.py         # Chat service
│       │       └── analytics_service.py    # Analytics service
│       │
│       ├── scripts/                         # Utility scripts
│       │   ├── __init__.py
│       │   ├── ingest.py                   # Knowledge base ingestion
│       │   └── test_memory_chat.py         # Memory chat testing
│       │
│       ├── tests/                           # Test suite
│       │   ├── __init__.py
│       │   ├── test_chunker.py
│       │   ├── test_conversation_manager.py
│       │   ├── test_decision_engine.py
│       │   ├── test_embeddings.py
│       │   ├── test_execute_plan.py
│       │   ├── test_factory.py
│       │   ├── test_file.py
│       │   ├── test_gemini.py
│       │   ├── test_graph.py
│       │   ├── test_graph_execution.py
│       │   ├── test_instance.py
│       │   ├── test_knowledge_service.py
│       │   ├── test_llm.py
│       │   ├── test_loader.py
│       │   ├── test_memory_integration.py
│       │   ├── test_memory_store.py
│       │   ├── test_observability.py
│       │   ├── test_planner.py
│       │   ├── test_planner_graph.py
│       │   ├── test_rag.py
│       │   ├── test_rag_answer.py
│       │   ├── test_retriever.py
│       │   ├── test_singleton.py
│       │   ├── test_support_service.py
│       │   ├── test_ticket_tool.py
│       │   ├── test_tool_executor.py
│       │   ├── test_vector_store.py
│       │   └── list_models.py
│       │
│       ├── knowledge_base/                  # Knowledge base documents
│       │   ├── faq.md                      # Frequently asked questions
│       │   ├── refund_policy.md            # Refund policy documentation
│       │   ├── shipping_policy.md         # Shipping policy documentation
│       │   └── warrenty_policy.md         # Warranty policy documentation
│       │
│       ├── chroma_db/                       # ChromaDB vector database
│       │   ├── chroma.sqlite3             # ChromaDB storage
│       │   └── [collection_uuid]/          # Vector store data
│       │       ├── data_level0.bin
│       │       ├── header.bin
│       │       ├── length.bin
│       │       └── link_lists.bin
│       │
│       └── .venv/                          # Virtual environment (excluded)
│
└── docs/
    └── infrastructure/
        └── docker/
```

## Architecture Overview

### Core Components

#### 1. **AI Core (`ai_core/`)**
The heart of the multi-agent system containing:

- **Agents**: Specialized AI agents for different tasks (intent, knowledge, ticket, response, memory)
- **Graph**: LangGraph-based workflow orchestration with state machine
- **Tools**: Registered tools for knowledge retrieval, ticket creation, memory access
- **LLM Integration**: Abstracted LLM providers (Gemini) with factory pattern
- **Knowledge**: RAG pipeline with ChromaDB vector store
- **Memory**: Conversation history management
- **Observability**: Tracing and monitoring decorators

#### 2. **Application Layer (`app/`)**
FastAPI application providing:

- **Routers**: REST API endpoints (`/health`, `/api/v1/support`)
- **Schemas**: Pydantic models for request/response validation
- **Services**: Business logic layer wrapping AI core
- **Middleware**: Request logging and processing
- **Config**: Environment-based configuration

#### 3. **Workflow Execution Flow**
```
Request → FastAPI Router → SupportService → WorkflowExecutor 
→ LangGraph → Agents → Tools → LLM → Response
```

### Key Design Patterns

- **Singleton Pattern**: KnowledgeService, LLMService, ConversationManager
- **Factory Pattern**: LLMFactory for provider creation
- **Registry Pattern**: ToolRegistry for tool registration
- **Decorator Pattern**: @traced for observability
- **State Machine**: LangGraph for workflow orchestration

## File Count Summary

- **ai_core/**: 62 Python files across 15 modules
- **app/**: 22 Python files (core, routers, schemas, services)
- **tests/**: 29 test files
- **scripts/**: 2 utility scripts
- **knowledge_base/**: 4 Markdown documents
- **chroma_db/**: Vector database storage

**Total**: 119+ Python files (excluding __pycache__ and .venv)

## Technology Stack

- **Framework**: FastAPI
- **Orchestration**: LangGraph
- **LLM**: Google Gemini (via langchain-google-genai)
- **Vector DB**: ChromaDB
- **Embeddings**: FAISS
- **Package Manager**: UV
- **Python**: 3.13+
