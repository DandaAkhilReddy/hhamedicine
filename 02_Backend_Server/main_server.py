"""
HHA Medicine Dashboard - Main Server
This is the main server that powers the Medical Billing KPI Dashboard
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)

# Server Configuration
PORT = 5010
HOST = '0.0.0.0'

def generate_kpi_data():
    """Generate realistic KPI data for the dashboard"""
    return {
        "revenue_metrics": {
            "total_revenue": 3456789.45,
            "monthly_revenue": 287899.12,
            "daily_revenue": 9596.64,
            "growth_percentage": 12.5,
            "collections_rate": 96.7
        },
        "claims_metrics": {
            "total_claims": 4567,
            "processed_today": 145,
            "pending_claims": 234,
            "denied_claims": 45,
            "approval_rate": 94.3,
            "clean_claim_rate": 98.2
        },
        "patient_metrics": {
            "total_patients": 8934,
            "new_patients_month": 234,
            "active_patients": 7234,
            "patient_satisfaction": 4.8
        },
        "performance_indicators": {
            "days_in_ar": 28,
            "first_pass_resolution": 89.5,
            "denial_rate": 5.7,
            "net_collection_rate": 96.7,
            "bad_debt_percentage": 2.1
        },
        "payer_mix": {
            "Medicare": 45,
            "Medicaid": 20,
            "Commercial": 30,
            "Self_Pay": 5
        },
        "department_performance": [
            {"name": "Cardiology", "revenue": 567890, "claims": 234},
            {"name": "Orthopedics", "revenue": 456789, "claims": 189},
            {"name": "Primary Care", "revenue": 678901, "claims": 456},
            {"name": "Pediatrics", "revenue": 345678, "claims": 267},
            {"name": "Emergency", "revenue": 789012, "claims": 512}
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.route('/')
def index():
    """Main API endpoint - returns API information"""
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
            "/health - System health check"
        ],
        "status": "operational"
    })

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "server": "HHA Medicine Dashboard",
        "timestamp": datetime.now().isoformat(),
        "uptime": "100%"
    })

@app.route('/api/kpi')
def get_all_kpis():
    """Get all KPI metrics"""
    return jsonify(generate_kpi_data())

@app.route('/api/revenue')
def get_revenue():
    """Get revenue metrics only"""
    data = generate_kpi_data()
    return jsonify(data["revenue_metrics"])

@app.route('/api/claims')
def get_claims():
    """Get claims metrics"""
    data = generate_kpi_data()
    return jsonify(data["claims_metrics"])

@app.route('/api/patients')
def get_patients():
    """Get patient metrics"""
    data = generate_kpi_data()
    return jsonify(data["patient_metrics"])

@app.route('/api/performance')
def get_performance():
    """Get performance indicators"""
    data = generate_kpi_data()
    return jsonify(data["performance_indicators"])

@app.route('/api/departments')
def get_departments():
    """Get department wise performance"""
    data = generate_kpi_data()
    return jsonify(data["department_performance"])

if __name__ == '__main__':
    print("="*60)
    print("  HHA Medicine - Medical Billing KPI Dashboard Server")
    print("="*60)
    print(f"  Starting server on http://localhost:{PORT}")
    print("  API Documentation: http://localhost:{PORT}/")
    print("  Health Check: http://localhost:{PORT}/health")
    print("="*60)
    print("  Press Ctrl+C to stop the server")
    print("="*60)
    
    app.run(host=HOST, port=PORT, debug=True)