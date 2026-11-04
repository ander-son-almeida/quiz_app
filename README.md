# Simulado HackerRank — Ciência de Dados

App em Streamlit com 872 questões de múltipla escolha (4 alternativas, resposta e explicação em cada uma), organizadas nas 11 seções do teste HackerRank.

| nº | Seção | No simulado | No banco |
| --- | --- | --- | --- |
| 1 | Inteligência Artificial Aplicada | 7 | 81 |
| 2 | Governança, Segurança e Privacidade | 5 | 50 |
| 3 | Entrega e Custo | 5 | 86 |
| 4 | Modelagem e Qualidade de Dados | 5 | 60 |
| 5 | Estatística Aplicada | 5 | 220 |
| 6 | Preparação de Dados | 5 | 109 |
| 7 | Fundamentos de Aprendizado de Máquina | 5 | 46 |
| 8 | Modelos Clássicos | 5 | 61 |
| 9 | Otimização de Modelos | 5 | 51 |
| 10 | Avaliação e Explicabilidade | 5 | 55 |
| 11 | Confiabilidade de Dados e Modelos e Séries Temporais | 5 | 53 |
| | **Total** | **57** | **872** |

## Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py
```

O navegador abre em `http://localhost:8501`.

No Databricks, a pasta pode ser publicada como Databricks App (tipo Streamlit) com `app.py` como ponto de entrada.

## Como usar

1. Escolha o tipo de teste:
   - **Simulado do exame**: 57 questões sorteadas com a mesma quantidade por seção do exame (7 + 5 × 10), agrupadas por seção na ordem do exame.
   - **Treino por seção**: escolha uma ou mais seções, filtre por conhecimento e nível e defina o número de questões.
2. Escolha o modo de correção:
   - **Responder tudo e ver o resultado no final**: navega livremente entre questões e seções (botões na barra lateral) e só vê a correção ao finalizar.
   - **Mostrar se acertei a cada questão**: após "Responder", aparecem o resultado, a alternativa correta e a explicação.
3. Opcional: limite de tempo em minutos (o tempo restante aparece na barra lateral; ao zerar, a prova é encerrada) e embaralhamento das alternativas.
4. No resultado: aproveitamento geral, por seção (na ordem do exame), por conhecimento e por nível; revisão com explicações; botão para refazer só as erradas; download das respostas em CSV.

## Arquivos

| Arquivo | Conteúdo |
| --- | --- |
| `app.py` | Aplicativo (apenas funções, sem classes) |
| `secoes.py` | Seções do exame, quantidade por seção no simulado e regra que aloca cada questão numa seção |
| `questoes.json` | Banco de questões usado pelo app |
| `fontes/*.txt` | Questões em texto legível, um bloco por conhecimento |
| `construir_base.py` | Converte `fontes/` em `questoes.json`, atribui a seção e valida a base |

## Como adicionar ou corrigir questões

Edite um arquivo em `fontes/` (ou crie outro) seguindo o formato:

```
# Ciência de Dados | Especialidade | Conhecimento

Q [2] Enunciado da questão
A) alternativa
B) alternativa
C) alternativa
D) alternativa
R: B
E: Explicação.
```

A seção do exame vem do conhecimento, pela tabela `POR_CONHECIMENTO` em `secoes.py`. Um conhecimento novo precisa ser incluído nessa tabela; para mover uma questão específica para outra seção, use `POR_NUMERO`. Se a distribuição do exame mudar, basta alterar `SECOES`.

Depois rode `python construir_base.py`. O script recria o `questoes.json`, mostra a contagem por seção e lista problemas (alternativas faltando, resposta inválida, enunciado repetido).
