"""#!/usr/bin/env python3
"""
Safe, AST-based expression evaluator for the CLI calculator.

This evaluator intentionally allows a small, well-defined subset of Python expressions:
- numeric constants (ints and floats)
- binary operators: +, -, *, /, %, **
- unary operators: +, -
- function calls for a whitelist of math functions (sin, cos, tan, sqrt, log, log10, pow, abs, factorial, floor, ceil)
- names for math constants: pi, e

It rejects all other syntax (attribute access, subscripts, comprehensions, imports, etc.) to avoid arbitrary code execution.
"""

import ast
import operator as _op
import math

# Mapping AST operator nodes to Python operator functions
_BINARY_OPS = {
    ast.Add: _op.add,
    ast.Sub: _op.sub,
    ast.Mult: _op.mul,
    ast.Div: _op.truediv,
    ast.Mod: _op.mod,
    ast.Pow: _op.pow,
}

_UNARY_OPS = {
    ast.UAdd: _op.pos,
    ast.USub: _op.neg,
}

_ALLOWED_FUNCS = {
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'sqrt': math.sqrt,
    'log': math.log,      # natural log
    'log10': math.log10,
    'pow': math.pow,
    'abs': abs,
    'factorial': math.factorial,
    'floor': math.floor,
    'ceil': math.ceil,
}

_ALLOWED_NAMES = {
    'pi': math.pi,
    'e': math.e,
}

def _ensure_number(value):
    if isinstance(value, (int, float)):
        return value
    raise ValueError(f'Non-numeric result: {value!r}')

def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)

    if isinstance(node, ast.Constant):  # Python 3.8+
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f'Unsupported constant: {node.value!r}')

    if isinstance(node, ast.Num):  # older ast compatibility
        return node.n

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _BINARY_OPS:
            raise ValueError(f'Operator {op_type.__name__} not allowed')
        left = _eval(node.left)
        right = _eval(node.right)
        left = _ensure_number(left)
        right = _ensure_number(right)
        func = _BINARY_OPS[op_type]
        return func(left, right)

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _UNARY_OPS:
            raise ValueError(f'Unary operator {op_type.__name__} not allowed')
        operand = _eval(node.operand)
        operand = _ensure_number(operand)
        return _UNARY_OPS[op_type](operand)

    if isinstance(node, ast.Call):
        # Only allow calls to simple names (no attribute access)
        if not isinstance(node.func, ast.Name):
            raise ValueError('Only direct function calls are allowed')
        func_name = node.func.id
        if func_name not in _ALLOWED_FUNCS:
            raise ValueError(f'Function {func_name!r} is not allowed')
        func = _ALLOWED_FUNCS[func_name]
        if node.keywords:
            raise ValueError('Keywords in function calls are not allowed')
        args = [_eval(a) for a in node.args]
        # Special validation for factorial: must be integer >= 0
        if func_name == 'factorial':
            if len(args) != 1:
                raise ValueError('factorial() takes exactly one argument')
            arg = args[0]
            if not (isinstance(arg, int) or (isinstance(arg, float) and arg.is_integer())):
                raise ValueError('factorial() argument must be an integer')
            i = int(arg)
            if i < 0:
                raise ValueError('factorial() argument must be >= 0')
            return func(i)
        # Evaluate and return
        evaluated_args = [_ensure_number(a) for a in args]
        return func(*evaluated_args)

    if isinstance(node, ast.Name):
        if node.id in _ALLOWED_NAMES:
            return _ALLOWED_NAMES[node.id]
        raise ValueError(f'Name {node.id!r} is not allowed')

    # Safe-guard: reject any other node types
    raise ValueError(f'Unsupported expression: {type(node).__name__}')

def evaluate(expression):
    """Evaluate the given arithmetic expression and return a number.

    Raises ValueError for unsupported syntax or names. Propagates ZeroDivisionError
    and other numeric errors from Python operators.
    """
    if not isinstance(expression, str):
        raise TypeError('Expression must be a string')
    try:
        parsed = ast.parse(expression, mode='eval')
    except SyntaxError as e:
        raise ValueError(f'Syntax error in expression: {e}')
    return _eval(parsed)