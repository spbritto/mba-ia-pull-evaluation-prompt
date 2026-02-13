"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """
    Faz pull de prompts do LangSmith Prompt Hub.
    
    Pula os prompts e os salva localmente em YAML.
    """
    print_section_header("INICIANDO PULL DE PROMPTS DO LANGSMITH")
    
    # Validar variáveis de ambiente obrigatórias
    required_vars = ['LANGSMITH_API_KEY', 'LANGSMITH_PROJECT', 'USERNAME_LANGSMITH_HUB']
    if not check_env_vars(required_vars):
        return False
    
    try:
        username = os.getenv('USERNAME_LANGSMITH_HUB')
        
        # Lista de prompts para fazer pull (NOTA: não incluir extensões ou URLs)
        # O formato deve ser username/nome-do-prompt
        prompts_to_pull = [
            "bug_to_user_story_v1",  # Tenta puxar do usuário logado no LangSmith
        ]
        
        prompts_data = {}
        
        for prompt_name in prompts_to_pull:
            print(f"\n📥 Fazendo pull de: {prompt_name}")
            try:
                # Fazer pull do prompt do hub
                prompt = hub.pull(prompt_name)
                
                # Extrair dados do prompt
                prompt_dict = {
                    "name": prompt_name,
                    "description": f"Prompt puxado do LangSmith Hub: {prompt_name}",
                    "system_prompt": prompt.template if hasattr(prompt, 'template') else str(prompt),
                    "version": "v1",
                    "source": "langsmith_hub",
                    "pulled_at": __import__('datetime').datetime.now().isoformat()
                }
                
                prompts_data[prompt_name] = prompt_dict
                print(f"   ✅ Pull realizado com sucesso!")
                
            except Exception as e:
                print(f"   ❌ Erro ao fazer pull de {prompt_name}: {e}")
                return False
        
        # Salvar prompts localmente
        output_file = Path(__file__).parent.parent / "prompts" / "raw_prompts.yml"
        print(f"\n💾 Salvando prompts em: {output_file}")
        
        if save_yaml(prompts_data, str(output_file)):
            print("   ✅ Arquivo salvo com sucesso!")
            return True
        else:
            print("   ❌ Erro ao salvar arquivo")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro durante pull de prompts: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Função principal"""
    try:
        success = pull_prompts_from_langsmith()
        
        if success:
            print("\n" + "=" * 50)
            print("✅ PULL DE PROMPTS CONCLUÍDO COM SUCESSO!")
            print("=" * 50)
            return 0
        else:
            print("\n" + "=" * 50)
            print("❌ FALHA NO PULL DE PROMPTS")
            print("=" * 50)
            return 1
            
    except Exception as e:
        print(f"\n❌ Erro não tratado: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
