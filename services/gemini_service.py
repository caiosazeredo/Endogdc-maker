# services/gemini_service.py - Serviço de Integração com Gemini
import requests
import json
import time
from flask import current_app
from models import GroqResponse, db

class GeminiService:
    def __init__(self):
        self.api_key = current_app.config.get('GEMINI_API_KEY')
        self.model = current_app.config.get('GEMINI_MODEL', 'gemini-2.0-flash')
        self.base_url = f'https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent'
    
    def generate_response(self, prompt, module_type='general', session_id=None, max_tokens=1000):
        """
        Gera resposta usando o modelo Gemini
        """
        try:
            url = f"{self.base_url}?key={self.api_key}"
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": 0.7
                }
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            start_time = time.time()
            response = requests.post(url, headers=headers, json=payload)
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                response_data = response.json()
                content = response_data['candidates'][0]['content']['parts'][0]['text']
                tokens_used = response_data.get('usageMetadata', {}).get('totalTokenCount', 0)
                
                # Salvar no banco de dados
                groq_response = GroqResponse(
                    session_id=session_id,
                    prompt=prompt,
                    response=content,
                    model_used=self.model,
                    tokens_used=tokens_used,
                    response_time_ms=response_time_ms,
                    module_type=module_type
                )
                db.session.add(groq_response)
                db.session.commit()
                
                return {
                    'success': True,
                    'content': content,
                    'tokens_used': tokens_used,
                    'response_time_ms': response_time_ms
                }
            else:
                return {
                    'success': False,
                    'error': f'API Error: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Exception: {str(e)}'
            }   