from PIL import Image, ImageStat
from ai_layout import should_use_light_logo
import json, os


def _find_assets_base():
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "assets")

ASSETS_BASE = _find_assets_base()

OUTPUT_SIZES = {
    "1080x1080": (1080, 1080),
    "1080x1350": (1080, 1350),
    "1080x1920": (1080, 1920),
}

# maps what the UI sends to the actual folder name on disk
DEALER_FOLDER_MAP = {
    "VW-Dehradun":   "VW-Dehradun",
    "VW-Haladawani": "VW-Haldawani",
}

FORMAT_TO_TEMPLATE = {
    "1080x1080": "template.png",
    "1080x1350": "template1.png",
    "1080x1920": "template1.png",
}


def _dealer_dir(brand, dealer):
    sub = "VW-dealers" if brand.lower() == "volkswagen" else "Tata-dealers"
    folder = DEALER_FOLDER_MAP.get(dealer, dealer)
    return os.path.join(ASSETS_BASE, "Dealership-panels", sub, folder)


def _resize_and_crop(img, target_w, target_h):
    img_w, img_h = img.size
    scale = max(target_w / img_w, target_h / img_h)
    new_w = int(img_w * scale)
    new_h = int(img_h * scale)
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def generate_creative(image_path, brand="Volkswagen", dealers_json="[]"):
    # parse the dealers list from json string
    try:
        dealers = json.loads(dealers_json)
    except Exception:
        dealers = []

    if not dealers:
        raise ValueError("No dealers selected")

    # always 1080x1080 for now
    target_w, target_h = 1080, 1080

    backend_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(backend_dir, "static")
    os.makedirs(static_dir, exist_ok=True)

    results = []

    background = Image.open(image_path).convert("RGBA")
    background = _resize_and_crop(background, target_w, target_h)
    print(f"\nBackground loaded: {target_w}x{target_h}")

    for dealer in dealers:
        print(f"\nProcessing: {dealer}")
        dealer_dir = _dealer_dir(brand, dealer)

        if not os.path.isdir(dealer_dir):
            print(f"  folder not found, skipping")
            continue



        creative = background.copy()

        # paste the panel template at the bottom
        template_path = os.path.join(dealer_dir, "template.png")
        if os.path.exists(template_path):
            panel = Image.open(template_path).convert("RGBA")
            # only scale width to match canvas, keep natural height ratio
            if panel.width != target_w:
                ratio = target_w / panel.width
                panel = panel.resize((target_w, int(panel.height * ratio)), Image.Resampling.LANCZOS)
            # place at bottom so it doesn't cover the car/subject
            y_pos = target_h - panel.height
            creative.paste(panel, (0, y_pos), panel)
            print(f"  panel added at bottom")
        else:
            print(f"  template not found: {template_path}")


        # pick logo based on background brightness
        use_light = should_use_light_logo(image_path)
        logo_filename = "logo-light.png" if use_light else "logo-dark.png"
     
        logo_path = os.path.join(dealer_dir, logo_filename)

        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")

            # fit logo inside a bounding box: wide enough for rectangular logos,
            # height is the constant reference so all logos appear the same visual weight
            max_logo_h = int(target_h * 0.10)   # 10% height — the size anchor
            max_logo_w = int(target_w * 0.25)   # 25% width — lets wide logos breathe
            orig_w, orig_h = logo.size
            scale = min(max_logo_w / orig_w, max_logo_h / orig_h)
            logo_w = int(orig_w * scale)
            logo_h = int(orig_h * scale)
            logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)

            margin = 20
            x = target_w - logo_w - margin
            y = margin
            creative.paste(logo, (x, y), logo)
            print(f"  logo added ({logo_filename})")
     
        else:
            print(f"  logo not found: {logo_path}")

        safe_dealer = dealer.replace(" ", "_").replace("/", "_")
        output_path = os.path.join(static_dir, f"output_{safe_dealer}.png")
        creative.convert("RGB").save(output_path, "PNG")
        print(f"  saved: {output_path}")

        results.append((dealer, output_path))

    print(f"\nDone: {len(results)}/{len(dealers)} processed")
    
    return results