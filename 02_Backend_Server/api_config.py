"""
API Configuration System for External Data Integration
=====================================================
Manages API credentials, connections, and data adapters for real-time data
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APICredentials:
    """Store API credentials securely"""
    name: str
    base_url: str
    api_key: str
    auth_type: str  # 'bearer', 'basic', 'api_key', 'oauth'
    additional_headers: Optional[Dict[str, str]] = None
    auth_endpoint: Optional[str] = None
    
class APIConfigManager:
    """Manage multiple API configurations"""
    
    def __init__(self, config_file: str = "api_config.json"):
        self.config_file = config_file
        self.apis: Dict[str, APICredentials] = {}
        self.load_config()
    
    def load_config(self):
        """Load API configurations from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    
                for api_name, config in config_data.items():
                    self.apis[api_name] = APICredentials(
                        name=config['name'],
                        base_url=config['base_url'],
                        api_key=config['api_key'],
                        auth_type=config['auth_type'],
                        additional_headers=config.get('additional_headers'),
                        auth_endpoint=config.get('auth_endpoint')
                    )
                logger.info(f"Loaded {len(self.apis)} API configurations")
        except Exception as e:
            logger.error(f"Error loading API config: {e}")
    
    def save_config(self):
        """Save API configurations to file"""
        try:
            config_data = {}
            for api_name, creds in self.apis.items():
                config_data[api_name] = {
                    'name': creds.name,
                    'base_url': creds.base_url,
                    'api_key': creds.api_key,
                    'auth_type': creds.auth_type,
                    'additional_headers': creds.additional_headers,
                    'auth_endpoint': creds.auth_endpoint
                }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            logger.info("API configuration saved")
        except Exception as e:
            logger.error(f"Error saving API config: {e}")
    
    def add_api(self, credentials: APICredentials):
        """Add new API configuration"""
        self.apis[credentials.name] = credentials
        self.save_config()
        logger.info(f"Added API configuration for {credentials.name}")
    
    def get_api(self, name: str) -> Optional[APICredentials]:
        """Get API credentials by name"""
        return self.apis.get(name)
    
    def list_apis(self) -> List[str]:
        """List all configured APIs"""
        return list(self.apis.keys())

class ExternalAPIAdapter:
    """Adapter for connecting to external APIs"""
    
    def __init__(self, config_manager: APIConfigManager):
        self.config_manager = config_manager
        self.session_cache = {}  # Cache authenticated sessions
    
    def get_headers(self, credentials: APICredentials) -> Dict[str, str]:
        """Build request headers for API"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'MedicalBillingDashboard/1.0'
        }
        
        # Add authentication headers
        if credentials.auth_type == 'bearer':
            headers['Authorization'] = f'Bearer {credentials.api_key}'
        elif credentials.auth_type == 'api_key':
            headers['X-API-Key'] = credentials.api_key
        elif credentials.auth_type == 'basic':
            import base64
            auth_string = base64.b64encode(credentials.api_key.encode()).decode()
            headers['Authorization'] = f'Basic {auth_string}'
        
        # Add additional headers
        if credentials.additional_headers:
            headers.update(credentials.additional_headers)
        
        return headers
    
    async def test_connection(self, api_name: str) -> Dict[str, Any]:
        """Test connection to external API"""
        credentials = self.config_manager.get_api(api_name)
        if not credentials:
            return {'success': False, 'error': f'API {api_name} not configured'}
        
        try:
            headers = self.get_headers(credentials)
            
            # Try a simple GET request to the base URL
            response = requests.get(
                credentials.base_url,
                headers=headers,
                timeout=10
            )
            
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'api_name': api_name
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'api_name': api_name
            }
    
    async def fetch_data(self, api_name: str, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Fetch data from external API"""
        credentials = self.config_manager.get_api(api_name)
        if not credentials:
            return {'error': f'API {api_name} not configured'}
        
        try:
            headers = self.get_headers(credentials)
            url = f"{credentials.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json(),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'status_code': response.status_code
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

class DataTransformer:
    """Transform external API data to dashboard format"""
    
    @staticmethod
    def transform_ingenious_med_data(raw_data: List[Dict]) -> List[Dict]:
        """Transform Ingenious Med API data to standard format"""
        transformed = []
        
        for record in raw_data:
            transformed_record = {
                'id': record.get('encounter_id', record.get('id')),
                'patient_name': record.get('patient_name', 'Unknown'),
                'doctor': record.get('provider_name', record.get('physician')),
                'amount': float(record.get('charge_amount', record.get('amount', 0))),
                'status': record.get('status', 'Unknown'),
                'chart_signed_date': record.get('chart_signed_date', record.get('service_date')),
                'insurance_payer': record.get('insurance', record.get('payer', 'Unknown')),
                'denial_reason': record.get('denial_reason'),
                'external_id': record.get('encounter_id', record.get('id'))
            }
            transformed.append(transformed_record)
        
        return transformed
    
    @staticmethod
    def transform_advancedmd_data(raw_data: List[Dict]) -> List[Dict]:
        """Transform AdvancedMD API data to standard format"""
        transformed = []
        
        for record in raw_data:
            transformed_record = {
                'id': record.get('claim_id', record.get('id')),
                'patient_name': record.get('patient_name', 'Unknown'),
                'doctor': record.get('rendering_provider', record.get('provider')),
                'amount': float(record.get('billed_amount', record.get('charge', 0))),
                'status': record.get('claim_status', 'Unknown'),
                'submission_date': record.get('date_submitted'),
                'payment_date': record.get('payment_date'),
                'insurance_payer': record.get('payer_name', 'Unknown'),
                'denial_reason': record.get('rejection_reason'),
                'external_id': record.get('claim_id', record.get('id'))
            }
            transformed.append(transformed_record)
        
        return transformed
    
    @staticmethod
    def calculate_kpis_from_external_data(data: List[Dict]) -> Dict[str, Any]:
        """Calculate KPIs from transformed external data"""
        if not data:
            return {}
        
        total_claims = len(data)
        denied_claims = len([d for d in data if 'denied' in str(d.get('status', '')).lower()])
        paid_claims = len([d for d in data if 'paid' in str(d.get('status', '')).lower()])
        
        denial_rate = (denied_claims / total_claims * 100) if total_claims > 0 else 0
        clean_claim_rate = (paid_claims / total_claims * 100) if total_claims > 0 else 0
        
        total_amount = sum(d.get('amount', 0) for d in data)
        avg_amount = total_amount / total_claims if total_claims > 0 else 0
        
        return {
            'total_claims': total_claims,
            'denied_claims': denied_claims,
            'paid_claims': paid_claims,
            'denial_rate': round(denial_rate, 2),
            'clean_claim_rate': round(clean_claim_rate, 2),
            'total_amount': round(total_amount, 2),
            'average_amount': round(avg_amount, 2),
            'last_updated': datetime.now().isoformat()
        }

# Global instances
api_config_manager = APIConfigManager()
api_adapter = ExternalAPIAdapter(api_config_manager)
data_transformer = DataTransformer()

# Predefined API templates for common healthcare systems
HEALTHCARE_API_TEMPLATES = {
    'ingenious_med': {
        'name': 'Ingenious Med',
        'base_url': 'https://api.ingeniousmed.com/v1',
        'auth_type': 'bearer',
        'endpoints': {
            'encounters': '/encounters',
            'providers': '/providers',
            'patients': '/patients'
        }
    },
    'advancedmd': {
        'name': 'AdvancedMD',
        'base_url': 'https://api.advancedmd.com/v1',
        'auth_type': 'api_key',
        'endpoints': {
            'claims': '/claims',
            'payments': '/payments',
            'denials': '/denials'
        }
    },
    'epic': {
        'name': 'Epic FHIR',
        'base_url': 'https://fhir.epic.com/interconnect-fhir-oauth',
        'auth_type': 'oauth',
        'endpoints': {
            'encounters': '/api/FHIR/R4/Encounter',
            'claims': '/api/FHIR/R4/Claim'
        }
    },
    'cerner': {
        'name': 'Cerner FHIR',
        'base_url': 'https://fhir-open.cerner.com/r4',
        'auth_type': 'oauth',
        'endpoints': {
            'encounters': '/Encounter',
            'claims': '/Claim'
        }
    }
}