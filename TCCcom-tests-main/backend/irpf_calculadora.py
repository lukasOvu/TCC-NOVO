"""
Classe e dados para cálculo do Imposto de Renda Pessoa Física (IRPF) e MEI.
Baseado nas regras de 2024 (ano-calendário 2023).
"""
import math
from typing import Dict

class CalculadoraIRPF:
    
    # Tabela Progressiva Mensal (Exemplo de 2024)
    # A IRPF Anual usa a tabela anual, mas a estrutura é similar
    # Usaremos a tabela ANUAL para o cálculo final
    
    # Tabela Progressiva Anual (2024, ano-calendário 2023)
    # Fonte: Receita Federal
    TABELA_ANUAL = [
        {"limite": 24511.92, "aliquota": 0.00, "deducao": 0.00},
        {"limite": 33919.80, "aliquota": 0.075, "deducao": 1838.39},
        {"limite": 45012.60, "aliquota": 0.15, "deducao": 4357.57},
        {"limite": 55976.16, "aliquota": 0.225, "deducao": 7615.11},
        {"limite": math.inf, "aliquota": 0.275, "deducao": 10432.32},
    ]
    
    # Limites e Deduções Anuais (2024, ano-calendário 2023)
    DED_DEPENDENTE_VALOR = 2275.08  # Valor por dependente
    DED_SIMPLIFICADA_PERCENTUAL = 0.20 # 20%
    DED_SIMPLIFICADA_LIMITE = 16758.24 # Limite da dedução simplificada
    DED_INSTRUCAO_LIMITE = 3561.50 # Limite de despesas com instrução
    
    def __init__(self):
        pass

    def _calcular_imposto_devido(self, base_calculo: float) -> Dict:
        """Calcula o imposto devido com base na tabela progressiva anual."""
        
        imposto_devido = 0.0
        aliquota_aplicada = 0.0
        deducao_parcela = 0.0
        
        for faixa in self.TABELA_ANUAL:
            if base_calculo <= faixa["limite"]:
                aliquota_aplicada = faixa["aliquota"]
                deducao_parcela = faixa["deducao"]
                imposto_devido = (base_calculo * aliquota_aplicada) - deducao_parcela
                break
        
        # Se a base de cálculo for maior que o limite da última faixa
        if base_calculo > self.TABELA_ANUAL[-2]["limite"]:
            faixa = self.TABELA_ANUAL[-1]
            imposto_devido = (base_calculo * faixa["aliquota"]) - faixa["deducao"]
            aliquota_aplicada = faixa["aliquota"]
            deducao_parcela = faixa["deducao"]

        # O imposto devido não pode ser negativo
        imposto_devido = max(0.0, imposto_devido)
        
        # Alíquota Efetiva
        aliquota_efetiva = (imposto_devido / base_calculo) * 100 if base_calculo > 0 else 0.0
        
        return {
            "imposto_devido": round(imposto_devido, 2),
            "aliquota_aplicada": aliquota_aplicada,
            "deducao_parcela": deducao_parcela,
            "aliquota_efetiva": round(aliquota_efetiva, 1)
        }

    def calcular_irpf_anual(self, 
                            rendimentos_tributaveis: float, 
                            despesas_dedutiveis: float, 
                            num_dependentes: int, 
                            despesas_instrucao: float,
                            imposto_retido_fonte: float) -> Dict:
        """
        Calcula o IRPF Anual, comparando a dedução legal (completa) com a dedução simplificada.
        Retorna o resultado da opção mais vantajosa.
        """
        
        # 1. CÁLCULO PELA DEDUÇÃO LEGAL (COMPLETA)
        
        # Dedução por dependente
        deducao_dependente = num_dependentes * self.DED_DEPENDENTE_VALOR
        
        # Dedução de instrução (limitada)
        deducao_instrucao = min(despesas_instrucao, self.DED_INSTRUCAO_LIMITE)
        
        # Total de deduções legais
        total_deducoes_legais = deducao_dependente + deducao_instrucao + despesas_dedutiveis
        
        # Base de Cálculo Legal
        base_calculo_legal = max(0.0, rendimentos_tributaveis - total_deducoes_legais)
        
        # Imposto Devido Legal
        res_legal = self._calcular_imposto_devido(base_calculo_legal)
        imposto_devido_legal = res_legal["imposto_devido"]
        
        # 2. CÁLCULO PELA DEDUÇÃO SIMPLIFICADA
        
        # Dedução Simplificada (20% limitado)
        deducao_simplificada = min(
            rendimentos_tributaveis * self.DED_SIMPLIFICADA_PERCENTUAL,
            self.DED_SIMPLIFICADA_LIMITE
        )
        
        # Base de Cálculo Simplificada
        base_calculo_simplificada = max(0.0, rendimentos_tributaveis - deducao_simplificada)
        
        # Imposto Devido Simplificado
        res_simplificada = self._calcular_imposto_devido(base_calculo_simplificada)
        imposto_devido_simplificado = res_simplificada["imposto_devido"]
        
        # 3. COMPARAÇÃO E RESULTADO FINAL
        
        # O contribuinte sempre escolhe a opção que resulta no MENOR IMPOSTO DEVIDO (ou maior restituição)
        
        if imposto_devido_legal <= imposto_devido_simplificado:
            # Opção Legal é mais vantajosa (ou igual)
            imposto_devido_final = imposto_devido_legal
            base_calculo_final = base_calculo_legal
            melhor_opcao = "Deduções Legais (Completa)"
            aliquota_final = res_legal["aliquota_efetiva"]
        else:
            # Opção Simplificada é mais vantajosa
            imposto_devido_final = imposto_devido_simplificado
            base_calculo_final = base_calculo_simplificada
            melhor_opcao = "Dedução Simplificada"
            aliquota_final = res_simplificada["aliquota_efetiva"]
            
        # 4. CÁLCULO FINAL (Restituição ou Imposto a Pagar)
        
        valor_final = imposto_devido_final - imposto_retido_fonte
        
        if valor_final < 0:
            status_final = "Restituição"
            valor_final = abs(valor_final)
        elif valor_final > 0:
            status_final = "Imposto a Pagar"
        else:
            status_final = "Imposto Zero"
            
        return {
            "rendimentos_tributaveis": rendimentos_tributaveis,
            "imposto_retido_fonte": imposto_retido_fonte,
            "melhor_opcao": melhor_opcao,
            "base_calculo_final": round(base_calculo_final, 2),
            "imposto_devido_final": round(imposto_devido_final, 2),
            "aliquota_final": aliquota_final,
            "status_final": status_final,
            "valor_final": round(valor_final, 2),
            # Detalhes das opções (para debug/informação)
            "detalhes_legal": {
                "base": round(base_calculo_legal, 2),
                "imposto": round(imposto_devido_legal, 2),
                "deducoes": round(total_deducoes_legais, 2)
            },
            "detalhes_simplificada": {
                "base": round(base_calculo_simplificada, 2),
                "imposto": round(imposto_devido_simplificado, 2),
                "deducao": round(deducao_simplificada, 2)
            }
        }
        
    def calcular_mei_anual(self, receita_bruta_anual: float) -> Dict:
        """
        Calcula o IRPF para MEI (Microempreendedor Individual).
        Assume a presunção de lucro (8% para comércio/indústria, 16% para transporte, 32% para serviços).
        O MEI é isento de IRPF sobre o lucro presumido. O que ultrapassa o lucro presumido é tributável.
        Aqui, vamos apenas calcular o limite de isenção.
        """
        
        # Presunção de Lucro (Exemplo: Serviços 32%)
        percentual_presuncao_servicos = 0.32
        
        # Lucro Presumido Isento
        lucro_presumido_isento = receita_bruta_anual * percentual_presuncao_servicos
        
        # Rendimento Tributável (o que excedeu o lucro presumido)
        rendimento_tributavel_mei = max(0.0, receita_bruta_anual - lucro_presumido_isento)
        
        # O cálculo final do imposto é feito sobre o rendimento tributável
        # Aqui, apenas retornamos o valor para ser usado no cálculo IRPF geral, se necessário.
        
        return {
            "receita_bruta": round(receita_bruta_anual, 2),
            "lucro_presumido_isento": round(lucro_presumido_isento, 2),
            "rendimento_tributavel_mei": round(rendimento_tributavel_mei, 2),
            "observacao": "O IRPF será calculado sobre o Rendimento Tributável do MEI, se houver."
        }

# Fim do irpf_calculadora.py
