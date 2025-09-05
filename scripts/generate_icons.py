#!/usr/bin/env python3
"""
Idempotent icon generation script.
Generates consistent icons for the demo repository.
"""

import shutil
import sys
from pathlib import Path
from PIL import Image, ImageDraw


def clean_assets(assets_dir: Path) -> None:
    """Clean generated assets before re-generating for idempotency."""
    icons_dir = assets_dir / "icons"
    if icons_dir.exists():
        print(f"Cleaning existing icons in {icons_dir}")
        shutil.rmtree(icons_dir)
    icons_dir.mkdir(parents=True, exist_ok=True)


def generate_icon(size: int, output_path: Path) -> None:
    """Generate a simple demo icon of the specified size."""
    # Create a simple colorful demo icon
    img = Image.new("RGB", (size, size), color="#4CAF50")
    draw = ImageDraw.Draw(img)

    # Draw a simple pattern
    margin = size // 8
    draw.rectangle(
        [margin, margin, size - margin, size - margin],
        fill="#2196F3",
        outline="#FFFFFF",
        width=2,
    )

    # Add a center circle
    center = size // 2
    radius = size // 4
    draw.ellipse(
        [center - radius, center - radius, center + radius, center + radius],
        fill="#FFFFFF",
    )

    img.save(output_path, "PNG")
    print(f"Generated icon: {output_path}")


def main():
    """Main function to generate all required icons."""
    try:
        # Determine the repository root
        repo_root = Path(__file__).parent.parent
        assets_dir = repo_root / "assets"

        print("Starting idempotent icon generation...")

        # Clean existing assets
        clean_assets(assets_dir)

        # Generate icons in common sizes
        icons_dir = assets_dir / "icons"
        sizes = [16, 32, 64, 128, 256]

        for size in sizes:
            icon_path = icons_dir / f"icon-{size}x{size}.png"
            generate_icon(size, icon_path)

        print(f"Successfully generated {len(sizes)} icons")

        # Verify all expected files exist
        for size in sizes:
            icon_path = icons_dir / f"icon-{size}x{size}.png"
            if not icon_path.exists():
                raise FileNotFoundError(f"Expected icon not found: {icon_path}")

        print("Icon generation completed successfully!")
        return 0

    except Exception as e:
        print(f"Error during icon generation: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
