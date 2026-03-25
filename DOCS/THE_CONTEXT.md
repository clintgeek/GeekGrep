# Project Context: geekGrep

> **📌 Living Document**: Development knowledge base for the geekGrep project. Updated by AI agents and humans with implementation decisions, progress, and learnings.

---

## 🎯 Quick Reference

**Project**: Local RAG document query system  
**Current Phase**: Planning → Implementation  
**Key Tech**: LangChain, ChromaDB, OpenAI API (primary) / Ollama (fallback), Streamlit  
**Full Spec**: See [THE_PLAN.md](./THE_PLAN.md)

---

## 📋 Development Status

### Current Sprint (Week 1) - 93% Complete
- [x] Project specification (THE_PLAN.md)
- [x] Architecture design  
- [x] Repo structure setup
- [x] Core dependencies (44 tests passing)
- [x] Steps 1-11: Loaders, Splitter, Store, Retriever, LLM, Pipeline, CLI, Web UI, File Watcher
- [x] Step 14: Docker & docker-compose
- [x] Documentation (README, IMPLEMENTATION_SUMMARY)
- [ ] Step 12: Metadata filtering (optional enhancement)
- [ ] Step 13: Async ingestion (optional enhancement)
- [ ] Step 15: Final polish (docstrings, benchmarks)

### Blockers
- None identified

---

## 🔧 Implementation Decisions

| Decision | Made | Rationale |
|----------|------|-----------|
| OpenAI primary, Ollama fallback | 2025-03-24 | No GPU available; CPU-only Ollama too slow. OpenAI for speed, Ollama for offline option |
| ChromaDB over FAISS | 2025-03-24 | Persistence + filtering needed |
| Streamlit for MVP | 2025-03-24 | Rapid prototyping |

---

## 💡 Technical Learnings

### Discoveries
- Memory management critical for large doc sets
- Async processing essential for UX
- Source citation = enterprise differentiator

### Issues Encountered
- *None yet*

---

## 🚀 Next Actions

1. Set up project structure
2. Install dependencies  
3. Basic ingestion pipeline
4. Vector storage setup

---

## 📝 Development Notes

*Space for ongoing implementation notes, debugging sessions, and technical discoveries.*

---

*For detailed functional requirements and business rationale, refer to THE_PLAN.md*