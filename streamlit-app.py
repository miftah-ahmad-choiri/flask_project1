from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

# ==========================
# Optional ngrok
# ==========================
USE_NGROK = False

if USE_NGROK:
    from pyngrok import ngrok


# ==========================
# Flask setup
# ==========================
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# ==========================
# Base directory
# ==========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
EXCEL_DIR = os.path.join(UPLOAD_DIR, "excel")
IMAGE_DIR = os.path.join(UPLOAD_DIR, "images")


# ==========================
# Create directories
# ==========================
for directory in [TEMPLATE_DIR, UPLOAD_DIR, EXCEL_DIR, IMAGE_DIR]:
    os.makedirs(directory, exist_ok=True)


print("\nDirectories ready:")
print("Templates:", TEMPLATE_DIR)
print("Uploads:", UPLOAD_DIR)
print("Excel:", EXCEL_DIR)
print("Images:", IMAGE_DIR)


# ==========================
# Routes
# ==========================
@app.route("/")
def home():
    try:
        return render_template("home.html")
    except Exception:
        return "<h2>home.html not found</h2>"


@app.route("/upload-page")
def upload_page():
    try:
        return render_template("index.html")
    except Exception:
        return "<h2>index.html not found</h2>"


@app.route("/health")
def health():
    return jsonify({"status": "backend_running"})


# ==========================
# Upload API
# ==========================
@app.route("/upload", methods=["POST"])
def upload():

    uploaded_files = request.files.getlist("files")

    if not uploaded_files:
        return jsonify({
            "status": "failed",
            "message": "No files uploaded"
        }), 400

    results = []
    excel_info = []

    for file in uploaded_files:

        if not file or file.filename == "":
            continue

        filename = os.path.basename(file.filename)
        lower_name = filename.lower()

        # ==================
        # Excel / CSV
        # ==================
        if lower_name.endswith((".xlsx", ".xls", ".csv")):

            dst = os.path.join(EXCEL_DIR, filename)
            file.save(dst)

            try:
                if lower_name.endswith(".csv"):
                    df = pd.read_csv(dst)
                else:
                    df = pd.read_excel(dst)

                excel_info.append({
                    "file": filename,
                    "rows": len(df),
                    "columns": df.columns.tolist()
                })

            except Exception as e:
                excel_info.append({
                    "file": filename,
                    "error": str(e)
                })

            results.append(f"Excel saved: {filename}")

        # ==================
        # Images
        # ==================
        elif lower_name.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):

            dst = os.path.join(IMAGE_DIR, filename)
            file.save(dst)

            results.append(f"Image saved: {filename}")

        # ==================
        # Unsupported
        # ==================
        else:
            results.append(f"Unsupported: {filename}")

    return jsonify({
        "status": "success",
        "results": results,
        "excel_info": excel_info
    })


# ==========================
# Main entry (FIXED)
# ==========================
if __name__ == "__main__":

    if USE_NGROK:
        public_url = ngrok.connect(5000)
        print("\nPublic URL:", public_url.public_url)

    print("\nFlask running at:")
    print("http://localhost:5000")

    # IMPORTANT FIX:
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,          # ❗ important fix
        use_reloader=False,   # ❗ prevents signal crash in restricted env
        threaded=True
    )
