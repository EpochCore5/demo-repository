#!/usr/bin/env python
"""
Icon Generation Script

This script generates SVG icons for agents, modules, and other components
in the EpochCore ecosystem.
"""

import os
import argparse
import logging
import math
import random
from typing import Dict, Any, List, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger("IconGenerator")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Icon Generation"
    )
    parser.add_argument(
        "--output-dir",
        default="assets/glyphs",
        help="Output directory for generated icons"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of icons to generate"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible generation"
    )
    return parser.parse_args()


def generate_color_palette() -> List[str]:
    """
    Generate a color palette for icons.
    
    Returns:
        List of hex color codes
    """
    # EpochCore brand colors
    brand_colors = [
        "#1A56DB",  # Primary blue
        "#7E3AF2",  # Purple
        "#047481",  # Teal
        "#0E9F6E",  # Green
        "#F05252",  # Red
        "#FF5A1F",  # Orange
        "#C27803",  # Amber
        "#1C64F2",  # Light blue
        "#7E3AF2",  # Violet
        "#0694A2",  # Cyan
    ]
    
    # Return the brand colors and some random variations
    return brand_colors


def generate_svg_shape(
    shape_type: str,
    size: int = 64,
    colors: List[str] = None
) -> str:
    """
    Generate a SVG shape.
    
    Args:
        shape_type: Type of shape to generate
        size: Size of the shape in pixels
        colors: List of colors to use
        
    Returns:
        SVG content as a string
    """
    if colors is None:
        colors = generate_color_palette()
    
    color1 = random.choice(colors)
    color2 = random.choice([c for c in colors if c != color1])
    
    svg = f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
    svg += 'xmlns="http://www.w3.org/2000/svg">\n'
    
    # Background
    svg += f'  <rect width="{size}" height="{size}" fill="#F9FAFB" />\n'
    
    if shape_type == "circles":
        # Generate overlapping circles
        for i in range(3):
            cx = random.randint(size // 4, 3 * size // 4)
            cy = random.randint(size // 4, 3 * size // 4)
            r = random.randint(size // 6, size // 3)
            opacity = random.uniform(0.6, 0.9)
            color = color1 if i % 2 == 0 else color2
            
            svg += f'  <circle cx="{cx}" cy="{cy}" r="{r}" '
            svg += f'fill="{color}" opacity="{opacity:.1f}" />\n'
    
    elif shape_type == "hexagon":
        # Generate a hexagon with inner details
        points = []
        center_x, center_y = size // 2, size // 2
        radius = size // 2 - 4
        
        for i in range(6):
            angle = 2 * math.pi * i / 6
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append(f"{x},{y}")
        
        svg += f'  <polygon points="{" ".join(points)}" '
        svg += f'fill="{color1}" opacity="0.8" />\n'
        
        # Inner hexagon
        inner_points = []
        inner_radius = radius * 0.6
        
        for i in range(6):
            angle = 2 * math.pi * i / 6
            x = center_x + inner_radius * math.cos(angle)
            y = center_y + inner_radius * math.sin(angle)
            inner_points.append(f"{x},{y}")
        
        svg += f'  <polygon points="{" ".join(inner_points)}" '
        svg += f'fill="{color2}" opacity="0.6" />\n'
    
    elif shape_type == "grid":
        # Generate a grid pattern
        cell_size = size // 8
        
        for x in range(0, size, cell_size):
            for y in range(0, size, cell_size):
                if random.random() > 0.5:
                    color = color1 if random.random() > 0.5 else color2
                    opacity = random.uniform(0.5, 1.0)
                    
                    svg += f'  <rect x="{x}" y="{y}" '
                    svg += f'width="{cell_size}" height="{cell_size}" '
                    svg += f'fill="{color}" opacity="{opacity:.1f}" />\n'
    
    elif shape_type == "waves":
        # Generate wave patterns
        for i in range(3):
            amplitude = random.randint(size // 10, size // 5)
            frequency = random.uniform(0.02, 0.05)
            phase = random.uniform(0, 2 * math.pi)
            
            points = []
            for x in range(0, size + 1, 4):
                y = (size // 2) + amplitude * math.sin(frequency * x + phase)
                points.append(f"{x},{y}")
            
            # Close the path
            points.append(f"{size},{size}")
            points.append(f"0,{size}")
            
            color = color1 if i % 2 == 0 else color2
            opacity = random.uniform(0.5, 0.8)
            
            svg += f'  <polygon points="{" ".join(points)}" '
            svg += f'fill="{color}" opacity="{opacity:.1f}" />\n'
    
    else:  # Default to abstract
        # Generate abstract shapes
        for i in range(5):
            shape_choice = random.choice(["rect", "circle", "ellipse"])
            
            if shape_choice == "rect":
                x = random.randint(0, size // 2)
                y = random.randint(0, size // 2)
                width = random.randint(size // 4, size // 2)
                height = random.randint(size // 4, size // 2)
                
                svg += f'  <rect x="{x}" y="{y}" '
                svg += f'width="{width}" height="{height}" '
                svg += f'rx="8" ry="8" '
            
            elif shape_choice == "circle":
                cx = random.randint(size // 4, 3 * size // 4)
                cy = random.randint(size // 4, 3 * size // 4)
                r = random.randint(size // 8, size // 4)
                
                svg += f'  <circle cx="{cx}" cy="{cy}" r="{r}" '
            
            else:  # ellipse
                cx = random.randint(size // 4, 3 * size // 4)
                cy = random.randint(size // 4, 3 * size // 4)
                rx = random.randint(size // 8, size // 3)
                ry = random.randint(size // 8, size // 3)
                
                svg += f'  <ellipse cx="{cx}" cy="{cy}" '
                svg += f'rx="{rx}" ry="{ry}" '
            
            color = color1 if i % 2 == 0 else color2
            opacity = random.uniform(0.5, 0.9)
            
            svg += f'fill="{color}" opacity="{opacity:.1f}" />\n'
    
    # Add a subtle grid overlay
    svg += f'  <path d="'
    
    # Horizontal lines
    for y in range(0, size + 1, size // 8):
        svg += f'M0,{y} L{size},{y} '
    
    # Vertical lines
    for x in range(0, size + 1, size // 8):
        svg += f'M{x},0 L{x},{size} '
    
    svg += f'" stroke="#000" stroke-width="0.5" opacity="0.05" />\n'
    
    svg += '</svg>'
    
    return svg


def generate_agent_icon(
    agent_id: str,
    output_dir: str,
    colors: List[str] = None,
    size: int = 128
) -> str:
    """
    Generate an icon for an agent.
    
    Args:
        agent_id: ID of the agent
        output_dir: Output directory
        colors: List of colors to use
        size: Size of the icon
        
    Returns:
        Path to the generated icon
    """
    if colors is None:
        colors = generate_color_palette()
    
    # Determine shape type based on agent ID
    if "oscillation" in agent_id:
        shape_type = "waves"
    elif "audit" in agent_id:
        shape_type = "grid"
    elif "registry" in agent_id:
        shape_type = "hexagon"
    elif "optimizer" in agent_id:
        shape_type = "circles"
    else:
        shape_type = "abstract"
    
    # Generate SVG content
    svg_content = generate_svg_shape(shape_type, size, colors)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save SVG file
    output_path = os.path.join(output_dir, f"{agent_id}.svg")
    with open(output_path, 'w') as f:
        f.write(svg_content)
    
    logger.info(f"Generated icon for agent {agent_id}: {output_path}")
    
    return output_path


def main():
    """Main execution function."""
    args = parse_args()
    
    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    logger.info(f"Generating {args.count} icons in {args.output_dir}")
    
    # Generate color palette
    colors = generate_color_palette()
    
    # First generate icons for known agents
    known_agents = [
        "oscillation_conflict_agent",
        "audit_evolution_manager",
        "failure_remediation_agent",
        "kpi_prediction_agent",
        "portfolio_optimizer"
    ]
    
    for agent_id in known_agents:
        generate_agent_icon(agent_id, args.output_dir, colors)
    
    # Generate additional random icons if requested
    if args.count > len(known_agents):
        shape_types = ["circles", "hexagon", "grid", "waves", "abstract"]
        
        for i in range(args.count - len(known_agents)):
            random_id = f"random_agent_{i+1}"
            shape_type = random.choice(shape_types)
            
            svg_content = generate_svg_shape(shape_type, 128, colors)
            
            output_path = os.path.join(args.output_dir, f"{random_id}.svg")
            with open(output_path, 'w') as f:
                f.write(svg_content)
            
            logger.info(f"Generated random icon: {output_path}")
    
    logger.info(f"Icon generation complete. {args.count} icons generated.")


if __name__ == "__main__":
    main()
