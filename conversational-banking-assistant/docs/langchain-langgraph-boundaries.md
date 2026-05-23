# LangChain and LangGraph Integration Boundaries

## 1. Overview
This document defines the strict boundaries for using LangChain and LangGraph in the **Conversational Banking Assistant** (CBA). CBA is a safety-first, auditable RAG system for regulated domains. To maintain high engineering standards and MSc-level auditability, we prioritize custom, framework-independent engineering for the core retrieval and evidence foundation, using external frameworks only for LLM orchestration and syntactic sugar.

## 2. Allowed LangChain Use
LangChain is permitted only at the **LLM interface boundary**.

| Feature | Allowed Use | Benefit |
| :--- | :--- | :--- |
| **Prompt Templates** | Using `ChatPromptTemplate` for managing system messages and few-shot examples. | Consistency and versioning of prompts. |
| **Model Wrappers** | Using `ChatOllama` or `ChatOpenAI` (for Gemini/LocalAI) to provide a unified interface. | Provider-swappable inference. |
| **Output Parsers** | Using Pydantic-based parsers to cast LLM responses into CBA domain models. | Type safety and validation. |
| **Callbacks** | Simple tracing or logging of model latency and token counts. | Debugging and performance monitoring. |

## 3. Disallowed LangChain Use
LangChain must NOT be used for core business logic or data retrieval.

- **No LangChain Retrievers:** Our `EvidencePacket` and hybrid retrieval (BM25 + Vector) are custom-built to ensure precise control over citations and rankings.
- **No Document Loaders:** Ingestion (PDF/HTML extraction) is handled by our custom pipeline to ensure metadata integrity.
- **No High-Level Chains:** Avoid `RetrievalQA` or `create_retrieval_chain`. The flow from Question -> Search -> EvidencePacket -> Prompt must be explicit in our code.
- **No VectorStore Abstractions:** We interact with our vector database via custom indices (`VectorIndex`) to ensure compatibility with our specific metadata filtering needs.
- **No Managed Memory:** Conversational state must be handled explicitly or via LangGraph states, not via opaque `ConversationBufferMemory`.

## 4. Allowed LangGraph Use
LangGraph is intended for **bounded orchestration** of the reasoning loop (Issue #28).

- **Explicit DAGs:** Defining the clear state transitions: `Start -> Plan -> Retrieve -> Draft grounded answer from EvidencePacket -> Apply guardrails -> Write audit event -> Final Answer`.
- **State Schema:** Using a TypedDict or Pydantic model for the graph state that includes the `EvidencePacket`.
- **Human-in-the-loop:** Using LangGraph's `interrupt` feature for safety-critical banking decisions (if added later).
- **Deterministic Routing:** Using logic-based edges rather than LLM-based "free routing".

## 5. Disallowed LangGraph Use
- **Autonomous Agents:** No `AgentExecutor` or free-roaming agents that can decide their own path.
- **Dynamic Tools:** Tools must be pre-defined and restricted to the `domain` logic.
- **Opaque State:** The graph state must be serializable and auditable at every node execution.
- **Financial Execution:** The LLM can suggest a calculation, but the execution must happen in a deterministic sandbox with manual approval if it affects user data.

## 6. Integration Map (Future Issues)

| Issue | Task | Framework Usage |
| :--- | :--- | :--- |
| **#12** | LLM Client | LangChain `BaseChatModel` interface. |
| **#13** | Ollama Runtime | LangChain `ChatOllama`. |
| **#14** | Grounded Answers | LangChain for prompting; `EvidencePacket` injected manually. |
| **#24** | Structured JSON | LangChain `.with_structured_output(PydanticModel)`. |
| **#28** | Planner-Executor | LangGraph for the workflow DAG. |

## 7. Acceptance Criteria (M5+)
- [ ] No LangChain imports in `src/cba/retrieval` or `src/cba/ingestion`.
- [ ] `EvidencePacket` remains the source of truth for all grounded answers.
- [ ] Every framework-mediated LLM call is logged in a format compatible with CBA's audit trail.
- [ ] System remains functional even if LangChain were replaced by a simple `requests` client for the LLM.

## 8. Risks
- **Framework Creep:** Allowing LangChain "convenience" to replace robust custom engineering.
- **Hiding Logic:** Using a complex Chain that makes it hard to see where a hallucination occurred.
- **Dependency Bloat:** Adding heavy libraries for features we only use 10% of.
- **Evaluation Difficulty:** Frameworks can make it harder to run unit tests on individual reasoning steps.
