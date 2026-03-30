"""
Phase 5: C++ Code Generator
Converts IR instructions to C++ source code.
"""

from typing import List, Dict, Any, Optional


class CppGenerator:
    def __init__(self):
        self.indent_level = 0
        self.lines = []
        self.declared_vars = set()

    def indent(self) -> str:
        return "    " * self.indent_level

    def emit(self, line: str):
        self.lines.append(self.indent() + line)

    def generate(self, ir: List[Dict]) -> str:
        headers = [
            "#include <iostream>",
            "#include <string>",
            "#include <vector>",
            "",
            "using namespace std;",
            ""
        ]
        func_defs = [i for i in ir if i.get("op") == "func_def"]
        top_level = [i for i in ir if i.get("op") != "func_def"]

        for instr in func_defs:
            self.gen_instr(instr)
            self.emit("")

        if top_level:
            self.emit("int main() {")
            self.indent_level += 1
            for instr in top_level:
                self.gen_instr(instr)
            self.emit("return 0;")
            self.indent_level -= 1
            self.emit("}")

        return "\n".join(headers + self.lines)

    def gen_instr(self, instr: Dict):
        op = instr.get("op")

        if op == "assign":
            var = instr["target"]
            val = self.gen_expr(instr["value"])
            vtype = self.infer_type(instr["value"])
            if var not in self.declared_vars:
                self.emit(f"{vtype} {var} = {val};")
                self.declared_vars.add(var)
            else:
                self.emit(f"{var} = {val};")

        elif op == "print":
            parts = " << \" \" << ".join(self.gen_expr(a) for a in instr.get("args", []))
            self.emit(f"cout << {parts} << endl;")

        elif op == "func_def":
            ret = self.cpp_type(instr.get("return_type")) if instr.get("return_type") else "void"
            params = []
            param_types = instr.get("param_types", [])
            for i, p in enumerate(instr.get("params", [])):
                pt = self.cpp_type(param_types[i]) if i < len(param_types) else "auto"
                params.append(f"{pt} {p}")
            self.emit(f"{ret} {instr['name']}({', '.join(params)}) {{")
            self.indent_level += 1
            saved = set(self.declared_vars)
            for p in instr.get("params", []):
                self.declared_vars.add(p)
            for sub in instr.get("body", []):
                self.gen_instr(sub)
            self.declared_vars = saved
            self.indent_level -= 1
            self.emit("}")

        elif op == "return":
            val = self.gen_expr(instr["value"]) if instr.get("value") else ""
            self.emit(f"return {val};")

        elif op == "if":
            self.emit(f"if ({self.gen_expr(instr['condition'])}) {{")
            self.indent_level += 1
            for sub in instr.get("body", []):
                self.gen_instr(sub)
            self.indent_level -= 1
            self.emit("}")
            for ec in instr.get("elseif", []):
                self.emit(f"else if ({self.gen_expr(ec['condition'])}) {{")
                self.indent_level += 1
                for sub in ec.get("body", []):
                    self.gen_instr(sub)
                self.indent_level -= 1
                self.emit("}")
            if instr.get("else"):
                self.emit("else {")
                self.indent_level += 1
                for sub in instr["else"]:
                    self.gen_instr(sub)
                self.indent_level -= 1
                self.emit("}")

        elif op == "while":
            self.emit(f"while ({self.gen_expr(instr['condition'])}) {{")
            self.indent_level += 1
            for sub in instr.get("body", []):
                self.gen_instr(sub)
            self.indent_level -= 1
            self.emit("}")

        elif op == "for":
            var = instr["var"]
            iterable = instr["iterable"]
            if iterable.get("kind") == "call" and iterable.get("name") == "range":
                args = iterable.get("args", [])
                if len(args) == 1:
                    end = self.gen_expr(args[0])
                    self.emit(f"for (int {var} = 0; {var} < {end}; {var}++) {{")
                elif len(args) == 2:
                    start, end = self.gen_expr(args[0]), self.gen_expr(args[1])
                    self.emit(f"for (int {var} = {start}; {var} < {end}; {var}++) {{")
                elif len(args) >= 3:
                    start, end, step = self.gen_expr(args[0]), self.gen_expr(args[1]), self.gen_expr(args[2])
                    self.emit(f"for (int {var} = {start}; {var} < {end}; {var} += {step}) {{")
            else:
                self.emit(f"for (auto {var} : {self.gen_expr(iterable)}) {{")
            self.indent_level += 1
            self.declared_vars.add(var)
            for sub in instr.get("body", []):
                self.gen_instr(sub)
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
        if expr is None:
            return "nullptr"
        if not isinstance(expr, dict):
            return str(expr)
        kind = expr.get("kind")

        if kind == "literal":
            v, vt = expr["value"], expr["vtype"]
            if vt == "string": return f'"{v}"'
            if vt == "bool": return "true" if v else "false"
            if v is None: return "nullptr"
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
            name, args = expr["name"], ", ".join(self.gen_expr(a) for a in expr.get("args", []))
            mapping = {"len": f"{args}.size()", "str": f"to_string({args})", "int": f"stoi({args})", "float": f"stof({args})"}
            return mapping.get(name, f"{name}({args})")

        if kind == "method_call":
            obj, method = expr["object"], expr["method"]
            args = ", ".join(self.gen_expr(a) for a in expr.get("args", []))
            if method == "append": return f"{obj}.push_back({args})"
            return f"{obj}.{method}({args})"

        if kind == "member":
            return f"{expr['object']}.{expr['member']}"

        if kind == "list":
            elements = ", ".join(self.gen_expr(e) for e in expr.get("elements", []))
            return f"{{{elements}}}"

        return "/* unknown */"

    def infer_type(self, expr: Any) -> str:
        if not isinstance(expr, dict): return "auto"
        vtype = expr.get("vtype") if expr.get("kind") == "literal" else None
        return {"int": "int", "float": "double", "string": "string", "bool": "bool"}.get(vtype, "auto")

    def cpp_type(self, t: Optional[str]) -> str:
        return {"int": "int", "float": "double", "str": "string", "bool": "bool", "None": "void"}.get(t, "auto")


def generate_cpp(ir: List[Dict]) -> str:
    return CppGenerator().generate(ir)
