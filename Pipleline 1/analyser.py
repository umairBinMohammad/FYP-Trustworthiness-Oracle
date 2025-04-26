import ast
import json
from typing import Dict, List

def parse_code_to_ast(filepath: str) -> ast.AST:
    """Parse a Python file into an AST."""
    with open(filepath) as f:
        return ast.parse(f.read())

def extract_all_functions(tree: ast.AST) -> Dict[str, Dict]:
    """Extract all functions in a file with their AST bodies."""
    functions = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions[node.name] = {
                "name": node.name,
                "args": [arg.arg for arg in node.args.args],
                "body": node.body
            }
    return functions

def compare_nodes(old_node: ast.AST, new_node: ast.AST, func_name: str = None) -> List[Dict]:
    """Compare two AST nodes and return differences."""
    changes = []

    # Case 1: Added new If condition
    if isinstance(new_node, ast.If) and not isinstance(old_node, ast.If):
        condition = ast.unparse(new_node.test)
        body = [ast.unparse(n) for n in new_node.body]
        changes.append({
            "type": "condition_added",
            "condition": condition,
            "body": body,
            "function": func_name
        })
    
    # Case 1: Changed 'if' Statements
    elif isinstance(old_node, ast.If) and isinstance(new_node, ast.If):
        old_cond = ast.unparse(old_node.test)
        new_cond = ast.unparse(new_node.test)
        if old_cond != new_cond:
            changes.append({
                "type": "condition_change",
                "target": new_cond.split()[0],  # Variable being checked
                "old": old_cond,
                "new": new_cond
            })
        if old_node.orelse != new_node.orelse:
            changes.append({"type": "else_block_change", "function": func_name})

    # Case 2: Loops (For, While)
    elif isinstance(old_node, ast.For) and isinstance(new_node, ast.For):
        old_target = ast.unparse(old_node.target)
        new_target = ast.unparse(new_node.target)
        old_iter = ast.unparse(old_node.iter)
        new_iter = ast.unparse(new_node.iter)
        if old_target != new_target or old_iter != new_iter:
            changes.append({
                "type": "loop_change",
                "target": f"for {new_target} in {new_iter}",
                "old": f"for {old_target} in {old_iter}",
                "new": f"for {new_target} in {new_iter}"
            })

    # Case 3: Variable Assignments & Renames
    elif isinstance(old_node, ast.Assign) and isinstance(new_node, ast.Assign):
        old_target = ast.unparse(old_node.targets[0])
        new_target = ast.unparse(new_node.targets[0])
        old_value = ast.unparse(old_node.value)
        new_value = ast.unparse(new_node.value)
        
        if old_target != new_target and old_value == new_value:
            changes.append({
                "type": "var_rename",
                "old": old_target,
                "new": new_target
            })
        elif old_target == new_target and old_value != new_value:
            changes.append({
                "type": "var_value_change",
                "target": old_target,
                "old": old_value,
                "new": new_value
            })

    # Case 4: Function/Method Modifications
    elif isinstance(old_node, ast.FunctionDef) and isinstance(new_node, ast.FunctionDef):
        old_params = [arg.arg for arg in old_node.args.args]
        new_params = [arg.arg for arg in new_node.args.args]
        if old_params != new_params:
            changes.append({
                "type": "param_change",
                "function": old_node.name,
                "old": old_params,
                "new": new_params
            })
        
        if ast.unparse(old_node.returns) != ast.unparse(new_node.returns):
            changes.append({
                "type": "return_type_change",
                "function": old_node.name,
                "old": ast.unparse(old_node.returns),
                "new": ast.unparse(new_node.returns)
            })

    # Case 5: Imports (Import, ImportFrom)
    elif isinstance(old_node, ast.Import) and isinstance(new_node, ast.Import):
        old_names = [f"{name.name} as {name.asname}" if name.asname else name.name for name in old_node.names]
        new_names = [f"{name.name} as {name.asname}" if name.asname else name.name for name in new_node.names]
        if old_names != new_names:
            changes.append({
                "type": "import_change",
                "old": old_names,
                "new": new_names
            })

    elif isinstance(old_node, ast.ImportFrom) and isinstance(new_node, ast.ImportFrom):
        old_module = old_node.module
        new_module = new_node.module
        old_names = [f"{name.name} as {name.asname}" if name.asname else name.name for name in old_node.names]
        new_names = [f"{name.name} as {name.asname}" if name.asname else name.name for name in new_node.names]
        if old_module != new_module or old_names != new_names:
            changes.append({
                "type": "import_from_change",
                "module": new_module,
                "old": old_names,
                "new": new_names
            })

    # Case 6: Error Handling (Try, Except, Raise)
    elif isinstance(old_node, ast.Try) and isinstance(new_node, ast.Try):
        old_handlers = [ast.unparse(h.type) for h in old_node.handlers]
        new_handlers = [ast.unparse(h.type) for h in new_node.handlers]
        if old_handlers != new_handlers:
            changes.append({
                "type": "exception_handler_change",
                "old": old_handlers,
                "new": new_handlers
            })

    elif isinstance(old_node, ast.Raise) and isinstance(new_node, ast.Raise):
        old_exc = ast.unparse(old_node.exc) if old_node.exc else None
        new_exc = ast.unparse(new_node.exc) if new_node.exc else None
        if old_exc != new_exc:
            changes.append({
                "type": "raise_change",
                "old": old_exc,
                "new": new_exc
            })

    # Case 7: Structural Changes (Class, Decorators)
    elif isinstance(old_node, ast.ClassDef) and isinstance(new_node, ast.ClassDef):
        old_decorators = [ast.unparse(d) for d in old_node.decorator_list]
        new_decorators = [ast.unparse(d) for d in new_node.decorator_list]
        if old_decorators != new_decorators:
            changes.append({
                "type": "class_decorator_change",
                "class": old_node.name,
                "old": old_decorators,
                "new": new_decorators
            })
        
        old_bases = [ast.unparse(b) for b in old_node.bases]
        new_bases = [ast.unparse(b) for b in new_node.bases]
        if old_bases != new_bases:
            changes.append({
                "type": "class_inheritance_change",
                "class": old_node.name,
                "old": old_bases,
                "new": new_bases
            })

    # Case 8: String/Formatting Changes (f-strings, etc.)
    elif isinstance(old_node, ast.Constant) and isinstance(new_node, ast.Constant):
        if isinstance(old_node.value, str) and isinstance(new_node.value, str):
            if old_node.value != new_node.value:
                changes.append({
                    "type": "string_change",
                    "old": old_node.value,
                    "new": new_node.value
                })

    elif isinstance(old_node, ast.JoinedStr) and isinstance(new_node, ast.JoinedStr):
        old_fstr = ast.unparse(old_node)
        new_fstr = ast.unparse(new_node)
        if old_fstr != new_fstr:
            changes.append({
                "type": "fstring_change",
                "old": old_fstr,
                "new": new_fstr
            })

    # Case 8: Return statements
    elif isinstance(old_node, ast.Return) and isinstance(new_node, ast.Return):
        old_val = ast.unparse(old_node.value) if old_node.value else None
        new_val = ast.unparse(new_node.value) if new_node.value else None
        if old_val != new_val:
            changes.append({
                "type": "return_change",
                "old": old_val,
                "new": new_val,
                "function": func_name
            })
    
    return changes


def compare_functions(old_func: Dict, new_func: Dict) -> List[Dict]:
    """Compare two function ASTs with semantic awareness."""
    changes = []
    old_nodes = old_func["body"]
    new_nodes = new_func["body"]
    
    # Compare nodes that exist in both versions
    for i in range(min(len(old_nodes), len(new_nodes))):
        changes.extend(compare_nodes(old_nodes[i], new_nodes[i], old_func["name"]))
    
    # Handle added nodes in new version
    if len(new_nodes) > len(old_nodes):
        for i in range(len(old_nodes), len(new_nodes)):
            node = new_nodes[i]
            if isinstance(node, ast.If):
                changes.append({
                    "type": "condition_added",
                    "condition": ast.unparse(node.test),
                    "body": [ast.unparse(n) for n in node.body],
                    "function": old_func["name"]
                })
    
    # Track statement reordering
    all_old = [ast.unparse(n) for n in old_nodes]
    all_new = [ast.unparse(n) for n in new_nodes]
    
    for stmt in set(all_old).intersection(set(all_new)):
        old_pos = all_old.index(stmt)
        new_pos = all_new.index(stmt)
        if old_pos != new_pos:
            changes.append({
                "type": "statement_reordered",
                "statement": stmt,
                "old_position": old_pos,
                "new_position": new_pos,
                "function": old_func["name"]
            })
    
    return changes

def analyze_patch(old_file: str, new_file: str) -> Dict:
    """Main function to compare two Python files."""
    old_ast = parse_code_to_ast(old_file)
    new_ast = parse_code_to_ast(new_file)
    
    old_funcs = extract_all_functions(old_ast)
    new_funcs = extract_all_functions(new_ast)
    
    all_changes = {}
    for func_name in old_funcs:
        if func_name in new_funcs:
            changes = compare_functions(old_funcs[func_name], new_funcs[func_name])
            if changes:
                all_changes[func_name] = changes
    
    return all_changes

if __name__ == "__main__":
    changes = analyze_patch("code1.py", "code2.py")
    with open("changes.json", "w") as f:
        json.dump(changes, f, indent=2)
    print("Analysis saved to changes.json.")
