#!/usr/bin/env python3
"""
Utility script to convert PNG logo to ICO format for Windows builds.
Requires Pillow to be installed.
"""

import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install pillow")
    sys.exit(1)


def convert_png_to_ico(png_path, ico_path, sizes=None):
    """
    Convert PNG image to ICO format with multiple sizes.
    
    Args:
        png_path: Path to source PNG file
        ico_path: Path to output ICO file
        sizes: List of sizes for the ICO file (default: [16, 32, 48, 64, 128, 256])
    """
    if sizes is None:
        sizes = [16, 32, 48, 64, 128, 256]
    
    try:
        # Open the PNG image
        img = Image.open(png_path)
        
        # Create list of resized images
        images = []
        for size in sizes:
            resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
            images.append(resized_img)
        
        # Save as ICO
        images[0].save(
            ico_path,
            format='ICO',
            sizes=[(size, size) for size in sizes],
            append_images=images[1:]
        )
        
        print(f"✅ Successfully converted {png_path} to {ico_path}")
        print(f"   Sizes: {sizes}")
        
    except Exception as e:
        print(f"❌ Error converting image: {e}")
        sys.exit(1)


def main():
    """Main function to convert logo.png to logo.ico"""
    png_path = Path("assets/images/logo.png")
    ico_path = Path("assets/images/logo.ico")
    
    if not png_path.exists():
        print(f"❌ Source file not found: {png_path}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    ico_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Converting {png_path} to {ico_path}...")
    convert_png_to_ico(png_path, ico_path)


if __name__ == "__main__":
    main()
