"""
HHA Medicine Dashboard - Main Server

Serves the built React frontend (../01_Frontend_Website) and the JSON KPI
API on the same origin. Port is taken from the PORT env var (Railway/Heroku
convention), falling back to 5010 for local development.
"""

import os
import random
from datetime import datetime, timedelta

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "01_Frontend_Website"))

app = Flask(__name__, static_folder=None)
CORS(app)


def generate_kpi_data():
    """Generate realistic KPI data for the dashboard."""
    return {
        "revenue_metrics": {
            "total_revenue": 3456789.45,
            "monthly_revenue": 287899.12,
            "daily_revenue": 9596.64,
            "growth_percentage": 12.5,
            "collections_rate": 96.7,
        },
        "claims_metrics": {
            "total_claims": 4567,
            "processed_today": 145,
            "pending_claims": 234,
            "denied_claims": 45,
            "approval_rate": 94.3,
            "clean_claim_rate": 98.2,
        },
        "patient_metrics": {
            "total_patients": 8934,
            "new_patients_month": 234,
            "active_patients": 7234,
            "patient_satisfaction": 4.8,
        },
        "performance_indicators": {
            "days_in_ar": 28,
            "first_pass_resolution": 89.5,
            "denial_rate": 5.7,
            "net_collection_rate": 96.7,
            "bad_debt_percentage": 2.1,
        },
        "payer_mix": {
            "Medicare": 45,
            "Medicaid": 20,
            "Commercial": 30,
            "Self_Pay": 5,
        },
        "department_performance": [
            {"name": "Cardiology", "revenue": 567890, "claims": 234},
            {"name": "Orthopedics", "revenue": 456789, "claims": 189},
            {"name": "Primary Care", "revenue": 678901, "claims": 456},
            {"name": "Pediatrics", "revenue": 345678, "claims": 267},
            {"name": "Emergency", "revenue": 789012, "claims": 512},
        ],
        "timestamp": datetime.now().isoformat(),
    }


@app.route("/api")
def api_index():
    return jsonify({
        "name": "HHA Medicine Medical Billing KPI Dashboard API",
        "version": "2.0.0",
        "description": "Professional medical billing analytics and KPI tracking system",
        "endpoints": [
            "/api/kpi - Get all KPI metrics",
            "/api/revenue - Revenue metrics only",
            "/api/claims - Claims processing metrics",
            "/api/patients - Patient statistics",
            "/api/performance - Performance indicators",
            "/api/departments - Department wise data",
            "/health - System health check",
        ],
        "status": "operational",
    })


@app.route("/health")
def health_check():
    return jsonify({
        "status": "healthy",
        "server": "HHA Medicine Dashboard",
        "timestamp": datetime.now().isoformat(),
        "uptime": "100%",
    })


@app.route("/api/kpi")
def get_all_kpis():
    return jsonify(generate_kpi_data())


@app.route("/api/revenue")
def get_revenue():
    return jsonify(generate_kpi_data()["revenue_metrics"])


@app.route("/api/claims")
def get_claims():
    return jsonify(generate_kpi_data()["claims_metrics"])


@app.route("/api/patients")
def get_patients():
    return jsonify(generate_kpi_data()["patient_metrics"])


@app.route("/api/performance")
def get_performance():
    return jsonify(generate_kpi_data()["performance_indicators"])


@app.route("/api/departments")
def get_departments():
    return jsonify(generate_kpi_data()["department_performance"])


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path: str):
    """Serve the React bundle. Unknown paths fall back to index.html for SPA routing."""
    if path:
        candidate = os.path.join(FRONTEND_DIR, path)
        if os.path.isfile(candidate):
            return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5010"))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"

    print("=" * 60)
    print("  HHA Medicine - Medical Billing KPI Dashboard Server")
    print("=" * 60)
    print(f"  Starting server on http://localhost:{port}")
    print(f"  Dashboard: http://localhost:{port}/")
    print(f"  API index: http://localhost:{port}/api")
    print(f"  Health:    http://localhost:{port}/health")
    print("=" * 60)

    app.run(host=host, port=port, debug=debug)
