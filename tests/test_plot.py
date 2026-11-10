import math
import tkinter as tk
import unittest

from lab5.expr import ExprError, compile_function
from lab5.plot import PlotFrame, parse_bound, sample


class TestSample(unittest.TestCase):
    def test_points_cover_segment(self):
        xs, ys = sample(lambda x: 2 * x, -1, 1, count=5)
        self.assertEqual(xs, [-1, -0.5, 0, 0.5, 1])
        self.assertEqual(ys, [-2, -1, 0, 1, 2])

    def test_undefined_points_become_nan(self):
        xs, ys = sample(compile_function("sqrt(x)"), -2, 2, count=5)
        self.assertTrue(all(math.isnan(y) for y in ys[:2]))
        self.assertEqual(ys[2:], [0, 1, math.sqrt(2)])

    def test_errors(self):
        with self.assertRaises(ExprError):
            sample(lambda x: x, 5, 1)
        with self.assertRaises(ExprError):
            sample(compile_function("log(x)"), -5, -1)
        with self.assertRaises(ExprError):
            parse_bound("десять")
        self.assertEqual(parse_bound("-2,5"), -2.5)


class TestPlotFrame(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.plot = PlotFrame(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_draw_replaces_or_adds_curves(self):
        self.assertTrue(self.plot.draw())
        self.plot.keep.set(True)
        self.plot.formula.set("x^2 - 4")
        self.assertTrue(self.plot.draw())
        self.assertEqual(len(self.plot.curves), 2)
        self.plot.keep.set(False)
        self.assertTrue(self.plot.draw())
        self.assertEqual(len(self.plot.curves), 1)
        self.assertEqual(self.plot.curves[0].get_label(), "f(x) = x^2 - 4")

    def test_bad_formula_shows_message(self):
        self.plot.formula.set("y + 1")
        self.assertFalse(self.plot.draw())
        self.assertEqual(self.plot.message.cget("text"),
                         "Неизвестное имя: y")
        self.assertEqual(self.plot.curves, [])

    def test_clear(self):
        self.plot.draw()
        self.plot.clear()
        self.assertEqual(self.plot.curves, [])


if __name__ == "__main__":
    unittest.main()
