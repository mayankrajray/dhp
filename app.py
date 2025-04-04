from flask import Flask, jsonify
import pandas as pd
import os

app = Flask(__name__)

# ------------------- CORS HEADERS -------------------
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# ------------------- ROUTES -------------------

@app.route("/")
def home():
    return "✅ Flask API is up and running!"

@app.route("/data", methods=["GET"])
def get_data():
    if not processed_data:
        return jsonify({"error": "❌ No data available. Check if 'stackoverflow_data.csv' exists and is correctly formatted."}), 500
    return jsonify(processed_data)

# ------------------- CSV PROCESSING -------------------

def load_and_process_csv(filename="stackoverflow_data.csv"):
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return {}

    try:
        df = pd.read_csv(file_path)

        # Validate required columns
        required_columns = {"Question", "Tag", "Published Date"}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"CSV must contain columns: {required_columns}")

        # Parse date and extract year
        df["Year"] = pd.to_datetime(df["Published Date"], errors='coerce').dt.year
        df.dropna(subset=["Year"], inplace=True)
        df["Year"] = df["Year"].astype(int)

        # Group by Year and Tag, then calculate percentages
        grouped = df.groupby(["Year", "Tag"]).size().unstack(fill_value=0)
        totals = grouped.sum(axis=1)
        percent_data = grouped.div(totals, axis=0) * 100

        print("[INFO] CSV processed successfully.")
        return percent_data.to_dict()

    except Exception as e:
        print(f"[ERROR] Failed to process CSV: {e}")
        return {}

# Load data once on startup
processed_data = load_and_process_csv()

# ------------------- MAIN -------------------
if __name__ == "__main__":
    app.run(debug=True)
