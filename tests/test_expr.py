import math
import unittest

from lab5.expr import ExprError, compile_function, evaluate, format_number


class TestEvaluate(unittest.TestCase):
    def test_arithmetic_and_priority(self):
        self.assertEqual(evaluate("2+3*4"), 14)
        self.assertEqual(evaluate("(2+3)*4"), 20)
        self.assertEqual(evaluate("-3+10/4"), -0.5)
        self.assertEqual(evaluate("2^10"), 1024)
        self.assertEqual(evaluate("17 % 5"), 2)

    def test_functions_and_constants(self):
        self.assertAlmostEqual(evaluate("sin(pi/2)"), 1)
        self.assertAlmostEqual(evaluate("sqrt(16) + log(e)"), 5)
        self.assertEqual(evaluate("abs(-7)"), 7)

    def test_variables(self):
        self.assertEqual(evaluate("x^2 + 1", x=3), 10)

    def test_errors(self):
        cases = {
            "1/0": "Деление на ноль",
            "": "Пустое выражение",
            "2+*3": "Синтаксическая ошибка",
            "y + 1": "Неизвестное имя: y",
            "sqrt(-4)": "sqrt: аргумент вне области определения",
            "(-8)^0.5": "Результат не является действительным числом",
            "2^5000": "Слишком большая степень",
        }
        for text, message in cases.items():
            with self.subTest(text=text):
                with self.assertRaises(ExprError) as ctx:
                    evaluate(text)
                self.assertEqual(str(ctx.exception), message)

    def test_rejects_code(self):
        for text in ("__import__('os')", "(1).real", "[1, 2]", "'a' * 3",
                     "True + 1", "sin(1, 2)", "x.y"):
            with self.subTest(text=text):
                with self.assertRaises(ExprError):
                    evaluate(text)

    def test_compile_function(self):
        func = compile_function("sin(x) / x")
        self.assertAlmostEqual(func(math.pi), 0)
        with self.assertRaises(ExprError):
            func(0)

    def test_format_number(self):
        self.assertEqual(format_number(4.0), "4")
        self.assertEqual(format_number(0.1 + 0.2), "0.3")
        self.assertEqual(format_number(2 ** 70), "1180591620717411303424")
        self.assertEqual(format_number(1 / 3), "0.333333333333")


if __name__ == "__main__":
    unittest.main()
