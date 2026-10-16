from inkex import Circle, LinearGradient, PathElement, Rectangle, Stop
from inkex.tester import TestCase
from inkex.tester.svg import svg

from lib.elements import FillStitch
from lib.elements.utils.fill_method import suggest_fill_method
from lib.svg import PIXELS_PER_MM

MM = PIXELS_PER_MM


def mm(value):
    return str(value * MM)


class FillMethodSuggestionTest(TestCase):
    def suggest(self, node):
        root = svg()
        root.add(node)
        return suggest_fill_method(FillStitch(node))[0]

    def test_rectangle_is_tatami(self) -> None:
        rect = Rectangle(attrib={"width": mm(30), "height": mm(20), "style": "fill:red"})
        self.assertEqual(self.suggest(rect), 'tatami_fill')

    def test_straight_narrow_bar_is_tatami(self) -> None:
        rect = Rectangle(attrib={"width": mm(50), "height": mm(3), "style": "fill:red"})
        self.assertEqual(self.suggest(rect), 'tatami_fill')

    def test_circle_is_circular(self) -> None:
        circle = Circle(attrib={"cx": mm(20), "cy": mm(20), "r": mm(15), "style": "fill:red"})
        self.assertEqual(self.suggest(circle), 'circular_fill')

    def test_tiny_dot_is_tatami(self) -> None:
        circle = Circle(attrib={"cx": mm(20), "cy": mm(20), "r": mm(1.5), "style": "fill:red"})
        self.assertEqual(self.suggest(circle), 'tatami_fill')

    def test_ring_is_contour(self) -> None:
        # 40mm square frame with a 30mm square hole
        d = (f"M 0,0 H {mm(40)} V {mm(40)} H 0 Z "
             f"M {mm(5)},{mm(5)} V {mm(35)} H {mm(35)} V {mm(5)} Z")
        ring = PathElement(attrib={"d": d, "style": "fill:red;fill-rule:evenodd"})
        self.assertEqual(self.suggest(ring), 'contour_fill')

    def test_narrow_curved_band_is_contour(self) -> None:
        # half of a 3mm wide ring, like a crescent / swoosh
        r_out, r_in = mm(20), mm(17)
        d = (f"M {mm(-20)},0 A {r_out},{r_out} 0 0 1 {mm(20)},0 "
             f"L {mm(17)},0 A {r_in},{r_in} 0 0 0 {mm(-17)},0 Z")
        band = PathElement(attrib={"d": d, "style": "fill:red"})
        self.assertEqual(self.suggest(band), 'contour_fill')

    def test_gradient_is_linear_gradient(self) -> None:
        root = svg()
        gradient = root.defs.add(LinearGradient(attrib={"id": "g"}))
        gradient.add(Stop(attrib={"offset": "0", "style": "stop-color:#ff0000"}))
        gradient.add(Stop(attrib={"offset": "1", "style": "stop-color:#0000ff"}))
        rect = root.add(Rectangle(attrib={"width": mm(30), "height": mm(20), "style": "fill:url(#g)"}))
        self.assertEqual(suggest_fill_method(FillStitch(rect))[0], 'linear_gradient_fill')

    def test_thin_line_is_not_filled(self) -> None:
        # 40mm long, 0.8mm wide wavy pen stroke
        d = (f"M 0,0 C {mm(10)},{mm(-5)} {mm(20)},{mm(5)} {mm(40)},0 "
             f"L {mm(40)},{mm(0.8)} C {mm(20)},{mm(5.8)} {mm(10)},{mm(-4.2)} 0,{mm(0.8)} Z")
        line = PathElement(attrib={"d": d, "style": "fill:red"})
        self.assertIsNone(self.suggest(line))

    def test_thin_ring_is_not_filled(self) -> None:
        # glasses frame: 10mm ring drawn with a 0.8mm pen
        d = (f"M 0,0 H {mm(10)} V {mm(10)} H 0 Z "
             f"M {mm(0.8)},{mm(0.8)} V {mm(9.2)} H {mm(9.2)} V {mm(0.8)} Z")
        ring = PathElement(attrib={"d": d, "style": "fill:red;fill-rule:evenodd"})
        self.assertIsNone(self.suggest(ring))

    def test_small_dot_is_still_filled(self) -> None:
        # an eye: 2mm dot is narrow but not a line
        dot = Circle(attrib={"cx": mm(5), "cy": mm(5), "r": mm(1), "style": "fill:red"})
        self.assertEqual(self.suggest(dot), 'tatami_fill')

    def test_hand_drawn_letter_is_not_filled(self) -> None:
        # a 4mm letter "A" drawn with a 0.8mm pen: outline with a small triangular counter
        d = (f"M 0,{mm(4)} L {mm(1.5)},0 H {mm(2.3)} L {mm(3.8)},{mm(4)} H {mm(3)} L {mm(2.6)},{mm(3)} "
             f"H {mm(1.2)} L {mm(0.8)},{mm(4)} Z "
             f"M {mm(1.5)},{mm(2.3)} H {mm(2.3)} L {mm(1.9)},{mm(1.1)} Z")
        letter = PathElement(attrib={"d": d, "style": "fill:red;fill-rule:evenodd"})
        self.assertIsNone(self.suggest(letter))
