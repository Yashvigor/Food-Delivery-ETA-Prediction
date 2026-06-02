import os
from PIL import Image, ImageDraw, ImageFont

def generate_visual_assets():
    """Generates modern dark-gradient logo and banner image assets for the Streamlit UI."""
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(os.path.join(assets_dir, "icons"), exist_ok=True)
    
    # 1. Create a Premium Logo (256x256)
    logo_path = os.path.join(assets_dir, "logo.png")
    logo = Image.new("RGBA", (256, 256), (15, 23, 42, 255)) # Dark navy background
    draw = ImageDraw.Draw(logo)
    
    # Draw a stylish glowing hexagon/shield
    draw.regular_polygon((128, 128, 90), 6, rotation=30, fill=(30, 41, 59, 255), outline=(0, 242, 254, 255), width=4)
    # Draw a smaller nested glowing hexagon
    draw.regular_polygon((128, 128, 70), 6, rotation=30, fill=(15, 23, 42, 255), outline=(79, 172, 254, 255), width=2)
    # Draw a stylized lightning bolt / dispatch symbol inside
    coords = [
        (138, 75),  # top-right
        (108, 130), # middle
        (133, 130), # indent
        (118, 185), # bottom-left
        (148, 130), # middle
        (123, 130)  # indent
    ]
    draw.polygon(coords, fill=(0, 242, 254, 255))
    
    logo.save(logo_path)
    print(f"Generated logo asset at: {logo_path}")
    
    # 2. Create a Premium banner (1200x300)
    banner_path = os.path.join(assets_dir, "banner.png")
    banner = Image.new("RGBA", (1200, 300), (11, 15, 25, 255)) # Sleek charcoal
    draw_banner = ImageDraw.Draw(banner)
    
    # Draw horizontal speed stripes
    for i in range(0, 1200, 20):
        # Gradient speed line opacity
        opacity = int(25 * (1 - (i / 1200)))
        draw_banner.line([(i, 0), (i - 100, 300)], fill=(0, 242, 254, opacity), width=2)
        
    # Draw operations HUD shapes
    draw_banner.regular_polygon((1000, 150, 110), 6, fill=(30, 41, 59, 100), outline=(79, 172, 254, 150), width=3)
    draw_banner.regular_polygon((1000, 150, 75), 6, fill=(15, 23, 42, 150), outline=(0, 242, 254, 200), width=2)
    
    banner.save(banner_path)
    print(f"Generated banner asset at: {banner_path}")

if __name__ == "__main__":
    generate_visual_assets()
