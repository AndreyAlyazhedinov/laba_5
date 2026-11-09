import ast
import math
import operator

BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
UNARY = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "sqrt": math.sqrt,
    "exp": math.exp,
    "log": math.log,
    "abs": abs,
}
CONSTANTS = {"pi": math.pi, "e": math.e}
ALLOWED = (ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name, ast.Call,
           ast.Load) + tuple(BINARY) + tuple(UNARY)


class ExprError(ValueError):
    pass


def parse(text, names=()):
    source = text.replace("^", "**").replace("×", "*").replace("÷", "/")
    source = source.strip()
    if not source:
        raise ExprError("Пустое выражение")
    try:
        tree = ast.parse(source, mode="eval").body
    except SyntaxError:
        raise ExprError("Синтаксическая ошибка") from None
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED):
            raise ExprError("Недопустимая конструкция")
        if isinstance(node, ast.Constant) and (
                isinstance(node.value, bool)
                or not isinstance(node.value, (int, float))):
            raise ExprError("Допустимы только числа")
        if isinstance(node, ast.Name) and node.id not in names \
                and node.id not in CONSTANTS and node.id not in FUNCTIONS:
            raise ExprError(f"Неизвестное имя: {node.id}")
        if isinstance(node, ast.Call) and (
                not isinstance(node.func, ast.Name)
                or node.func.id not in FUNCTIONS
                or len(node.args) != 1 or node.keywords):
            raise ExprError("Недопустимый вызов функции")
    return tree


def _eval(node, env):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in env:
            return env[node.id]
        if node.id in CONSTANTS:
            return CONSTANTS[node.id]
        raise ExprError(f"{node.id} — функция, нужны скобки")
    if isinstance(node, ast.UnaryOp):
        return UNARY[type(node.op)](_eval(node.operand, env))
    if isinstance(node, ast.Call):
        name = node.func.id
        try:
            return FUNCTIONS[name](_eval(node.args[0], env))
        except (ValueError, OverflowError):
            raise ExprError(f"{name}: аргумент вне области определения") \
                from None
    left = _eval(node.left, env)
    right = _eval(node.right, env)
    if isinstance(node.op, ast.Pow) and abs(right) > 1000:
        raise ExprError("Слишком большая степень")
    try:
        result = BINARY[type(node.op)](left, right)
    except ZeroDivisionError:
        raise ExprError("Деление на ноль") from None
    except OverflowError:
        raise ExprError("Слишком большое число") from None
    if isinstance(result, complex):
        raise ExprError("Результат не является действительным числом")
    return result


def evaluate(text, **env):
    return _eval(parse(text, env), env)


def compile_function(text, var="x"):
    tree = parse(text, (var,))
    return lambda value: _eval(tree, {var: value})


def format_number(value):
    if isinstance(value, float) and value.is_integer() and abs(value) < 1e15:
        return str(int(value))
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)
