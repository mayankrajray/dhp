from flask import Flask, jsonify
import pandas as pd
import os

app = Flask(__name__)
# CORS(app)  # Enable Cross-Origin Resource Sharing
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"  # Allow all origins
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


@app.route("/")
def home():
    return "Flask API is running!"


# Load the CSV file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "stackoverflow_data.csv")
df = pd.read_csv(file_path)
data = {}

if os.path.exists(file_path):
    try:
        df = pd.read_csv(file_path)
        print("CSV loaded successfully!")
        
        # Ensure correct column names and process the data
        required_columns = {"Question", "Tag", "Published Date"}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"CSV must contain columns: {required_columns}")

        # Convert 'Date' to Year and handle errors
        df["Year"] = pd.to_datetime(df["Published Date"], errors='coerce').dt.year
        df.dropna(subset=["Year"], inplace=True)
        df["Year"] = df["Year"].astype(int)

        # Group by Year and Tag, then calculate percentages
        grouped_data = df.groupby(["Year", "Tag"]).size().unstack(fill_value=0)
        yearly_totals = grouped_data.sum(axis=1)
        percentage_data = grouped_data.div(yearly_totals, axis=0) * 100  # Convert to percentage
        data = percentage_data.to_dict()
        print(f"Data loaded: {data}")  # Check the contents of data
    
    except Exception as e:
        print(f"Error processing CSV: {e}")
        data = {}  # Clear the data in case of error
else:
    print(f"File not found at: {file_path}")
    data = {}  # Clear the data if file doesn't exist


@app.route("/data", methods=["GET"])
def get_data():
    if not data:
        return jsonify({"error": "No data available. Ensure data.csv is correctly formatted and available."}), 404
    return jsonify(data)

