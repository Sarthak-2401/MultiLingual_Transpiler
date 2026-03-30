from fastapi import APIRouter, HTTPException
from models.request_models import TranspileRequest
from transpiler_core.tokenizer import tokenize, TokenizeError
from transpiler_core.parser import parse, ParseError
from transpiler_core.semantic_analyzer import analyze
from transpiler_core.ir import ast_to_ir
from transpiler_core.codegen.cpp_generator import generate_cpp
from transpiler_core.codegen.js_generator import generate_js

router = APIRouter()

@router.post("/transpile")
def transpile(req: TranspileRequest):
    # Phase 1: Lexical Analysis
    try:
        tokens = tokenize(req.source_code)
    except TokenizeError as e:
        raise HTTPException(400, detail=f"Tokenize error at line {e.line}: {str(e)}")

    # Phase 2: Syntax Analysis
    try:
        ast = parse(tokens)
    except ParseError as e:
        raise HTTPException(400, detail=f"Parse error: {str(e)}")

    # Phase 3: Semantic Analysis
    semantic_result = analyze(ast)

    # Phase 4: Intermediate Representation
    ir = ast_to_ir(ast)

    # Phase 5: Code Generation
    if req.target_lang == "cpp":
        output_code = generate_cpp(ir)
    elif req.target_lang == "javascript":
        output_code = generate_js(ir)
    else:
        raise HTTPException(400, detail=f"Unsupported target language: {req.target_lang}")

    return {
        "tokens": [t.to_dict() for t in tokens],
        "ast": ast,
        "semantic_errors": semantic_result["errors"],
        "symbol_table": semantic_result["symbol_table"],
        "functions": semantic_result["functions"],
        "ir": ir,
        "output_code": output_code,
    }
