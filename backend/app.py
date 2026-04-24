from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from generator import generate_creative
import os, zipfile, io


app = Flask(__name__)
CORS(app)

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BACKEND_DIR, "uploads")
STATIC_DIR  = os.path.join(BACKEND_DIR, "static")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)


@app.route("/generate", methods=["POST"])
def generate():
    try:
        print("\n" + "="*60)
        print("NEW GENERATION REQUEST")
        print("="*60)

        if "image" not in request.files:
            return jsonify({"error": "No image uploaded", "status": "failed"}), 400

        image_file = request.files["image"]
        brand = request.form.get("brand", "Volkswagen")
        dealers_json = request.form.get("dealers", "[]")
        include_logo = request.form.get("includeLogo", "false").lower() == "true"
        include_brand_assets = request.form.get("includeBrandAssets", "false").lower() == "true"
        output_format = request.form.get("outputFormat", "1080x1080")

        print(f"Brand: {brand}")
        print(f"Dealers: {dealers_json}")
        print(f"Logo: {include_logo} | Panel: {include_brand_assets}")
        print(f"Format: {output_format}")

        # clear old generated images first
        for filename in os.listdir(STATIC_DIR):
            if filename.endswith(".png"):
                filepath = os.path.join(STATIC_DIR, filename)
                os.remove(filepath)

        bg_image_path = os.path.join(UPLOADS_DIR, "background.jpg")
        image_file.save(bg_image_path)
        print(f"\nBackground saved to: {bg_image_path}")

        results = generate_creative(
            image_path=bg_image_path,
            brand=brand,
            dealers_json=dealers_json,
        )

        response_results = [
            {
                "dealer": dealer,
                "image": f"http://127.0.0.1:5000/output/{os.path.basename(path)}",
            }
            for dealer, path in results
        ]

        print(f"\nDone — {len(response_results)} creative(s) generated")
        for r in response_results:
            print(f"  - {r['dealer']}")

        return jsonify({"results": response_results, "status": "success"})

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "status": "failed"}), 500


@app.route("/output/<filename>")
def serve_image(filename):
    try:
        return send_from_directory(STATIC_DIR, filename)
    except Exception as e:
        print(f"Error serving {filename}: {e}")
        return jsonify({"error": str(e)}), 404


@app.route("/download_zip")
def download_zip():
    try:
        png_files = [f for f in os.listdir(STATIC_DIR) if f.endswith(".png")]

        if not png_files:
            return jsonify({"error": "No generated files found. Generate first."}), 404

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname in png_files:
                fpath = os.path.join(STATIC_DIR, fname)
                zf.write(fpath, fname)

        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name="creatives.zip",
        )

    except Exception as e:
        print(f"ZIP error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print(f"\nFlask running from: {os.getcwd()}\n")
    app.run(debug=True, port=5000)