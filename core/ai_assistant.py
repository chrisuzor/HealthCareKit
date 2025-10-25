"""
AI Assistant Module for Maxio Health System
Handles AI-powered health analysis using DEEPSEEK API
"""

import requests
import json
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_BASE, DEEPSEEK_MODEL

class AIHealthAssistant:
    def __init__(self):
        """Initialize the AI assistant with API configuration"""
        self.api_key = DEEPSEEK_API_KEY
        self.api_base = DEEPSEEK_API_BASE
        self.model = DEEPSEEK_MODEL
        
    def analyze_vitals_with_ai(self, vitals_data, user_concern):
        """Analyze vital signs with AI to provide enhanced health insights"""
        try:
            # Create a comprehensive prompt including vital data
            vital_summary = self._create_vital_summary(vitals_data, user_concern)
            
            # Prepare the API request
            api_response = self._make_ai_request(vital_summary)
            
            return api_response
            
        except requests.exceptions.RequestException as e:
            return f"Error: Unable to connect to AI service. {str(e)}"
        except Exception as e:
            return f"Error: Unable to analyze vitals. {str(e)}"
    
    def _create_vital_summary(self, vitals_data, user_concern):
        """Create a formatted summary of vital signs and user concern"""
        if vitals_data:
            return f"""
            Current Vital Signs:
            - Heart Rate: {vitals_data['heart_rate']} BPM
            - Blood Pressure: {vitals_data['blood_pressure_systolic']}/{vitals_data['blood_pressure_diastolic']} mmHg
            - Temperature: {vitals_data['temperature']}°C
            - Oxygen Saturation: {vitals_data['oxygen_saturation']}%
            - Respiratory Rate: {vitals_data['respiratory_rate']} breaths/min
            
            User Health Concern: {user_concern}
            """
        else:
            return f"""
            No vital signs data available. ESP32 sensor not connected.
            
            User Health Concern: {user_concern}
            
            Please provide general health advice based on the user's concern.
            """
    
    def _make_ai_request(self, vital_summary):
        """Make a request to the AI API"""
        # Set up the request headers
        headers = self._get_request_headers()
        
        # Prepare the request data
        request_data = self._prepare_request_data(vital_summary)
        
        # Make the API request
        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=request_data,
            timeout=30
        )
        
        # Process the response
        return self._process_api_response(response)
    
    def _get_request_headers(self):
        """Get the headers needed for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _prepare_request_data(self, vital_summary):
        """Prepare the data to send to the AI API"""
        return {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": """You are an advanced healthcare AI assistant. Analyze the provided vital signs 
                    along with the user's health concern to provide comprehensive health insights. 
                    Consider how the vital signs might relate to their symptoms and provide actionable advice. 
                    and try and suggest the infections or diseases that the user might be suffering from.
                    also suggest the medicines or actions that the user might need to take to cure the disease."""
                },
                {
                    "role": "user",
                    "content": vital_summary
                }
            ],
            "max_tokens": 300,
            "temperature": 0.7
        }
    
    def _process_api_response(self, response):
        """Process the API response and return the AI's answer"""
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            return f"Error: API request failed with status {response.status_code}"
    
    def get_health_insights(self, vitals_data):
        """Get general health insights based on vital signs"""
        try:
            # Create a summary of vital signs
            vital_summary = self._create_general_insight_summary(vitals_data)
            
            # Make the API request
            api_response = self._make_general_insight_request(vital_summary)
            
            return api_response
            
        except Exception as e:
            return f"Error generating insights: {str(e)}"
    
    def _create_general_insight_summary(self, vitals_data):
        """Create a summary for general health insights"""
        if vitals_data:
            return f"""
            Vital Signs Summary:
            - Heart Rate: {vitals_data['heart_rate']} BPM
            - Blood Pressure: {vitals_data['blood_pressure_systolic']}/{vitals_data['blood_pressure_diastolic']} mmHg
            - Temperature: {vitals_data['temperature']}°C
            - Oxygen Saturation: {vitals_data['oxygen_saturation']}%
            - Respiratory Rate: {vitals_data['respiratory_rate']} breaths/min
            
            Please provide a brief health assessment and general wellness recommendations.
            """
        else:
            return """
            No vital signs data available. ESP32 sensor not connected.
            
            Please provide general health and wellness recommendations.
            """
    
    def _make_general_insight_request(self, vital_summary):
        """Make a request for general health insights"""
        headers = self._get_request_headers()
        
        request_data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a healthcare AI assistant providing general health insights and wellness advice."
                },
                {
                    "role": "user",
                    "content": vital_summary
                }
            ],
            "max_tokens": 200,
            "temperature": 0.5
        }
        
        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=request_data,
            timeout=30
        )
        
        return self._process_api_response(response)
    
    def test_api_connection(self):
        """Test if the DEEPSEEK API connection is working"""
        try:
            # Prepare a simple test request
            headers = self._get_request_headers()
            
            test_data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, this is a test message."
                    }
                ],
                "max_tokens": 10
            }
            
            # Make the test request
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=test_data,
                timeout=10
            )
            
            # Return True if the request was successful
            return response.status_code == 200
            
        except Exception:
            return False 