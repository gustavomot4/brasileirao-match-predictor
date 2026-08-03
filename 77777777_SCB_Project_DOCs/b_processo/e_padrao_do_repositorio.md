---
tags: [scb, padrao, processo, meta]
status: atual
tipo: padrao
data: 2026-08-02
aliases: ["Padrão do repositório", "Padrão SPO", "Convenções"]
---

# Padrão do repositório — como todo projeto meu deve ser organizado

> Padrão extraído do **SPO** (`spo-inventory-management`) e aplicado ao SCB em 2026-08-02.
> Serve para **replicar em projetos novos**: copiar a estrutura, trocar o nome do projeto e seguir as regras.
> Quem lê isto: eu, e todo agente de IA que abrir o repositório.

---

## 1. As 3 regras que sustentam o padrão

1. **Duas pastas, uma raiz limpa.** Toda documentação em `77777777_<PROJ>_Project_DOCs/`; todo código em uma única pasta de código. Na raiz só ficam o `README.md` e arquivos de configuração do repositório.
2. **Uma verdade por assunto.** Cada informação tem **um** dono. Nenhum arquivo repete o que outro já diz — ele **aponta**. Duplicata é dívida: envelhece em silêncio e depois mente.
3. **O que não tem dono, não entra.** Arquivo sem papel definido (rascunho vazio, sonda descartável, cache, duplicata "por garantia") não é versionado. Se já entrou, sai — o histórico do git guarda.

---

## 2. Estrutura de pastas

```
<PROJETO>/
├── 77777777_<PROJ>_Project_DOCs/   # documentação (prefixo 7777... = fica sempre no topo)
│   ├── INDICE.md                   # nota-casa: mapa de navegação do vault
│   ├── a_contexto/                 # a VERDADE do projeto
│   ├── b_processo/                 # como se TRABALHA (inclui prompts/)
│   ├── c_docs_tecnicos/            # runbooks, evidências, relatórios
│   ├── d_historico/                # changelog datado
│   └── e_qa/                       # relatórios de QA, quando forem arquivos próprios
├── <pasta_de_codigo>/              # todo o código + seu README técnico
│   ├── <pacote>/                   # o pacote/aplicação
│   ├── scripts/                    # utilitários avulsos rodados à mão
│   ├── tests/                      # 1 arquivo de teste por módulo
│   └── dados/ | prisma/ | public/  # dados, schema, estáticos — conforme a stack
├── .gitattributes
├── .gitignore
└── README.md                       # porta de entrada
```

**No SCB:** `77777777_SCB_Project_DOCs/` + `scb_analytics/`.
**No SPO:** `77777777_SPO_Project_DOCs/` + `src/`.

`e_qa/` só existe quando o QA vira arquivo separado (como no SPO, uma passagem por arquivo). No SCB os achados são **QA-NN** dentro de `a_contexto/f_decisoes_arquitetura.md` — pasta vazia não se cria.

---

## 3. Nomes de arquivo

| Regra | Exemplo |
|---|---|
| Docs: `prefixo_de_ordem` + `snake_case` minúsculo, **sem acento e sem espaço** | `c_regras_de_negocio.md` |
| O prefixo é a **ordem de leitura** da pasta, não uma categoria | `a_`, `b_`, `c_`… |
| Quando o número já tem significado, ele **manda** (fase, versão, passo) | `prompts/03_qa_adversarial.md` = fase 3 |
| Pontos de entrada em MAIÚSCULA (convenção universal, o GitHub renderiza) | `README.md`, `INDICE.md` |
| Código segue a convenção da linguagem, não esta | `backtest_harness.py`, `tailwind.config.ts` |
| Teste espelha o módulo | `scb/odds.py` → `tests/test_odds.py` |
| Nada de "Sem título", "novo", "final", "v2", "cópia" | — |

Renomeou? Use **`git mv`** — o histórico do arquivo sobrevive.

---

## 4. O que cada pasta de doc contém

**`a_contexto/` — a verdade.** O que o projeto é, o que decidiu e por quê.

- `a_contexto_fonte.md` — **≤ 1 página**, atualizado **por substituição**. É o que se cola em toda sessão de IA. Estado atual mora **só aqui**.
- `b_plano.md` — plano **congelado**. Mudança de rumo vira decisão nova, não replanejamento.
- `c_regras_de_negocio.md` — as regras inegociáveis.
- `d_modelo_matematico.md` / `d_schema.md` — o contrato técnico congelado do domínio.
- `e_dados.md` — fontes, colunas, lacunas **declaradas** (lacuna nunca vira invenção).
- `f_decisoes_arquitetura.md` — **ADRs D-NN**, append-only, registrando adoções **e rejeições** (memória contra re-explorar o que já falhou) + questões abertas Q-NN.
- `g_heranca_*.md` — o que veio de um projeto anterior e as lições já pagas.

**`b_processo/` — como se trabalha.**

- `a_manual_do_dono.md` — o papel de quem dirige: o que só ele decide.
- `b_checklist.md` — os **portões de aceite** por tipo de entrega.
- `c_backlog.md` — quadro Kanban; concluído fica em ✅, não se apaga.
- `d_aprendizados_para_agentes.md` — o que seguir e o que evitar, honesto.
- `e_padrao_do_repositorio.md` — este arquivo.
- `prompts/` — um prompt de papel por fase do pipeline.

**`c_docs_tecnicos/`** — runbook de operação, relatórios de baseline/benchmark, inventários. O que se consulta para **operar**, não para decidir.

**`d_historico/a_changelog.md`** — log datado. **Ninguém carrega em sessão; só se escreve nele.** É o que permite o contexto-fonte continuar com 1 página.

---

## 5. Ciclo de trabalho (pipeline de 6 fases)

```
abrir sessão
  → colar: prompt do papel (b_processo/prompts/) + a_contexto_fonte.md + SÓ o arquivo do momento
  → pedir DELTA (o trecho que muda), nunca "refaz tudo"
  → passar no PORTÃO (b_checklist.md) — rodar na máquina real, não confiar no sandbox
  → registrar D-NN (decisão) / QA-NN (bug)
  → atualizar a_contexto_fonte.md POR SUBSTITUIÇÃO; o datado vai para a_changelog.md
  → commit
```

| Fase | Prompt | Portão |
|---|---|---|
| 0 Bootstrap | `00_bootstrap_contexto` | contexto-fonte ≤ 1 página + critério de aceite escrito |
| 1 Planejamento | `01_planejador` | aprovação do dono → o plano congela |
| 2–3 Implementação | `02_implementador` | testes verdes por módulo, um módulo por vez |
| 4 QA adversarial | `03_qa_adversarial` | nenhum achado crítico/alto aberto |
| 5 Evolução | `04_auditor_evolucao` | evidência estatística + guardas de não-regressão |
| 6 Entrega | `05_revisao_entrega` | checklist de empacotamento completo |

---

## 6. Cabeçalho dos documentos

Todo `.md` de doc começa com YAML:

```yaml
---
tags: [projeto, tipo]
status: atual | congelado | histórico | vivo
tipo: contexto | plano | guia | runbook | checklist | padrao
data: AAAA-MM-DD
---
```

`status` e `data` são obrigatórios: é o que separa "isto vale hoje" de "isto é registro do que valia".

---

## 7. Git

- **Mensagem de commit:** `TIPO: o que mudou (por quê)`. Tipos em uso: `ADD`, `FIX`, `DOCS`, `REFACTOR`, `CHORE`, ou o marcador do projeto (`M6.7:`, `D-42/D-43:`).
- Bug corrigido cita o **QA-NN**; decisão cita o **D-NN**.
- `.gitattributes` normaliza fim de linha para **LF** (`.bat` fica CRLF) — evita o churn CRLF↔LF do Windows.
- **Nunca versionar:** `.venv/`, `node_modules/`, `__pycache__/`, `.pytest_cache/`, bancos regeneráveis (`*.sqlite`, `*.db`), `*.zip`, `.env`, tokens e credenciais, sondas/rascunhos descartáveis, workspace volátil do editor.
- **Sempre versionar:** dados curados e snapshots que o projeto precisa para rodar do zero (lição paga: sem eles o zip "completo" não roda).

---

## 8. README — a porta de entrada

O `README.md` da raiz responde, nesta ordem:

1. **O que é** (1 parágrafo) + **stack** em uma linha + o aviso de limite, se houver.
2. **Como o projeto foi feito** — o pipeline de agentes, para quem for continuar.
3. **Como rodar** — do zero, copiável, incluindo o que é pré-requisito.
4. **Comandos disponíveis** — tabela.
5. **Estrutura do projeto** — árvore comentada.
6. **Convenções** — o resumo deste documento.
7. **Tecnologias** — tabela.

O README **não é a fonte da verdade** do estado: ele mostra o essencial e aponta para o contexto-fonte. Quando o código tem README próprio (`<pasta_de_codigo>/README.md`), ele cobre só o técnico e aponta para os docs.

---

## 9. Checklist para abrir um projeto novo

- [ ] Criar `77777777_<PROJ>_Project_DOCs/` com `a_contexto/`, `b_processo/`, `c_docs_tecnicos/`, `d_historico/`
- [ ] Copiar `b_processo/prompts/00..05` e este `e_padrao_do_repositorio.md` do projeto anterior
- [ ] Escrever `a_contexto_fonte.md` (≤1 página) **antes de qualquer código** — fase 0
- [ ] Escrever o critério de aceite no dia 1 (portões), em `b_checklist.md`
- [ ] `.gitignore` + `.gitattributes` (LF) antes do primeiro commit
- [ ] `README.md` na estrutura da seção 8
- [ ] `INDICE.md` como nota-casa do vault
- [ ] Primeiro commit só depois de conferir que nada regenerável/secreto entrou
