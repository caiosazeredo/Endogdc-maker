# services/groq_service.py - Serviço de Integração com LLM
import requests
import json
import time
from flask import current_app
from models import GroqResponse, db

class GroqService:
    def __init__(self):
        self.api_key = current_app.config.get('GROQ_API_KEY')
        self.model = current_app.config.get('GROQ_MODEL', 'llama3-70b-8192')
        self.base_url = 'https://api.groq.com/openai/v1/chat/completions'
    
    def generate_response(self, prompt, module_type='general', session_id=None, max_tokens=1000):
        """
        Gera resposta usando o modelo Groq
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': max_tokens,
                'temperature': 0.7,
                'top_p': 1,
                'stream': False
            }
            
            start_time = time.time()
            response = requests.post(self.base_url, headers=headers, json=payload)
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                response_data = response.json()
                content = response_data['choices'][0]['message']['content']
                tokens_used = response_data.get('usage', {}).get('total_tokens', 0)
                
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
    
    def generate_brainstorm_suggestions(self, existing_cards, session_id=None):
        """
        Gera sugestões para brainstorming baseado nos cards existentes
        """
        if not existing_cards:
            prompt = """Como um especialista em design de jogos educativos, gere 3 ideias criativas e inovadoras para jogos educacionais. 
            Foque em diferentes tipos de jogos (digital, tabuleiro, RPG, etc.) e diferentes áreas educacionais.
            
            Responda apenas com as ideias, uma por linha, sem numeração."""
        else:
            cards_text = '\n'.join([f"- {card.text}" for card in existing_cards])
            prompt = f"""Como um especialista em design de jogos educativos, analise as seguintes ideias já geradas:

{cards_text}

Baseado nessas ideias existentes, gere 3 novas ideias que sejam:
1. Complementares às ideias existentes
2. Inovadoras e criativas
3. Focadas em diferentes aspectos educacionais

Responda apenas com as novas ideias, uma por linha, sem numeração."""
        
        return self.generate_response(prompt, 'brainstorm', session_id)
    
    def generate_socratic_suggestions(self, cards, session_id=None):
        """
        Gera sugestões para as questões socráticas baseado nos cards
        """
        cards_text = '\n'.join([f"- {card.text}" for card in cards])
        
        prompt = f"""Como um especialista em método socrático aplicado ao design de jogos educativos, analise as seguintes ideias:

{cards_text}

Gere sugestões para responder às seguintes questões socráticas:

1. PROBLEMA: Qual é o principal problema educacional que estas ideias tentam resolver?
2. JUSTIFICAÇÃO: Por que estas abordagens são adequadas para resolver o problema identificado?
3. IMPACTO: Qual seria o impacto educacional esperado na aprendizagem dos estudantes?
4. MOTIVAÇÃO: O que motivaria os estudantes a se engajarem com estes jogos?

Responda em formato JSON:
{{"problem": "...", "justification": "...", "impact": "...", "motivation": "..."}}"""
        
        return self.generate_response(prompt, 'socratic', session_id)
    
    def generate_bloom_objectives(self, socratic_answers, session_id=None):
        """
        Gera objetivos educacionais baseados na Taxonomia de Bloom
        """
        prompt = f"""Como um especialista em taxonomia de Bloom, analise o seguinte problema educacional e crie objetivos de aprendizagem:

Problema: {socratic_answers.problem}
Motivação: {socratic_answers.motivation}
Impacto: {socratic_answers.impact}

Crie 6 objetivos educacionais, um para cada nível da taxonomia de Bloom (Criar, Avaliar, Analisar, Aplicar, Compreender, Lembrar).
Os objetivos devem começar com um verbo no infinitivo.

Responda APENAS neste formato JSON, sem texto adicional:
{{"objectives":[{{"text":"[verbo] [resto do objetivo]","level":"[nível da taxonomia]"}},{{"text":"[verbo] [resto do objetivo]","level":"[nível da taxonomia]"}}]}}"""
        
        return self.generate_response(prompt, 'bloom', session_id)
    
    def generate_gamedesign_suggestions(self, context, section_name, session_id=None):
        """
        Gera sugestões para o Game Design Canvas
        """
        prompt = f"""Como um especialista em design de jogos educativos, gere sugestões para a seção "{section_name}" do Game Design Canvas.

Contexto do projeto:
{context}

Forneça 3-5 sugestões específicas e práticas para esta seção, considerando:
- Viabilidade técnica
- Eficácia educacional  
- Engajamento dos jogadores
- Recursos necessários

Responda apenas com as sugestões, uma por linha, sem numeração."""
        
        return self.generate_response(prompt, 'gamedesign', session_id)