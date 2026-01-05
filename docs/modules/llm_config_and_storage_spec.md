Perfect — this is the right moment to **freeze a canonical spec** and formalize the contracts.
Below is a **single, authoritative, production-grade document**, followed by **exact Python interfaces** and **Sangama API contracts**.

You can treat this as **v1.0 canonical architecture**.

---

# 📘 Pravaha

## LLM Configuration, Storage Versioning & Artifact Contract

**Canonical Specification (v1.0)**

---

## 0. Scope & Authority

This document is the **single source of truth** for:

* LLM output configuration
* Storage layout & versioning
* Artifact normalization
* Backend ↔ UI contracts

### Explicit Non-Responsibilities

* ❌ Akashavani implements **no storage logic**
* ❌ Client implements **no filesystem logic**
* ❌ UI never parses filenames

All storage semantics live **exclusively in Pravaha**.

---

## 1. Architectural Responsibility Model

```
Client / UI
  └─ consumes logical artifact metadata
     └─ no filesystem assumptions

Pravaha (Backend / Library)
  ├─ LLMConfigManager
  ├─ StoragePathResolver
  ├─ ArtifactVersionResolver
  ├─ StorageRepository
  └─ Artifact Metadata API
```

---

## 2. Core Concepts

### 2.1 Logical Artifact (Primary Abstraction)

A **Logical Artifact** is the only unit exposed outside Pravaha.

| Field     | Description                  |
| --------- | ---------------------------- |
| `feature` | Workflow step / capability   |
| `product` | Domain entity (optional)     |
| `model`   | Model alias                  |
| `version` | Integer (monotonic)          |
| `stage`   | `INTERMEDIATE` or `FINAL`    |
| `path`    | Physical path (opaque to UI) |

> Storage layout is an **implementation detail**.

---

## 3. Storage Architecture (Backend-Only)

### 3.1 Storage Stages

| Stage            | Purpose                        | Mutability    |
| ---------------- | ------------------------------ | ------------- |
| **Intermediate** | Structural / transient outputs | Replaceable   |
| **Final**        | User-consumable artifacts      | Referenceable |

---

### 3.2 Directory Layout (Internal)

| Stage        | Path Pattern                                       |
| ------------ | -------------------------------------------------- |
| Intermediate | `.Amsha/output/intermediate/output/{FeatureName}/` |
| Final        | `.Amsha/final/{ProductName}/{FeatureName}/`        |

> Consumers never hardcode these paths.

---

## 4. Versioning Strategy (Filename-Based)

### 4.1 Version Definition

> **Version** is a monotonically increasing integer representing successive outputs of the same
> `(stage, feature, product, model)` tuple.

---

### 4.2 Filename Pattern

```
v1 → {alias}.json
v2 → {alias}_1.json
vN → {alias}_{N-1}.json
```

---

### 4.3 Version Resolution Algorithm (Canonical)

1. Resolve base directory (stage, feature, product)
2. Resolve model alias via `LLMConfigManager`
3. Scan files matching `{alias}*.json`
4. Parse suffixes:

   * no suffix → version 1
   * `_K` → version `K+1`
5. Next version = `max(version) + 1`

---

## 5. LLM Configuration (`llm_config.yaml`)

### 5.1 Augmented Schema (Canonical)

```yaml
llm:
  creative:
    models:
      gemini:
        model: "gemini/gemini-2.5-flash"
        output_config:
          alias: "gemini-2.5-flash"
          structure: "flat"
          display_name: "Gemini 2.5 Flash"

      gpt:
        model: "lm_studio/openai/gpt-oss-20b"
        output_config:
          alias: "gpt-oss-20b"
          structure: "folder"
          folder_name: "openai"
          display_name: "GPT OSS 20B"
```

---

### 5.2 `structure` Semantics (Backend Only)

| Structure | Physical Result                       |
| --------- | ------------------------------------- |
| `flat`    | `{base}/{alias}_N.json`               |
| `folder`  | `{base}/{folder_name}/{alias}_N.json` |

> **Important:**
> Structure affects **only filesystem layout**, never versioning or UI representation.

---

## 6. Pravaha Internal Services (Exact Interfaces)

### 6.1 `LLMConfigManager`

```python
class LLMOutputConfig(TypedDict):
    alias: str
    structure: Literal["flat", "folder"]
    folder_name: NotRequired[str]
    display_name: NotRequired[str]
```

```python
class LLMConfigManager(Protocol):
    def resolve_output_config(self, model_key: str) -> LLMOutputConfig:
        """
        Resolves output configuration for a model.
        """
    
    def get_all_config(self) -> dict:
        """
        Returns the complete LLM configuration dictionary.
        """
```

> **Implementation Note (Caching)**:
> `LLMConfigManager` enforces a single source of truth by caching provided config files to `.Pravaha/config/llm_config.yaml`. All reads occur from this cached location.

---

### 6.2 `ArtifactVersionResolver`

```python
class ArtifactVersionResolver(Protocol):
    def get_latest_version(
        self,
        stage: StorageStage,
        feature: str,
        product: str | None,
        model_alias: str
    ) -> int | None

    def get_next_version(
        self,
        stage: StorageStage,
        feature: str,
        product: str | None,
        model_alias: str
    ) -> int
```

---

### 6.3 `StoragePathResolver` (Critical)

```python
class StorageStage(Enum):
    INTERMEDIATE = "intermediate"
    FINAL = "final"
```

```python
class StoragePathResolver(Protocol):
    def resolve_output_path(
        self,
        stage: StorageStage,
        feature: str,
        product: str | None,
        model_key: str
    ) -> Path:
        """
        Returns deterministic path for the NEXT version.
        """
```

Responsibilities:

* Uses `LLMConfigManager`
* Uses `ArtifactVersionResolver`
* Applies `flat` / `folder` rules
* **No file writing**

---

### 6.4 `StorageRepository`

```python
class StorageRepository(Protocol):
    def write_json(self, path: Path, payload: dict) -> None
    def read_json(self, path: Path) -> dict
    def list_files(self, path: Path) -> list[Path]
```

---

## 7. Artifact Metadata Model (Canonical)

```python
class ArtifactMetadata(TypedDict):
    feature: str
    product: str | None
    model: str
    version: int
    stage: Literal["intermediate", "final"]
    path: str
    created_at: str
    display_name: str | None
```

---

## 8. API Contracts

### 8.1 API Usage Rule

> Clients operate exclusively on **ArtifactMetadata**.
> They never infer version, model, or structure from filenames.

### 8.2 API Hierarchy (Flat Logical View)

```
Feature
 └─ Product (optional)
     └─ Model
         └─ Version 1
         └─ Version 2
         └─ Version N
```

### 8.3 HTTP Endpoints (Hybrid Mode)

The Storage API operates in a **Hybrid Mode**:
- **Knowledge**: Legacy directory browsing.
- **Intermediate / Final**: Metadata-driven Artifact browsing.

#### 1. Browse / List Artifacts

```http
GET /storage/{bucket}/browse?path=...
```

**Behavior**:
- `bucket=knowledge`: Returns file/folder list (Legacy).
- `bucket=output|intermediate`: Returns list of **Artifacts** (JSON).

**Response (Artifacts)**:
```json
[
  {
    "feature": "ScientificKnowledge",
    "product": "Photosynthesis",
    "model": "gemini-2.5-flash",
    "version": 3,
    "stage": "final",
    "path": "...",
    "created_at": "2026-01-04T12:00:00Z",
    "display_name": "Gemini 2.5 Flash"
  }
]
```

#### 2. Read Content

```http
GET /storage/{bucket}/read?path=...
```

**Behavior**:
- Returns content wrapped in `{"content": ...}` for backward compatibility.
- For artifacts, `path` is the absolute path returned by `list`.

#### 3. LLM Configuration

```http
GET /api/llm/config
```

**Response**:
- Returns the full content of `llm_config.yaml` as a JSON object.

---

## 9. Hard Guarantees

✔ Storage layout can change without UI changes
✔ Folder → flat migration is possible
✔ Version folders can be introduced later
✔ Deterministic reproducibility
✔ Clean separation of concerns

---

## 10. Explicit Non-Goals (Locked)

❌ UI-driven storage decisions
❌ Provider-based UI grouping
❌ Filename parsing in UI
❌ Akashavani storage logic

---

## 11. Architectural Status

**This specification is considered stable for v1.x.**

Future additions must:

* Preserve logical artifact abstraction
* Remain backward-compatible at the metadata level

---

## Final Assessment

This is now:

* **Canonical**
* **Unambiguous**
* **Implementation-ready**
* **Future-proof**

You’ve cleanly separated:

* *Intent* (workflow)
* *Execution* (Pravaha)
* *Persistence* (storage)
* *Visibility* (Sangama)


