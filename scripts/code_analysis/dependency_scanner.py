"""
Module Dependency Scanner and Analyzer

Scans Python source files to build module dependency graphs
and detect circular dependencies.
"""

import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class ModuleDependencyScanner:
    """Scans source code to build module import graph."""
    
    def __init__(self, source_root: Path):
        self.source_root = source_root
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.module_files: Dict[str, Path] = {}
        
    def scan(self) -> Dict[str, Set[str]]:
        """Scan all Python files and build dependency graph."""
        print(f"Scanning modules in: {self.source_root}")
        
        # Find all Python files
        for py_file in self.source_root.rglob("*.py"):
            if "__pycache__" in str(py_file) or "test" in str(py_file):
                continue
                
            module_name = self._get_module_name(py_file)
            self.module_files[module_name] = py_file
            
            # Extract imports
            imports = self._extract_imports(py_file)
            self.dependencies[module_name] = imports
        
        # Filter to only internal dependencies
        self._filter_internal_dependencies()
        
        return dict(self.dependencies)
    
    def _get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name."""
        rel_path = file_path.relative_to(self.source_root)
        
        # Remove .py extension
        parts = list(rel_path.parts[:-1]) + [rel_path.stem]
        
        # Skip __init__ and use parent dir name
        if parts[-1] == "__init__":
            parts = parts[:-1]
        
        # Get domain subdirectory for categorization
        if "domain" in parts:
            domain_idx = parts.index("domain")
            if domain_idx + 1 < len(parts):
                return parts[domain_idx + 1].capitalize()
        
        # Fallback to first significant part
        return parts[0].capitalize() if parts else "Unknown"
    
    def _extract_imports(self, file_path: Path) -> Set[str]:
        """Parse file and extract import statements."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(file_path))
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return set()
        
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Extract module name
                    module = alias.name.split(".")[0]
                    imports.add(module)
                    
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # Get root module
                    parts = node.module.split(".")
                    
                    # Check if it's a pravaha module
                    if "pravaha" in parts:
                        pravaha_idx = parts.index("pravaha")
                        if pravaha_idx + 2 < len(parts):
                            # Extract domain module (e.g., pravaha.domain.auth -> Auth)
                            if parts[pravaha_idx + 1] == "domain":
                                module = parts[pravaha_idx + 2].capitalize()
                                imports.add(module)
        
        return imports
    
    def _filter_internal_dependencies(self):
        """Keep only dependencies to modules we know about."""
        known_modules = set(self.module_files.keys())
        
        for module in self.dependencies:
            self.dependencies[module] = {
                dep for dep in self.dependencies[module]
                if dep in known_modules and dep != module
            }
    
    def find_circular_dependencies(self) -> List[Tuple[str, str]]:
        """Find circular dependencies in the graph."""
        circular = []
        
        for module_a in self.dependencies:
            for module_b in self.dependencies[module_a]:
                if module_a in self.dependencies.get(module_b, set()):
                    # Found circular dependency
                    pair = tuple(sorted([module_a, module_b]))
                    if pair not in circular:
                        circular.append(pair)
        
        return circular
    
    def get_most_imported(self, top_n: int = 5) -> List[Tuple[str, int]]:
        """Get modules that are imported the most."""
        import_counts = defaultdict(int)
        
        for module, deps in self.dependencies.items():
            for dep in deps:
                import_counts[dep] += 1
        
        sorted_modules = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_modules[:top_n]
    
    def get_most_dependent(self, top_n: int = 5) -> List[Tuple[str, int]]:
        """Get modules that import the most other modules."""
        sorted_modules = sorted(
            [(mod, len(deps)) for mod, deps in self.dependencies.items()],
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_modules[:top_n]
    
    def get_isolated_modules(self) -> List[str]:
        """Find modules with no dependencies and not depended upon."""
        all_modules = set(self.dependencies.keys())
        depended_upon = set()
        
        for deps in self.dependencies.values():
            depended_upon.update(deps)
        
        isolated = []
        for module in all_modules:
            has_no_deps = len(self.dependencies[module]) == 0
            not_depended_on = module not in depended_upon
            
            if has_no_deps and not_depended_on:
                isolated.append(module)
        
        return isolated
