# Sangama - Storage Module Guide

**Application**: Sangama UI  
**Module**: Storage Browser & Management  
**Last Updated**: 2026-01-12

---

## Current Implementation

### Features

1. **Storage Browser**: Browse output/intermediate/knowledge files
2. **Multi-Tab Interface**: Open multiple files simultaneously
3. **File Preview**: View file contents
4. **Version Management**: Handle versioned artifacts

### Architecture

```
features/storage/
├── data/
│   └── StorageRepositoryImpl.ts
├── domain/
│   ├── StorageRepository.ts
│   └── types.ts
└── presentation/
    ├── viewmodels/
    │   └── useStorageBrowserViewModel.ts
    └── views/
        ├── OutputDashboard.tsx
        ├── IntermediateDashboard.tsx
        └── KnowledgeDashboard.tsx
```

---

## Integration with Workflows

### File Input Support

Workflows support file inputs from storage:

```typescript
// Workflow node with file input
{
  "id": "node-1",
  "task_name": "process_document",
  "inputs": {
    "data": {
      "key_name": "data",
      "source": "file",  // ← File input!
      "path": "knowledge/documents/input.json",
      "format": "json",
      "fileSource": "knowledge",  // knowledge | output | intermediate
      "autoSelectLatest": true,
      "selectedVersion": "v1.0.0"
    }
  }
}
```

### How It Works

**When executing a workflow node with file inputs**:

1. **Client checks file source**:
   ```typescript
   if (input.source === 'file') {
     const filePath = input.path
     const fileData = await loadFileFromStorage(filePath, input.fileSource)
     // Send fileData to application API
   }
   ```

2. **Load from appropriate storage category**:
   ```typescript
   async function loadFileFromStorage(path: string, source: FileSource) {
     const category = source // 'knowledge' | 'output' | 'intermediate'
     const response = await storageRepo.loadContent(category, path)
     return response.data
   }
   ```

3. **Handle versioning if needed**:
   ```typescript
   if (input.autoSelectLatest) {
     // Get latest version
     const versions = await storageRepo.listVersions(category, path)
     const latest = versions[0]
     return loadVersion(latest.path)
   } else if (input.selectedVersion) {
     return loadVersion(input.selectedVersion)
   }
   ```

---

## Current Features Review

### ✅ What Works

1. **Tree Browsing**: Feature/Product/Version hierarchy
2. **File Loading**: Content preview with syntax highlighting
3. **Multi-Tab**: Open multiple files
4. **Download**: Save files locally

### ⚠️ Workflow Integration Gaps

#### 1. Missing: File Picker for Workflow Inputs

**Current**: Manual path entry  
**Needed**: Visual file picker

**Implementation**:
```typescript
// NEW: components/FilePicker.tsx
export const FilePicker = ({ 
  category, 
  onSelect 
}: { 
  category: 'knowledge' | 'output' | 'intermediate',
  onSelect: (path: string) => void 
}) => {
  const { tree } = useStorageBrowserViewModel(category)
  
  return (
    <TreeView>
      {tree.map(node => (
        <TreeNode 
          key={node.id} 
          node={node}
          onClick={() => onSelect(node.path)}
        />
      ))}
    </TreeView>
  )
}

// Usage in InputConfigurationPanel:
{input.source === 'file' && (
  <FilePicker 
    category={input.fileSource || 'knowledge'}
    onSelect={(path) => updateInput({ ...input, path })}
  />
)}
```

---

#### 2. Missing: Version  Selector

**Current**: Manual version entry  
**Needed**: Dropdown with available versions

```typescript
// NEW: components/VersionSelector.tsx
export const VersionSelector = ({ 
  category, 
  filePath, 
  onSelect 
}: VersionSelectorProps) => {
  const [versions, setVersions] = useState<FileVersion[]>([])
  
  useEffect(() => {
    storageRepo.listVersions(category, filePath).then(setVersions)
  }, [category, filePath])
  
  return (
    <Select onChange={(v) => onSelect(v)}>
      <option value="">Latest</option>
      {versions.map(v => (
        <option key={v.path} value={v.path}>
          {v.timestamp} - {v.size} bytes
        </option>
      ))}
    </Select>
  )
}
```

---

#### 3. Missing: Data Dependency Resolution

**Scenario**: Node B needs output from Node A

**Current**: No helper to load node outputs  
**Needed**: Client-side output resolution

```typescript
// NEW: services/WorkflowDataResolver.ts
export class WorkflowDataResolver {
  constructor(
    private storageRepo: StorageRepository,
    private workflowRepo: WorkflowRepository
  ) {}
  
  async resolveNodeInputs(
    runId: string, 
    node: WorkflowNode
  ): Promise<Record<string, any>> {
    const resolved = {}
    
    for (const [key, input] of Object.entries(node.inputs)) {
      if (input.source === 'direct') {
        resolved[key] = input.value
      } 
      else if (input.source === 'file') {
        // Load from storage
        const data = await this.loadFile(input)
        resolved[key] = data
      }
      else if (input.source.startsWith('node:')) {
        // Load from previous node output
        const nodeId = input.source.replace('node:', '')
        const output = await this.workflowRepo.getNodeOutput(runId, nodeId)
        resolved[key] = output.data
      }
    }
    
    return resolved
  }
  
  private async loadFile(input: FileInputItem) {
    const content = await this.storageRepo.loadContent(
      input.fileSource,
      input.path
    )
    
    if (input.format === 'json') {
      return JSON.parse(content)
    }
    return content
  }
}
```

---

## API Endpoints Used

### Storage Configuration

```http
GET /api/storage/config
POST /api/storage/config
```

Used to get/set storage paths.

### Storage Browsing

```http
GET /api/storage/{category}/browse?path={path}
```

Categories: `output`, `intermediate`, `knowledge`

Returns tree structure with files and folders.

### Content Loading

```http
GET /api/storage/{category}/content?path={path}
```

Returns file content as text/binary.

---

## Improvements Needed

### 1. Lazy Loading for Large Trees

**Current**: Loads entire tree at once  
**Issue**: Slow for large storage

**Solution**: Load on-demand

```typescript
const loadChildrenOnExpand = async (nodeId: string) => {
  if (!loadedNodes.has(nodeId)) {
    const children = await storageRepo.browse(nodePath)
    setTree(prev => insertChildren(prev, nodeId, children))
    loadedNodes.add(nodeId)
  }
}
```

---

### 2. Search Functionality

**Current**: Browse only  
**Needed**: Search by filename/content

```typescript
// NEW API endpoint needed in Akashavani:
GET /api/storage/{category}/search?query={query}

// UI implementation:
const [searchQuery, setSearchQuery] = useState('')
const [searchResults, setSearchResults] = useState<FileNode[]>([])

const handleSearch = async (query: string) => {
  const results = await storageRepo.search(category, query)
  setSearchResults(results)
}

<SearchBar onSearch={handleSearch} />
<SearchResults results={searchResults} />
```

---

### 3. Upload Files from UI

**Current**: Manual file placement  
**Needed**: Upload via UI

```typescript
const uploadFile = async (file: File, category: string, path: string) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('path', path)
  
  await storageRepo.upload(category, formData)
  
  // Refresh tree
  await refreshTree()
}

// UI:
<FileUploader 
  category="knowledge"
  onUpload={uploadFile}
/>
```

**Requires**: New Akashavani endpoint `POST /api/storage/{category}/upload`

---

### 4. Delete Files

**Current**: No delete functionality  
**Needed**: Delete files/folders

```typescript
const deleteFile = async (category: string, path: string) => {
  if (confirm(`Delete ${path}?`)) {
    await storageRepo.delete(category, path)
    await refreshTree()
  }
}
```

**Requires**: New endpoint `DELETE /api/storage/{category}?path={path}`

---

## Integration Checklist for Workflows

When using storage in workflows:

- [ ] Add `FilePicker` component for file input selection
- [ ] Add `VersionSelector` for version selection
- [ ] Implement `WorkflowDataResolver` for input resolution
- [ ] Handle file loading errors gracefully
- [ ] Show upload progress for large files
- [ ] Cache loaded files to avoid re-loading

---

## Best Practices

1. **File Paths**: Use forward slashes `/` consistently
2. **Version Selection**: Default to latest unless explicitly specified
3. **Error Handling**: Handle missing files gracefully
4. **Caching**: Cache file content to reduce API calls
5. **Large Files**: Show loading indicators for files >1MB

---

## Summary

**Status**: 🟡 **Good but Needs Workflow Integration**

**Current Strengths**:
- Tree browsing works well
- Multi-tab interface functional
- File preview solid

**Workflow Integration Gaps**:
- No visual file picker (manual path entry)
- No version selector UI
- Missing data dependency resolution
- No upload/delete from UI

**Priority**: 🟡 **Medium** - Can use storage with workflows via manual paths, but UX improvements needed
