# Sangama - LLM Configuration Guide

**Application**: Sangama UI  
**Module**: LLM Model Configuration  
**Last Updated**: 2026-01-12

---

## Overview

The LLM module allows users to configure and manage different LLM models for use in applications and workflows.

---

## Current Implementation

### Features

1. **Model Selection**: Choose from configured LLM models
2. **Mode Selection**: Creative vs Evaluation presets
3. **Parameter Control**: Temperature, top_p, max_tokens
4. **API Key Management**: Configure API keys per model

### Data Flow

```typescript
// Frontend selects model and mode
const llmConfig: LLMConfigOverride = {
  model_config: {
    base_url: "https://api.openai.com/v1",
    model: "gpt-4",
    api_key: "sk-..."
  },
  llm_parameters: {
    temperature: 0.7,
    top_p: 0.9,
    max_completion_tokens: 2000
  }
}

// Sent to backend with application request
await ApplicationRepo.runApplicationStream(baseUrl, {
  task_name: "generate_content",
  inputs: [...],
  llm_config_override: llmConfig  // ← LLM config here
})
```

---

## Integration Points

### 1. Application Execution

When executing applications, LLM config is passed as `llm_config_override`:

```typescript
const { handleRun } = useApplicationViewModel()

// Execute with custom LLM config
await handleRun(inputs, llmConfig)
```

### 2. Workflow Nodes

LLM config can be set at node level or globally:

**Global LLM Node**:
```json
{
  "id": "global-llm",
  "node_type": "GLOBAL_LLM",
  "llm_config": {
    "model_config": {"model": "gpt-4"},
    "llm_parameters": {"temperature": 0.7}
  }
}
```

**Node-Specific Override**:
```json
{
  "id": "node-1",
  "node_type": "APP",
  "task_name": "generate_content",
  "llm_config": {  // ← Overrides global
    "model_config": {"model": "gpt-3.5-turbo"},
    "llm_parameters": {"temperature": 0.9}
  }
}
```

### 3. LLM Config Repository

**File**: `src/renderer/src/features/llm/data/LLMConfigRepository.ts` (if exists)

Loads available models from backend:

```typescript
const models = await api.get<LLMModel[]>('/api/llm/models')
// Returns list of configured models with metadata
```

---

## API Endpoints

### GET `/api/llm/models`

List all configured LLM models.

**Response**:
```json
[
  {
    "id": "gpt-4",
    "name": "GPT-4",
    "provider": "openai",
    "base_url": "https://api.openai.com/v1",
    "modes": ["creative", "evaluation"]
  },
  {
    "id": "gemma-3-12b",
    "name": "Gemma 3 12B",
    "provider": "lm_studio",
    "base_url": "http://localhost:1234/v1",
    "modes": ["creative"]
  }
]
```

### GET `/api/llm/config`

Get current LLM configuration file content.

**Response**: JSON object with all configured models

### POST `/api/llm/config`

Update LLM configuration.

**Request**: Updated config JSON

---

## UI Components Status

### ✅ What Exists (Likely)

Based on workflow node configuration, there should be:

1. **Model Selector Dropdown**
   - List of available models
   - Shows model name and provider

2. **Mode Toggle**
   - Creative (higher temperature)
   - Evaluation (lower temperature)

3. **Parameter Sliders**
   - Temperature (0.0 - 1.0)
   - Top P (0.0 - 1.0)
   - Max Tokens (configurable range)

### ⚠️ Potential Gaps

#### 1. API Key Management UI

**Current**: Likely manual config file editing  
**Better**: UI for API key input

```typescript
// NEW: components/APIKeyManager.tsx
const APIKeyManager = ({ modelId }: { modelId: string }) => {
  const [apiKey, setApiKey] = useState('')
  const [saved, setSaved] = useState(false)
  
  const saveKey = async () => {
    await llmConfigRepo.updateAPIKey(modelId, apiKey)
    setSaved(true)
  }
  
  return (
    <div>
      <Input 
        type="password" 
        value={apiKey}
        onChange={(e) => setApiKey(e.target.value)}
        placeholder="Enter API key"
      />
      <Button onClick={saveKey}>Save</Button>
      {saved && <CheckIcon />}
    </div>
  )
}
```

**Requires**: Backend endpoint to securely update API keys

---

#### 2. Model Testing

**Missing**: Test model connection before using

```typescript
const testModelConnection = async (modelConfig: LLMModelConfig) => {
  try {
    const response = await api.post('/api/llm/test', { model_config: modelConfig })
    if (response.isSuccess) {
      return { success: true, message: 'Connection successful!' }
    }
  } catch (error) {
    return { success: false, message: error.message }
  }
}

// UI:
<Button onClick={() => testModelConnection(currentConfig)}>
  Test Connection
</Button>
```

---

#### 3. Model Presets

**Current**: Manual parameter entry  
**Better**: Save/load presets

```typescript
interface LLMPreset {
  name: string
  description: string
  model_config: LLMModelConfig
  llm_parameters: LLMParameters
}

const presets: LLMPreset[] = [
  {
    name: "Creative Writing",
    description: "High creativity for content generation",
    model_config: { model: "gpt-4" },
    llm_parameters: { temperature: 0.9, top_p: 0.95 }
  },
  {
    name: "Code Generation",
    description: "Focused and precise",
    model_config: { model: "gpt-4" },
    llm_parameters: { temperature: 0.2, top_p: 0.9 }
  }
]

// UI: Preset dropdown
<Select onChange={(name) => loadPreset(name)}>
  {presets.map(p => <option value={p.name}>{p.name}</option>)}
</Select>
```

---

## Best Practices

### 1. Secure API Key Storage

**Don't**:
```typescript
const apiKey = "sk-1234..."  // Hardcoded!
```

**Do**:
```typescript
// Store in encrypted local storage or environment
const apiKey = await secureStorage.get('openai_api_key')
```

### 2. Model Availability Checks

```typescript
const checkModelAvailability = async (modelId: string) => {
  const models = await api.get('/api/llm/models')
  return models.data.some(m => m.id === modelId)
}

// Before using model:
if (!await checkModelAvailability(selectedModel)) {
  alert('Selected model not available!')
}
```

### 3. Parameter Validation

```typescript
const validateParameters = (params: LLMParameters) => {
  if (params.temperature < 0 || params.temperature > 1) {
    throw new Error('Temperature must be between 0 and 1')
  }
  if (params.top_p < 0 || params.top_p > 1) {
    throw new Error('Top P must be between 0 and 1')
  }
  // ... other validations
}
```

---

## Workflow Integration

### Priority in Workflow Execution

1. **Node-specific LLM config** (highest priority)
2. **Global LLM node config**
3. **Application default config** (lowest priority)

**Resolution Logic**:
```typescript
const resolveLLMConfig = (
  node: WorkflowNode, 
  globalLLMNode?: WorkflowNode
): LLMConfigOverride | undefined => {
  // Priority 1: Node has own config
  if (node.llm_config) {
    return node.llm_config
  }
  
  // Priority 2: Use global LLM node
  if (globalLLMNode?.llm_config) {
    return globalLLMNode.llm_config
  }
  
  // Priority 3: undefined (use app default)
  return undefined
}
```

---

## Improvements Needed

### High Priority

1. **API Key UI Management**
   - Secure input/storage
   - Per-model key configuration
   
2. **Connection Testing**
   - Test button for each model
   - Error feedback

### Medium Priority

3. **Presets System**
   - Save frequently used configs
   - Quick switching

4. **Model Info Display**
   - Show model capabilities
   - Token limits
   - Pricing info (if available)

### Low Priority

5. **Usage Tracking**
   - Track token usage per model
   - Cost estimation

6. **Advanced Parameters**
   - Stop sequences
   - Presence penalty
   - Frequency penalty

---

## Testing Checklist

- [ ] Select different models from dropdown
- [ ] Toggle between creative/evaluation modes
- [ ] Adjust temperature slider
- [ ] Test with workflow global LLM node
- [ ] Test with node-specific override
- [ ] Verify priority resolution works
- [ ] Test API key update (if implemented)

---

## Summary

**Status**: 🟢 **Working** - Core functionality solid

**Strengths**:
- Model selection works
- Mode presets functional
- Parameter control available
- Workflow integration clear

**Improvements**:
- UI for API key management
- Connection testing
- Preset system
- Better validation

**Priority**: 🟢 **Low** - Works well, enhancements optional
