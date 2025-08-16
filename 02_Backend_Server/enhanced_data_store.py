"""
Enhanced Data Store with Comprehensive Claim Tracking
====================================================
Includes detailed patient info, denial tracking, resubmissions, and analytics
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import random
import json

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
class EnhancedEncounter:
    """Enhanced Encounter/Claim data model"""
    id: int
    patient_id: int
    patient_name: str
    patient_mrn: str
    patient_dob: str
    patient_phone: str
    patient_address: str
    patient_insurance_id: str
    doctor: str
    doctor_npi: str
    facility: str
    facility_tax_id: str
    service_date: datetime
    cpt_codes: List[str]
    cpt_descriptions: List[str]
    icd_codes: List[str]
    icd_descriptions: List[str]
    amount: float
    status: str
    priority: str  # "Normal", "Urgent", "STAT"
    chart_signed_date: datetime
    submission_date: Optional[datetime] = None
    payment_date: Optional[datetime] = None
    denial_date: Optional[datetime] = None
    denial_reason: Optional[str] = None
    denial_code: Optional[str] = None
    denial_category: Optional[str] = None
    insurance_payer: str = "Blue Cross"
    policy_number: str = ""
    group_number: str = ""
    authorization_number: str = ""
    referral_number: str = ""
    needs_assignment: bool = False
    appeal_status: Optional[str] = None
    appeal_date: Optional[datetime] = None
    appeal_deadline: Optional[datetime] = None
    risk_score: float = 0.0
    resubmission_count: int = 0
    claim_history: List[ClaimHistory] = None
    provider_notes: str = ""
    billing_notes: str = ""
    expected_payment: float = 0.0
    actual_payment: float = 0.0
    adjustment_amount: float = 0.0
    patient_responsibility: float = 0.0
    copay_amount: float = 0.0
    deductible_amount: float = 0.0
    days_in_ar: int = 0
    follow_up_date: Optional[datetime] = None
    last_worked_date: Optional[datetime] = None
    assigned_to: str = ""
    
    def __post_init__(self):
        if self.claim_history is None:
            self.claim_history = []
        if self.expected_payment == 0.0:
            self.expected_payment = self.amount * random.uniform(0.75, 0.95)
        if self.patient_responsibility == 0.0:
            self.patient_responsibility = self.amount * random.uniform(0.05, 0.25)

class EnhancedDataStore:
    """Enhanced data storage with comprehensive claim tracking"""
    
    def __init__(self):
        self.encounters = []
        self.patients = []
        self.doctor_assignments = {}
        self._initialize_comprehensive_data()
    
    def _initialize_comprehensive_data(self):
        """Create comprehensive sample data with detailed tracking"""
        
        # Sample data
        doctors = [
            {"name": "Dr. Sarah Johnson", "npi": "1234567890", "specialty": "Internal Medicine"},
            {"name": "Dr. Michael Chen", "npi": "2345678901", "specialty": "Cardiology"},
            {"name": "Dr. Emily Rodriguez", "npi": "3456789012", "specialty": "Emergency Medicine"},
            {"name": "Dr. David Smith", "npi": "4567890123", "specialty": "Family Medicine"},
            {"name": "Dr. Lisa Williams", "npi": "5678901234", "specialty": "Orthopedics"},
            {"name": "Dr. Robert Davis", "npi": "6789012345", "specialty": "Dermatology"}
        ]
        
        facilities = [
            {"name": "Metro General Hospital", "tax_id": "12-3456789"},
            {"name": "Sunrise Medical Center", "tax_id": "23-4567890"},
            {"name": "Valley Health Clinic", "tax_id": "34-5678901"}
        ]
        
        payers = [
            "Aetna", "Blue Cross Blue Shield", "Cigna", "United Healthcare", 
            "Medicare", "Medicaid", "Humana", "Anthem"
        ]
        
        # CPT codes and descriptions
        cpt_codes = {
            "99213": "Office visit, established patient, moderate complexity",
            "99214": "Office visit, established patient, moderate to high complexity",
            "99215": "Office visit, established patient, high complexity",
            "99232": "Hospital visit, subsequent care",
            "99233": "Hospital visit, subsequent care, high complexity",
            "99291": "Critical care, first 30-74 minutes",
            "99292": "Critical care, each additional 30 minutes",
            "93000": "Electrocardiogram, routine",
            "80053": "Comprehensive metabolic panel",
            "85025": "Complete blood count with differential"
        }
        
        # ICD-10 codes and descriptions
        icd_codes = {
            "Z00.00": "Encounter for general adult medical examination",
            "I10": "Essential hypertension", 
            "E78.5": "Hyperlipidemia",
            "K21.9": "Gastroesophageal reflux disease",
            "M79.3": "Panniculitis, unspecified",
            "R50.9": "Fever, unspecified",
            "J44.1": "Chronic obstructive pulmonary disease with acute exacerbation",
            "N18.6": "End stage renal disease",
            "F32.9": "Major depressive disorder, single episode, unspecified"
        }
        
        # Denial reasons with codes and categories
        denial_reasons = {
            "16": {"reason": "Claim/service lacks information or has submission/billing error", "category": "Information"},
            "18": {"reason": "Duplicate claim/service", "category": "Duplicate"},
            "27": {"reason": "Expenses incurred after coverage terminated", "category": "Eligibility"},
            "50": {"reason": "These are non-covered services", "category": "Coverage"},
            "96": {"reason": "Non-covered charges", "category": "Coverage"},
            "109": {"reason": "Claim not covered by this payer/contractor", "category": "Coverage"},
            "197": {"reason": "Precertification/authorization/notification absent", "category": "Authorization"},
            "204": {"reason": "This service/equipment/drug is not covered under the patient's current benefit plan", "category": "Coverage"}
        }
        
        # Generate enhanced encounters
        now = datetime.now()
        
        for i in range(1, 51):  # Create 50 comprehensive encounters
            doctor = random.choice(doctors)
            facility = random.choice(facilities)
            payer = random.choice(payers)
            
            # Generate patient data
            patient_names = [
                "John Smith", "Mary Johnson", "Robert Williams", "Patricia Brown",
                "Michael Jones", "Linda Davis", "William Miller", "Elizabeth Wilson",
                "David Moore", "Jennifer Taylor", "Richard Anderson", "Maria Thomas",
                "Charles Jackson", "Susan White", "Joseph Harris", "Lisa Martin"
            ]
            
            patient_name = random.choice(patient_names)
            service_date = now - timedelta(days=random.randint(1, 90))
            
            # Determine claim status and history
            status_options = ["Pending Submission", "Submitted to Insurance", "Pending Payment", "Paid", "Denied", "Under Appeal"]
            status = random.choice(status_options)
            
            # Generate CPT and ICD codes
            selected_cpts = random.sample(list(cpt_codes.keys()), random.randint(1, 3))
            selected_icds = random.sample(list(icd_codes.keys()), random.randint(1, 2))
            
            amount = sum(random.uniform(50, 500) for _ in selected_cpts)
            
            # Create detailed encounter
            enc = EnhancedEncounter(
                id=i,
                patient_id=((i - 1) % 16) + 1,  # 16 unique patients
                patient_name=patient_name,
                patient_mrn=f"MRN{100000 + ((i - 1) % 16) + 1}",
                patient_dob=(now - timedelta(days=random.randint(18*365, 80*365))).strftime("%Y-%m-%d"),
                patient_phone=f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}",
                patient_address=f"{random.randint(100,9999)} {random.choice(['Main', 'Oak', 'Elm', 'Park'])} St",
                patient_insurance_id=f"{random.choice(['ABC', 'XYZ', 'DEF'])}{random.randint(100000000, 999999999)}",
                doctor=doctor["name"],
                doctor_npi=doctor["npi"],
                facility=facility["name"],
                facility_tax_id=facility["tax_id"],
                service_date=service_date,
                cpt_codes=selected_cpts,
                cpt_descriptions=[cpt_codes[code] for code in selected_cpts],
                icd_codes=selected_icds,
                icd_descriptions=[icd_codes[code] for code in selected_icds],
                amount=round(amount, 2),
                status=status,
                priority=random.choice(["Normal", "Urgent", "STAT"]) if status == "Denied" else "Normal",
                chart_signed_date=service_date + timedelta(days=random.randint(0, 3)),
                insurance_payer=payer,
                policy_number=f"POL{random.randint(10000000, 99999999)}",
                group_number=f"GRP{random.randint(1000, 9999)}",
                authorization_number=f"AUTH{random.randint(1000000, 9999999)}" if random.random() > 0.7 else "",
                referral_number=f"REF{random.randint(100000, 999999)}" if random.random() > 0.8 else "",
                risk_score=random.uniform(0.1, 0.9),
                provider_notes=random.choice([
                    "Patient reported chronic pain, prescribed medication",
                    "Follow-up visit for ongoing condition",
                    "Routine preventive care visit",
                    "Acute condition requiring immediate attention",
                    "Consultation for second opinion"
                ]),
                assigned_to=random.choice(["Billing Specialist A", "Billing Specialist B", "Manager"])
            )
            
            # Set dates based on status
            if status in ["Submitted to Insurance", "Pending Payment", "Paid", "Denied", "Under Appeal"]:
                enc.submission_date = enc.chart_signed_date + timedelta(days=random.randint(1, 5))
                
            if status == "Paid":
                enc.payment_date = enc.submission_date + timedelta(days=random.randint(10, 45))
                enc.actual_payment = enc.expected_payment * random.uniform(0.85, 1.0)
                
            elif status == "Denied":
                enc.denial_date = enc.submission_date + timedelta(days=random.randint(5, 30))
                denial_code = random.choice(list(denial_reasons.keys()))
                enc.denial_code = denial_code
                enc.denial_reason = denial_reasons[denial_code]["reason"]
                enc.denial_category = denial_reasons[denial_code]["category"]
                enc.resubmission_count = random.randint(0, 3)
                
                # Add claim history for denied claims
                if enc.resubmission_count > 0:
                    for sub_num in range(1, enc.resubmission_count + 1):
                        history = ClaimHistory(
                            submission_number=sub_num,
                            submission_date=enc.submission_date + timedelta(days=sub_num * 14),
                            status="Denied" if sub_num < enc.resubmission_count else "Under Review",
                            response_date=enc.submission_date + timedelta(days=sub_num * 14 + 7),
                            denial_reason=random.choice(list(denial_reasons.values()))["reason"],
                            notes=f"Resubmission #{sub_num} - Updated coding/documentation"
                        )
                        enc.claim_history.append(history)
                
                if random.random() > 0.6:  # 40% of denied claims under appeal
                    enc.appeal_status = "Under Appeal"
                    enc.appeal_date = enc.denial_date + timedelta(days=random.randint(5, 15))
                    enc.appeal_deadline = enc.denial_date + timedelta(days=60)
            
            # Calculate AR days
            if enc.submission_date and not enc.payment_date:
                enc.days_in_ar = (now - enc.submission_date).days
                
            # Set follow-up dates
            if status in ["Denied", "Under Appeal"]:
                enc.follow_up_date = now + timedelta(days=random.randint(1, 14))
                enc.last_worked_date = now - timedelta(days=random.randint(1, 7))
            
            self.encounters.append(enc)
    
    def get_denial_analytics(self):
        """Get comprehensive denial analytics"""
        denied_claims = [e for e in self.encounters if e.status == "Denied"]
        
        # Denial by category
        category_breakdown = {}
        for claim in denied_claims:
            category = claim.denial_category or "Unknown"
            category_breakdown[category] = category_breakdown.get(category, 0) + 1
        
        # Denial by doctor
        doctor_breakdown = {}
        for claim in denied_claims:
            doctor_breakdown[claim.doctor] = doctor_breakdown.get(claim.doctor, 0) + 1
        
        # Denial by payer
        payer_breakdown = {}
        for claim in denied_claims:
            payer_breakdown[claim.insurance_payer] = payer_breakdown.get(claim.insurance_payer, 0) + 1
        
        # Resubmission success rate
        total_resubmissions = sum(e.resubmission_count for e in denied_claims)
        successful_resubmissions = len([e for e in self.encounters if e.resubmission_count > 0 and e.status == "Paid"])
        
        return {
            "total_denials": len(denied_claims),
            "denial_rate": (len(denied_claims) / len(self.encounters) * 100) if self.encounters else 0,
            "category_breakdown": category_breakdown,
            "doctor_breakdown": doctor_breakdown,
            "payer_breakdown": payer_breakdown,
            "total_resubmissions": total_resubmissions,
            "successful_resubmissions": successful_resubmissions,
            "resubmission_success_rate": (successful_resubmissions / total_resubmissions * 100) if total_resubmissions > 0 else 0,
            "appeals_pending": len([e for e in denied_claims if e.appeal_status == "Under Appeal"]),
            "high_priority_denials": len([e for e in denied_claims if e.priority in ["Urgent", "STAT"]])
        }

# Global enhanced data store
enhanced_data_store = EnhancedDataStore()