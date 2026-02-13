"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import load_yaml


@pytest.fixture
def prompt_data():
    """Carrega dados do prompt v2 para testes"""
    prompts_file = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
    
    if not prompts_file.exists():
        pytest.skip(f"Arquivo de prompt não encontrado: {prompts_file}")
    
    data = load_yaml(str(prompts_file))
    
    if not data or 'bug_to_user_story_v2' not in data:
        pytest.fail("Estrutura inválida do arquivo YAML")
    
    return data['bug_to_user_story_v2']


class TestPrompts:
    
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert 'system_prompt' in prompt_data, "Campo 'system_prompt' não encontrado"
        
        system_prompt = prompt_data.get('system_prompt', '').strip()
        assert system_prompt, "Campo 'system_prompt' está vazio"
        assert len(system_prompt) > 50, "system_prompt é muito curto (mínimo 50 caracteres)"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        system_prompt = prompt_data.get('system_prompt', '').lower()
        
        # Palavras-chave que indicam definição de persona
        persona_keywords = [
            'você é um',
            'seu papel',
            'sua responsabilidade',
            'especializado em',
            'product manager',
            'assistente',
            'avaliador'
        ]
        
        found_persona = any(keyword in system_prompt for keyword in persona_keywords)
        assert found_persona, "Persona não definida. System prompt deve começar com 'Você é um...'"

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato User Story padrão."""
        system_prompt = prompt_data.get('system_prompt', '')
        
        format_keywords = [
            'user story',
            'como ',
            'eu quero',
            'para que',
            'critérios de aceitação',
            'estrutura'
        ]
        
        system_prompt_lower = system_prompt.lower()
        found_format = any(keyword in system_prompt_lower for keyword in format_keywords)
        
        assert found_format, "Prompt deve especificar o formato esperado (User Story)"

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        assert 'examples' in prompt_data, "Campo 'examples' não encontrado (Few-shot Learning obrigatório)"
        
        examples = prompt_data.get('examples', [])
        assert len(examples) > 0, "Deve haver pelo menos 1 exemplo de Few-shot Learning"
        
        # Validar estrutura de cada exemplo
        for idx, example in enumerate(examples):
            assert 'input' in example, f"Exemplo {idx} sem campo 'input'"
            assert 'output' in example, f"Exemplo {idx} sem campo 'output'"
            assert example['input'].strip(), f"Exemplo {idx} tem input vazio"
            assert example['output'].strip(), f"Exemplo {idx} tem output vazio"

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        system_prompt = prompt_data.get('system_prompt', '')
        user_prompt = prompt_data.get('user_prompt', '')
        description = prompt_data.get('description', '')
        
        full_text = system_prompt + user_prompt + description
        
        forbidden_patterns = [
            '[TODO]',
            'TODO:',
            '[TBD]',
            'TBD:',
            '[FIXME]',
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in full_text, f"Encontrado placeholder incompleto: {pattern}"

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get('techniques_applied', [])
        
        assert isinstance(techniques, list), "techniques_applied deve ser uma lista"
        assert len(techniques) >= 2, f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
