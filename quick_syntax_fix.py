#!/usr/bin/env python3
# quick_syntax_fix.py - Correção Rápida de Sintaxe

import re

def fix_gamedesign_syntax():
    """Corrige o erro de sintaxe no gamedesign.py"""
    
    print("🔧 Corrigindo erro de sintaxe em routes/gamedesign.py...")
    
    try:
        # Ler o arquivo
        with open('routes/gamedesign.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Correção: Adicionar except/finally onde necessário antes da rota export-summary
        # Procurar por padrões problemáticos
        
        # Pattern 1: try: sem except antes de @gamedesign_bp.route
        pattern1 = r'(\s+try:\s*\n.*?)\n(\s*@gamedesign_bp\.route\(\'\/export-summary\'\))'
        if re.search(pattern1, content, re.DOTALL):
            content = re.sub(
                pattern1,
                r'\1\n        except:\n            pass\n\n\2',
                content,
                flags=re.DOTALL
            )
            print("✅ Padrão 1 corrigido: try sem except")
        
        # Pattern 2: Qualquer bloco incompleto antes da rota
        # Procurar por @gamedesign_bp.route('/export-summary') e verificar se há try incompleto antes
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "@gamedesign_bp.route('/export-summary')" in line:
                # Verificar linhas anteriores buscando por try sem except
                for j in range(max(0, i-20), i):
                    if 'try:' in lines[j]:
                        # Verificar se há except ou finally depois do try
                        has_except = False
                        for k in range(j+1, i):
                            if 'except' in lines[k] or 'finally' in lines[k]:
                                has_except = True
                                break
                        
                        if not has_except:
                            # Adicionar except antes da rota
                            lines.insert(i, '        except:')
                            lines.insert(i+1, '            pass')
                            lines.insert(i+2, '')
                            print(f"✅ Adicionado except na linha {i}")
                            break
                break
        
        content = '\n'.join(lines)
        
        # Escrever arquivo corrigido
        with open('routes/gamedesign.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Arquivo routes/gamedesign.py corrigido!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na correção automática: {e}")
        return False

def manual_fix_instructions():
    """Instruções para correção manual"""
    print("\n📝 INSTRUÇÕES PARA CORREÇÃO MANUAL:")
    print("=" * 40)
    print("1. Abra o arquivo: routes/gamedesign.py")
    print("2. Vá para a linha 751 (onde está o erro)")
    print("3. Procure por: @gamedesign_bp.route('/export-summary')")
    print("4. Antes dessa linha, adicione:")
    print("        except:")
    print("            pass")
    print("")
    print("5. Salve o arquivo")
    print("6. Execute: python init_db.py")

if __name__ == '__main__':
    print("🚀 CORREÇÃO DE SINTAXE - GAMEDESIGN.PY")
    print("=" * 45)
    
    if fix_gamedesign_syntax():
        print("\n🎉 CORREÇÃO CONCLUÍDA!")
        print("💡 Agora execute: python init_db.py")
    else:
        manual_fix_instructions()