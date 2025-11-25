# Virtual Environment Usage for Pravaha Development

## Issue
Installation should happen in virtual environment, not user-level packages, to ensure isolation and reproducibility.

## Solution

### Always Activate Virtual Environment First

**PowerShell (Windows):**
```powershell
# Activate venv
.\\venv\\Scripts\\Activate.ps1

# Verify activation (should show venv path)
$env:VIRTUAL_ENV

# Now install/run commands
pip install -e .
```

**Bash/Linux:**
```bash
# Activate venv
source venv/bin/activate

# Verify
echo $VIRTUAL_ENV

# Install/run
pip install -e .
```

**On macOS:**
```bash
# Activate venv
source venv/bin/activate

# Verify
echo $VIRTUAL_ENV

# Install
pip install -e .
```

---

## How to Tell If Virtual Environment is Active

**PowerShell (Windows):**
```powershell
if (Test-Path env:VIRTUAL_ENV) {
    Write-Host "✅ Virtual env active: $env:VIRTUAL_ENV"
} else {
    Write-Host "❌ No virtual environment active"
}
```

**Bash/Linux/macOS:**
```bash
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ Virtual env active: $VIRTUAL_ENV"
else
    echo "❌ No virtual environment active"
fi
```

**Prompt Indicator:**
```
(venv) $ pwd                    # ✅ Active (note the (venv) prefix)
/home/dell/PycharmProjects/Pravaha

$ pwd                           # ❌ Not active
/home/dell/PycharmProjects/Pravaha
```

---

## Installation Path Check

**User-level (Wrong for dev):**
```
/home/dell/.local/lib/python3.12/site-packages
c:\\users\\username\\appdata\\roaming\\python\\python312\\site-packages
```

**Virtual environment (Correct):**
```
/home/dell/PycharmProjects/Pravaha/venv/lib/python3.12/site-packages
e:\\projects\\pravaha\\venv\\lib\\site-packages
```

**Check where packages are installed:**
```bash
# Should show venv path when active
python -c "import site; print(site.getsitepackages())"
```

---

## Workflow for Development

### 1. One-Time Setup

**Linux/Mac:**
```bash
cd /home/dell/PycharmProjects/Pravaha

# Create venv (if not exists)
python -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install in editable mode
pip install -e .
```

**Windows PowerShell:**
```powershell
cd C:\\Projects\\Pravaha

# Create venv
python -m venv venv

# Activate
.\\venv\\Scripts\\Activate.ps1

# Upgrade pip
pip install --upgrade pip

# Install
pip install -e .
```

### 2. Daily Workflow

```bash
# Always activate first
source venv/bin/activate  # Linux/Mac
# OR
.\\venv\\Scripts\\Activate.ps1  # Windows

# Then work normally
python scripts/test_api.py
pytest
uvicorn main:app --reload
git commit -m "Update"
```

### 3. Deactivate When Done

```bash
deactivate
```

---

## VS Code Integration

### Auto-Activate in VS Code

1. **Select Python Interpreter:**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Python: Select Interpreter"
   - Choose `./venv/bin/python` (Linux/Mac) or `.\\venv\\Scripts\\python.exe` (Windows)

2. **VS Code will auto-activate venv in new terminals**

3. **Verify in new terminal:**
   ```bash
   # Should see (venv) prefix
   (venv) $ python --version
   ```

4. **Settings.json (Optional):**
   ```json
   {
       "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
       "python.terminal.activateEnvironment": true
   }
   ```

---

## PyCharm Integration

1. **Open Project Settings:**
   - File → Settings (or Preferences on Mac)
   - Project: Pravaha → Python Interpreter

2. **Add Interpreter:**
   - Click gear icon → Add
   - Select "Existing environment"
   - Choose `venv/bin/python` (Linux/Mac) or `venv\\Scripts\\python.exe` (Windows)

3. **PyCharm will auto-activate venv in terminals**

---

## Common Issues & Solutions

### Issue 1: "Command not found" after pip install

**Cause:** Virtual environment not activated

**Solution:**
```bash
# Activate venv first
source venv/bin/activate  # Linux/Mac
.\\venv\\Scripts\\Activate.ps1  # Windows

# Then install
pip install -e .
```

### Issue 2: "Installing to user packages"

**Cause:** Venv not activated when running pip

**Solution:**
```bash
# Check if venv is active
echo $VIRTUAL_ENV  # Linux/Mac
$env:VIRTUAL_ENV   # Windows

# If empty, activate
source venv/bin/activate
```

### Issue 3: "Module not found" after installation

**Cause:** Installed in user packages, but venv is active (or vice versa)

**Solution:**
```bash
# Reinstall in venv
source venv/bin/activate
pip uninstall pravaha
pip install -e .
```

### Issue 4: "Permission denied" when activating

**Cause:** Script execution policy on Windows

**Solution (Windows):**
```powershell
# Check execution policy
Get-ExecutionPolicy

# If Restricted, change to RemoteSigned
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Now activate
.\\venv\\Scripts\\Activate.ps1
```

### Issue 5: Different Python version in venv

**Cause:** Created venv with wrong Python executable

**Solution:**
```bash
# Remove old venv
rm -rf venv

# Create with specific Python version
python3.12 -m venv venv  # Linux/Mac
py -3.12 -m venv venv    # Windows

# Activate and install
source venv/bin/activate
pip install -e .
```

---

## Best Practices

### ✅ Always Activate VENV Before:
- Installing packages (`pip install`)
- Running scripts (`python script.py`)
- Running development servers (`uvicorn`)
- Running tests (`pytest`)
- Committing code (to ensure consistency)

### ✅ Project Structure:
```
Pravaha/
├── venv/                 # Virtual environment (gitignored)
├── src/
│   └── nikhil/pravaha/
├── docs/
├── pyproject.toml
├── requirements.txt      # Dev dependencies
└── README.md
```

### ✅ Add to .gitignore:
```gitignore
# Virtual environments
venv/
.venv/
env/
ENV/

# Python artifacts
*.pyc
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
build/
dist/
*.egg-info/
```

### ✅ Document in README:
Always include setup instructions in project README:

```markdown
## Development Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate:
   ```bash
   source venv/bin/activate  # Linux/Mac
   .\\venv\\Scripts\\Activate.ps1  # Windows
   ```

3. Install:
   ```bash
   pip install -e .
   ```
```

---

## Shell Profile (Optional)

### Bash Profile (~/.bashrc or ~/.bash_profile)

```bash
# Add function for quick activation
venv() {
    if [ -f ./venv/bin/activate ]; then
        source ./venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ No venv found in current directory"
    fi
}

# Usage: just type 'venv' in project directory
```

### PowerShell Profile

```powershell
# Edit profile
notepad $PROFILE

# Add function
function venv {
    if (Test-Path .\\venv\\Scripts\\Activate.ps1) {
        .\\venv\\Scripts\\Activate.ps1
        Write-Host "✅ Virtual environment activated"
    } else {
        Write-Host "❌ No venv found in current directory"
    }
}

# Save and reload
. $PROFILE

# Usage: just type 'venv' in project directory
```

### Zsh Profile (~/.zshrc)

```bash
# Add function for quick activation
venv() {
    if [ -f ./venv/bin/activate ]; then
        source ./venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ No venv found in current directory"
    fi
}
```

---

## Verification Checklist

Before starting development, verify:

- [ ] Virtual environment exists (`venv/` directory present)
- [ ] Virtual environment is activated (prompt shows `(venv)`)
- [ ] `$VIRTUAL_ENV` or `$env:VIRTUAL_ENV` is set
- [ ] `which python` or `Get-Command python` points to venv
- [ ] `pip list` shows packages in venv location
- [ ] IDE/editor is using venv interpreter

---

## CI/CD Considerations

### GitHub Actions Example:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Create virtual environment
        run: python -m venv venv
      
      - name: Activate and install
        run: |
          source venv/bin/activate
          pip install --upgrade pip
          pip install -e .
      
      - name: Run tests
        run: |
          source venv/bin/activate
          pytest
```

---

## Troubleshooting Reference

| Symptom | Cause | Solution |
|---------|-------|----------|
| No `(venv)` prefix | Not activated | Run activate script |
| `pip list` shows few packages | Wrong venv or user packages | Check `$VIRTUAL_ENV` |
| Import errors | Package in different location | Reinstall in active venv |
| Permission denied | Execution policy (Windows) | `Set-ExecutionPolicy RemoteSigned` |
| Wrong Python version | Used wrong Python to create venv | Delete and recreate with correct Python |

---

## Summary

**Problem:** Packages should be isolated to project virtual environment  
**Solution:** Always activate venv before any development work  
**Verification:** Check `$VIRTUAL_ENV` is set and points to project  
**Quick Command:** `source venv/bin/activate` (Linux/Mac) or `.\\venv\\Scripts\\Activate.ps1` (Windows)

---

**Remember:** When in doubt, deactivate and reactivate the virtual environment to ensure a clean state.
