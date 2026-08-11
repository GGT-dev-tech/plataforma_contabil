import yaml
import os
from datetime import date
from decimal import Decimal
from typing import Dict, Any, List

class LayoutParseError(Exception):
    pass

class YAMLLayoutBuilder:
    """
    Construtor dinâmico de arquivos SPED (TXT) baseado em layouts YAML.
    Substitui a necessidade de classes hardcoded para cada alteração do leiaute da Receita Federal.
    """
    
    def __init__(self, yaml_filename: str):
        self.layout_def = self._load_yaml(yaml_filename)
        
    def _load_yaml(self, filename: str) -> dict:
        # Resolve o caminho a partir deste arquivo (builders.py está em exportacao/)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        yaml_path = os.path.join(current_dir, 'layouts', filename)
        
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Layout YAML não encontrado: {yaml_path}")
            
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
            
    def gerar_linha(self, bloco: str, registro: str, dados: Dict[str, Any]) -> str:
        """
        Gera uma linha posicional do SPED baseada nas regras do YAML.
        
        Args:
            bloco: Ex 'I'
            registro: Ex 'I200'
            dados: Dicionário com chaves iguais ao `nome` definido no YAML.
        """
        try:
            reg_def = self.layout_def['blocos'][bloco][registro]
        except KeyError:
            raise LayoutParseError(f"Registro {registro} não encontrado no bloco {bloco} do layout.")
            
        campos_def = reg_def.get('campos', {})
        # O SPED usa pipe '|' no inicio e fim de cada campo
        linha_parts = [""]
        
        # Os campos no YAML devem estar ordenados por chave (1, 2, 3...)
        chaves_ordenadas = sorted(campos_def.keys(), key=lambda x: int(x))
        
        for ch in chaves_ordenadas:
            campo = campos_def[ch]
            nome = campo['nome']
            valor = dados.get(nome)
            
            # 1. Trata Fixo
            if 'fixo' in campo:
                linha_parts.append(str(campo['fixo']))
                continue
                
            # 2. Trata Obrigatório
            if campo.get('obrigatorio', False) and (valor is None or valor == ""):
                raise LayoutParseError(f"Campo obrigatório {nome} não informado no registro {registro}")
                
            if valor is None:
                linha_parts.append("")
                continue
                
            # 3. Formatações por Tipo
            tipo = campo.get('tipo', 'STR')
            
            if tipo == "STR":
                v_str = str(valor)
                if 'tamanho' in campo and len(v_str) > campo['tamanho']:
                    v_str = v_str[:campo['tamanho']]
                linha_parts.append(v_str)
                
            elif tipo == "DATA":
                if isinstance(valor, date):
                    formato = campo.get('formato', 'DDMMAAAA')
                    if formato == "DDMMAAAA":
                        linha_parts.append(valor.strftime("%d%m%Y"))
                    else:
                        linha_parts.append(valor.strftime("%Y-%m-%d"))
                else:
                    # Se vier string, confia no input ou tenta parse (MVP: confia)
                    linha_parts.append(str(valor))
                    
            elif tipo == "NUMERAL":
                dec_places = campo.get('dec', 2)
                try:
                    # Formata garantindo o numero de casas decimais sem separador de milhar. Decimal em PT-BR no SPED usa vírgula
                    # Ex: 1000.50 -> 1000,50
                    v_float = float(valor)
                    format_str = f"{{:.{dec_places}f}}"
                    v_str = format_str.format(v_float).replace('.', ',')
                    linha_parts.append(v_str)
                except (ValueError, TypeError):
                    raise LayoutParseError(f"Valor inválido para NUMERAL no campo {nome}: {valor}")
            else:
                linha_parts.append(str(valor))
                
        # Adiciona um último elemento vazio para garantir o pipe final
        linha_parts.append("")
        
        return "|".join(linha_parts)
