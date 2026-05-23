from flask import (
    Flask,
    render_template,
    request,
    jsonify
)

from flask_cors import CORS
from pyngrok import ngrok

import pandas as pd
import os
import shutil

# ==========================
# Flask setup
# ==========================
app = Flask(__name__)

CORS(
    app,
    resources={
        r"/*": {
            "origins": "*"
        }
    }
)

# ==========================
# Directories
# ==========================
BASE_DIR = "/content/uploads"

EXCEL_DIR = (
    f"{BASE_DIR}/excel"
)

IMAGE_DIR = (
    f"{BASE_DIR}/images"
)

os.makedirs(
    EXCEL_DIR,
    exist_ok=True
)

os.makedirs(
    IMAGE_DIR,
    exist_ok=True
)

# ==========================
# Home page
# ==========================
@app.route("/")
def home():

    return render_template(
        "home.html"
    )


# ==========================
# Upload page
# ==========================
@app.route("/upload-page")
def upload_page():

    return render_template(
        "index.html"
    )


# ==========================
# API upload endpoint
# ==========================
@app.route(
    "/upload",
    methods=["POST"]
)
def upload():

    uploaded_files = (
        request.files.getlist(
            "files"
        )
    )

    results = []

    excel_info = []

    for file in uploaded_files:

        filename = (
            file.filename
        )

        lower_name = (
            filename.lower()
        )

        # Excel files
        if lower_name.endswith(
            (
                ".xlsx",
                ".xls",
                ".csv"
            )
        ):

            dst = os.path.join(
                EXCEL_DIR,
                filename
            )

            file.save(dst)

            try:

                df = pd.read_excel(
                    dst
                )

                excel_info.append({
                    "file":
                        filename,
                    "rows":
                        len(df),
                    "columns":
                        df.columns.tolist()
                })

            except Exception:

                pass

            results.append(
                f"Excel saved: {filename}"
            )

        # Images
        elif lower_name.endswith(
            (
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".webp"
            )
        ):

            dst = os.path.join(
                IMAGE_DIR,
                filename
            )

            file.save(dst)

            results.append(
                f"Image saved: {filename}"
            )

        else:

            results.append(
                f"Unsupported: {filename}"
            )

    return jsonify({
        "status":
            "success",

        "results":
            results,

        "excel_info":
            excel_info
    })


# ==========================
# Start ngrok
# ==========================
public_url = ngrok.connect(
    5000
)

print(
    "\nPublic URL:",
    public_url.public_url
)

# ==========================
# Run Flask
# ==========================
app.run(
    host="0.0.0.0",
    port=5000
)
