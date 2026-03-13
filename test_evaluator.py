# Test cases for the evaluator

# Sample expressions to evaluate
expressions = [
    "2 + 2",
    "2 * (3 + 4)",
    "sin(pi / 2)",
    "log10(100)",
    "factorial(5)",
]

# Evaluate and print results
for expr in expressions:
    try:
        result = evaluate(expr)
        print(f'Evaluating: {expr} = {result}')
    except ValueError as e:
        print(f'Error evaluating {expr}: {e}")
