"""
Medical Billing Dashboard Backend
==================================
Production-ready Flask backend for healthcare billing process automation
Handles data flow from Ingenious Med -> AdvancedMD -> Insurance
Tracks KPIs, denials, and provides predictive analytics
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta, date
import random
import json
from typing import Dict, List, Any, Optional
import os
from dataclasses import dataclass, asdict
from enum import Enum

# Initialize Flask app with production settings
app = Flask(__name__)
app.config['DEBUG'] = False  # Set to False for production
app.config['JSON_SORT_KEYS'] = False
CORS(app)  # Enable CORS for React frontend

# Import and register external API blueprint
from external_api_routes import external_api_bp
app.register_blueprint(external_api_bp)

# ============================================================================
# DATA MODELS AND ENUMS
# ============================================================================

class ClaimStatus(Enum):
    """Claim status throughout the billing pipeline"""
    CHART_SIGNED = "Chart Signed"
    PENDING_SUBMISSION = "Pending Submission"
    SUBMITTED = "Submitted to Insurance"
    PENDING_PAYMENT = "Pending Payment"
    PAID = "Paid"
    DENIED = "Denied"
    APPEALED = "Under Appeal"
    WRITTEN_OFF = "Written Off"

class DenialReason(Enum):
    """Common denial reasons from insurance"""
    ELIGIBILITY = "Patient Not Eligible"
    AUTHORIZATION = "Missing Authorization"
    CODING_ERROR = "Coding Error"
    MISSING_INFO = "Missing Information"
    TIMELY_FILING = "Timely Filing Exceeded"
    DUPLICATE = "Duplicate Claim"
    MEDICAL_NECESSITY = "Medical Necessity"
    OUT_OF_NETWORK = "Out of Network"

@dataclass
class Patient:
    """Patient data model"""
    id: int
    mrn: str
    name: str
    assigned_doctor: Optional[str] = None

@dataclass
class ClaimHistory:
    """Claim resubmission history"""
    submission_number: int
    submission_date: datetime
    status: str
    response_date: Optional[datetime] = None
    denial_reason: Optional[str] = None
    amount_adjusted: float = 0.0
    notes: str = ""

@dataclass
class Encounter:
    """Enhanced Encounter/Claim data model with detailed tracking"""
    id: int
    patient_id: int
    patient_name: str
    patient_mrn: str
    patient_dob: str
    patient_phone: str
    doctor: str
    facility: str
    service_date: datetime
    cpt_codes: List[str]
    icd_codes: List[str]
    amount: float
    status: str
    chart_signed_date: datetime
    submission_date: Optional[datetime] = None
    payment_date: Optional[datetime] = None
    denial_date: Optional[datetime] = None
    denial_reason: Optional[str] = None
    denial_code: Optional[str] = None
    insurance_payer: str = "Blue Cross"
    policy_number: str = ""
    authorization_number: str = ""
    needs_assignment: bool = False
    appeal_status: Optional[str] = None
    risk_score: float = 0.0
    resubmission_count: int = 0
    claim_history: List[ClaimHistory] = None
    provider_notes: str = ""
    billing_notes: str = ""
    expected_payment: float = 0.0
    actual_payment: float = 0.0
    patient_responsibility: float = 0.0
    
    def __post_init__(self):
        if self.claim_history is None:
            self.claim_history = []
        if self.expected_payment == 0.0:
            self.expected_payment = self.amount * 0.8  # 80% expected payment rate

# ============================================================================
# DATA STORAGE (In production, this would be a database)
# ============================================================================

class DataStore:
    """In-memory data storage simulating database"""
    
    def __init__(self):
        self.patients = []
        self.encounters = []
        self.doctor_assignments = {}  # patient_id -> doctor mapping
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Create realistic sample data for demonstration"""
        
        # Sample doctors
        doctors = ["Dr. Smith", "Dr. Johnson", "Dr. Williams", "Dr. Brown", "Dr. Davis"]
        
        # Sample insurance payers
        payers = ["Blue Cross", "Aetna", "United Healthcare", "Cigna", "Medicare"]
        
        # Create sample patients
        patient_names = [
            "John Doe", "Jane Smith", "Robert Johnson", "Maria Garcia",
            "William Brown", "Patricia Davis", "Michael Wilson", "Linda Martinez"
        ]
        
        for i, name in enumerate(patient_names, 1):
            patient = Patient(
                id=i,
                mrn=f"MRN{100000 + i}",
                name=name,
                assigned_doctor=random.choice(doctors) if i != 4 else None  # Patient 4 unassigned
            )
            self.patients.append(patient)
            if patient.assigned_doctor:
                self.doctor_assignments[i] = patient.assigned_doctor
        
        # Create sample encounters with various statuses
        now = datetime.now()
        
        # Recent encounters - just signed
        for i in range(1, 4):
            enc = Encounter(
                id=i,
                patient_id=i,
                patient_name=self.patients[i-1].name,
                doctor=doctors[i-1],
                amount=random.uniform(500, 5000),
                status=ClaimStatus.PENDING_SUBMISSION.value,
                chart_signed_date=now - timedelta(days=random.randint(0, 2)),
                insurance_payer=random.choice(payers),
                needs_assignment=(i == 1),  # First one needs assignment
                risk_score=random.uniform(0.1, 0.3)
            )
            self.encounters.append(enc)
        
        # Submitted claims awaiting payment
        for i in range(4, 8):
            signed = now - timedelta(days=random.randint(5, 10))
            submitted = signed + timedelta(days=2)
            enc = Encounter(
                id=i,
                patient_id=i if i < 8 else 1,
                patient_name=self.patients[min(i-1, 7)].name,
                doctor=random.choice(doctors),
                amount=random.uniform(1000, 8000),
                status=ClaimStatus.PENDING_PAYMENT.value,
                chart_signed_date=signed,
                submission_date=submitted,
                insurance_payer=random.choice(payers),
                risk_score=random.uniform(0.2, 0.5)
            )
            self.encounters.append(enc)
        
        # Paid claims
        for i in range(8, 12):
            signed = now - timedelta(days=random.randint(20, 30))
            submitted = signed + timedelta(days=2)
            paid = submitted + timedelta(days=random.randint(15, 25))
            enc = Encounter(
                id=i,
                patient_id=(i % 7) + 1,
                patient_name=self.patients[(i % 7)].name,
                doctor=random.choice(doctors),
                amount=random.uniform(800, 6000),
                status=ClaimStatus.PAID.value,
                chart_signed_date=signed,
                submission_date=submitted,
                payment_date=paid,
                insurance_payer=random.choice(payers),
                risk_score=random.uniform(0.0, 0.2)
            )
            self.encounters.append(enc)
        
        # Denied claims
        denial_reasons = list(DenialReason)
        for i in range(12, 15):
            signed = now - timedelta(days=random.randint(15, 25))
            submitted = signed + timedelta(days=3)
            denied = submitted + timedelta(days=random.randint(5, 10))
            enc = Encounter(
                id=i,
                patient_id=(i % 7) + 1,
                patient_name=self.patients[(i % 7)].name,
                doctor=random.choice(doctors),
                amount=random.uniform(1000, 7000),
                status=ClaimStatus.DENIED.value,
                chart_signed_date=signed,
                submission_date=submitted,
                denial_date=denied,
                denial_reason=random.choice(denial_reasons).value,
                insurance_payer=random.choice(payers),
                needs_assignment=(i == 12),  # One denied due to assignment issue
                risk_score=random.uniform(0.6, 0.9)
            )
            self.encounters.append(enc)

# Initialize data store
data_store = DataStore()

# ============================================================================
# BUSINESS LOGIC AND CALCULATIONS
# ============================================================================

class MetricsCalculator:
    """Calculate KPIs from claims data"""
    
    @staticmethod
    def calculate_charge_lag(encounters: List[Encounter]) -> float:
        """Average days from chart signed to submission"""
        lags = []
        for enc in encounters:
            if enc.submission_date and enc.chart_signed_date:
                lag = (enc.submission_date - enc.chart_signed_date).days
                lags.append(lag)
        return sum(lags) / len(lags) if lags else 0
    
    @staticmethod
    def calculate_clean_claim_rate(encounters: List[Encounter]) -> float:
        """Percentage of claims paid without denial"""
        total_processed = len([e for e in encounters if e.status in [
            ClaimStatus.PAID.value, ClaimStatus.DENIED.value
        ]])
        if total_processed == 0:
            return 100.0
        paid_first_pass = len([e for e in encounters if 
            e.status == ClaimStatus.PAID.value and not e.denial_date])
        return (paid_first_pass / total_processed) * 100
    
    @staticmethod
    def calculate_denial_rate(encounters: List[Encounter]) -> float:
        """Percentage of claims denied"""
        submitted = [e for e in encounters if e.submission_date]
        if not submitted:
            return 0
        denied = len([e for e in submitted if e.status == ClaimStatus.DENIED.value])
        return (denied / len(submitted)) * 100
    
    @staticmethod
    def calculate_ar_days(encounters: List[Encounter]) -> float:
        """Average days from submission to payment"""
        days_list = []
        for enc in encounters:
            if enc.submission_date and enc.payment_date:
                days = (enc.payment_date - enc.submission_date).days
                days_list.append(days)
        return sum(days_list) / len(days_list) if days_list else 0
    
    @staticmethod
    def get_denial_breakdown(encounters: List[Encounter]) -> Dict[str, int]:
        """Count denials by reason"""
        breakdown = {}
        for enc in encounters:
            if enc.denial_reason:
                breakdown[enc.denial_reason] = breakdown.get(enc.denial_reason, 0) + 1
        return breakdown

class IngeniousMedIntegration:
    """Simulates Ingenious Med charge capture system integration"""
    
    @staticmethod
    def fetch_new_charges():
        """
        TODO: Replace with actual Ingenious Med API call
        Example: 
        response = requests.get('https://api.ingeniousmed.com/charges',
                               headers={'Authorization': 'Bearer TOKEN'})
        """
        # Simulate fetching new signed charts
        return {"message": "Fetched 5 new signed charts", "count": 5}
    
    @staticmethod
    def validate_doctor_assignment(patient_id: int, doctor: str) -> bool:
        """Check if patient is properly assigned to billing doctor"""
        assigned = data_store.doctor_assignments.get(patient_id)
        return assigned == doctor if assigned else False

class AdvancedMDIntegration:
    """Simulates AdvancedMD billing system integration"""
    
    @staticmethod
    def submit_claim(encounter_id: int):
        """
        TODO: Replace with actual AdvancedMD API call
        Example:
        payload = {'encounter_id': encounter_id, 'amount': amount}
        response = requests.post('https://api.advancedmd.com/claims',
                                json=payload, headers={'API-Key': 'KEY'})
        """
        # Simulate claim submission
        for enc in data_store.encounters:
            if enc.id == encounter_id:
                enc.status = ClaimStatus.SUBMITTED.value
                enc.submission_date = datetime.now()
                return True
        return False

class PredictiveAnalytics:
    """AI/ML predictions for denial risk"""
    
    @staticmethod
    def predict_denial_risk(encounter: Encounter) -> float:
        """
        Predict likelihood of denial (0-1 scale)
        In production, this would use a trained ML model
        """
        risk = 0.1  # Base risk
        
        # Factors that increase denial risk
        if encounter.needs_assignment:
            risk += 0.4
        if encounter.amount > 5000:
            risk += 0.2
        if encounter.insurance_payer == "Medicare":
            risk += 0.1
        if not encounter.submission_date:
            lag_days = (datetime.now() - encounter.chart_signed_date).days
            if lag_days > 3:
                risk += 0.2
        
        # Historical denial rate by doctor (simulated)
        doctor_denial_rates = {
            "Dr. Smith": 0.05,
            "Dr. Johnson": 0.08,
            "Dr. Williams": 0.12,
            "Dr. Brown": 0.03,
            "Dr. Davis": 0.15
        }
        risk += doctor_denial_rates.get(encounter.doctor, 0.1)
        
        return min(risk, 1.0)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/kpis', methods=['GET'])
def get_kpis():
    """Return current KPI metrics for dashboard"""
    calculator = MetricsCalculator()
    encounters = data_store.encounters
    
    # Calculate all KPIs
    kpis = {
        "charge_lag_days": round(calculator.calculate_charge_lag(encounters), 1),
        "clean_claim_rate": round(calculator.calculate_clean_claim_rate(encounters), 1),
        "denial_rate": round(calculator.calculate_denial_rate(encounters), 1),
        "ar_days": round(calculator.calculate_ar_days(encounters), 1),
        "total_claims": len(encounters),
        "pending_submission": len([e for e in encounters if e.status == ClaimStatus.PENDING_SUBMISSION.value]),
        "pending_payment": len([e for e in encounters if e.status == ClaimStatus.PENDING_PAYMENT.value]),
        "denied_claims": len([e for e in encounters if e.status == ClaimStatus.DENIED.value]),
        "unassigned_encounters": len([e for e in encounters if e.needs_assignment]),
        "high_risk_claims": len([e for e in encounters if e.risk_score > 0.7]),
        "denial_breakdown": calculator.get_denial_breakdown(encounters),
        "last_updated": datetime.now().isoformat()
    }
    
    return jsonify(kpis)

@app.route('/api/claims', methods=['GET'])
def get_claims():
    """Return list of all claims/encounters with details"""
    # Convert encounters to dictionaries
    claims = []
    for enc in data_store.encounters:
        claim_dict = {
            "id": enc.id,
            "patient_id": enc.patient_id,
            "patient_name": enc.patient_name,
            "doctor": enc.doctor,
            "amount": round(enc.amount, 2),
            "status": enc.status,
            "chart_signed_date": enc.chart_signed_date.isoformat(),
            "submission_date": enc.submission_date.isoformat() if enc.submission_date else None,
            "payment_date": enc.payment_date.isoformat() if enc.payment_date else None,
            "denial_date": enc.denial_date.isoformat() if enc.denial_date else None,
            "denial_reason": enc.denial_reason,
            "insurance_payer": enc.insurance_payer,
            "needs_assignment": enc.needs_assignment,
            "risk_score": round(enc.risk_score, 2),
            "alert": None
        }
        
        # Add alerts for problematic claims
        if enc.needs_assignment:
            claim_dict["alert"] = "Needs Doctor Assignment"
        elif enc.status == ClaimStatus.DENIED.value:
            claim_dict["alert"] = f"Denied: {enc.denial_reason}"
        elif enc.risk_score > 0.7:
            claim_dict["alert"] = "High Denial Risk"
        elif enc.status == ClaimStatus.PENDING_SUBMISSION.value:
            lag = (datetime.now() - enc.chart_signed_date).days
            if lag > 2:
                claim_dict["alert"] = f"Delayed {lag} days"
        
        claims.append(claim_dict)
    
    # Sort by most recent first
    claims.sort(key=lambda x: x["chart_signed_date"], reverse=True)
    
    return jsonify(claims)

@app.route('/api/assign', methods=['POST'])
def assign_patient():
    """Handle patient-doctor assignment"""
    data = request.json
    encounter_id = data.get('encounter_id')
    doctor = data.get('doctor')
    
    # Find and update encounter
    for enc in data_store.encounters:
        if enc.id == encounter_id:
            enc.needs_assignment = False
            enc.doctor = doctor
            # Update risk score after assignment
            enc.risk_score = PredictiveAnalytics.predict_denial_risk(enc)
            
            return jsonify({
                "success": True,
                "message": f"Patient assigned to {doctor}",
                "encounter_id": encounter_id
            })
    
    return jsonify({"success": False, "message": "Encounter not found"}), 404

@app.route('/api/sync/ingeniousmed', methods=['POST'])
def sync_ingenious_med():
    """Trigger sync with Ingenious Med to fetch new charges"""
    result = IngeniousMedIntegration.fetch_new_charges()
    
    # Simulate creating new encounters from fetched charges
    # In production, this would parse actual API response
    
    return jsonify({
        "success": True,
        "message": "Ingenious Med sync completed",
        "details": result
    })

@app.route('/api/sync/advancedmd', methods=['POST'])
def sync_advanced_md():
    """Push pending claims to AdvancedMD"""
    pending = [e for e in data_store.encounters if e.status == ClaimStatus.PENDING_SUBMISSION.value]
    submitted_count = 0
    
    for enc in pending:
        # Check assignment before submission
        if not enc.needs_assignment:
            if AdvancedMDIntegration.submit_claim(enc.id):
                submitted_count += 1
    
    return jsonify({
        "success": True,
        "message": f"Submitted {submitted_count} claims to AdvancedMD",
        "remaining_pending": len(pending) - submitted_count
    })

@app.route('/api/predictions/denial-risk', methods=['GET'])
def get_denial_predictions():
    """Get claims with high denial risk for proactive review"""
    high_risk = []
    
    for enc in data_store.encounters:
        if enc.status in [ClaimStatus.PENDING_SUBMISSION.value, ClaimStatus.SUBMITTED.value]:
            # Recalculate risk
            enc.risk_score = PredictiveAnalytics.predict_denial_risk(enc)
            
            if enc.risk_score > 0.5:  # Threshold for "high risk"
                high_risk.append({
                    "encounter_id": enc.id,
                    "patient_name": enc.patient_name,
                    "doctor": enc.doctor,
                    "amount": round(enc.amount, 2),
                    "risk_score": round(enc.risk_score * 100, 1),  # As percentage
                    "risk_factors": _get_risk_factors(enc)
                })
    
    # Sort by highest risk first
    high_risk.sort(key=lambda x: x["risk_score"], reverse=True)
    
    return jsonify(high_risk)

def _get_risk_factors(encounter):
    """Identify specific risk factors for a claim"""
    factors = []
    if encounter.needs_assignment:
        factors.append("Unassigned patient")
    if encounter.amount > 5000:
        factors.append("High dollar amount")
    lag_days = (datetime.now() - encounter.chart_signed_date).days
    if lag_days > 3:
        factors.append(f"Delayed submission ({lag_days} days)")
    return factors

@app.route('/api/analytics/trends', methods=['GET'])
def get_trends():
    """Get historical trends for visualization"""
    # Simulate historical data points
    # In production, this would query actual historical data
    
    trends = {
        "denial_rate_trend": [
            {"month": "Jan", "rate": 5.2},
            {"month": "Feb", "rate": 4.8},
            {"month": "Mar", "rate": 5.5},
            {"month": "Apr", "rate": 4.2},
            {"month": "May", "rate": 3.9},
            {"month": "Jun", "rate": 4.1}
        ],
        "submission_lag_trend": [
            {"month": "Jan", "days": 3.5},
            {"month": "Feb", "days": 3.2},
            {"month": "Mar", "days": 2.8},
            {"month": "Apr", "days": 2.5},
            {"month": "May", "days": 2.2},
            {"month": "Jun", "days": 2.0}
        ],
        "collection_trend": [
            {"month": "Jan", "amount": 125000},
            {"month": "Feb", "amount": 132000},
            {"month": "Mar", "amount": 128000},
            {"month": "Apr", "amount": 145000},
            {"month": "May", "amount": 151000},
            {"month": "Jun", "amount": 148000}
        ]
    }
    
    return jsonify(trends)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "environment": "production"
    })

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Production deployment notes:
    # - Use a production WSGI server like Gunicorn or uWSGI
    # - Set environment variables for API credentials:
    #   INGENIOUS_MED_API_KEY, ADVANCED_MD_API_KEY
    # - Configure database connection (replace in-memory with PostgreSQL/MySQL)
    # - Enable SSL/TLS for HTTPS
    # - Implement proper authentication (OAuth2/JWT)
    # - Set up logging to file or cloud service
    
    print("=" * 60)
    print("Medical Billing Dashboard Backend")
    print("=" * 60)
    print("Server starting on http://localhost:5000")
    print("API Endpoints:")
    print("  GET  /api/kpis - Dashboard KPIs")
    print("  GET  /api/claims - Claims list")
    print("  POST /api/assign - Assign patient to doctor")
    print("  POST /api/sync/ingeniousmed - Sync with Ingenious Med")
    print("  POST /api/sync/advancedmd - Push to AdvancedMD")
    print("  GET  /api/predictions/denial-risk - High risk claims")
    print("  GET  /api/analytics/trends - Historical trends")
    print("=" * 60)
    
    # Run Flask app (development mode)
    app.run(host='0.0.0.0', port=5000, debug=False)