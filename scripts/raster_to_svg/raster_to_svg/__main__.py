import os
import subprocess
import pathlib
import argparse

# Adjust these two constants depending on your OS:
# • On Windows (ImageMagick 7+), use "magick" rather than "convert" 
# • On Linux/macOS, use "convert"
IMAGEMAGICK_CMD = "magick"     # ← Windows: typically "magick"
# IMAGEMAGICK_CMD = "convert"  # ← Linux/macOS: if `convert` is on your PATH

POTRACE_CMD = "potrace"        # Potrace must be in your PATH

# Paths
root_path = pathlib.Path(__file__).parent
RASTERIZED_PATH = root_path / "rasterized"
LAYERS_PATH     = root_path / "layers"

# Make sure the layers folder exists
LAYERS_PATH.mkdir(parents=True, exist_ok=True)

def png_to_svg(png_path: pathlib.Path, svg_path: pathlib.Path, invert: bool = False):
    """
    1. Extracts the alpha channel from `png_path` into a PGM file.
    2. Optionally inverts (negates) the alpha channel.
    3. Runs Potrace on that PGM to create an SVG at `svg_path`.
    4. Deletes the intermediate PGM.
    """
    pgm_path = png_path.with_suffix(".pgm")

    # Build ImageMagick command
    cmd = [
        IMAGEMAGICK_CMD,
        str(png_path),
        "-alpha", "extract"
    ]
    if invert:
        cmd.append("-negate")
    cmd.append(str(pgm_path))

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ImageMagick failed to produce PGM from {png_path}") from e

    try:
        subprocess.run(
            [
                POTRACE_CMD,
                str(pgm_path),
                "-s",
                "-o", str(svg_path)
            ],
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Potrace failed to trace {pgm_path} into {svg_path}") from e

    pgm_path.unlink()

def batch_convert(input_dir, output_dir, invert=False):
    input_dir = pathlib.Path(input_dir)
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for file in input_dir.glob("*.png"):
        svg_path = output_dir / f"{file.stem}.svg"
        print(f"→ {file.name} → {svg_path.name}")
        png_to_svg(file, svg_path, invert=invert)
    print("All done!")

def main():
    parser = argparse.ArgumentParser(description="Batch convert PNGs to SVGs using alpha channel (optionally inverted)")
    parser.add_argument('--invert', action='store_true', help='Invert (negate) the alpha channel before tracing')
    parser.add_argument('--in', dest='input_dir', default=os.getcwd(), help='Input folder (default: current directory)')
    parser.add_argument('--out', dest='output_dir', default=os.getcwd(), help='Output folder (default: current directory)')
    args = parser.parse_args()
    batch_convert(args.input_dir, args.output_dir, invert=args.invert)

if __name__ == "__main__":
    main()
