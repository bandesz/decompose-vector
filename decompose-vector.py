#!/usr/bin/env python3
"""
Decompose SVG or DXF paths into individual <line> and <path> segments.
- Input can be SVG (via svgpathtools) or DXF (via ezdxf).
- Output is always an SVG.
- Each segment becomes its own element (good for Cricut Design Space or Silhouette Studio).
- Duplicate straight lines are removed.
- Tiny "ghost" lines (from closepath) are skipped.
"""

import sys
from math import hypot, radians, cos, sin
from svgpathtools import svg2paths, Line, Arc, CubicBezier, QuadraticBezier
from xml.etree.ElementTree import Element, SubElement, ElementTree

import ezdxf
from ezdxf.bbox import extents

def normalize_point(pt, precision=6):
    """Round a point to avoid floating point noise."""
    return (round(pt.real, precision), round(pt.imag, precision))

def line_key(p1, p2):
    """Return a normalized key for a line segment (order-independent)."""
    return tuple(sorted([p1, p2]))

def line_length(x1, y1, x2, y2):
    """Compute Euclidean length of a line segment."""
    return hypot(x1 - x2, y1 - y2)

def decompose_svg(input_file, output_file):
    paths, attributes = svg2paths(input_file)

    # Root SVG element
    svg_out = Element('svg', xmlns="http://www.w3.org/2000/svg")

    seen_lines = set()

    for path_idx, path in enumerate(paths):
        for seg_idx, seg in enumerate(path):

            if isinstance(seg, Line):
                x1, y1, x2, y2 = seg.start.real, seg.start.imag, seg.end.real, seg.end.imag
                if line_length(x1, y1, x2, y2) < 1:
                    continue

                key = line_key(normalize_point(seg.start), normalize_point(seg.end))
                if key in seen_lines:
                    print(f"Duplicate line skipped: {key}")
                    continue
                seen_lines.add(key)

                SubElement(svg_out, 'line', {
                    'x1': str(x1), 'y1': str(y1),
                    'x2': str(x2), 'y2': str(y2),
                    'stroke': 'black', 'fill': 'none',
                    'id': f"path{path_idx}_seg{seg_idx}"
                })

            elif isinstance(seg, Arc):
                SubElement(svg_out, 'path', {
                    'd': f"M {seg.start.real},{seg.start.imag} "
                         f"A {seg.radius.real},{seg.radius.imag} {seg.rotation} "
                         f"{1 if seg.large_arc else 0},{1 if seg.sweep else 0} "
                         f"{seg.end.real},{seg.end.imag}",
                    'stroke': 'black', 'fill': 'none',
                    'id': f"path{path_idx}_seg{seg_idx}"
                })

            elif isinstance(seg, CubicBezier):
                SubElement(svg_out, 'path', {
                    'd': f"M {seg.start.real},{seg.start.imag} "
                         f"C {seg.control1.real},{seg.control1.imag} "
                         f"{seg.control2.real},{seg.control2.imag} "
                         f"{seg.end.real},{seg.end.imag}",
                    'stroke': 'black', 'fill': 'none',
                    'id': f"path{path_idx}_seg{seg_idx}"
                })

            elif isinstance(seg, QuadraticBezier):
                SubElement(svg_out, 'path', {
                    'd': f"M {seg.start.real},{seg.start.imag} "
                         f"Q {seg.control.real},{seg.control.imag} "
                         f"{seg.end.real},{seg.end.imag}",
                    'stroke': 'black', 'fill': 'none',
                    'id': f"path{path_idx}_seg{seg_idx}"
                })

    return svg_out

def decompose_dxf(input_file, output_file):
    doc = ezdxf.readfile(input_file)
    msp = doc.modelspace()

    # Get modelspace extents to set viewBox
    svg_attributes = {'xmlns': "http://www.w3.org/2000/svg"}
    try:
        min_coord, max_coord = extents(msp)
        min_x, min_y = min_coord.x, min_coord.y
        width = max_coord.x - min_x
        height = max_coord.y - min_y

        # From DXF specification for $INSUNITS
        UNITS = {
            0: "", 1: "in", 2: "ft", 3: "mi", 4: "mm", 5: "cm", 6: "m",
            7: "km", 8: "µin", 9: "mils", 10: "yd", 11: "Å", 12: "nm",
            13: "µm", 14: "dm", 15: "dam", 16: "hm", 17: "Gm",
            18: "au", 19: "ly", 20: "pc"
        }
        unit_code = doc.header.get('$INSUNITS', 0)
        unit_str = UNITS.get(unit_code, "")

        svg_attributes['viewBox'] = f"{min_x} {min_y} {width} {height}"
        svg_attributes['width'] = f"{width}{unit_str}"
        svg_attributes['height'] = f"{height}{unit_str}"

    except (ezdxf.DXFError, ValueError): # No entities in modelspace
        pass

    svg_out = Element('svg', **svg_attributes)
    seen_lines = set()
    seg_idx = 0

    for e in msp:
        if e.dxftype() == "LINE":
            x1, y1, _ = e.dxf.start
            x2, y2, _ = e.dxf.end
            if line_length(x1, y1, x2, y2) < 1:
                continue

            key = line_key((round(x1, 6), round(y1, 6)),
                           (round(x2, 6), round(y2, 6)))
            if key in seen_lines:
                print(f"Duplicate line skipped: {key}")
                continue
            seen_lines.add(key)

            SubElement(svg_out, 'line', {
                'x1': str(x1), 'y1': str(y1),
                'x2': str(x2), 'y2': str(y2),
                'stroke': 'black', 'fill': 'none',
                'id': f"dxf_seg{seg_idx}"
            })
            seg_idx += 1

        elif e.dxftype() == "ARC":
            cx, cy, _ = e.dxf.center
            r = e.dxf.radius
            start_angle = radians(e.dxf.start_angle)
            end_angle = radians(e.dxf.end_angle)
            x1, y1 = cx + r * cos(start_angle), cy + r * sin(start_angle)
            x2, y2 = cx + r * cos(end_angle), cy + r * sin(end_angle)

            large_arc = 1 if (e.dxf.end_angle - e.dxf.start_angle) % 360 > 180 else 0
            sweep = 1  # DXF arcs are CCW

            SubElement(svg_out, 'path', {
                'd': f"M {x1},{y1} A {r},{r} 0 {large_arc},{sweep} {x2},{y2}",
                'stroke': 'black', 'fill': 'none',
                'id': f"dxf_seg{seg_idx}"
            })
            seg_idx += 1

        elif e.dxftype() == 'LWPOLYLINE':
            # Explode polyline into individual segments (lines/arcs)
            for segment in e.virtual_entities():
                if segment.dxftype() == 'LINE':
                    x1, y1, _ = segment.dxf.start
                    x2, y2, _ = segment.dxf.end
                    if line_length(x1, y1, x2, y2) < 1:
                        continue

                    key = line_key((round(x1, 6), round(y1, 6)),
                                   (round(x2, 6), round(y2, 6)))
                    if key in seen_lines:
                        print(f"Duplicate line skipped: {key}")
                        continue
                    seen_lines.add(key)

                    SubElement(svg_out, 'line', {
                        'x1': str(x1), 'y1': str(y1),
                        'x2': str(x2), 'y2': str(y2),
                        'stroke': 'black', 'fill': 'none',
                        'id': f"dxf_seg{seg_idx}"
                    })
                    seg_idx += 1
                elif segment.dxftype() == 'ARC':
                    cx, cy, _ = segment.dxf.center
                    r = segment.dxf.radius
                    start_angle = radians(segment.dxf.start_angle)
                    end_angle = radians(segment.dxf.end_angle)
                    x1, y1 = cx + r * cos(start_angle), cy + r * sin(start_angle)
                    x2, y2 = cx + r * cos(end_angle), cy + r * sin(end_angle)

                    large_arc = 1 if (segment.dxf.end_angle - segment.dxf.start_angle) % 360 > 180 else 0
                    sweep = 1  # DXF arcs are CCW

                    SubElement(svg_out, 'path', {
                        'd': f"M {x1},{y1} A {r},{r} 0 {large_arc},{sweep} {x2},{y2}",
                        'stroke': 'black', 'fill': 'none',
                        'id': f"dxf_seg{seg_idx}"
                    })
                    seg_idx += 1

    return svg_out

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python decompose.py input.svg|input.dxf output.svg")
        sys.exit(1)

    input_file, output_file = sys.argv[1], sys.argv[2]
    if input_file.lower().endswith(".svg"):
        svg_out = decompose_svg(input_file, output_file)
    elif input_file.lower().endswith(".dxf"):
        svg_out = decompose_dxf(input_file, output_file)
    else:
        print("Unsupported input format. Must be .svg or .dxf")
        sys.exit(1)

    # Prettify XML output
    from xml.dom import minidom
    from xml.etree import ElementTree as ET

    rough_string = ET.tostring(svg_out, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_string = reparsed.toprettyxml(indent="  ")

    with open(output_file, "w") as f:
        f.write(pretty_string)

    print(f"Decomposed file written to {output_file}")
