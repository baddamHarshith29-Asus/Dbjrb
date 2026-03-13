#!/usr/bin/env python3
"""Simple CLI calculator with REPL and single-expression mode.

Usage examples:
  python cli_calculator.py "2 + 2 * (3 - 1)"
  python cli_calculator.py          # starts interactive REPL

Commands in REPL:
  :exit, :quit           Exit the REPL
  :clear                 Clear the screen
  :help                  Show brief help

This uses evaluator.evaluate(expression) for safe evaluation.
"""

import argparse
import os
import sys

try:
    import readline  # optional, improves REPL experience
except Exception:
    readline = None

from evaluator import evaluate

def format_result(value):
    try:
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
    except Exception:
        pass
    return str(value)

def repl():
    histfile = os.path.join(os.path.expanduser('~'), '.dbjrb_calc_history')
    if readline and hasattr(readline, 'read_history_file'):
        try:
            readline.read_history_file(histfile)
        except Exception:
            pass

    print("Python CLI Calculator — type :help for commands")
    while True:
        try:
            line = input('calc> ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nExiting.')
            break

        if not line:
            continue

        if line in (':exit', ':quit', 'exit', 'quit'):
            print('Goodbye.')
            break
        if line == ':clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            continue
        if line == ':help':
            print('Commands: :exit, :quit, :clear, :help')
            print('Enter arithmetic expressions using + - * / % ** and functions like sin(), cos(), sqrt(), log(), factorial()')
            continue

        try:
            result = evaluate(line)
            print(format_result(result))
        except Exception as e:
            print('Error:', e)

    if readline and hasattr(readline, 'write_history_file'):
        try:
            readline.write_history_file(histfile)
        except Exception:
            pass

def main():
    parser = argparse.ArgumentParser(description='Python CLI calculator')
    parser.add_argument('expression', nargs='?', help='Expression to evaluate (if omitted, starts REPL)')
    args = parser.parse_args()

    if args.expression:
        try:
            result = evaluate(args.expression)
            print(format_result(result))
        except Exception as e:
            print('Error:', e)
            sys.exit(1)
    else:
        repl()


if __name__ == '__main__':
    main()
