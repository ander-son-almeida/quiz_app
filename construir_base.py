"""Converte os arquivos de texto em fontes/ no banco questoes.json.

Formato de cada arquivo:
    # <Tema> | <Especialidade> | <Conhecimento>     (cabeçalho de bloco)
    Q<numero> [<nivel>] <enunciado, pode continuar em várias linhas e ter ```código```>
    A) ...
    B) ...
    C) ...
    D) ...
    R: <letra correta>
    E: <explicação>

Uso: python construir_base.py
"""
import json
import re
from pathlib import Path

from secoes import SECOES, secao_da_questao

PASTA = Path(__file__).parent
RE_CABECALHO = re.compile(r"^# (.+?) \| (.+?) \| (.+)$")
RE_QUESTAO = re.compile(r"^Q(\d*) \[(\d)\] ?(.*)$")
RE_ALTERNATIVA = re.compile(r"^([A-D])\) (.*)$")
LETRAS = ["A", "B", "C", "D"]


def ler_arquivo(caminho):
    """Lê um arquivo-fonte e devolve a lista de questões em dicionários."""
    questoes = []
    contexto = None
    atual = None
    campo = None
    linhas = caminho.read_text(encoding="utf-8").splitlines()

    def fechar():
        if atual is not None:
            atual["enunciado"] = "\n".join(atual["enunciado"]).strip()
            atual["explicacao"] = " ".join(atual["explicacao"]).strip()
            questoes.append(atual)

    for numero_linha, linha in enumerate(linhas, start=1):
        cab = RE_CABECALHO.match(linha)
        if cab:
            fechar()
            atual, campo = None, None
            contexto = {"tema": cab.group(1).strip(),
                        "especialidade": cab.group(2).strip(),
                        "conhecimento": cab.group(3).strip()}
            continue
        q = RE_QUESTAO.match(linha)
        if q and campo in (None, "explicacao"):
            fechar()
            if contexto is None:
                raise ValueError(f"{caminho.name}:{numero_linha} questão sem cabeçalho")
            atual = {**contexto,
                     "numero_original": int(q.group(1)) if q.group(1) else None,
                     "nivel": int(q.group(2)),
                     "enunciado": [q.group(3)],
                     "alternativas": {},
                     "resposta": None,
                     "explicacao": [],
                     "arquivo": caminho.name,
                     "linha": numero_linha}
            campo = "enunciado"
            continue
        if atual is None:
            continue
        alt = RE_ALTERNATIVA.match(linha)
        if alt and campo in ("enunciado", "alternativas"):
            atual["alternativas"][alt.group(1)] = alt.group(2).strip()
            campo = "alternativas"
            continue
        if linha.startswith("R: "):
            atual["resposta"] = linha[3:].strip()
            campo = "resposta"
            continue
        if linha.startswith("E: "):
            atual["explicacao"].append(linha[3:])
            campo = "explicacao"
            continue
        if campo == "enunciado":
            atual["enunciado"].append(linha)
        elif campo == "explicacao" and linha.strip():
            atual["explicacao"].append(linha.strip())
    fechar()
    return questoes


def validar(questoes):
    """Devolve a lista de problemas encontrados na base."""
    problemas = []
    vistos = {}
    for q in questoes:
        local = f"{q['arquivo']}:{q['linha']}"
        if sorted(q["alternativas"]) != LETRAS:
            problemas.append(f"{local} alternativas {sorted(q['alternativas'])}")
        if q["resposta"] not in LETRAS:
            problemas.append(f"{local} resposta inválida {q['resposta']!r}")
        if not q["explicacao"]:
            problemas.append(f"{local} sem explicação")
        if not 1 <= q["nivel"] <= 4:
            problemas.append(f"{local} nível {q['nivel']}")
        if len(set(q["alternativas"].values())) < 4:
            problemas.append(f"{local} alternativas repetidas")
        chave = q["enunciado"].lower()
        if chave in vistos:
            problemas.append(f"{local} enunciado repetido de {vistos[chave]}")
        vistos[chave] = local
    return problemas


def construir():
    """Lê todos os arquivos, numera, valida e grava questoes.json."""
    questoes = []
    for caminho in sorted((PASTA / "fontes").glob("*.txt")):
        questoes.extend(ler_arquivo(caminho))
    for i, q in enumerate(questoes, start=1):
        q["id"] = i
        q["origem"] = "Banco original (Q1–Q400)" if q["numero_original"] <= 400 else "Banco complementar"
        q["secao"] = secao_da_questao(q)
    problemas = validar(questoes)
    saida = [{k: q[k] for k in ("id", "secao", "tema", "especialidade", "conhecimento", "nivel",
                                  "enunciado", "alternativas", "resposta", "explicacao",
                                  "origem", "numero_original")}
             for q in questoes]
    (PASTA / "questoes.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1),
                                         encoding="utf-8")
    return saida, problemas


if __name__ == "__main__":
    base, problemas = construir()
    from collections import Counter
    print(f"Total: {len(base)} questões")
    print("Por tema:", dict(Counter(q["tema"] for q in base)))
    por_secao = Counter(q["secao"] for q in base)
    for secao in SECOES:
        print(f"  {por_secao[secao]:4d}  {secao}")
    print("Por origem:", dict(Counter(q["origem"] for q in base)))
    print("Por nível:", dict(sorted(Counter(q["nivel"] for q in base).items())))
    print("Letra correta:", dict(sorted(Counter(q["resposta"] for q in base).items())))
    print("Problemas:", len(problemas))
    for p in problemas:
        print("  ", p)
