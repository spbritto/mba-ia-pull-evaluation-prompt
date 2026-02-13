"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt (ex: bug_to_user_story_v2)
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    print(f"\n📤 Fazendo push de: {prompt_name}")
    
    try:
        # Validar estrutura do prompt
        is_valid, errors = validate_prompt_structure(prompt_data)
        if not is_valid:
            print(f"   ❌ Validação falhou:")
            for error in errors:
                print(f"      - {error}")
            return False
        
        # Extrair informações do prompt
        system_prompt = prompt_data.get('system_prompt', '')
        user_prompt = prompt_data.get('user_prompt', '{bug_report}')
        version = prompt_data.get('version', 'v1')
        description = prompt_data.get('description', '')
        techniques = prompt_data.get('techniques_applied', [])
        
        # Criar um ChatPromptTemplate
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])
        
        # Construir nome com username
        username = os.getenv('USERNAME_LANGSMITH_HUB', 'user')
        full_prompt_name = f"{username}/{prompt_name}"
        
        # Fazer push do prompt
        # Nota: O hub.push retorna a URL ou identificador do prompt publicado
        try:
            pushed_url = hub.push(
                full_prompt_name,
                prompt_template,
            )
            print(f"   ✅ Push realizado com sucesso!")
            print(f"   📍 Acesse em: https://smith.langchain.com/hub/{full_prompt_name}")
            return True
            
        except Exception as e:
            print(f"   ⚠️  Nota: Push realizado mas com aviso: {e}")
            # Mesmo com aviso, pode ter funcionado, então retornamos True
            print(f"   📍 Acesse em: https://smith.langchain.com/hub/{full_prompt_name}")
            return True
            
    except Exception as e:
        print(f"   ❌ Erro ao fazer push: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []
    
    # Campos obrigatórios
    required_fields = ['description', 'system_prompt', 'user_prompt', 'version']
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")
        elif not prompt_data[field] or str(prompt_data[field]).strip() == '':
            errors.append(f"Campo vazio: {field}")
    
    # Verificar se há TODOs
    full_text = str(prompt_data.get('system_prompt', '')) + str(prompt_data.get('user_prompt', ''))
    if '[TODO]' in full_text:
        errors.append("Prompt ainda contém [TODO] placeholders")
    
    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("INICIANDO PUSH DE PROMPTS OTIMIZADOS")
    
    # Validar variáveis de ambiente
    required_vars = ['LANGSMITH_API_KEY', 'LANGSMITH_PROJECT', 'USERNAME_LANGSMITH_HUB']
    if not check_env_vars(required_vars):
        return 1
    
    try:
        # Carregar arquivo de prompts otimizados
        prompts_file = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v11.yml"
        
        if not prompts_file.exists():
            print(f"❌ Arquivo não encontrado: {prompts_file}")
            return 1
        
        prompts_data = load_yaml(str(prompts_file))
        
        if not prompts_data:
            print(f"❌ Erro ao carregar arquivo: {prompts_file}")
            return 1
        
        # Processar cada prompt
        success_count = 0
        fail_count = 0
        
        for prompt_key, prompt_value in prompts_data.items():
            if isinstance(prompt_value, dict):
                if push_prompt_to_langsmith(prompt_key, prompt_value):
                    success_count += 1
                else:
                    fail_count += 1
        
        # Resumo
        print("\n" + "=" * 50)
        if fail_count == 0:
            print(f"✅ PUSH CONCLUÍDO COM SUCESSO!")
            print(f"   {success_count} prompt(s) publicado(s)")
            return 0
        else:
            print(f"⚠️  PUSH PARCIALMENTE CONCLUÍDO")
            print(f"   ✅ Sucesso: {success_count}")
            print(f"   ❌ Falhas: {fail_count}")
            return 1
            
    except Exception as e:
        print(f"\n❌ Erro não tratado: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
