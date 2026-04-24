from PIL import Image, ImageStat
import os



def should_use_light_logo(image_path):
    # check brightness only in the top-right corner where the logo will be placed
    try:
        img = Image.open(image_path).convert('RGB')
        w, h = img.size

        # sample top-right 25% × 25% — exactly where the logo lands
        region = img.crop((w * 3 // 4, 0, w, h // 4))
        gray = region.convert('L')
        stat = ImageStat.Stat(gray)
        avg_brightness = stat.mean[0]

        print(f"Image brightness: {avg_brightness:.1f}/255")

        if avg_brightness < 128:
            print("dark background - using light logo")
            return True
        else:
            print("light background - using dark logo")
            return False

    except Exception as e:
        print(f"brightness detection failed: {e}")
        return True  # fallback to light logo


def detect_subject_and_place_panel(image_path):
    try:
        img = Image.open(image_path)
        width, height = img.size

        gray = img.convert('L')

        top_region    = gray.crop((0, 0, width, height // 3))
        bottom_region = gray.crop((0, height * 2 // 3, width, height))

        def get_brightness(region):
            stat = ImageStat.Stat(region)
            return stat.mean[0]

        top_bright = get_brightness(top_region)
        bottom_bright = get_brightness(bottom_region)

        top_var = ImageStat.Stat(top_region).stddev[0]
        bottom_var = ImageStat.Stat(bottom_region).stddev[0]

        print(f"top - brightness={top_bright:.1f}, var={top_var:.1f}")
        print(f"bottom - brightness={bottom_bright:.1f}, var={bottom_var:.1f}")

        # put panel where the image is cleaner (less variance)
        if bottom_var < top_var:
            print("placing panel at bottom")
            return "bottom"
        else:
            print("placing panel at top")
            return "top"

    except Exception as e:
        print(f"placement detection failed: {e}")
        return "bottom"


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "../assets/Sample-input-images/vw1.jpg"

    print("\n=== Testing AI Functions ===\n")
    placement = detect_subject_and_place_panel(path)
    print(f"\nPanel placement: {placement}")

    logo_type = should_use_light_logo(path)
    print(f"Logo type: {'light' if logo_type else 'dark'}")