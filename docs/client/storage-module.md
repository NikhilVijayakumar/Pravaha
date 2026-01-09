# Storage Module - Client Documentation

> **💡 Quick Start:** Use **[API Factory](api-factory.md)** to auto-configure storage! This guide shows storage organization details.

The Storage module provides organized file system management for outputs, intermediate results, and knowledge bases.

## Overview

Features:
- **Three Categories**: Output (final results), Intermediate (temp data), Knowledge (reference data)
- **Hierarchical Structure**: Version/Feature/Product organization for outputs
- **Recursive Browsing**: Navigate nested folder structures
- **File Reading**: Read JSON and text files via API
- **Dynamic Config**: Update storage paths at runtime

## Storage Categories

### 1. Output
Final results from your applications.

**Default Path:** `./output`

**Structure:**
```
output/
├── v1.0/                    # Version
│   ├── feature-a/           # Feature
│   │   ├── product-1/       # Product
│   │   │   └── result.json
│   │   └── default/
│   │       └── output.json
│   └── feature-b/
│       └── default/
│           └── data.json
```

### 2. Intermediate
Temporary/in-progress data.

**Default Path:** `./intermediate`

**Structure:** Same as Output

### 3. Knowledge
Reference data, documentation, knowledge bases.

**Default Path:** `./knowledge`

**Structure:** Simple file tree (no version/feature/product)
```
knowledge/
├── docs/
│   └── guide.md
└── data/
    └── reference.json
```

## Setup

### Initialize Storage Manager

```python
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager

# Use defaults
storage_manager = LocalStorageManager()

# Specify custom paths
storage_manager = LocalStorageManager(
    output_path="custom/output",
    intermediate_path="custom/intermediate",
    knowledge_path="custom/knowledge"
)
```

### Wire Up API

```python
from pravaha.domain.storage.provider.storage_api_provider import StorageAPIProvider

provider = StorageAPIProvider(storage_manager)
app.include_router(provider.router, prefix="/api")
```

## API Endpoints

### GET `/api/storage/{category}/browse`
Browse files and folders recursively.

**Parameters:**
- `path` (optional): Subfolder path

**Examples:**
```bash
# Browse root
GET /api/storage/output/browse

# Browse nested folder
GET /api/storage/output/browse?path=v1.0/feature-a

# Browse knowledge
GET /api/storage/knowledge/browse?path=docs
```

**Response:**
```json
{
  "name": "v1.0",
  "type": "folder",
  "children": [
    {
      "name": "feature-a",
      "type": "folder",
      "children": [
        {
          "name": "result.json",
          "type": "file",
          "version": "v1.0",
          "feature": "feature-a",
          "product": "default",
          "display_name": "Result.json",
          "path": "v1.0/feature-a/default/result.json"
        }
      ]
    }
  ]
}
```

### GET `/api/storage/{category}/read`
Read file contents.

**Parameters:**
- `path`: File path (required)

**Examples:**
```bash
# Read JSON file
GET /api/storage/output/read?path=v1.0/feature-a/default/result.json

# Read text file
GET /api/storage/knowledge/read?path=docs/guide.md
```

**Response:**
- JSON files: Parsed JSON object
- Text files: Plain text string

### POST `/api/storage/config`
Update storage paths dynamically.

**Request:**
```json
{
  "output_path": "new/output/path",
  "intermediate_path": "new/intermediate/path",
  "knowledge_path": "new/knowledge/path"
}
```

### GET `/api/storage/config`
Get current storage configuration.

**Response:**
```json
{
  "output_path": "/absolute/path/to/output",
  "intermediate_path": "/absolute/path/to/intermediate",
  "knowledge_path": "/absolute/path/to/knowledge"
}
```

## Using Storage Provider

### Save Output Files

```python
from pravaha.domain.storage.provider.output_storage_provider import OutputStorageProvider

output_provider = OutputStorageProvider(
    base_path="./output",
    version="v1.0",
    feature="my-feature"
)

# Save with default product
output_provider.save_output(
    data={"result": "success"},
    filename="result.json"
)

# Save with specific product
output_provider.save_output(
    data={"result": "success"},
    filename="result.json",
    product="product-a"
)
```

### Save Intermediate Results

```python
from pravaha.domain.storage.provider.intermediate_storage_provider import IntermediateStorageProvider

intermediate_provider = IntermediateStorageProvider(
    base_path="./intermediate",
    version="v1.0",
    feature="processing"
)

intermediate_provider.save_intermediate(
    data={"step": 1, "status": "in_progress"},
    filename="step1.json"
)
```

## Configuration File

Storage config is saved to:`.Pravaha/config/storage_config.json`

```json
{
  "output_path": "output",
  "intermediate_path": "intermediate",
  "knowledge_path": "knowledge"
}
```

## Best Practices

1. **Version Your Outputs**: Use semantic versioning (v1.0, v2.0, etc.)
2. **Organize by Feature**: Group related outputs by feature name
3. **Use Products for Variants**: Different LLM configs = different products
4. **Knowledge as Reference**: Store docs, schemas, examples in knowledge
5. **Intermediate for Debug**: Save intermediate steps for debugging
6. **Relative Paths**: Storage paths are relative to project root

## Example: Full Workflow

```python
# In your application
def generate_report(topic, version="v1.0"):
    # Save intermediate
    intermediate = IntermediateStorageProvider(
        version=version,
        feature="report-generation"
    )
    intermediate.save_intermediate(
        {"status": "started", "topic": topic},
        "status.json"
    )
    
    # Generate report
    report = create_report(topic)
    
    # Save final output
    output = OutputStorageProvider(
        version=version,
        feature="report-generation",
        product="gpt-4"
    )
    output.save_output(report, f"{topic}_report.json")
    
    return report
```

Result structure:
```
output/v1.0/report-generation/gpt-4/quantum_report.json
intermediate/v1.0/report-generation/default/status.json
```
