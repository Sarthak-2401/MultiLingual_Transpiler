"""
Phase 5: JavaScript Code Generator
Converts IR instructions to modern JavaScript (ES6+).
"""

from typing import List, Dict, Any


class JsGenerator:
    def __init__(self):
        self.indent_level = 0
        self.lines = []
        self.declared_vars = set()

    def indent(self) -> str:
        return "  " * self.indent_level

    def emit(self, line: str):
        self.lines.append(self.indent() + line)

    def generate(self, ir: List[Dict]) -> str:
        for instr in ir:
            self.gen_instr(instr)
        return "\n".join(self.lines)

    def gen_instr(self, instr: Dict):
        op = instr.get("op")

        if op == "assign":
            var = instr["target"]
            val = self.gen_expr(instr["value"])
            if var not in self.declared_vars:
                self.emit(f"let {var} = {val};")
                self.declared_vars.add(var)
            else:
                self.emit(f"{var} = {val};")

        elif op == "print":
            args = ", ".join(self.gen_expr(a) for a in instr.get("args", []))
            self.emit(f"console.log({args});")

        elif op == "func_def":
            params = ", ".join(instr.get("params", []))
            self.emit(f"function {instr['name']}({params}) {{")
            self.indent_level += 1
            saved = set(self.declared_vars)
            for p in instr.get("params", []):
                self.declared_vars.add(p)
            for sub in instr.get("body", []):
                self.gen_instr(sub)
            self.declared_vars = saved
            self.indent_level -= 1
            self.emit("}")
            self.emit("")

        elif op == "return":
            val = self.gen_expr(instr["value"]) if instr.get("value") else ""
            self.emit(f"return {val};")

        elif op == "if":
            self.emit(f"if ({self.gen_expr(instr['condition'])}) {{")
            self.indent_level += 1
            for sub in instr.get("body", []): self.gen_instr(sub)
            self.indent_level -= 1
            self.emit("}")
            for ec in instr.get("elseif", []):
                self.emit(f"else if ({self.gen_expr(ec['condition'])}) {{")
                self.indent_level += 1
                for sub in ec.get("body", []): self.gen_instr(sub)
                self.indent_level -= 1
                self.emit("}")
            if instr.get("else"):
                self.emit("else {")
                self.indent_level += 1
                for sub in instr["else"]: self.gen_instr(sub)
                self.indent_level -= 1
                self.emit("}")

        elif op == "while":
            self.emit(f"while ({self.gen_expr(instr['condition'])}) {{")
            self.indent_level += 1
            for sub in instr.get("body", []): self.gen_instr(sub)
            self.indent_level -= 1
            self.emit("}")

        elif op == "for":
            var = instr["var"]
            iterable = instr["iterable"]
            if iterable.get("kind") == "call" and iterable.get("name") == "range":
                args = iterable.get("args", [])
                if len(args) == 1:
                    end = self.gen_expr(args[0])
                    self.emit(f"for (let {var} = 0; {var} < {end}; {var}++) {{")
                elif len(args) == 2:
                    start, end = self.gen_expr(args[0]), self.gen_expr(args[1])
                    self.emit(f"for (let {var} = {start}; {var} < {end}; {var}++) {{")
                elif len(args) >= 3:
                    start, end, step = self.gen_expr(args[0]), self.gen_expr(args[1]), self.gen_expr(args[2])
                    self.emit(f"for (let {var} = {start}; {var} < {end}; {var} += {step}) {{")
            else:
                self.emit(f"for (const {var} of {self.gen_expr(iterable)}) {{")
            self.indent_level += 1
            self.declared_vars.add(var)
            for sub in instr.get("body", []): self.gen_instr(sub)
            self.indent_level -= 1
            self.emit("}")

        elif op == "expr":
            self.emit(f"{self.gen_expr(instr['expr'])};")
        elif op == "pass":
            self.emit("// pass")
        elif op == "break":
            self.emit("break;")
        elif op == "continue":
            self.emit("continue;")

    def gen_expr(self, expr: Any) -> str:
        if expr is None: return "null"
        if not isinstance(expr, dict): return str(expr)
        kind = expr.get("kind")

        if kind == "literal":
            v, vt = expr["value"], expr["vtype"]
            if vt == "string": return f'"{v}"'
            if vt == "bool": return "true" if v else "false"
            if v is None: return "null"
            return str(v)

        if kind == "var": return expr["name"]

        if kind == "binop":
            op = expr["op"]
            op = {"and": "&&", "or": "||"}.get(op, op)
            return f"({self.gen_expr(expr['left'])} {op} {self.gen_expr(expr['right'])})"

        if kind == "unop":
            op = {"not": "!"}.get(expr["op"], expr["op"])
            return f"({op}{self.gen_expr(expr['operand'])})"

        if kind == "call":
            name, args_str = expr["name"], ", ".join(self.gen_expr(a) for a in expr.get("args", []))
            if name == "range":
                args = expr.get("args", [])
                if len(args) == 1:
                    return f"Array.from({{length: {self.gen_expr(args[0])}}}, (_, i) => i)"
                elif len(args) == 2:
                    start, end = self.gen_expr(args[0]), self.gen_expr(args[1])
                    return f"Array.from({{length: {end} - {start}}}, (_, i) => i + {start})"
            if name == "len": return f"{args_str}.length"
            if name == "str": return f"String({args_str})"
            if name == "int": return f"parseInt({args_str})"
            if name == "float": return f"parseFloat({args_str})"
            if name == "list": return f"[{args_str}]"
            return f"{name}({args_str})"

        if kind == "method_call":
            obj, method = expr["object"], expr["method"]
            args = ", ".join(self.gen_expr(a) for a in expr.get("args", []))
            return f"{obj}.{method}({args})"

        if kind == "member":
            return f"{expr['object']}.{expr['member']}"

        if kind == "list":
            elements = ", ".join(self.gen_expr(e) for e in expr.get("elements", []))
            return f"[{elements}]"

        return "/* unknown */"


def generate_js(ir: List[Dict]) -> str:
    return JsGenerator().generate(ir)
