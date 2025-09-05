#!/usr/bin/env python
"""
SVG to PNG Converter

This script converts SVG files to PNG files at various sizes.
"""

import os
import argparse
import logging
from typing import List

try:
    from cairosvg import svg2png
except ImportError:
    print("CairoSVG not found. Please install with: pip install cairosvg")
    exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger("SVGToPNG")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="SVG to PNG Converter"
    )
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Input directory containing SVG files"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for PNG files"
    )
    parser.add_argument(
        "--sizes",
        default="16,24,32,48,64,128",
        help="Comma-separated list of sizes to generate"
    )
    return parser.parse_args()


def convert_svg_to_png(
    svg_path: str,
    output_dir: str,
    sizes: List[int]
) -> List[str]:
    """
    Convert SVG file to PNG files at various sizes.
    
    Args:
        svg_path: Path to the SVG file
        output_dir: Output directory
        sizes: List of sizes to generate
        
    Returns:
        List of paths to generated PNG files
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get base filename without extension
    base_name = os.path.splitext(os.path.basename(svg_path))[0]
    
    # Read SVG file
    with open(svg_path, 'rb') as f:
        svg_data = f.read()
    
    # Generate PNG files at various sizes
    output_paths = []
    for size in sizes:
        output_path = os.path.join(output_dir, f"{base_name}_{size}.png")
        
        try:
            svg2png(
                bytestring=svg_data,
                write_to=output_path,
                output_width=size,
                output_height=size
            )
            
            output_paths.append(output_path)
            logger.info(f"Generated {size}x{size} PNG: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to convert {svg_path} to {size}x{size} PNG: {e}")
    
    return output_paths


def main():
    """Main execution function."""
    args = parse_args()
    
    # Parse sizes
    try:
        sizes = [int(s.strip()) for s in args.sizes.split(",")]
    except ValueError:
        logger.error("Invalid sizes specified. Using default sizes.")
        sizes = [16, 24, 32, 48, 64, 128]
    
    # Ensure input directory exists
    if not os.path.isdir(args.input_dir):
        logger.error(f"Input directory does not exist: {args.input_dir}")
        exit(1)
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Find all SVG files
    svg_files = [
        os.path.join(args.input_dir, f)
        for f in os.listdir(args.input_dir)
        if f.lower().endswith(".svg")
    ]
    
    logger.info(f"Found {len(svg_files)} SVG files in {args.input_dir}")
    
    # Convert each SVG file to PNG
    total_converted = 0
    for svg_file in svg_files:
        output_paths = convert_svg_to_png(svg_file, args.output_dir, sizes)
        total_converted += len(output_paths)
    
    logger.info(
        f"Conversion complete. Generated {total_converted} PNG files in {args.output_dir}"
    )


if __name__ == "__main__":
    main()
