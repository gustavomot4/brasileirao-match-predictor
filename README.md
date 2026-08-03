---
tags: [scb, readme, guia]
status: atual
tipo: guia
data: 2026-08-02
---

# ⚽ SCB — Sistema Campeonato Brasileiro (Série A)

Sistema **local e gratuito** que prevê partidas do **Brasileirão Série A** (e de ligas configuráveis) entregando **P(V/E/D), gols esperados, mercados derivados, confiança e simulação da tabela** (título/G4/G6/Z4) — nunca certezas. Port evoluído do **SCM** (análises da Copa 2026) para ligas de pontos corridos: mesmo motor auditável Elo → Poisson → ensemble, validado por backtest **antes** de qualquer uso.

**Stack:** Python 3.11+ · NumPy/pandas · SQLite · Flask (web local) · pytest

> ⚠️ **Não é ferramenta de aposta.** O mercado é usado como régua de comparação (benchmark), não como alvo de lucro.

**Estado:** modelo oficial **`scb-v0.4-sot-goals-e0`** — walk-forward BRA 0,6131 / E0 0,5894 (ECE 1,1% / 2,3%), M0–M7.2 executadas.
A verdade viva do projeto mora em [[a_contexto_fonte|CONTEXT]] (`77777777_SCB_Project_DOCs/a_contexto/a_contexto_fonte.md`) — este README é a porta de entrada, não a fonte.

---

## 🤖 Como este projeto foi feito (vibe coding)

Este é um projeto de **vibe coding**: em vez de escrever o código linha a linha, ele foi construído **descrevendo em linguagem natural o que se queria** e deixando agentes de IA implementarem, com uma pessoa dirigindo e revisando cada etapa.

O processo é um **pipeline de 6 fases com prompts de papel** (em `77777777_SCB_Project_DOCs/b_processo/prompts/`):

| Fase | Papel | Portão |
|---|---|---|
| 0 — Bootstrap | `00_bootstrap_contexto` | CONTEXT ≤ 1 página + critério de aceite escrito |
| 1 — Planejamento | `01_planejador` | aprovação do dono → o plano **congela** |
| 2–3 — Implementação | `02_implementador` | `pytest` verde por módulo + teste anti look-ahead |
| 4 — QA adversarial | `03_qa_adversarial` | nenhum achado crítico/alto aberto (QA-NN) |
| 5 — Evolução | `04_auditor_evolucao` | ΔBrier com IC que não cruza zero (D-NN) |
| 6 — Entrega | `05_revisao_entrega` | [[b_checklist|CHECKLIST]] de empacotamento completo |

O ciclo de **toda** sessão de trabalho:

> abrir sessão → colar o **prompt do papel** + o **[[a_contexto_fonte|CONTEXT]]** + **só o arquivo do momento** → pedir **delta** (nunca "refaz tudo") → passar no **portão** ([[b_checklist|CHECKLIST]]) → registrar **D-NN/QA-NN** em [[f_decisoes_arquitetura|DECISIONS]] → atualizar o CONTEXT **por substituição** e jogar o datado no [[a_changelog|CHANGELOG]].

Quem dirige o projeto começa por [[a_manual_do_dono|Manual do dono]].

---

## ▶️ Como rodar

**Pré-requisito:** Python 3.11+. Todos os comandos rodam a partir de `scb_analytics/`.

```bash
cd scb_analytics
pip install -r requirements.txt
python -m pytest -q                  # esperado: 99 passed
```

### Primeira vez (montar o banco)

```bash
python -m scb.ingest --download      # 1x: baixa o snapshot (BRA + 33 temporadas da E0)
python -m scb.ingest                 # dados/*.csv -> dados/scb.sqlite (OFFLINE)
```

### Rebuild completo do modelo (nesta ordem)

```bash
python -m scb.elo_engine             # ratings point-in-time
python -m scb.features_pit           # features anti look-ahead (~20s)
python -m scb.draw_curve             # curva de empate POR LIGA (congelada)
python -m scb.predictor              # 18.200 previsões
python -m scb.backtest_harness       # esperado: BRA 0,6131 / E0 0,5894
```

### Web (5 telas, estilo EA FC)

Duplo clique em **`scb_analytics/Abrir SCB.bat`** (ou `python -m scb.web`) → <http://127.0.0.1:5000>.
Telas: **Prever Confronto** · **Tabela** (Simulada + Classificação real) · **Calibração** · **Jogos** · **Prospectivo**.

➡️ Operar a rodada é **1 clique**: Prospectivo → **⟳ Atualizar rodada (ESPN)** busca placar, estatísticas e calendário e **liquida** os registros. Runbook completo: [[a_runbook_operacao|Operação BRA 2026]].

---

## 🧰 Comandos disponíveis

| Comando | Descrição |
|---|---|
| `python -m pytest -q` | Suíte completa (99 testes) |
| `python -m scb.ingest --download` | Baixa o snapshot das fontes (único passo que usa internet) |
| `python -m scb.ingest` | CSV → SQLite (idempotente, guarda anti-duplicata ±2 dias) |
| `python -m scb.elo_engine` | Ratings Elo point-in-time |
| `python -m scb.features_pit [--incremental]` | Features anti look-ahead |
| `python -m scb.draw_curve` | Curva de empate empírica por liga |
| `python -m scb.predictor [--incremental]` | Gera as previsões versionadas |
| `python -m scb.backtest_harness` | Backtest walk-forward contra as 4 réguas |
| `python -m scb.simulate_league --season 2026` | Monte Carlo da tabela (título/G4/G6/Z4) |
| `python -m scb.registrar auto --dias 4` | Registro prospectivo imutável da rodada |
| `python -m scb.web` | Sobe a web local |
| `python scripts/baixar_escudos.py` / `_bra.py` | Escudos (uso pessoal, 1x por temporada) |
| `python scripts/poc_m1.py` | Inventário da fonte de dados (POC M1) |

---

## 🗂️ Estrutura do projeto

```
SCB/
├── 77777777_SCB_Project_DOCs/       # TODA a documentação (vault Obsidian)
│   ├── INDICE.md                    # nota-casa: mapa de navegação
│   ├── a_contexto/                  # a verdade do projeto
│   │   ├── a_contexto_fonte.md      # CONTEXT — ≤1 página, colado em toda sessão
│   │   ├── b_plano.md               # plano CONGELADO (arquitetura, milestones M0–M7)
│   │   ├── c_regras_de_negocio.md   # as 7 regras inegociáveis
│   │   ├── d_modelo_matematico.md   # contrato matemático SCB v1.0 (congelado)
│   │   ├── e_dados.md               # fontes, colunas, schema-alvo, lacunas
│   │   ├── f_decisoes_arquitetura.md# ADRs D-NN + questões Q-NN (append-only)
│   │   └── g_heranca_scm.md         # mapa do port + lições pagas pelo SCM
│   ├── b_processo/                  # como se trabalha aqui
│   │   ├── a_manual_do_dono.md      # papel do dono do projeto
│   │   ├── b_checklist.md           # portões de aceite por tipo de entrega
│   │   ├── c_backlog.md             # quadro Kanban por milestone
│   │   ├── d_aprendizados_para_agentes.md
│   │   ├── e_padrao_do_repositorio.md  # ESTE padrão, para replicar em novos projetos
│   │   └── prompts/00..05           # prompts de papel, um por fase
│   ├── c_docs_tecnicos/             # operação e evidências
│   │   ├── a_runbook_operacao.md    # runbook da rodada do BRA
│   │   ├── b_backtest_baseline.md   # números do portão da M4
│   │   └── c_poc_m1_dados.md        # inventário da fonte
│   └── d_historico/
│       └── a_changelog.md           # log datado (ninguém carrega; só escreve)
├── scb_analytics/                   # TODO o código
│   ├── scb/                         # o pacote (motor, web, templates)
│   ├── scripts/                     # utilitários avulsos (rodados à mão)
│   ├── dados/                       # snapshots curados + banco SQLite (regenerável)
│   ├── static/logos/                # escudos
│   ├── tests/                       # pytest — 1 arquivo por módulo
│   ├── Abrir SCB.bat                # launcher da web (Windows)
│   ├── requirements.txt
│   └── README.md                    # README técnico do código
├── .gitattributes                   # normalização de fim-de-linha (LF)
├── .gitignore
└── README.md                        # este arquivo — porta de entrada
```

Regra de ouro: **documentação em `77777777_SCB_Project_DOCs/`, código em `scb_analytics/`.** A raiz só tem o README e os arquivos de configuração do repositório.

---

## 📖 Este repositório é um vault Obsidian

Abrir no Obsidian: **Open folder as vault** → selecionar a pasta `SCB`. Nota-casa: [[INDICE|Índice]] (fixe-a).
Plugins recomendados: **Kanban** (o [[c_backlog|BACKLOG]] usa esse formato) e **Obsidian Git** (commit/push de dentro do app; opcional).
O `.gitignore` já ignora o workspace volátil do Obsidian.

---

## 📐 Convenções de desenvolvimento

- **Nomes de arquivo de doc:** `prefixo_de_ordem` + `snake_case` minúsculo, sem acento (`c_regras_de_negocio.md`). O prefixo é a **ordem de leitura** da pasta; nos prompts o número é a **fase** do pipeline.
- **Uma verdade por assunto:** estado atual mora só em `a_contexto_fonte.md`; histórico só em `a_changelog.md`; decisões só em `f_decisoes_arquitetura.md`. Nenhum doc repete o que outro já diz — aponta.
- **Docs têm cabeçalho YAML** com `status` (atual/congelado/histórico) e `data`.
- **Decisão nova = D-NN** em `f_decisoes_arquitetura.md` (append-only, adotada **e** rejeitada). **Bug = QA-NN**, citado na mensagem do commit.
- **Nada entra no modelo sem portão:** ΔBrier pareado com IC bootstrap (B=10k, seed fixa) que não cruza zero + guardas de não-regressão.
- **Nada lê a internet dentro do cálculo** — download é sempre um passo à parte, sobre snapshot em disco.
- **Nomes de time no padrão football-data (EN)**; Monte Carlo sempre com seed fixa.
- **Mudou fórmula?** Bump de `MODEL_VERSION` + rebuild completo documentado.
- **Fim de linha LF** no repositório (garantido pelo `.gitattributes`); `.bat` fica CRLF.
- **Nunca versionar:** `.venv/`, `__pycache__/`, `.pytest_cache/`, `*.sqlite`, `*.zip`, `.env`, tokens/credenciais, sondas descartáveis (`_sonda_*.json`) e o workspace do Obsidian.

O padrão completo — pensado para ser copiado em projetos novos — está em [[e_padrao_do_repositorio|Padrão do repositório]].

---

## 🧪 Tecnologias

| Tecnologia | Papel |
|---|---|
| Python 3.11+ | Linguagem |
| NumPy / pandas | Motor numérico e manipulação dos dados |
| SQLite | Banco local (`dados/scb.sqlite`, regenerável) |
| Flask | Web local (5 telas) |
| pytest | Suíte de testes (99), com teste anti look-ahead obrigatório |
| Obsidian | Vault de documentação (wikilinks, Kanban) |
| football-data.co.uk | Fonte primária de resultados e odds (snapshot) |
| ESPN (API pública) | 2ª fonte grátis da rodada: placar, stats e calendário (D-42) |

---

## 🧬 Origem

Sistema-mãe: **SCM** (vault Obsidian + `scm_analytics/`, modelo `baseline-v0.5.1-confed`, ~194 testes). A análise que origina este projeto é *"Viabilidade — modelo para ligas de clubes (Brasileirão e alternativas)"* (2026-06-28). **Não carregar o vault do SCM inteiro em sessão** — os docs de `a_contexto/` já destilam o necessário.

---

*SCB — Sistema Campeonato Brasileiro | `scb-v0.4-sot-goals-e0` | Projeto de vibe coding · 2026*
