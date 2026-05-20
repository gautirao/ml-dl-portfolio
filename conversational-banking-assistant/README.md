# Conversational Banking Assistant

**Status:** Planned / In design  
**Architecture Theme:** Safety-First Local RAG for Regulated Domains

## 📖 Summary
The **Conversational Banking Assistant** is a planned prototype local AI chatbot designed to answer questions from publicly available banking policy, fee, and overdraft documents. It demonstrates how conversational AI can be made safer and more reliable in a regulated domain by using document retrieval, citations, deterministic tools, confidence checks, refusal rules, and comprehensive audit logging.

## 🎯 Problem Statement
Generic LLMs often hallucinate financial details or provide unsupported advice when queried about specific banking policies. In a regulated environment, "creative" answers are a liability. This project addresses these risks by grounding every response in verified documents and enforcing strict guardrails.

## 🏗️ Architecture Principles
> "The LLM explains, but does not act as the source of truth. Retrieval provides evidence, deterministic tools perform calculations, guardrails decide safety, and audit logging records every decision."

- **Local-First:** All inference and data processing happen locally to ensure privacy and control.
- **Evidence-Based:** No answer is generated without retrieved snippets and corresponding citations.
- **Safety by Design:** Hard refusal rules for financial advice and unsupported claims.
- **Auditable:** Every step—from retrieval to final output—is logged for evaluation and debugging.

## 🛠️ Planned Tech Stack
- **Language:** Python 3.12
- **Runtime LLM:** Ollama (Primary: Qwen 3.5 4B / Qwen 3 4B; Fallback: Llama 3.2 3B)
- **API Framework:** FastAPI
- **Frontend:** Streamlit (for rapid prototyping)
- **Database/Storage:** DuckDB (Audit logs & Metadata), Qdrant or Chroma (Vector Store)
- **Embeddings:** `sentence-transformers`
- **Orchestration:** Custom provider-swappable interface built for Ollama runtime, with Gemini API usable for development/debugging.
- **Testing:** `pytest` and `pytest-bdd` (Behavior-Driven Development)

## 🚀 Key Features
- **Intelligent ingestion of PDF/HTML banking documents.**
- **Hybrid Retrieval:** Combining vector search with keyword search and metadata filtering.
- **Deterministic Calculation Tools:** Handling overdraft cost examples via code, not LLM arithmetic.
- **Citation-Backed Answers:** Explicit links to source document sections.
- **Guardrail Engine:** Intercepting sensitive queries or low-confidence retrievals.
- **Evaluation Framework:** Audit logs and a small golden dataset for regression testing.

## 🧪 Development Approach
This project follows a **TDD/BDD (Test/Behavior Driven Development)** approach:
1. Define user stories in Gherkin syntax (`.feature` files).
2. Implement failing tests using `pytest-bdd`.
3. Develop the minimum code required to pass the tests.
4. Refactor and optimize for local LLM performance.

## ⚠️ Disclaimer
This project is an **independent educational prototype** and is not affiliated with any bank or financial institution. It does not provide financial advice. All documents used are publicly available for informational purposes only.

---
*Targeted for recruiters and hiring managers to showcase expertise in RAG governance, local LLM orchestration, and safety-conscious AI engineering.*
