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
