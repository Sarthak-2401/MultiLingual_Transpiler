"""
Phase 3: Semantic Analysis
Validates program correctness and annotates the AST.

Checks:
  - Variable used before declaration
  - Function called with wrong number of arguments
  - Return outside function
  - Basic scope tracking
"""

from typing import Dict, List, Any

class SemanticError:
    def __init__(self, message: str, node: Dict = None):
        self.message = message
        self.node = node

    def to_dict(self):
        return {"error": self.message}


class Scope:
    def __init__(self, parent=None):
        self.vars = set()
        self.parent = parent

    def declare(self, name: str):
        self.vars.add(name)

    def lookup(self, name: str) -> bool:
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.lookup(name)
        return False


class SemanticAnalyzer:
    def __init__(self):
        self.errors: List[SemanticError] = []
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self.function_defs: Dict[str, int] = {}  # name -> param count
        self.in_function = False

        # Built-ins always available
        for builtin in ("print", "range", "len", "int", "float", "str", "bool", "list", "input", "abs", "max", "min"):
            self.global_scope.declare(builtin)

    def error(self, msg: str, node=None):
        self.errors.append(SemanticError(msg, node))

    def enter_scope(self):
        self.current_scope = Scope(parent=self.current_scope)

    def exit_scope(self):
        self.current_scope = self.current_scope.parent

    def analyze(self, ast: Dict) -> Dict:
        self.visit(ast)
        return {
            "errors": [e.to_dict() for e in self.errors],
            "symbol_table": list(self.global_scope.vars),
            "functions": self.function_defs,
        }

    def visit(self, node: Any):
        if node is None or not isinstance(node, dict):
            return
        kind = node.get("type")
        handler = getattr(self, f"visit_{kind}", self.visit_generic)
        handler(node)

    def visit_generic(self, node: Dict):
        for val in node.values():
            if isinstance(val, dict):
                self.visit(val)
            elif isinstance(val, list):
                for item in val:
                    self.visit(item)

    def visit_Program(self, node: Dict):
        for stmt in node.get("body", []):
            self.visit(stmt)

    def visit_Assignment(self, node: Dict):
        self.visit(node.get("right"))
        self.current_scope.declare(node["left"])

    def visit_FunctionDef(self, node: Dict):
        name = node["name"]
        params = node.get("params", [])
        self.global_scope.declare(name)
        self.function_defs[name] = len(params)
        self.enter_scope()
        prev_in_fn = self.in_function
        self.in_function = True
        for p in params:
            self.current_scope.declare(p["name"])
        for stmt in node.get("body", []):
            self.visit(stmt)
        self.in_function = prev_in_fn
        self.exit_scope()

    def visit_Return(self, node: Dict):
        if not self.in_function:
            self.error("'return' outside function")
        self.visit(node.get("value"))

    def visit_If(self, node: Dict):
        self.visit(node.get("condition"))
        self.enter_scope()
        for stmt in node.get("body", []):
            self.visit(stmt)
        self.exit_scope()
        for elif_clause in node.get("elseif", []):
            self.visit(elif_clause.get("condition"))
            self.enter_scope()
            for stmt in elif_clause.get("body", []):
                self.visit(stmt)
            self.exit_scope()
        if node.get("else"):
            self.enter_scope()
            for stmt in node["else"]:
                self.visit(stmt)
            self.exit_scope()

    def visit_While(self, node: Dict):
        self.visit(node.get("condition"))
        self.enter_scope()
        for stmt in node.get("body", []):
            self.visit(stmt)
        self.exit_scope()

    def visit_For(self, node: Dict):
        self.visit(node.get("iterable"))
        self.enter_scope()
        self.current_scope.declare(node["var"])
        for stmt in node.get("body", []):
            self.visit(stmt)
        self.exit_scope()

    def visit_Identifier(self, node: Dict):
        name = node["name"]
        if not self.current_scope.lookup(name):
            self.error(f"Variable '{name}' used before declaration")

    def visit_FunctionCall(self, node: Dict):
        name = node["name"]
        if not self.current_scope.lookup(name):
            self.error(f"Function '{name}' called but not defined")
        else:
            if name in self.function_defs:
                expected = self.function_defs[name]
                actual = len(node.get("args", []))
                if expected != actual:
                    self.error(f"Function '{name}' expects {expected} args, got {actual}")
        for arg in node.get("args", []):
            self.visit(arg)

    def visit_Print(self, node: Dict):
        for arg in node.get("args", []):
            self.visit(arg)

    def visit_BinaryOp(self, node: Dict):
        self.visit(node.get("left"))
        self.visit(node.get("right"))

    def visit_UnaryOp(self, node: Dict):
        self.visit(node.get("operand"))

    def visit_ExprStatement(self, node: Dict):
        self.visit(node.get("expr"))

    def visit_Number(self, node: Dict): pass
    def visit_Float(self, node: Dict): pass
    def visit_String(self, node: Dict): pass
    def visit_Boolean(self, node: Dict): pass
    def visit_None(self, node: Dict): pass
    def visit_Pass(self, node: Dict): pass
    def visit_Break(self, node: Dict): pass
    def visit_Continue(self, node: Dict): pass
    def visit_List(self, node: Dict):
        for el in node.get("elements", []):
            self.visit(el)
    def visit_MethodCall(self, node: Dict):
        for arg in node.get("args", []):
            self.visit(arg)
    def visit_MemberAccess(self, node: Dict): pass


def analyze(ast: Dict) -> Dict:
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(ast)
