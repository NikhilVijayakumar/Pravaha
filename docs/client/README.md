# Client Documentation Index

**Last Updated**: 2026-01-12

This directory contains documentation for Pravaha client applications.

---

## 📁 Directory Structure

```
docs/client/
├── README.md (this file)
├── api-factory.md          # API Factory setup guide
├── bot-module.md            # Bot/Application module (general)
├── llm-module.md            # LLM configuration module
├── storage-module.md        # Storage management module
├── workflow-module.md       # Workflow orchestration (NEW: client-driven)
├── akashavani/             # Akashavani-specific docs
│   ├── overview.md          # Code review & improvements
│   ├── modules.md           # Module configuration guide
│   └── fastapi-setup.md     # FastAPI setup & deployment
└── sangama/                # Sangama-specific docs
    ├── overview.md          # Code review & improvements
    ├── bot-module.md        # Application execution integration
    ├── storage-module.md    # Storage browser integration
    └── llm-module.md        # LLM configuration UI
```

---

## 🎯 Quick Start for Different Audiences

### For Akashavani Developers (Backend)

**You're building the FastAPI backend using Pravaha.**

**Start Here**:
1. [API Factory](api-factory.md) - Quickest way to set up everything
2. [Akashavani Overview](akashavani/overview.md) - Code review & improvements
3. [Akashavani Modules](akashavani/modules.md) - Module-specific configuration
4. [FastAPI Setup](akashavani/fastapi-setup.md) - Server setup & deployment

**Key Files**:
- [Workflow Module](workflow-module.md) - **Updated for client-driven execution!**

---

### For Sangama Developers (Frontend)

**You're building the Electron UI that connects to Akashavani.**

**Start Here**:
1. [Sangama Overview](sangama/overview.md) - Code review & priorities
2. [Sangama Bot Module](sangama/bot-module.md) - Application execution
3. [Sangama Storage Module](sangama/storage-module.md) - Storage integration
4. [Sangama LLM Module](sangama/llm-module.md) - LLM configuration UI

**Critical**:
- [Workflow Module](workflow-module.md) - **Must implement execution loop!**

---

### For New Developers

**You're learning the Pravaha ecosystem.**

**Learning Path**:
1. [API Factory](api-factory.md) - Understand the auto-configuration
2. [Bot Module](bot-module.md) - Learn application execution
3. [Storage Module](storage-module.md) - Understand file management
4. [LLM Module](llm-module.md) - Configure LLM models
5. [Workflow Module](workflow-module.md) - Build complex workflows

---

## 📖 Documentation by Module

### Core Modules

#### [API Factory](api-factory.md)
**Purpose**: One-line setup for all Pravaha features  
**Audience**: Backend developers (Akashavani)  
**Status**: ✅ Up to date

**Quick Example**:
```python
from pravaha.domain.api.factory.api_factory import create_fastapi_app

app = create_fastapi_app(
    bot_manager=bot_manager,
    task_config=task_config,
    storage_manager=storage_manager,
    llm_config_path="config/llm_config.json"
)
```

---

#### [Bot Module](bot-module.md)
**Purpose**: Execute domain applications with LLM integration  
**Audience**: Both backend and frontend  
**Status**: ✅ Up to date

**Key Concepts**:
- Task configuration
- Streaming execution
- LLM config override

---

#### [Storage Module](storage-module.md)
**Purpose**: Manage output/intermediate/knowledge files  
**Audience**: Both backend and frontend  
**Status**: ✅ Up to date

**Key Concepts**:
- Three storage categories
- Versioning system
- File organization patterns

---

#### [LLM Module](llm-module.md)
**Purpose**: Configure and manage LLM models  
**Audience**: Backend developers  
**Status**: ✅ Up to date

**Key Concepts**:
- Model configuration
- Creative vs Evaluation modes
- API key management

---

#### [Workflow Module](workflow-module.md) 🔥 **UPDATED**
**Purpose**: Build and execute multi-step workflows  
**Audience**: **Both - Critical for integration!**  
**Status**: ✅ **Completely rewritten for client-driven execution**

**What Changed**:
- ❌ Old: Server executes workflows automatically
- ✅ New: Client polls and executes nodes

**Key Concepts**:
- Client-driven execution model
- Polling loop
- State machine (NEW → PENDING → IN_PROGRESS → COMPLETED)
- Node types (APPLICATION, UTILITY, config nodes)

---

## 🏢 Application-Specific Documentation

### Akashavani (Backend)

#### [Overview](akashavani/overview.md)
- Code quality review (8/10)
- Critical updates (workflow engine)
- Configuration recommendations
- Testing & deployment

#### [Modules Guide](akashavani/modules.md)
- Bot module status
- Storage enhancements
- Workflow updates
- LLM configuration
- Environment setup

**Current Status**: ✅ Excellent - minimal changes needed

---

### Sangama (Frontend)

#### [Overview](sangama/overview.md)
- Code quality review (7/10)
- **Critical**: Execution loop missing!
- Type updates needed
- UI improvements

#### [Bot Module Integration](sangama/bot-module.md)
- Current implementation review
- Workflow integration patterns
- Improvements & refactoring
- Testing recommendations

#### [Storage Module Integration](sangama/storage-module.md)
- File picker requirements
- Version selector
- Data dependency resolution
- Upload/delete features

**Current Status**: 🟡 Good architecture, needs execution loop

---

## 🚀 Implementation Priorities

### For Sangama (Frontend)

**Phase 1 - Critical** (2-3 hours):
1. Implement `useWorkflowExecutionLoop` hook
2. Add repository methods (`getExecutionStatus`, etc.)
3. Update types (`ExecutionStatus`, new states)

**Phase 2 - High** (1 day):
4. Add execution progress UI
5. Wire up execution in WorkflowDashboard

**Phase 3 - Medium** (1-2 days):
6. File picker for storage inputs
7. Version selector
8. Enhanced error handling

---

### For Akashavani (Backend)

**Phase 1 - Critical** (10 minutes):
1. Update Pravaha: `pip install -e .`
2. Restart server

**Phase 2 - Recommended** (1-2 days):
3. Add environment variables
4. Add logging middleware
5. Storage upload/delete endpoints

**Phase 3 - Optional**:
6. Unit tests
7. Production deployment config

---

## 📝 Documentation Conventions

### File Naming
- Module docs: `{module}-module.md`
- App-specific: `{app}/{topic}.md`
- Lowercase with hyphens

### Structure
- Overview section
- Current implementation
- API endpoints
- Best practices
- Examples

### Status Indicators
- ✅ Working / Up to date
- 🟡 Needs attention
- 🔴 Critical issue
- 🔥 Recently updated

---

## 🔄 Recent Updates

### 2026-01-12
- ✅ Completely rewrote [workflow-module.md](workflow-module.md) for client-driven execution
- ✅ Created [akashavani/](akashavani/) directory with app-specific guides
- ✅ Created [sangama/](sangama/) directory with integration guides
- ✅ Updated all cross-references

### What Changed
- Workflow execution model: server-side → client-driven
- New API endpoints: `/execution/*`
- State management: OrchestrationEngine
- Documentation: Reorganized by application

---

## 🆘 Getting Help

### For Implementation Questions
- Check app-specific documentation first
- Review module documentation
- See code examples in docs

### For Bug Reports
- Check current status in overview docs
- Verify Pravaha version is latest
- Review recent updates section

### For Feature Requests
- Review improvement docs
- Check if already planned
- Consider priority level

---

## 📚 Additional Resources

- [Implementation Plan](../client_driven_execution/implementation_plan.md) - Technical details
- [Walkthrough](../client_driven_execution/walkthrough.md) - What was implemented
- [UI Analysis](../client_driven_execution/ui_analysis.md) - UI codebase review

---

**Maintained by**: Pravaha Development Team  
**Questions?**: Check app-specific overview documents first
