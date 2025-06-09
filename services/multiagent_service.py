# services/multiagent_service.py - Serviço Multiagentes
import json
import random
from services.groq_service import GroqService
from services.gemini_service import GeminiService
from models import Card, SocraticSessionAnswers, BloomObjective, GdcNote

class MultiAgentService:
    def __init__(self):
        self.groq_service = GroqService()
        self.gemini_service = GeminiService()
        
        # Definição dos agentes especializados
        self.agents = {
            'coordinator': {
                'name': 'Agente Coordenador',
                'description': 'Coordena a discussão entre agentes e sintetiza propostas',
                'service': 'groq',
                'emoji': '🎯'
            },
            'narrative': {
                'name': 'Especialista em Narrativa',
                'description': 'Especializado em storytelling e design narrativo',
                'service': 'gemini',
                'emoji': '📖'
            },
            'mechanics': {
                'name': 'Especialista em Mecânicas',
                'description': 'Foca em mecânicas de jogo e sistemas de feedback',
                'service': 'groq',
                'emoji': '⚙️'
            },
            'pedagogy': {
                'name': 'Especialista Pedagógico',
                'description': 'Especializado em design instrucional e pedagogia',
                'service': 'gemini',
                'emoji': '👨‍🎓'
            },
            'engagement': {
                'name': 'Especialista em Engajamento',
                'description': 'Foca em motivação e elementos de engajamento',
                'service': 'groq',
                'emoji': '🎮'
            },
            'technology': {
                'name': 'Especialista Técnico',
                'description': 'Avalia viabilidade técnica e recursos necessários',
                'service': 'gemini',
                'emoji': '💻'
            }
        }
    
    def get_session_context(self, session_id):
        """Coleta o contexto completo da sessão"""
        context = {
            'ideas': [],
            'socratic_answers': None,
            'objectives': [],
            'current_canvas': {}
        }
        
        # Buscar ideias do brainstorming
        cards = Card.query.filter_by(session_id=session_id).all()
        context['ideas'] = [card.text for card in cards]
        
        # Buscar respostas socráticas
        socratic = SocraticSessionAnswers.query.filter_by(session_id=session_id).first()
        if socratic:
            context['socratic_answers'] = {
                'problem': socratic.problem,
                'justification': socratic.justification,
                'impact': socratic.impact,
                'motivation': socratic.motivation
            }
        
        # Buscar objetivos de Bloom
        objectives = BloomObjective.query.filter_by(session_id=session_id).all()
        context['objectives'] = [{'text': obj.text, 'level': obj.level} for obj in objectives]
        
        # Buscar notas do canvas atual
        notes = GdcNote.query.filter_by(session_id=session_id).all()
        for note in notes:
            section_name = note.section.name
            if section_name not in context['current_canvas']:
                context['current_canvas'][section_name] = []
            context['current_canvas'][section_name].append(note.text)
        
        return context
    
    def start_multiagent_discussion(self, session_id, user_message, focus_section=None):
        """Inicia uma discussão multiagentes sobre o design do jogo"""
        context = self.get_session_context(session_id)
        
        # Prompt base com contexto
        base_context = self._build_base_context(context)
        
        # Selecionar agentes relevantes baseado na seção ou mensagem
        relevant_agents = self._select_relevant_agents(user_message, focus_section)
        
        # Coordenar discussão entre agentes
        discussion_results = []
        
        for agent_id in relevant_agents:
            agent = self.agents[agent_id]
            agent_response = self._get_agent_response(
                agent_id, agent, base_context, user_message, context
            )
            discussion_results.append({
                'agent': agent,
                'response': agent_response
            })
        
        # Coordenador sintetiza as propostas
        synthesis = self._synthesize_proposals(discussion_results, context, user_message)
        
        return {
            'context': context,
            'agents_responses': discussion_results,
            'synthesis': synthesis,
            'suggestions': self._extract_actionable_suggestions(synthesis)
        }
    
    def _build_base_context(self, context):
        """Constrói o contexto base para os agentes"""
        context_parts = ["=== CONTEXTO DO PROJETO DE JOGO EDUCATIVO ==="]
        
        if context['ideas']:
            context_parts.append(f"\nIDEIAS DO BRAINSTORMING:")
            for idea in context['ideas'][:5]:  # Limitar a 5 ideias
                context_parts.append(f"- {idea}")
        
        if context['socratic_answers']:
            sa = context['socratic_answers']
            context_parts.append(f"\nREFLEXÃO SOCRÁTICA:")
            context_parts.append(f"Problema: {sa['problem']}")
            context_parts.append(f"Motivação: {sa['motivation']}")
        
        if context['objectives']:
            context_parts.append(f"\nOBJETIVOS EDUCACIONAIS:")
            for obj in context['objectives'][:3]:  # Limitar a 3 objetivos
                context_parts.append(f"- {obj['text']} ({obj['level']})")
        
        if context['current_canvas']:
            context_parts.append(f"\nCANVAS ATUAL:")
            for section, notes in context['current_canvas'].items():
                if notes:
                    context_parts.append(f"{section}: {', '.join(notes[:2])}")
        
        return '\n'.join(context_parts)
    
    def _select_relevant_agents(self, user_message, focus_section):
        """Seleciona agentes relevantes baseado na mensagem e seção"""
        # Sempre incluir o coordenador
        selected = ['coordinator']
        
        # Adicionar agentes baseado no foco ou palavras-chave
        keywords_agents = {
            'narrativa': ['narrative'],
            'história': ['narrative'],
            'personagem': ['narrative'],
            'mecânica': ['mechanics'],
            'regras': ['mechanics'],
            'sistema': ['mechanics'],
            'aprendizado': ['pedagogy'],
            'educacional': ['pedagogy'],
            'pedagogia': ['pedagogy'],
            'motivação': ['engagement'],
            'engajamento': ['engagement'],
            'diversão': ['engagement'],
            'tecnologia': ['technology'],
            'implementação': ['technology'],
            'recursos': ['technology']
        }
        
        message_lower = user_message.lower()
        for keyword, agents in keywords_agents.items():
            if keyword in message_lower:
                selected.extend(agents)
        
        # Se seção específica mencionada
        if focus_section:
            section_agents = {
                'Narrativa': ['narrative'],
                'Mecânicas de Jogo': ['mechanics'],
                'Objetivos de Aprendizagem': ['pedagogy'],
                'Motivação e Engajamento': ['engagement'],
                'Tecnologia': ['technology']
            }
            if focus_section in section_agents:
                selected.extend(section_agents[focus_section])
        
        # Se nenhum agente específico, adicionar alguns aleatórios
        if len(selected) == 1:  # Apenas coordenador
            available_agents = list(self.agents.keys())
            available_agents.remove('coordinator')
            selected.extend(random.sample(available_agents, min(2, len(available_agents))))
        
        return list(set(selected))  # Remove duplicatas
    
    def _get_agent_response(self, agent_id, agent, base_context, user_message, context):
        """Obtém resposta de um agente específico"""
        # Prompts especializados por agente
        agent_prompts = {
            'coordinator': f"""Você é o Agente Coordenador de um sistema multiagentes para design de jogos educativos.
            
{base_context}

MENSAGEM DO USUÁRIO: {user_message}

Como coordenador, analise a situação e forneça diretrizes gerais para o design. Foque em:
- Coerência geral do projeto
- Prioridades de design
- Conectar elementos entre diferentes aspectos do jogo

Responda de forma concisa e estruturada.""",

            'narrative': f"""Você é o Especialista em Narrativa em um sistema de design de jogos educativos.
            
{base_context}

MENSAGEM DO USUÁRIO: {user_message}

Como especialista em narrativa, foque em:
- Storytelling e worldbuilding
- Desenvolvimento de personagens
- Progressão narrativa
- Conexão entre narrativa e objetivos educacionais

Forneça sugestões específicas para elementos narrativos.""",

            'mechanics': f"""Você é o Especialista em Mecânicas de Jogo em um sistema de design de jogos educativos.

{base_context}

MENSAGEM DO USUÁRIO: {user_message}

Como especialista em mecânicas, foque em:
- Sistemas de jogo e regras
- Loops de feedback
- Progressão e recompensas
- Mecânicas que reforçam o aprendizado

Forneça sugestões específicas para mecânicas de jogo.""",

            'pedagogy': f"""Você é o Especialista Pedagógico em um sistema de design de jogos educativos.

{base_context}

MENSAGEM DO USUÁRIO: {user_message}

Como especialista pedagógico, foque em:
- Alinhamento com objetivos educacionais
- Métodos de ensino eficazes
- Avaliação da aprendizagem
- Adaptação a diferentes estilos de aprendizagem

Forneça sugestões baseadas em princípios pedagógicos sólidos.""",

            'engagement': f"""Você é o Especialista em Engajamento em um sistema de design de jogos educativos.

{base_context}

MENSAGEM DO USUÁRIO: {user_message}

Como especialista em engajamento, foque em:
- Elementos motivacionais
- Flow e imersão
- Sistemas de recompensa
- Manutenção do interesse do jogador

Forneça sugestões para maximizar o engajamento dos estudantes.""",

            'technology': f"""Você é o Especialista Técnico em um sistema de design de jogos educativos.

{base_context}

MENSAGEM DO USUÁRIO: {user_message}

Como especialista técnico, foque em:
- Viabilidade técnica
- Recursos necessários
- Plataformas e tecnologias
- Considerações de implementação

Forneça sugestões práticas e viáveis tecnicamente."""
        }
        
        prompt = agent_prompts.get(agent_id, agent_prompts['coordinator'])
        
        # Usar o serviço apropriado para cada agente
        if agent['service'] == 'groq':
            result = self.groq_service.generate_response(prompt, 'multiagent')
        else:  # gemini
            result = self.gemini_service.generate_response(prompt, 'multiagent')
        
        if result['success']:
            return result['content']
        else:
            return f"Erro ao obter resposta: {result['error']}"
    
    def _synthesize_proposals(self, discussion_results, context, user_message):
        """Coordenador sintetiza as propostas dos agentes"""
        agents_responses = []
        for result in discussion_results:
            agent_name = result['agent']['name']
            response = result['response']
            agents_responses.append(f"{agent_name}: {response}")
        
        synthesis_prompt = f"""Como Agente Coordenador, sintetize as seguintes propostas dos agentes especialistas para criar sugestões coerentes e implementáveis:

PROPOSTAS DOS AGENTES:
{chr(10).join(agents_responses)}

CONTEXTO DA CONVERSA: {user_message}

Sintetize as propostas em sugestões específicas e práticas para o Endo-GDC. 
Organize por seções do canvas quando relevante.
Evite contradições entre as propostas.
Forneça justificativas baseadas nas diferentes perspectivas dos agentes."""
        
        result = self.groq_service.generate_response(synthesis_prompt, 'multiagent_synthesis')
        
        if result['success']:
            return result['content']
        else:
            return "Erro ao sintetizar propostas dos agentes."
    
    def _extract_actionable_suggestions(self, synthesis):
        """Extrai sugestões acionáveis da síntese"""
        extraction_prompt = f"""A partir da seguinte síntese de agentes especialistas, extraia sugestões específicas e acionáveis para o Game Design Canvas:

{synthesis}

Formate as sugestões como uma lista JSON com a seguinte estrutura:
{{
  "suggestions": [
    {{
      "section": "Nome da Seção do Canvas",
      "action": "add|modify|remove",
      "content": "Conteúdo específico da sugestão",
      "justification": "Justificativa para a sugestão"
    }}
  ]
}}

Foque em sugestões práticas que podem ser implementadas diretamente no canvas."""
        
        result = self.groq_service.generate_response(extraction_prompt, 'suggestion_extraction')
        
        if result['success']:
            try:
                # Tentar extrair JSON da resposta
                response_text = result['content'].strip()
                
                # Procurar por JSON na resposta
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_text = response_text[start_idx:end_idx]
                    return json.loads(json_text)
                else:
                    # Se não encontrar JSON válido, criar estrutura básica
                    return {
                        "suggestions": [
                            {
                                "section": "Geral",
                                "action": "add",
                                "content": synthesis[:200] + "...",
                                "justification": "Sugestão baseada na discussão dos agentes especialistas"
                            }
                        ]
                    }
            except:
                # Em caso de erro, retornar estrutura básica
                return {
                    "suggestions": [
                        {
                            "section": "Geral",
                            "action": "add", 
                            "content": synthesis[:200] + "...",
                            "justification": "Sugestão baseada na discussão dos agentes especialistas"
                        }
                    ]
                }
        else:
            return {"suggestions": []}