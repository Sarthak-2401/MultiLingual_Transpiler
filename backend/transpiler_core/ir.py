"""
Phase 4: Intermediate Representation (IR)
Converts AST into a flat, language-independent IR.

IR instructions are simple operation dicts:
  { "op": "assign", "target": "x", "value": ... }
  { "op": "call", "name": "print", "args": [...] }
  { "op": "if", "condition": ..., "body": [...], ... }
  etc.
"""

from typing import Dict, List, Any


def ast_to_ir(ast: Dict) -> List[Dict]:
    """Convert a Program AST node to a list of IR instructions."""
    return lower_stmts(ast.get("body", []))


def lower_stmts(stmts: List[Dict]) -> List[Dict]:
    result = []
    for s in stmts:
        result.extend(lower_stmt(s))
    return result


def lower_stmt(node: Dict) -> List[Dict]:
    kind = node.get("type")

    if kind == "Assignment":
        return [{"op": "assign", "target": node["left"], "value": lower_expr(node["right"])}]

    if kind == "FunctionDef":
        return [{
            "op": "func_def",
            "name": node["name"],
            "params": [p["name"] for p in node.get("params", [])],
            "param_types": [p.get("type") for p in node.get("params", [])],
            "return_type": node.get("return_type"),
            "body": lower_stmts(node.get("body", []))
        }]

    if kind == "Return":
        return [{"op": "return", "value": lower_expr(node["value"]) if node.get("value") else None}]

    if kind == "Print":
        return [{"op": "print", "args": [lower_expr(a) for a in node.get("args", [])]}]

    if kind == "If":
        ir = {
            "op": "if",
            "condition": lower_expr(node["condition"]),
            "body": lower_stmts(node.get("body", [])),
            "elseif": [
                {"condition": lower_expr(c["condition"]), "body": lower_stmts(c["body"])}
                for c in node.get("elseif", [])
            ],
            "else": lower_stmts(node["else"]) if node.get("else") else None
        }
        return [ir]

    if kind == "While":
        return [{"op": "while", "condition": lower_expr(node["condition"]), "body": lower_stmts(node.get("body", []))}]

    if kind == "For":
        return [{"op": "for", "var": node["var"], "iterable": lower_expr(node["iterable"]), "body": lower_stmts(node.get("body", []))}]

    if kind == "ExprStatement":
        return [{"op": "expr", "expr": lower_expr(node["expr"])}]

    if kind == "Pass":
        return [{"op": "pass"}]

    if kind == "Break":
        return [{"op": "break"}]

    if kind == "Continue":
        return [{"op": "continue"}]

    return [{"op": "unknown", "raw": node}]


def lower_expr(node: Any) -> Any:
    if node is None:
        return None
    if not isinstance(node, dict):
        return node

    kind = node.get("type")

    if kind == "Number":
        return {"kind": "literal", "vtype": "int", "value": node["value"]}
    if kind == "Float":
        return {"kind": "literal", "vtype": "float", "value": node["value"]}
    if kind == "String":
        return {"kind": "literal", "vtype": "string", "value": node["value"]}
    if kind == "Boolean":
        return {"kind": "literal", "vtype": "bool", "value": node["value"]}
    if kind == "None":
        return {"kind": "literal", "vtype": "null", "value": None}
    if kind == "Identifier":
        return {"kind": "var", "name": node["name"]}
    if kind == "BinaryOp":
        return {"kind": "binop", "op": node["op"], "left": lower_expr(node["left"]), "right": lower_expr(node["right"])}
    if kind == "UnaryOp":
        return {"kind": "unop", "op": node["op"], "operand": lower_expr(node["operand"])}
    if kind == "FunctionCall":
        return {"kind": "call", "name": node["name"], "args": [lower_expr(a) for a in node.get("args", [])]}
    if kind == "MethodCall":
        return {"kind": "method_call", "object": node["object"], "method": node["method"], "args": [lower_expr(a) for a in node.get("args", [])]}
    if kind == "MemberAccess":
        return {"kind": "member", "object": node["object"], "member": node["member"]}
    if kind == "List":
        return {"kind": "list", "elements": [lower_expr(e) for e in node.get("elements", [])]}

    return {"kind": "unknown", "raw": node}
