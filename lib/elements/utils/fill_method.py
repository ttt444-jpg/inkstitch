# Authors: see git history
#
# Copyright (c) 2026 Authors
# Licensed under the GNU GPL version 3.0 or later.  See the file LICENSE for details.

from math import pi

from shapely.geometry import Polygon

from ...i18n import _
from ...svg import PIXELS_PER_MM

# Thresholds are in mm / ratios and only decide which fill method is preselected.
# The user can always pick another one.
LINE_MAX_WIDTH_MM = 1.5          # thinner shapes are drawn lines: fills don't work, use Fill to Stroke
LINE_MAX_COMPACTNESS = 0.4       # ... but only if elongated, so small dots still get a fill
ROUND_MIN_COMPACTNESS = 0.9      # 4*pi*area / perimeter^2: circle = 1, square = 0.79
ROUND_MIN_DIAMETER_MM = 5        # tiny dots stitch fine with tatami
RING_MIN_HOLE_RATIO = 0.3        # holes take up at least this share of the outline area
NARROW_MAX_WIDTH_MM = 4          # average width of the shape
NARROW_MAX_RECTANGULARITY = 0.7  # straight bars fill their bounding rectangle and stay tatami


def suggest_fill_method(element):
    """Return (fill_method_id, reason) for the fill method that suits this FillStitch best.

    fill_method_id is None if the shape is a drawn line that shouldn't be filled at all.
    """
    if element.gradient is not None:
        return 'linear_gradient_fill', _("it has a linear gradient")

    if element.get_guide_lines():
        return 'guided_fill', _("it has a guide line")

    shape = element.shape
    if shape.is_empty:
        return 'tatami_fill', _("solid area")

    polygon = max(shape.geoms, key=lambda geom: geom.area)
    average_width_mm = 2 * polygon.area / polygon.length / PIXELS_PER_MM
    if average_width_mm <= LINE_MAX_WIDTH_MM and 4 * pi * polygon.area / polygon.length ** 2 < LINE_MAX_COMPACTNESS:
        return None, _("looks like a drawn line (about %.1f mm wide)") % average_width_mm

    holes_area = sum(Polygon(hole).area for hole in polygon.interiors)
    if len(polygon.interiors) and holes_area / (polygon.area + holes_area) >= RING_MIN_HOLE_RATIO:
        return 'contour_fill', _("it is ring-shaped")

    perimeter = polygon.exterior.length
    if not len(polygon.interiors) and perimeter > 0:
        compactness = 4 * pi * polygon.area / perimeter ** 2
        diameter_mm = 2 * (polygon.area / pi) ** 0.5 / PIXELS_PER_MM
        if compactness >= ROUND_MIN_COMPACTNESS and diameter_mm >= ROUND_MIN_DIAMETER_MM:
            return 'circular_fill', _("it is round")

    rectangularity = polygon.area / max(polygon.minimum_rotated_rectangle.area, 1e-9)
    if average_width_mm <= NARROW_MAX_WIDTH_MM and rectangularity <= NARROW_MAX_RECTANGULARITY:
        return 'contour_fill', _("it is narrow and curved")

    return 'tatami_fill', _("solid area")
