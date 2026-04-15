"""
Converts an SVG file to a 256x256 PNG.

Usage: python scripts/svg_to_png.py <input.svg> [output.png]

If output is omitted, writes to the same path with a .png extension.
Requires: pip install cairosvg
"""

import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python svg_to_png.py <input.svg> [output.png]", file=sys.stderr)
        sys.exit(1)

    input_path = os.path.abspath(sys.argv[1])
    if len(sys.argv) >= 3:
        output_path = os.path.abspath(sys.argv[2])
    else:
        # Replace .svg extension with .png
        root, _ = os.path.splitext(input_path)
        output_path = root + ".png"

    if not os.path.isfile(input_path):
        print(f"File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    import cairosvg

    cairosvg.svg2png(
        url=input_path,
        write_to=output_path,
        output_width=256,
        output_height=256,
    )
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
