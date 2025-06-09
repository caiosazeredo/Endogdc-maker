# test_agents.py - Teste Individual dos Agentes
"""
Script para testar individualmente os agentes do sistema multiagentes.
Útil para desenvolvimento e debugging.

Uso: python test_agents.py
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from services.multiagent_service import MultiAgentService
from services.groq_service import GroqService
from services.gemini_service import GeminiService

def test_individual_services():
    """Testa serviços individualmente"""
    print("🧪 TESTE INDIVIDUAL DOS SERVIÇOS DE IA")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        # Teste Groq
        print("\n🤖 Testando Groq...")
        groq_service = GroqService()
        groq_result = groq_service.generate_response(
            "Olá! Você está funcionando?", 
            'test'
        )
        
        if groq_result['success']:
            print(f"   ✓ Groq OK: {groq_result['content'][:50]}...")
        else:
            print(f"   ✗ Groq ERRO: {groq_result['error']}")
        
        # Teste Gemini
        print("\n🧠 Testando Gemini...")
        gemini_service = GeminiService()
        gemini_result = gemini_service.generate_response(
            "Olá! Você está funcionando?", 
            'test'
        )
        
        if gemini_result['success']:
            print(f"   ✓ Gemini OK: {gemini_result['content'][:50]}...")
        else:
            print(f"   ✗ Gemini ERRO: {gemini_result['error']}")

def test_multiagent_system():
    """Testa sistema multiagentes"""
    print("\n👥 TESTE DO SISTEMA MULTIAGENTES")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        multiagent = MultiAgentService()
        
        # Teste com pergunta simples
        test_message = "Como criar um jogo educativo sobre matemática para crianças?"
        
        print(f"\nPergunta de teste: {test_message}")
        print("\nRespostas dos agentes:")
        print("-" * 30)
        
        try:
            # Simular sessão (sem banco para teste)
            result = multiagent.start_multiagent_discussion(
                session_id=None, 
                user_message=test_message
            )
            
            for response in result['agents_responses']:
                agent_name = response['agent']['name']
                agent_emoji = response['agent']['emoji']
                content = response['response'][:100] + "..."
                
                print(f"{agent_emoji} {agent_name}:")
                print(f"   {content}")
                print()
            
            print("🎯 Síntese do Coordenador:")
            print(f"   {result['synthesis'][:100]}...")
            
            if result['suggestions']['suggestions']:
                print(f"\n💡 {len(result['suggestions']['suggestions'])} sugestões geradas")
            
        except Exception as e:
            print(f"❌ Erro no sistema multiagentes: {e}")

def test_specific_agent():
    """Testa agente específico"""
    print("\n🎯 TESTE DE AGENTE ESPECÍFICO")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        multiagent = MultiAgentService()
        
        # Testar agente de narrativa (Gemini)
        agent = multiagent.agents['narrative']
        print(f"\nTestando: {agent['emoji']} {agent['name']}")
        print(f"Serviço: {agent['service'].upper()}")
        
        context = """
IDEIAS DO BRAINSTORMING:
- Jogo de matemática para crianças
- Aventura em mundo mágico
- Resolver problemas com números

REFLEXÃO SOCRÁTICA:
Problema: Crianças têm dificuldade com matemática básica
Motivação: Tornar matemática divertida e envolvente
"""
        
        response = multiagent._get_agent_response(
            'narrative', 
            agent, 
            context, 
            "Como criar uma narrativa envolvente para este jogo?", 
            {}
        )
        
        print(f"\nResposta:")
        print(f"   {response[:200]}...")

def interactive_test():
    """Teste interativo com input do usuário"""
    print("\n💬 TESTE INTERATIVO")
    print("=" * 50)
    print("Digite 'sair' para encerrar")
    
    app = create_app()
    
    with app.app_context():
        multiagent = MultiAgentService()
        
        while True:
            user_input = input("\n🤔 Sua pergunta para os agentes: ").strip()
            
            if user_input.lower() in ['sair', 'exit', 'quit', '']:
                break
            
            try:
                result = multiagent.start_multiagent_discussion(
                    session_id=None,
                    user_message=user_input
                )
                
                print(f"\n{'='*20} RESPOSTAS {'='*20}")
                
                for response in result['agents_responses']:
                    agent = response['agent']
                    content = response['response']
                    
                    print(f"\n{agent['emoji']} {agent['name']}:")
                    print(f"{content}")
                
                print(f"\n🎯 SÍNTESE:")
                print(f"{result['synthesis']}")
                
            except Exception as e:
                print(f"❌ Erro: {e}")

def main():
    """Menu principal"""
    print("🧪 SISTEMA DE TESTE DOS AGENTES MULTIAGENTES")
    print("=" * 50)
    print("Escolha uma opção:")
    print("1. Testar serviços individuais (Groq/Gemini)")
    print("2. Testar sistema multiagentes")
    print("3. Testar agente específico")
    print("4. Teste interativo")
    print("5. Executar todos os testes")
    
    choice = input("\nOpção (1-5): ").strip()
    
    if choice == '1':
        test_individual_services()
    elif choice == '2':
        test_multiagent_system()
    elif choice == '3':
        test_specific_agent()
    elif choice == '4':
        interactive_test()
    elif choice == '5':
        test_individual_services()
        test_multiagent_system()
        test_specific_agent()
    else:
        print("Opção inválida!")
        return
    
    print("\n" + "=" * 50)
    print("✅ Testes concluídos!")

if __name__ == '__main__':
    main()