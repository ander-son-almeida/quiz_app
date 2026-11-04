"""Simulado de múltipla escolha no formato do teste HackerRank de Ciência de Dados.

Execução: streamlit run app.py
Base de dados: questoes.json (gerado por construir_base.py a partir de fontes/).
Seções do exame e distribuição do simulado: secoes.py.
"""
import json
import random
import re
import time
from pathlib import Path

import pandas as pd
import streamlit as st

from secoes import SECOES

PASTA = Path(__file__).parent
ARQUIVO_BASE = PASTA / "questoes.json"
LETRAS = ["A", "B", "C", "D"]
NOMES_SECAO = list(SECOES)
TOTAL_SIMULADO = sum(SECOES.values())
TIPO_SIMULADO = f"Simulado do exame ({TOTAL_SIMULADO} questões)"
TIPO_TREINO = "Treino por seção"
MODO_IMEDIATO = "Mostrar se acertei a cada questão"
MODO_FINAL = "Responder tudo e ver o resultado no final"
NOMES_NIVEL = {1: "1 · noção", 2: "2 · aplica com apoio", 3: "3 · autonomia", 4: "4 · domina"}
COLUNA_PERCENTUAL = {"aproveitamento": st.column_config.ProgressColumn(
    format="percent", min_value=0, max_value=1)}


# ---------------------------------------------------------------- dados

@st.cache_data
def carregar_base():
    """Lê o banco de questões e devolve um dicionário id → questão."""
    questoes = json.loads(ARQUIVO_BASE.read_text(encoding="utf-8"))
    return {q["id"]: q for q in questoes}


def ids_por_secao(base):
    """Dicionário seção → lista de ids, na ordem das seções do exame."""
    grupos = {secao: [] for secao in NOMES_SECAO}
    for qid, q in base.items():
        grupos[q["secao"]].append(qid)
    return grupos


def sortear_simulado(base):
    """Sorteia as questões do simulado: a quantidade de cada seção definida em SECOES,
    agrupadas por seção na ordem do exame."""
    grupos = ids_por_secao(base)
    ids = []
    for secao, quantidade in SECOES.items():
        ids.extend(random.sample(grupos[secao], quantidade))
    return ids


def filtrar(base, secoes, conhecimentos, niveis):
    """Ids das questões que atendem aos filtros do modo treino."""
    return [qid for qid, q in base.items()
            if q["secao"] in secoes
            and q["conhecimento"] in conhecimentos
            and q["nivel"] in niveis]


def ordenar_por_secao(ids, base):
    """Ordena os ids pela ordem das seções do exame, mantendo a ordem interna."""
    return sorted(ids, key=lambda qid: NOMES_SECAO.index(base[qid]["secao"]))


def escapar_cifrao(texto):
    """Evita que 'R$ 10 ... R$ 20' seja lido como fórmula LaTeX pelo Markdown."""
    return re.sub(r"(?<!\\)\$", r"\\$", texto)


def remapear_letras(texto, ordem):
    """Ajusta referências como 'opção A' quando as alternativas foram embaralhadas."""
    def trocar(m):
        return f"{m.group(1)} {LETRAS[ordem.index(m.group(2))]}"
    return re.sub(r"\b(opção|caso) ([A-D])\b", trocar, texto)


def formatar_tempo(segundos):
    segundos = max(0, int(segundos))
    return f"{segundos // 60} min {segundos % 60:02d} s"


# ---------------------------------------------------------------- estado

def estado_inicial():
    """Cria as chaves de sessão na primeira execução."""
    padrao = {"fase": "config", "ids": [], "ordens": {}, "respostas": {}, "indice": 0,
              "confirmadas": set(), "modo": MODO_IMEDIATO, "tipo": TIPO_SIMULADO,
              "inicio": None, "fim": None, "limite_seg": 0, "esgotado": False}
    for chave, valor in padrao.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


def limpar_respostas():
    """Apaga as respostas da prova anterior (dicionário e widgets de rádio)."""
    st.session_state.respostas = {}
    for chave in [k for k in st.session_state if str(k).startswith("resp_")]:
        del st.session_state[chave]


def iniciar_prova(ids, modo, tipo, embaralhar_alt, limite_min=0):
    """Prepara a sessão para uma nova prova com a lista de ids informada."""
    limpar_respostas()
    st.session_state.ids = list(ids)
    st.session_state.ordens = {qid: (random.sample(LETRAS, 4) if embaralhar_alt else LETRAS[:])
                               for qid in ids}
    st.session_state.indice = 0
    st.session_state.confirmadas = set()
    st.session_state.modo = modo
    st.session_state.tipo = tipo
    st.session_state.inicio = time.time()
    st.session_state.fim = None
    st.session_state.limite_seg = int(limite_min) * 60
    st.session_state.esgotado = False
    st.session_state.fase = "prova"


def tempo_restante():
    """Segundos restantes, ou None se a prova não tem limite de tempo."""
    if not st.session_state.limite_seg:
        return None
    return st.session_state.limite_seg - (time.time() - st.session_state.inicio)


def resposta_marcada(qid):
    """Letra exibida que o usuário marcou (ou None).

    As respostas ficam num dicionário próprio porque o Streamlit apaga o estado de um
    widget quando ele deixa de ser desenhado (ao navegar para outra questão)."""
    return st.session_state.respostas.get(qid)


def guardar_resposta(qid):
    """Callback do rádio: copia a escolha para o dicionário de respostas."""
    st.session_state.respostas = {**st.session_state.respostas,
                                  qid: st.session_state.get(f"resp_{qid}")}


def letra_correta_exibida(qid, base):
    """Letra correta na ordem em que as alternativas foram mostradas."""
    ordem = st.session_state.ordens[qid]
    return LETRAS[ordem.index(base[qid]["resposta"])]


def acertou(qid, base):
    """True se a resposta marcada é a correta."""
    return resposta_marcada(qid) == letra_correta_exibida(qid, base)


def finalizar(esgotado=False):
    """Encerra a prova e vai para a tela de resultado."""
    st.session_state.fim = time.time()
    st.session_state.esgotado = esgotado
    st.session_state.fase = "resultado"


def ir_para(indice):
    st.session_state.indice = indice


def navegar_numero(chave):
    """Callback do campo 'Ir para a questão nº' (numeração a partir de 1)."""
    st.session_state.indice = int(st.session_state[chave]) - 1


def confirmar(qid):
    st.session_state.confirmadas = st.session_state.confirmadas | {qid}


def voltar_config():
    limpar_respostas()
    st.session_state.fase = "config"


# ---------------------------------------------------------------- tela inicial

def tabela_secoes(base):
    """Seções do exame com a quantidade no simulado e no banco."""
    grupos = ids_por_secao(base)
    return pd.DataFrame([{"nº": n, "seção": secao, "no simulado": SECOES[secao],
                          "no banco": len(grupos[secao])}
                         for n, secao in enumerate(NOMES_SECAO, start=1)])


def opcoes_comuns(chave):
    """Correção, embaralhamento e limite de tempo, usados nos dois tipos de teste."""
    col1, col2 = st.columns(2)
    with col1:
        modo = st.radio("Correção", [MODO_FINAL, MODO_IMEDIATO], key=f"modo_{chave}")
    with col2:
        limite = st.number_input("Limite de tempo em minutos (0 = sem limite)", min_value=0,
                                 max_value=600, value=0, step=5, key=f"limite_{chave}")
        embaralhar = st.checkbox("Embaralhar as alternativas", value=False,
                                 key=f"emb_{chave}")
    return modo, int(limite), embaralhar


def config_simulado(base):
    st.markdown(f"{TOTAL_SIMULADO} questões sorteadas do banco, agrupadas pelas "
                f"{len(SECOES)} seções na ordem do exame, com a mesma quantidade por seção.")
    modo, limite, embaralhar = opcoes_comuns("sim")
    if st.button("Iniciar simulado", type="primary", width="stretch"):
        iniciar_prova(sortear_simulado(base), modo, TIPO_SIMULADO, embaralhar, limite)
        st.rerun()


def config_treino(base):
    secoes = st.multiselect("Seções", NOMES_SECAO, default=NOMES_SECAO)
    das_secoes = [q for q in base.values() if q["secao"] in secoes]
    todos_conhecimentos = sorted({q["conhecimento"] for q in das_secoes})
    with st.expander("Filtros opcionais (conhecimento e nível)"):
        conhecimentos = st.multiselect("Conhecimentos", todos_conhecimentos,
                                       default=todos_conhecimentos,
                                       key="conh_" + "|".join(secoes))
        niveis = st.multiselect("Níveis", [1, 2, 3, 4], default=[1, 2, 3, 4],
                                format_func=NOMES_NIVEL.get)

    disponiveis = filtrar(base, secoes, conhecimentos, niveis)
    if not disponiveis:
        st.warning("Nenhuma questão atende aos filtros. Amplie a seleção.")
        return

    col1, col2 = st.columns(2)
    with col1:
        quantidade = st.number_input(f"Número de questões (disponíveis: {len(disponiveis)})",
                                     min_value=1, max_value=len(disponiveis),
                                     value=min(20, len(disponiveis)), step=1)
    with col2:
        agrupar = st.checkbox("Agrupar as questões por seção", value=True)
    modo, limite, embaralhar = opcoes_comuns("treino")

    if st.button("Iniciar treino", type="primary", width="stretch"):
        ids = random.sample(disponiveis, int(quantidade))
        if agrupar:
            ids = ordenar_por_secao(ids, base)
        iniciar_prova(ids, modo, TIPO_TREINO, embaralhar, limite)
        st.rerun()


def tela_config(base):
    """Tela inicial: tipo de teste e opções."""
    st.title("Simulado HackerRank — Ciência de Dados")
    st.caption(f"Banco com {len(base)} questões de múltipla escolha, cada uma com resposta "
               f"e explicação, distribuídas nas {len(SECOES)} seções do exame.")
    with st.expander("Seções do exame"):
        st.dataframe(tabela_secoes(base), hide_index=True, width="stretch",
                     height=(len(SECOES) + 1) * 35 + 3)

    tipo = st.radio("Tipo de teste", [TIPO_SIMULADO, TIPO_TREINO], horizontal=True)
    if tipo == TIPO_SIMULADO:
        config_simulado(base)
    else:
        config_treino(base)


# ---------------------------------------------------------------- prova

def mostrar_questao(qid, base, numero, total, bloqueada):
    """Desenha enunciado e alternativas de uma questão."""
    q = base[qid]
    ordem = st.session_state.ordens[qid]
    st.markdown(f"**Questão {numero} de {total}** · {q['conhecimento']} · nível {q['nivel']}")
    st.markdown(escapar_cifrao(q["enunciado"]))
    textos = {LETRAS[i]: q["alternativas"][letra] for i, letra in enumerate(ordem)}
    marcada = resposta_marcada(qid)
    st.radio("Escolha uma alternativa", LETRAS,
             index=LETRAS.index(marcada) if marcada else None, key=f"resp_{qid}",
             format_func=lambda L: f"{L}) {escapar_cifrao(textos[L])}",
             on_change=guardar_resposta, args=(qid,),
             disabled=bloqueada, label_visibility="collapsed")


def mostrar_correcao(qid, base):
    """Mostra se acertou, a alternativa correta e a explicação."""
    q = base[qid]
    ordem = st.session_state.ordens[qid]
    correta = letra_correta_exibida(qid, base)
    marcada = resposta_marcada(qid)
    texto_correto = escapar_cifrao(q["alternativas"][q["resposta"]])
    if marcada is None:
        st.warning(f"Sem resposta. Correta: **{correta})** {texto_correto}")
    elif marcada == correta:
        st.success(f"Acertou. **{correta})** {texto_correto}")
    else:
        st.error(f"Errou: você marcou {marcada}. Correta: **{correta})** {texto_correto}")
    st.info(escapar_cifrao(remapear_letras(q["explicacao"], ordem)))


def placar_parcial(base):
    """Acertos e respondidas até o momento (modo imediato)."""
    feitas = st.session_state.confirmadas
    certos = sum(acertou(qid, base) for qid in feitas)
    return certos, len(feitas)


def secoes_da_prova(base):
    """Lista de (seção, índice da primeira questão, índices) na ordem da prova."""
    blocos = {}
    for k, qid in enumerate(st.session_state.ids):
        blocos.setdefault(base[qid]["secao"], []).append(k)
    return [(secao, indices[0], indices) for secao, indices in blocos.items()]


@st.fragment(run_every=1)
def cronometro():
    """Mostra o tempo restante e encerra a prova quando o tempo acaba."""
    if st.session_state.fase != "prova":
        return
    restante = tempo_restante()
    if restante is None:
        return
    if restante <= 0:
        finalizar(esgotado=True)
        st.rerun()
    st.metric("Tempo restante", formatar_tempo(restante))


def painel_lateral(base, imediato):
    """Barra lateral: tempo, progresso por seção e ações."""
    ids = st.session_state.ids
    with st.sidebar:
        st.subheader("Simulado" if st.session_state.tipo == TIPO_SIMULADO else "Treino")
        cronometro()
        st.caption(f"Correção: {'a cada questão' if imediato else 'no final'}")
        st.markdown("**Seções**")
        for secao, primeiro, indices in secoes_da_prova(base):
            feitas = sum(resposta_marcada(ids[k]) is not None for k in indices)
            atual = primeiro <= st.session_state.indice <= indices[-1]
            rotulo = f"{'▶ ' if atual else ''}{secao} · {feitas}/{len(indices)}"
            st.button(rotulo, key=f"sec_{primeiro}", on_click=ir_para, args=(primeiro,),
                      width="stretch", disabled=imediato)
        st.divider()
        st.button("Encerrar e ver resultado", on_click=finalizar)
        st.button("Abandonar e voltar ao início", on_click=voltar_config)


def tela_prova(base):
    """Tela de resolução, nos dois modos de correção."""
    ids = st.session_state.ids
    total = len(ids)
    i = st.session_state.indice
    qid = ids[i]
    imediato = st.session_state.modo == MODO_IMEDIATO

    painel_lateral(base, imediato)

    secoes = secoes_da_prova(base)
    pos = next(n for n, (_, _, indices) in enumerate(secoes, start=1) if i in indices)
    st.subheader(f"Seção {pos} de {len(secoes)} · {base[qid]['secao']}")

    respondidas = sum(resposta_marcada(x) is not None for x in ids)
    st.progress((i + 1) / total, text=f"Questão {i + 1} de {total} · respondidas: {respondidas}")
    if imediato:
        certos, feitas = placar_parcial(base)
        if feitas:
            st.caption(f"Placar parcial: {certos} de {feitas} ({certos / feitas:.0%})")

    confirmada = qid in st.session_state.confirmadas
    mostrar_questao(qid, base, i + 1, total, bloqueada=imediato and confirmada)

    if imediato:
        if not confirmada:
            st.button("Responder", type="primary", on_click=confirmar, args=(qid,),
                      disabled=resposta_marcada(qid) is None)
        else:
            mostrar_correcao(qid, base)
            if i + 1 < total:
                st.button("Próxima questão", type="primary", on_click=ir_para, args=(i + 1,))
            else:
                st.button("Ver resultado", type="primary", on_click=finalizar)
    else:
        col1, col2, col3 = st.columns(3)
        col1.button("← Anterior", on_click=ir_para, args=(i - 1,), disabled=i == 0,
                    width="stretch")
        col2.button("Próxima →", on_click=ir_para, args=(i + 1,), disabled=i + 1 == total,
                    width="stretch")
        faltam = total - respondidas
        rotulo = "Finalizar e corrigir" if faltam == 0 else f"Finalizar ({faltam} em branco)"
        col3.button(rotulo, type="primary", on_click=finalizar, width="stretch")
        st.number_input("Ir para a questão nº", min_value=1, max_value=total, value=i + 1,
                        step=1, key=f"nav_{i}", on_change=navegar_numero, args=(f"nav_{i}",))


# ---------------------------------------------------------------- resultado

def tabela_desempenho(base, coluna, ordem=None):
    """Acertos por agrupamento (seção, conhecimento ou nível)."""
    linhas = [{coluna: base[qid][coluna], "acerto": int(acertou(qid, base)),
               "em_branco": int(resposta_marcada(qid) is None)}
              for qid in st.session_state.ids]
    df = pd.DataFrame(linhas)
    resumo = df.groupby(coluna).agg(questoes=("acerto", "size"), acertos=("acerto", "sum"),
                                    em_branco=("em_branco", "sum")).reset_index()
    resumo["aproveitamento"] = resumo["acertos"] / resumo["questoes"]
    if ordem:
        return resumo.sort_values(coluna, key=lambda s: s.map(ordem.index))
    return resumo.sort_values("aproveitamento")


def tabela_respostas(base):
    """Uma linha por questão, para revisão e download."""
    linhas = []
    for n, qid in enumerate(st.session_state.ids, start=1):
        q = base[qid]
        linhas.append({"nº": n, "id": qid, "seção": q["secao"],
                       "conhecimento": q["conhecimento"], "nível": q["nivel"],
                       "sua_resposta": resposta_marcada(qid) or "",
                       "correta": letra_correta_exibida(qid, base),
                       "acertou": acertou(qid, base), "enunciado": q["enunciado"]})
    return pd.DataFrame(linhas)


def tela_resultado(base):
    """Placar final, desempenho por seção, conhecimento e nível, e revisão."""
    ids = st.session_state.ids
    total = len(ids)
    certos = sum(acertou(qid, base) for qid in ids)
    branco = sum(resposta_marcada(qid) is None for qid in ids)
    erros = total - certos - branco
    duracao = (st.session_state.fim or time.time()) - (st.session_state.inicio or time.time())

    st.title("Resultado")
    if st.session_state.esgotado:
        st.warning("O tempo acabou. As questões não respondidas contam como em branco.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Aproveitamento", f"{certos / total:.0%}")
    c2.metric("Acertos", f"{certos} de {total}")
    c3.metric("Erros / em branco", f"{erros} / {branco}")
    c4.metric("Tempo", formatar_tempo(duracao))

    st.subheader("Por seção (na ordem do exame)")
    st.dataframe(tabela_desempenho(base, "secao", ordem=NOMES_SECAO), hide_index=True,
                 width="stretch", column_config=COLUNA_PERCENTUAL)

    st.subheader("Por conhecimento (do mais fraco ao mais forte)")
    st.dataframe(tabela_desempenho(base, "conhecimento"), hide_index=True,
                 width="stretch", column_config=COLUNA_PERCENTUAL)

    st.subheader("Por nível")
    st.dataframe(tabela_desempenho(base, "nivel"), hide_index=True, width="stretch",
                 column_config=COLUNA_PERCENTUAL)

    st.subheader("Revisão das questões")
    so_erradas = st.checkbox("Mostrar só erradas e em branco", value=True)
    for n, qid in enumerate(ids, start=1):
        if so_erradas and acertou(qid, base):
            continue
        q = base[qid]
        marca = "✅" if acertou(qid, base) else ("⬜" if resposta_marcada(qid) is None else "❌")
        with st.expander(f"{marca} Questão {n} · {q['secao']} · {q['conhecimento']}"):
            st.markdown(escapar_cifrao(q["enunciado"]))
            ordem = st.session_state.ordens[qid]
            for i, letra in enumerate(ordem):
                st.markdown(f"- **{LETRAS[i]})** {escapar_cifrao(q['alternativas'][letra])}")
            mostrar_correcao(qid, base)

    st.divider()
    erradas = [qid for qid in ids if not acertou(qid, base)]
    col1, col2, col3 = st.columns(3)
    if col1.button("Refazer só as erradas", disabled=not erradas, width="stretch"):
        iniciar_prova(ordenar_por_secao(random.sample(erradas, len(erradas)), base),
                      st.session_state.modo, TIPO_TREINO, embaralhar_alt=False)
        st.rerun()
    col2.download_button("Baixar respostas (CSV)",
                         tabela_respostas(base).to_csv(index=False, sep=";").encode("utf-8-sig"),
                         file_name="resultado_simulado.csv", mime="text/csv",
                         width="stretch")
    col3.button("Novo teste", type="primary", on_click=voltar_config, width="stretch")


# ---------------------------------------------------------------- principal

def main():
    st.set_page_config(page_title="Simulado HackerRank DS", page_icon="📝", layout="centered")
    estado_inicial()
    base = carregar_base()
    if st.session_state.fase == "prova":
        restante = tempo_restante()
        if restante is not None and restante <= 0:
            finalizar(esgotado=True)
    fase = st.session_state.fase
    if fase == "prova":
        tela_prova(base)
    elif fase == "resultado":
        tela_resultado(base)
    else:
        tela_config(base)


main()
