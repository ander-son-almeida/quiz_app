"""Seções do exame HackerRank e regra de alocação das questões.

Cada questão recebe a seção pelo seu conhecimento (POR_CONHECIMENTO). As exceções,
para questões cujo assunto pertence a outra seção, ficam em POR_NUMERO, indexadas
pelo número original da questão (Q1, Q2, ...).
"""

# Seções na ordem do exame e quantidade de questões de cada uma no simulado completo.
SECOES = {
    "Inteligência Artificial Aplicada": 7,
    "Governança, Segurança e Privacidade": 5,
    "Entrega e Custo": 5,
    "Modelagem e Qualidade de Dados": 5,
    "Estatística Aplicada": 5,
    "Preparação de Dados": 5,
    "Fundamentos de Aprendizado de Máquina": 5,
    "Modelos Clássicos": 5,
    "Otimização de Modelos": 5,
    "Avaliação e Explicabilidade": 5,
    "Confiabilidade de Dados e Modelos e Séries Temporais": 5,
}

IA = "Inteligência Artificial Aplicada"
GOV = "Governança, Segurança e Privacidade"
ENT = "Entrega e Custo"
MQD = "Modelagem e Qualidade de Dados"
EST = "Estatística Aplicada"
PREP = "Preparação de Dados"
FAM = "Fundamentos de Aprendizado de Máquina"
CLA = "Modelos Clássicos"
OTM = "Otimização de Modelos"
AVA = "Avaliação e Explicabilidade"
CONF = "Confiabilidade de Dados e Modelos e Séries Temporais"

POR_CONHECIMENTO = {
    # Inteligência Artificial Aplicada
    "(Multi-)Agentes": IA, "Aplicações de LLMs": IA, "Embeddings, Vector Search e RAG": IA,
    "Frameworks de Desenvolvimento": IA, "LLMs, LMMs e Foundation Models": IA, "NLP": IA,
    "Prompt Engineering": IA, "Transformers": IA, "Deep Learning": IA,
    "Monitoramento e Curadoria de IA": CONF,
    # Governança, Segurança e Privacidade
    "Vieses Algorítmicos e IA Responsável": GOV, "Privacidade e Proteção de Dados": GOV,
    "Segurança de Dados e Acessos": GOV, "Segurança de Aplicações de IA": GOV,
    "Governança de Dados e Modelos": GOV,
    # Entrega e Custo
    "Fundamentos Cloud": ENT, "Deploy e Release Management": ENT, "Esteiras CI/CD": ENT,
    "MLOps": ENT, "MLOps e Produção": ENT, "Processamento Paralelo e Distribuído": ENT,
    "Metodologias Ágeis e Híbridas": ENT, "Modelagem de Processos BPMN": ENT,
    "Controle de Versão": ENT, "Boas Práticas de Programação": ENT, "Design Patterns": ENT,
    "Testes Unitários e Integrados": ENT,
    # Modelagem e Qualidade de Dados
    "Qualidade de Dados": MQD, "SQL": MQD, "SQL Avançado": MQD, "Análise de Outliers": MQD,
    "Modelagem de Dados": MQD,
    # Estatística Aplicada
    "Estatística Descritiva": EST, "Distribuições de Probabilidade": EST,
    "Técnicas de Amostragem": EST, "Amostragem e Planejamento": EST,
    "Análise Multivariada": EST, "Estimação e Intervalos": EST, "Inferência Bayesiana": EST,
    "Inferência Causal": EST, "Inferência Estatística": EST,
    "Planejamento de Experimentos": EST, "Testes de Hipótese": EST, "Probabilidade": EST,
    "Problemas Clássicos": EST, "Variáveis Aleatórias e Distribuições": EST,
    "Análise de Sobrevivência": EST, "ANOVA e Comparações Múltiplas": EST,
    "Testes Não Paramétricos e Qui-quadrado": EST,
    # Preparação de Dados
    "Python e pandas": PREP, "PySpark e Big Data": PREP, "NumPy e scikit-learn": PREP,
    "Python": PREP, "Estruturas de Dados e Algoritmos": PREP,
    "Feature Engineering / Selection": PREP, "Engenharia de Features e Dados": PREP,
    # Fundamentos de Aprendizado de Máquina
    "Aprendizado Não Supervisionado": FAM, "Aprendizado por Reforço": FAM,
    "Machine Learning Supervisionado": FAM, "Conceitos Fundamentais de ML": FAM,
    # Modelos Clássicos
    "Aprendizado Supervisionado": CLA, "Regressão Linear": CLA,
    "GLM e Regressão Logística": CLA,
    # Otimização de Modelos
    "Regularização e Tuning de Hiperparâmetros": OTM, "Otimização Linear Contínua": OTM,
    "Otimização Linear Discreta": OTM, "Otimização Não Linear Convexa": OTM,
    "Otimização Não Linear Não Convexa": OTM, "Heurísticas e Meta-heurísticas": OTM,
    # Avaliação e Explicabilidade
    "Explicabilidade": AVA, "Métricas de Avaliação e Monitoramento": AVA,
    "Avaliação e Validação de Modelos": AVA, "Visualização de Dados": AVA,
    # Confiabilidade de Dados e Modelos e Séries Temporais
    "Séries Temporais": CONF, "Séries Temporais e Previsão": CONF, "DataOps": CONF,
    "Monitoramento e Confiabilidade": CONF,
}

POR_NUMERO = {
    # Governança, Segurança e Privacidade
    8: GOV,  # responsabilidade compartilhada na nuvem
    325: GOV, 326: GOV,  # proteções em agentes
    337: GOV,  # guardrails
    766: GOV,  # menor privilégio para agentes
    # Entrega e Custo
    339: ENT, 761: ENT, 767: ENT, 770: ENT,  # custo e memória de LLMs
    392: ENT,  # orquestração de jobs
    # Modelagem e Qualidade de Dados
    394: MQD,  # histórico de dimensões (SCD)
    # Confiabilidade de Dados e Modelos
    20: CONF, 21: CONF,  # expectations e anomalia de volume
    256: CONF, 260: CONF,  # PSI e calibração em produção
    399: CONF,  # gatilho de retreino
    771: CONF, 781: CONF, 783: CONF, 785: CONF,  # drift e monitoramento
    # Modelos Clássicos (árvores, ensembles, regressão quantílica)
    669: CLA, 670: CLA, 676: CLA, 679: CLA, 680: CLA, 682: CLA,
    # Otimização de Modelos
    675: OTM,  # taxa de aprendizado do boosting
    # Avaliação e Explicabilidade
    677: AVA, 678: AVA,  # calibração e corte por custo
    # Inteligência Artificial Aplicada
    343: IA,  # curadoria de dados para ajuste fino
}


def secao_da_questao(questao):
    """Devolve a seção do exame a que a questão pertence."""
    numero = questao.get("numero_original")
    if numero in POR_NUMERO:
        return POR_NUMERO[numero]
    return POR_CONHECIMENTO[questao["conhecimento"]]
