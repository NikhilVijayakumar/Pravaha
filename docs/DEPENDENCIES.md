# Framework Dependencies - Status & Migration Roadmap

**Last Updated:** 2025-11-25  
**Review Schedule:** Quarterly (March, June, September, December)

---

## Purpose

This document tracks all external framework dependencies in Pravaha, assesses their risks, and documents isolation strategies. As a protocol-based library, we must minimize framework coupling to ensure long-term stability and flexibility.

---

## Critical Framework Dependencies

### 1. FastAPI (0.121.3)
**Category:** Web Framework  
**Risk Level:** 🟡 **MEDIUM** - Framework dependency in factory layer

**Usage:**
- API factory pattern in `domain/api/factory/`
- REST endpoint creation
- Request/response handling via Pydantic
- Dependency injection for routes

**Isolation Status:** ✅ **Excellent**
- ✅ Only used in `api_factory.py` (outer layer)
- ✅ Domain protocols are framework-agnostic
- ✅ Business logic completely independent
- ✅ Protocol-based design allows framework swap

**Migration Path:**
Already well-isolated via protocol pattern:
1. Domain protocols (`BotManagerProtocol`, `TaskConfigProtocol`) are framework-independent
2. Factory pattern allows creating alternative implementations
3. Could create `flask_factory.py` or `django_factory.py` without changing protocols

**Alternative Frameworks:**
- **Flask** - Simpler, more lightweight
- **Django REST Framework** - Full-featured
- **Starlette** - Lightweight ASGI framework (FastAPI is built on this)
- **Tornado** - WebSocket and streaming focus
- **aiohttp** - Async HTTP

**Action Items:**
- ✅ Well isolated via factory pattern
- [ ] Monitor FastAPI changelog for breaking changes
- [ ] Consider Starlette for even lighter weight (Q3 2025)

**Example Alternative Implementation:**
```python
# Hypothetical Flask factory
from flask import Flask, request, jsonify, Response

def create_flask_api(bot_manager: BotManagerProtocol, task_config: TaskConfigProtocol):
    app = Flask(__name__)
    
    @app.route('/run/utility', methods=['POST'])
    def run_utility():
        data = request.json
        task = task_config.UtilsType(data['task_name'])
        result = bot_manager.run(task)
        return jsonify({"status": "success", "result": result})
    
    return app
```

---

### 2. sse-starlette (3.0.3)
**Category:** SSE Streaming Library  
**Risk Level:** 🟢 **LOW** - Specialized utility dependency

**Usage:**
- Server-Sent Events (SSE) streaming in `api_factory.py`
- `EventSourceResponse` for streaming endpoints
- Real-time LLM response streaming

**Isolation Status:** ✅ **Excellent**
- Only used in streaming endpoint
- Could be replaced with custom SSE implementation
- No business logic dependency

**Migration Path:**
Easy to replace with:
1. Custom SSE implementation (simple text/event-stream)
2. Alternative SSE libraries
3. WebSocket (if bidirectional needed)

**Alternative Libraries:**
- **Custom SSE** - Simple response generator
- **WebSocket** - For bidirectional streaming
- **starlette.responses.StreamingResponse** - Built-in alternative

**Action Items:**
- ✅ Well isolated
- [ ] Consider custom SSE implementation to reduce dependencies (Q4 2025)

**Custom SSE Alternative Example:**
```python
from fastapi.responses import StreamingResponse

async def event_stream():
    for chunk in data:
        yield f"data: {chunk}\n\n"

return StreamingResponse(event_stream(), media_type="text/event-stream")
```

---

### 3. PyYAML (6.0.2)
**Category:** Configuration Parsing  
**Risk Level:** 🟢 **LOW** - Utility dependency

**Usage:**
- Currently listed in dependencies
- Likely for future config file support
- Not critical to core functionality

**Isolation Status:** ✅ **Excellent**
- Utility function only
- Not exposed in public API
- Easily replaceable

**Migration Path:**
- Can use `json`, `toml`, or other config formats
- No impact on protocols

**Alternative Libraries:**
- **json** (stdlib) - For simple configs
- **toml** / **tomli** - Modern config format
- **python-dotenv** - Environment-based config
- **pydantic-settings** - Type-safe settings

**Action Items:**
- ✅ Well isolated
- [ ] Consider if still needed (currently not used in core code)

---

## Utility Libraries (Zero Risk)

Standard library and type-checking only:

| Library | Usage | Risk | Isolation |
|---------|-------|------|-----------|
| typing | Type hints | 🟢 ZERO | ✅ Stdlib |
| enum | Enum definitions | 🟢 ZERO | ✅ Stdlib |
| inspect | Stream type checking | 🟢 ZERO | ✅ Stdlib |
| asyncio | Async utilities | 🟢 ZERO | ✅ Stdlib |
| threading | Sync-to-async conversion | 🟢 ZERO | ✅ Stdlib |

---

## Dependencies NOT Used (But Common in Similar Projects)

These are **intentionally excluded** to keep Pravaha lightweight:

| Library | Why Excluded | Alternative |
|---------|--------------|-------------|
| Pydantic (direct) | Comes with FastAPI | FastAPI's Pydantic |
| SQLAlchemy | Not a database library | Client's choice |
| Redis | Not a caching library | Client's choice |
| Celery | Not a task queue | Client's choice |
| LangChain | Framework-agnostic | Client integrates |
| CrewAI | Protocol-based, not tied | Client integrates |

---

## Dependency Isolation Architecture

```
┌─────────────────────────────────────────┐
│  Client Application                     │
│  (Pure Python, No Framework Coupling)   │
└─────────────────┬───────────────────────┘
                  │ Implements Protocols
                  ↓
┌─────────────────────────────────────────┐
│  Pravaha Protocols (Domain Layer)       │
│  - BotManagerProtocol                   │
│  - TaskConfigProtocol                   │
│  (ZERO external dependencies)           │
└─────────────────┬───────────────────────┘
                  │ Used by
                  ↓
┌─────────────────────────────────────────┐
│  API Factory (Infrastructure Layer)     │
│  - FastAPI (framework)                  │
│  - sse-starlette (SSE streaming)        │
│  (Framework-specific, replaceable)      │
└─────────────────────────────────────────┘
```

**Key Insight:** Protocols have ZERO dependencies, so clients remain framework-agnostic.

---

## Dependency Review Schedule

### Quarterly Review (Every 3 Months)

1. **Check for Updates:**
   ```bash
   cd /home/dell/PycharmProjects/Pravaha
   source venv/bin/activate
   pip list --outdated
   ```

2. **Review Changelogs:**
   - **FastAPI**: Check for Pydantic v2 updates, breaking changes
   - **sse-starlette**: Monitor for Starlette compatibility
   - **PyYAML**: Security advisories

3. **Update This Document:**
   - Change risk levels if frameworks become unmaintained
   - Update isolation status
   - Document new dependencies

4. **Measure Coupling:**
   ```bash
   # Count framework imports in domain layer (should be 0)
   grep -r "from fastapi" src/nikhil/pravaha/domain/api/protocol/ | wc -l
   
   # Count framework imports in factory (should be minimal)
   grep -r "from fastapi" src/nikhil/pravaha/domain/api/factory/ | wc -l
   ```

### Annual Review (Every 12 Months)

1. **Framework Health Assessment:**
   - Is FastAPI actively maintained?
   - Are there better ASGI framework alternatives?
   - Community size and activity?

2. **Migration Feasibility:**
   - Cost/benefit of switching to Starlette
   - Custom SSE implementation vs sse-starlette
   - Impact on client projects

3. **Refactoring Priority:**
   - High-risk, poorly isolated → Immediate action
   - Medium-risk, partial isolation → Plan refactoring
   - Low-risk, well isolated → Monitor only

---

## Dependency Update Policy

### Safe Updates (Patch Versions)

**Examples:** `0.121.3` → `0.121.4`

```bash
# Can update immediately
pip install --upgrade fastapi
```

**Rules:**
- ✅ Update patch versions freely
- ✅ Run tests after update
- ✅ Document in git commit

### Careful Updates (Minor Versions)

**Examples:** `0.121.3` → `0.122.0`

**Rules:**
- ⚠️ Review changelog first
- ⚠️ Test thoroughly
- ⚠️ Update `pyproject.toml`
- ⚠️ Notify dependent projects

### Breaking Updates (Major Versions)

**Examples:** `0.121.3` → `1.0.0` or Pydantic v1 → v2

**Rules:**
- 🔴 Create feature branch
- 🔴 Full regression testing
- 🔴 Bump Pravaha MAJOR version
- 🔴 Create migration guide

---

## Framework Selection Criteria

When evaluating new framework dependencies:

### ✅ Prefer Dependencies That:
- Are well-maintained (commits in last month)
- Have large community (>5000 GitHub stars for frameworks)
- Follow semantic versioning
- Are ASGI-compatible (for async support)
- Can be isolated to infrastructure layer

### ❌ Avoid Dependencies That:
- Are abandoned (no commits in 3+ months)
- Have frequent breaking changes
- Require changes to domain layer
- Lock into specific infrastructure
- Have global state requirements

### 🔍 Evaluation Checklist:
- [ ] GitHub activity (commits, issues, stars)
- [ ] Changelog review (breaking change frequency)
- [ ] Isolation test (can we contain it to factory?)
- [ ] Alternative evaluation
- [ ] Community size and support

---

## Emergency Response Plan

### If FastAPI is Deprecated or Has Critical Vulnerability:

**Week 1: Assessment**
- Evaluate severity
- Check for security patches
- Identify migration options (Starlette, Flask, etc.)

**Week 2-3: Create Alternative Factory**
```python
# New factory with alternative framework
def create_starlette_api(bot_manager: BotManagerProtocol, task_config: TaskConfigProtocol):
    # Same protocols, different framework
    ...
```

**Week 4: Testing**
- Full test suite
- Integration testing
- Performance benchmarks

**Week 5-6: Gradual Migration**
- Feature flag for framework selection
- Deprecate old factory
- Document migration path

---

## Metrics & Success Criteria

### Current Metrics (v1.0.0):

| Metric | Current | Target |
|--------|---------|---------|
| Domain layer framework imports | 0 | 0 |
| Total production dependencies | 3 | ≤ 5 |
| Framework coupling in protocols | 0% | 0% |
| Frameworks with isolation | 100% | 100% |
| Alternative implementations | 1 (FastAPI) | 2 |

### Success Indicators:

✅ **Excellent Health (Current State):**
- Domain protocols have zero dependencies
- All frameworks isolated to factory layer
- Could swap FastAPI in < 1 day
- Dependency updates don't affect clients

⚠️ **Needs Attention:**
- Framework import in protocol layer
- Breaking dependency update required
- Framework response time degrading

🔴 **High Risk:**
- Domain layer depends on framework
- Framework deprecated or unmaintained
- No viable migration path

---

## Pydantic Strategy

**Important Note:** Pravaha doesn't directly depend on Pydantic in `pyproject.toml`.

### Why?
- FastAPI includes Pydantic as a dependency
- We get Pydantic "for free" via FastAPI
- Reduces dependency tree complexity

### What We Use:
```python
from pydantic import BaseModel  # Via FastAPI

class UtilityRequest(BaseModel):
    task_name: UtilsType
```

### If FastAPI is Removed:
- Would need to add `pydantic>=2.0` to dependencies
- Or use dataclasses with manual validation

---

## Dependency Tree Visualization

```
Pravaha 1.0.0
├── fastapi==0.121.3
│   ├── pydantic>=2.0
│   ├── starlette
│   └── typing-extensions
├── sse-starlette==3.0.3
│   └── starlette
└── PyYAML==6.0.2
```

**Total Dependency Count:** ~3 direct, ~10 transitive

**Comparison:**
- **Minimal:** 3 dependencies (Pravaha) ✅
- **Moderate:** 10-20 dependencies
- **Heavy:** 50+ dependencies (full-stack frameworks)

---

## Recommendations

### Short Term (Q1-Q2 2025)
- [x] Document all dependencies (this file)
- [ ] Set up automated dependency scanning (Dependabot)
- [ ] Create alternative factory example (Flask or Starlette)
- [ ] Add dependency update tests to CI/CD

### Medium Term (Q3-Q4 2025)
- [ ] Evaluate custom SSE implementation
- [ ] Research Starlette-only approach (remove FastAPI)
- [ ] Create framework benchmark comparison
- [ ] Publish framework migration guide

### Long Term (2026+)
- [ ] Support multiple framework factories (FastAPI, Flask, Starlette)
- [ ] Achieve complete framework independence
- [ ] Zero-dependency protocol package option

---

**Next Review Date:** 2025-12-25  
**Responsible:** Pravaha Maintainers  
**Escalation:** If any dependency reaches 🔴 HIGH RISK, evaluate alternatives immediately
