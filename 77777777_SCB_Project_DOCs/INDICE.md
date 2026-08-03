---
tags: [scb, indice, mapa]
status: atual
tipo: indice
data: 2026-08-02
aliases: ["Home", "Mapa do vault"]
---

# Índice — SCB (Sistema Campeonato Brasileiro)

> Nota-casa do vault. **Fixe esta nota** (pin) e navegue por aqui.
> Porta de entrada do repositório (como rodar, estrutura, tecnologias): [[README]].

## 🧭 Toda sessão de trabalho começa assim

Prompt do papel (abaixo) + [[a_contexto_fonte|CONTEXT]] + só o arquivo do momento → pedir **delta** → conferir [[b_checklist|CHECKLIST]] → registrar D-NN em [[f_decisoes_arquitetura|DECISIONS]] → atualizar [[a_contexto_fonte|CONTEXT]] por substituição (o datado vai pro [[a_changelog|CHANGELOG]]).

## Visão do projeto

- [[a_manual_do_dono|Manual do dono]] — **comece aqui, Gustavo**: seu papel, o ciclo de sessão, onde você entra em cada milestone
- [[a_contexto_fonte|CONTEXT]] — contexto-fonte (≤1 página, o que se cola em TODA sessão) · **é aqui que mora o estado atual**
- [[b_plano|PLANO]] — plano congelado v1.0 (arquitetura, milestones M0–M7, riscos)
- [[README]] — porta de entrada: como rodar, comandos, estrutura, convenções
- [[c_backlog|BACKLOG]] — quadro de tarefas (plugin Kanban)
- [[f_decisoes_arquitetura|DECISIONS]] — ADRs D-NN + questões abertas Q-NN
- [[a_changelog|CHANGELOG]] — log datado (fora do contexto das sessões)
- [[b_checklist|CHECKLIST]] — portões de aceite por tipo de entrega
- [[e_padrao_do_repositorio|Padrão do repositório]] — como este repo é organizado e como replicar em projetos novos

## Contexto para agentes (a "memória destilada" do SCM)

- [[d_aprendizados_para_agentes|Aprendizados para agentes]] — **lições deste projeto p/ os próximos** (o que seguir, o que evitar; honesto)
- [[c_regras_de_negocio|REGRAS-DE-NEGOCIO]] — as 7 inegociáveis + regras de trabalho
- [[d_modelo_matematico|MODELO-MATEMATICO]] — contrato SCB v1.0 (congelado): o que fica/sai/recalibra/candidatos C1–C7
- [[g_heranca_scm|HERANCA-SCM]] — mapa de port módulo a módulo + lições pagas
- [[e_dados|DADOS]] — fontes, colunas, schema-alvo, lacunas declaradas, POC M1

## Prompts de papel (colar no início da sessão conforme a fase)

- [[00_bootstrap_contexto]] · Fase 0 — manter o CONTEXT verdadeiro
- [[01_planejador]] · Fase 1 — planejar/defender o plano congelado
- [[02_implementador]] · Fases 2–3 — construir módulo a módulo, por delta
- [[03_qa_adversarial]] · Fase 4 — quebrar o que foi construído
- [[04_auditor_evolucao]] · Fase 5 — busca céptica de melhorias
- [[05_revisao_entrega]] · Fase 6 — empacotar e conferir

## Operação e resultados

- [[a_runbook_operacao|Operação BRA 2026]] — runbook da rodada (1 clique na web)
- [[b_backtest_baseline|Backtest baseline (2026-07-16)]] — os números do portão da M4
- [[c_poc_m1_dados|POC M1 — dados (2026-07-15)]] — inventário da fonte

## Onde fica cada coisa

| Pasta | O que guarda |
|---|---|
| `a_contexto/` | a verdade do projeto: contexto, plano, regras, contrato, dados, decisões |
| `b_processo/` | como se trabalha: manual, checklist, backlog, aprendizados, padrão, `prompts/` |
| `c_docs_tecnicos/` | runbook de operação, backtest baseline, POC de dados |
| `d_historico/` | changelog datado (ninguém carrega; só escreve) |
| `../scb_analytics/` | todo o código, dados curados, testes e a web |

> **Estado do projeto:** não é repetido aqui — a verdade viva está em [[a_contexto_fonte|CONTEXT]] (regra 2 do [[e_padrao_do_repositorio|Padrão do repositório]]: uma verdade por assunto).
