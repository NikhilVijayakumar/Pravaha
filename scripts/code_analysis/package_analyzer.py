"""
Package Dependency Analyzer

Analyzes installed packages, checks for updates, and detects issues.
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from packaging import version as pkg_version


class PackageDependencyAnalyzer:
    """Analyzes package dependencies and versions."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.pyproject_path = project_root / "pyproject.toml"
        
    def get_installed_packages(self) -> Dict[str, str]:
        """Get all installed packages and their versions."""
        print("Getting installed packages...")
        
        result = subprocess.run(
            ["pip", "list", "--format=json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Error getting packages: {result.stderr}")
            return {}
        
        packages = json.loads(result.stdout)
        return {pkg["name"].lower(): pkg["version"] for pkg in packages}
    
    def get_outdated_packages(self) -> List[Dict]:
        """Get packages that have updates available (only for declared dependencies)."""
        print("Checking for outdated packages (declared dependencies only)...")
        
        # Get declared dependencies from pyproject.toml
        declared = self.parse_pyproject_dependencies()
        
        if not declared:
            print("No dependencies found in pyproject.toml")
            return []
        
        # Get installed versions
        installed = self.get_installed_packages()
        
        outdated = []
        
        # Check each declared dependency
        for pkg_name in declared.keys():
            current_version = installed.get(pkg_name.lower())
            
            if not current_version:
                print(f"  ⚠️ Declared package '{pkg_name}' not installed")
                continue
            
            # Get latest version from PyPI
            latest_version = self._get_latest_pypi_version(pkg_name)
            
            if latest_version and latest_version != current_version:
                update_type = self._classify_update(current_version, latest_version)
                
                outdated.append({
                    "name": pkg_name,
                    "version": current_version,
                    "latest_version": latest_version,
                    "update_type": update_type
                })
                
                print(f"  📦 {pkg_name}: {current_version} → {latest_version} ({update_type})")
        
        return outdated
    
    def _get_latest_pypi_version(self, package_name: str) -> Optional[str]:
        """Get the latest version of a package from PyPI."""
        try:
            result = subprocess.run(
                ["pip", "index", "versions", package_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse output: "package (X.Y.Z)"
                # First line usually has "Available versions: X.Y.Z, ..."
                lines = result.stdout.splitlines()
                for line in lines:
                    if "Available versions:" in line or package_name in line:
                        # Extract first version number
                        import re
                        versions = re.findall(r'\d+\.\d+(?:\.\d+)?(?:\.\w+)?', line)
                        if versions:
                            return versions[0]
        except Exception as e:
            print(f"  ⚠️ Could not check {package_name}: {e}")
        
        return None
    
    def _classify_update(self, current: str, latest: str) -> str:
        """Classify update as major, minor, or patch."""
        try:
            curr_ver = pkg_version.parse(current)
            latest_ver = pkg_version.parse(latest)
            
            # Simple heuristic
            curr_parts = str(curr_ver).split('.')
            latest_parts = str(latest_ver).split('.')
            
            if len(curr_parts) >= 1 and len(latest_parts) >= 1:
                if curr_parts[0] != latest_parts[0]:
                    return "MAJOR"
                elif len(curr_parts) >= 2 and len(latest_parts) >= 2:
                    if curr_parts[1] != latest_parts[1]:
                        return "MINOR"
            
            return "PATCH"
        except:
            return "UNKNOWN"
    
    def parse_pyproject_dependencies(self) -> Dict[str, str]:
        """Parse dependencies from pyproject.toml ([project] format)."""
        if not self.pyproject_path.exists():
            print(f"pyproject.toml not found at {self.pyproject_path}")
            return {}
        
        dependencies = {}
        
        with open(self.pyproject_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Look for dependencies = [ ... ]
        in_deps = False
        in_dev_deps = False
        
        for line in content.splitlines():
            stripped = line.strip()
            
            # Check for dependencies section start
            if "dependencies = [" in stripped:
                in_deps = True
                continue
            elif "optional-dependencies]" in stripped:
                # Entering optional deps section
                in_deps = False
                continue
            elif stripped.startswith("dev = ["):
                in_dev_deps = True
                continue
            
            # Check for section end
            if (in_deps or in_dev_deps) and "]" in stripped:
                in_deps = False
                in_dev_deps = False
                continue
            
            # Parse dependency line
            if (in_deps or in_dev_deps) and stripped and not stripped.startswith("#"):
                # Remove quotes and comma
                dep = stripped.strip(' ",')
                
                if not dep:
                    continue
                
                if "@" in dep:
                    # Git dependency: "Nibandha @ git+..."
                    pkg_name = dep.split("@")[0].strip().lower()
                    dependencies[pkg_name] = "git"
                elif "==" in dep:
                    parts = dep.split("==")
                    dependencies[parts[0].strip().lower()] = parts[1].strip()
                elif ">=" in dep:
                    parts = dep.split(">=")
                    dependencies[parts[0].strip().lower()] = parts[1].strip()
                elif dep:
                    # No version specified
                    dependencies[dep.strip().lower()] = "latest"
        
        return dependencies
    
    def find_unused_dependencies(self) -> List[str]:
        """Find dependencies in pyproject.toml that might not be used."""
        # This is a simple heuristic - scan source for imports
        declared = set(self.parse_pyproject_dependencies().keys())
        
        if not declared:
            return []
        
        # Scan source files for imports
        imported = set()
        src_dir = self.project_root / "src"
        
        if src_dir.exists():
            for py_file in src_dir.rglob("*.py"):
                imported.update(self._extract_imports_from_file(py_file))
        
        # Find unused (with common exceptions)
        exceptions = {
            "pytest", "pytest-cov", "black", "ruff", "mypy",
            "pytest-json-report", "import-linter", "pytest-asyncio",
            "httpx", "uvicorn"
        }
        
        unused = []
        for dep in declared:
            # Normalize name (replace - with _)
            normalized = dep.replace("-", "_")
            
            if dep not in exceptions and dep not in imported and normalized not in imported:
                unused.append(dep)
        
        return unused
    
    def _extract_imports_from_file(self, file_path: Path) -> set:
        """Extract import names from a Python file."""
        imports = set()
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    
                    # Simple regex for imports
                    if line.startswith("import "):
                        parts = line.split()
                        if len(parts) >= 2:
                            pkg = parts[1].split(".")[0].lower()
                            imports.add(pkg)
                    
                    elif line.startswith("from "):
                        parts = line.split()
                        if len(parts) >= 2:
                            pkg = parts[1].split(".")[0].lower()
                            imports.add(pkg)
        except:
            pass
        
        return imports
    
    def analyze(self) -> Dict:
        """Run full analysis."""
        print("Running package dependency analysis...")
        
        installed = self.get_installed_packages()
        outdated = self.get_outdated_packages()
        declared = self.parse_pyproject_dependencies()
        unused = self.find_unused_dependencies()
        
        # Statistics
        up_to_date = len(declared) - len(outdated)
        major_updates = sum(1 for p in outdated if p["update_type"] == "MAJOR")
        minor_updates = sum(1 for p in outdated if p["update_type"] == "MINOR")
        patch_updates = sum(1 for p in outdated if p["update_type"] == "PATCH")
        
        return {
            "installed_count": len(installed),
            "outdated_count": len(outdated),
            "up_to_date_count": up_to_date,
            "major_updates": major_updates,
            "minor_updates": minor_updates,
            "patch_updates": patch_updates,
            "declared_count": len(declared),
            "unused_count": len(unused),
            "outdated_packages": outdated,
            "unused_packages": unused,
            "installed_packages": installed
        }
