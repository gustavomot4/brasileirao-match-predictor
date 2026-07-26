"""espn — 2ª fonte GRÁTIS e estruturada (D-NN): resultados + estatísticas + jogos futuros
do Brasileirão via API pública da ESPN (site.api.espn.com, sem chave, sem custo).

Substitui a api-futebol (paga) para a operação da rodada. Respeita as regras:
  - R$ 0 (sem chave/assinatura);
  - NÃO inventa: lê CAMPOS estruturados (não texto); time fora do mapa é PULADO com aviso;
  - download é passo à parte (o cálculo/web lê o snapshot em disco).

Este módulo é PURO no parse (testável sem rede). A parte de rede (`fetch`) importa
`requests` só quando chamada. Endpoint não-oficial (zona cinza de ToS, uso pessoal/estudo),
mesma categoria da football-data e do CDN de escudos já usados no projeto.

Mapa de times ancorado no ID ESTÁVEL da ESPN -> nome canônico no banco (football-data).
"""
from __future__ import annotations

from typing import Optional

BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard"

# ESPN team_id -> nome do time como está no banco (teams.name). IDs não mudam; nomes/acentos sim.
ESPN_TEAM = {
    "3458": "Athletico-PR", "7632": "Atletico-MG", "9967": "Bahia", "6086": "Botafogo RJ",
    "9318": "Chapecoense-SC", "874": "Corinthians", "3456": "Coritiba", "2022": "Cruzeiro",
    "819": "Flamengo RJ", "3445": "Fluminense", "6273": "Gremio", "1936": "Internacional",
    "9169": "Mirassol", "2029": "Palmeiras", "6079": "Bragantino", "4936": "Remo",
    "2674": "Santos", "2026": "Sao Paulo", "3454": "Vasco", "3457": "Vitoria",
}

# nomes das colunas do snapshot dados/bra_stats.csv (mesmo schema da api-futebol)
COLS = ["date", "home", "away", "home_score", "away_score", "ht_home", "ht_away",
        "shots_home", "shots_away", "sot_home", "sot_away", "fouls_home", "fouls_away",
        "corners_home", "corners_away", "yellow_home", "yellow_away", "red_home", "red_away",
        "possession_home", "possession_away", "pass_acc_home", "pass_acc_away",
        "tackles_home", "tackles_away", "saves_home", "saves_away"]


def _stat(stats: list, name: str) -> Optional[str]:
    for s in stats or []:
        if s.get("name") == name:
            return s.get("displayValue")
    return None


def _int(v) -> Optional[int]:
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return None


def _first_half(dv: str) -> bool:
    """'18' -> True, '45'+7' -> True (acréscimo do 1ºT), '52' -> False. Best-effort."""
    if not dv:
        return False
    base = dv.split("'")[0].strip()
    try:
        return int(base) <= 45
    except ValueError:
        return False


def parse_event(ev: dict) -> Optional[dict]:
    """Um jogo da ESPN -> dict com status + (se finalizado) placar+stats OU (se futuro) só o
    confronto. Retorna None e um motivo se algum time está fora do mapa (NÃO inventa)."""
    comp = (ev.get("competitions") or [ev])[0]
    state = (((comp.get("status") or ev.get("status") or {}).get("type")) or {}).get("state")
    date = (comp.get("date") or ev.get("date") or "")[:10]
    cs = comp.get("competitors") or []
    home = next((c for c in cs if c.get("homeAway") == "home"), None)
    away = next((c for c in cs if c.get("homeAway") == "away"), None)
    if not home or not away:
        return {"skip": "sem mandante/visitante", "id": ev.get("id")}
    hid = str((home.get("team") or {}).get("id"))
    aid = str((away.get("team") or {}).get("id"))
    if hid not in ESPN_TEAM or aid not in ESPN_TEAM:
        falta = [str((c.get("team") or {}).get("displayName")) for c, i in ((home, hid), (away, aid)) if i not in ESPN_TEAM]
        return {"skip": f"time fora do mapa: {', '.join(falta)}", "id": ev.get("id")}
    H, A = ESPN_TEAM[hid], ESPN_TEAM[aid]

    if state == "pre":                       # jogo FUTURO -> fixture
        return {"kind": "fixture", "date": date, "home": H, "away": A}
    if state != "post":                      # ao vivo / adiado -> ignora (settle espera FT)
        return {"skip": f"status={state}", "id": ev.get("id"), "date": date, "home": H, "away": A}

    hs, aws = _int(home.get("score")), _int(away.get("score"))
    hsr = home.get("statistics") or []
    asr = away.get("statistics") or []
    # cartões e HT vêm dos eventos (details); o resto do bloco statistics
    yh = yl = rh = rl = 0
    hth = hta = 0
    for d in (comp.get("details") or []):
        tid = str((d.get("team") or {}).get("id"))
        mine_home = tid == hid
        if d.get("yellowCard"):
            yh += mine_home; yl += (not mine_home)
        if d.get("redCard"):
            rh += mine_home; rl += (not mine_home)
        if d.get("scoringPlay") and _first_half((d.get("clock") or {}).get("displayValue", "")):
            # gol contra conta pro adversário
            scorer_home = mine_home ^ bool(d.get("ownGoal"))
            hth += scorer_home; hta += (not scorer_home)

    row = {c: "" for c in COLS}
    row.update({
        "date": date, "home": H, "away": A, "home_score": hs, "away_score": aws,
        "ht_home": hth, "ht_away": hta,
        "shots_home": _int(_stat(hsr, "totalShots")), "shots_away": _int(_stat(asr, "totalShots")),
        "sot_home": _int(_stat(hsr, "shotsOnTarget")), "sot_away": _int(_stat(asr, "shotsOnTarget")),
        "fouls_home": _int(_stat(hsr, "foulsCommitted")), "fouls_away": _int(_stat(asr, "foulsCommitted")),
        "corners_home": _int(_stat(hsr, "wonCorners")), "corners_away": _int(_stat(asr, "wonCorners")),
        "yellow_home": yh, "yellow_away": yl, "red_home": rh, "red_away": rl,
        "possession_home": _int(_stat(hsr, "possessionPct")), "possession_away": _int(_stat(asr, "possessionPct")),
    })
    return {"kind": "result", "row": row}


def parse_scoreboard(data: dict) -> dict:
    """JSON de /scoreboard -> {results:[row...], fixtures:[{date,home,away}...], skipped:[...]}."""
    results, fixtures, skipped = [], [], []
    for ev in (data.get("events") or []):
        out = parse_event(ev)
        if out is None:
            continue
        if out.get("kind") == "result":
            results.append(out["row"])
        elif out.get("kind") == "fixture":
            fixtures.append({"league": "BRA", "round": "", "date": out["date"],
                             "home": out["home"], "away": out["away"]})
        elif "skip" in out:
            skipped.append(out["skip"])
    return {"results": results, "fixtures": fixtures, "skipped": skipped}


def _calendar_dates(sess, base_json=None) -> list:
    """Datas de jogo da temporada (leagues[0].calendar), como AAAAMMDD."""
    data = base_json or sess.get(BASE, timeout=30).json()
    cal = ((data.get("leagues") or [{}])[0].get("calendar")) or []
    return [c[:10].replace("-", "") for c in cal if isinstance(c, str)]


def fetch(dates: Optional[list] = None) -> dict:
    """Parte de REDE (chame no botão/CLI). Busca o scoreboard por data e junta tudo.
    `dates`=None -> usa o calendário da temporada. Determinístico no parse; a rede é só
    coleta. Devolve results+fixtures+skipped agregados (dedup por (date,home,away))."""
    import time
    import requests
    sess = requests.Session()
    sess.headers.update({"User-Agent": "SCB/1.0 (uso pessoal)"})
    base = sess.get(BASE, timeout=30).json()
    dates = dates or _calendar_dates(sess, base)
    res, fix, skip = {}, {}, []
    for d in dates:
        try:
            j = sess.get(BASE, params={"dates": d}, timeout=30).json()
        except Exception as e:
            skip.append(f"{d}: erro de rede {e}")
            continue
        p = parse_scoreboard(j)
        for r in p["results"]:
            res[(r["date"], r["home"], r["away"])] = r
        for f in p["fixtures"]:
            fix[(f["date"], f["home"], f["away"])] = f
        skip += p["skipped"]
        time.sleep(0.3)
    return {"results": list(res.values()), "fixtures": list(fix.values()), "skipped": skip}


# ---- aplicar o que a ESPN trouxe nos snapshots em disco (offline; baixo churn) ----------

def _paths():
    from pathlib import Path
    d = Path(__file__).resolve().parent.parent / "dados"
    return d / "bra_stats.csv", d / "fixtures.csv"


def _write_results(rows: list) -> int:
    """Funde os resultados no bra_stats.csv. Só PREENCHE o que falta (linha ausente ou sem
    placar) — não sobrescreve dado já completo (evita churn e reescrever fonte verificada)."""
    import csv
    import os
    BRA_STATS, _ = _paths()
    have = {}
    if BRA_STATS.exists():
        with BRA_STATS.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                have[(r["date"], r["home"], r["away"])] = r
    novos = 0
    for r in rows:
        k = (r["date"], r["home"], r["away"])
        cur = have.get(k)
        if cur is None or str(cur.get("home_score") or "").strip() == "":
            have[k] = r
            novos += 1
    with BRA_STATS.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        for k in sorted(have, key=lambda x: (x[0] or "")):
            w.writerow(have[k])
        fh.flush()
        os.fsync(fh.fileno())
    return novos


def _write_fixtures(fixtures: list) -> int:
    """Atualiza o calendário do BRA: reescreve a DATA de confrontos existentes (remarcações)
    e adiciona confrontos novos, MANTENDO as outras ligas (E0) e os números de rodada."""
    import csv
    import os
    _, FIX = _paths()
    campos = ["league", "round", "date", "home", "away"]
    linhas = []
    if FIX.exists():
        with FIX.open(encoding="utf-8") as fh:
            linhas = list(csv.DictReader(fh))
    idx = {(r["league"], r["home"], r["away"]): r for r in linhas}
    mudou = 0
    for f in fixtures:
        k = ("BRA", f["home"], f["away"])
        if k in idx:
            if (idx[k].get("date") or "") != f["date"]:        # remarcação
                idx[k]["date"] = f["date"]; mudou += 1
        else:
            linhas.append({"league": "BRA", "round": "", "date": f["date"],
                           "home": f["home"], "away": f["away"]}); mudou += 1
    with FIX.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        for r in linhas:
            w.writerow(r)
        fh.flush()
        os.fsync(fh.fileno())
    return mudou


def atualizar_rodada(conn) -> dict:
    """UM CLIQUE: busca a ESPN -> grava snapshots -> casa em matches/match_stats -> liquida.
    Rede só aqui (download à parte); o cálculo segue lendo o snapshot. Devolve resumo."""
    from . import ingest, registrar
    dados = fetch()
    novos = _write_results(dados["results"])
    fx = _write_fixtures(dados["fixtures"])
    BRA_STATS, _ = _paths()
    casados = ingest.load_bra_stats(conn, BRA_STATS)
    conn.commit()
    liq = registrar.settle(conn)
    return {"resultados_novos": novos, "stats_casados": casados,
            "fixtures_atualizados": fx, "liquidados": liq.get("preenchidos", 0),
            "em_aberto": liq.get("em_aberto", 0), "pulados": len(dados["skipped"]),
            "avisos": dados["skipped"][:8]}
