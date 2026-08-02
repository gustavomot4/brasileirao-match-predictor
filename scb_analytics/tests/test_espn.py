"""Testes do parser ESPN (scb/espn.py) — PUROS, sem rede. Fixture com valores REAIS
da rodada 2026-05-31 (Bragantino 3-1 Inter, Palmeiras 1-0 Chape) + um jogo futuro
+ um time fora do mapa (deve pular, não inventar)."""
from scb import espn


def _comp(state, date, competitors, details=None, name=None):
    if name is None:
        name = "STATUS_FULL_TIME" if state == "post" else state.upper()
    return {"competitions": [{"status": {"type": {"state": state, "name": name}}, "date": date,
                              "competitors": competitors, "details": details or []}]}


def _team(ha, tid, name, score=None, stats=None):
    c = {"homeAway": ha, "team": {"id": tid, "displayName": name}, "statistics": stats or []}
    if score is not None:
        c["score"] = score
    return c


def _st(**kw):
    campos = {"totalShots": "shots", "shotsOnTarget": "sot", "foulsCommitted": "fouls",
              "wonCorners": "corners", "possessionPct": "poss"}
    return [{"name": k, "displayValue": str(kw[v])} for k, v in campos.items() if v in kw]


SCOREBOARD = {"events": [
    # Bragantino 3-1 Internacional — gols 18', 45'+7', 52' (Bra) e 79' (Int) => HT 2-0
    _comp("post", "2026-05-31T14:00Z", [
        _team("home", "6079", "Red Bull Bragantino", "3", _st(shots=18, sot=7, fouls=19, corners=6, poss="51.7")),
        _team("away", "1936", "Internacional", "1", _st(shots=8, sot=2, fouls=17, corners=1, poss="48.3")),
    ], details=[
        {"team": {"id": "6079"}, "scoringPlay": True, "ownGoal": False, "clock": {"displayValue": "18'"}},
        {"team": {"id": "1936"}, "yellowCard": True, "clock": {"displayValue": "22'"}},
        {"team": {"id": "6079"}, "scoringPlay": True, "ownGoal": False, "clock": {"displayValue": "45'+7'"}},
        {"team": {"id": "6079"}, "scoringPlay": True, "ownGoal": False, "clock": {"displayValue": "52'"}},
        {"team": {"id": "1936"}, "scoringPlay": True, "ownGoal": False, "clock": {"displayValue": "79'"}},
    ]),
    # Palmeiras 1-0 Chapecoense — vermelho do Palmeiras aos 43', gol aos 65' => HT 0-0, red_home 1
    _comp("post", "2026-05-31T19:00Z", [
        _team("home", "2029", "Palmeiras", "1", _st(shots=13, sot=4, fouls=9, corners=3, poss="48.3")),
        _team("away", "9318", "Chapecoense", "0", _st(shots=15, sot=3, fouls=9, corners=2, poss="51.7")),
    ], details=[
        {"team": {"id": "2029"}, "redCard": True, "clock": {"displayValue": "43'"}},
        {"team": {"id": "2029"}, "scoringPlay": True, "ownGoal": False, "clock": {"displayValue": "65'"}},
    ]),
    # jogo FUTURO (pre) -> fixture
    _comp("pre", "2026-08-08T20:00Z", [
        _team("home", "819", "Flamengo"), _team("away", "2029", "Palmeiras"),
    ]),
    # time FORA do mapa -> pular (não inventar)
    _comp("post", "2026-08-01T20:00Z", [
        _team("home", "99999", "Time Fantasma", "2"), _team("away", "2029", "Palmeiras", "0"),
    ]),
    # ADIADO: a ESPN marca como state="post" (a pegadinha!) mas name=STATUS_POSTPONED, score 0-0.
    # NÃO pode virar resultado — vira "cancelado" (p/ desfazer um 0-0 fantasma).
    _comp("post", "2026-07-29T20:00Z", [
        _team("home", "2026", "São Paulo", "0"), _team("away", "2674", "Santos", "0"),
    ], name="STATUS_POSTPONED"),
]}


def test_parse_scoreboard_conta():
    p = espn.parse_scoreboard(SCOREBOARD)
    assert len(p["results"]) == 2                          # só os 2 STATUS_FULL_TIME
    assert len(p["fixtures"]) == 1
    assert len(p["cancelados"]) == 1                        # o adiado NÃO virou resultado
    assert any("fora do mapa" in s for s in p["skipped"])


def test_adiado_nao_vira_resultado():
    """O bug real: ESPN marca adiado com state='post'. Só STATUS_FULL_TIME pode virar placar."""
    p = espn.parse_scoreboard(SCOREBOARD)
    assert not any(r["home"] == "Sao Paulo" for r in p["results"])   # SP×Santos adiado: fora dos resultados
    c = p["cancelados"][0]
    assert c["home"] == "Sao Paulo" and c["away"] == "Santos" and c["date"] == "2026-07-29"


def test_resultado_bragantino():
    p = espn.parse_scoreboard(SCOREBOARD)
    r = next(x for x in p["results"] if x["home"] == "Bragantino")
    assert r["away"] == "Internacional"
    assert (r["home_score"], r["away_score"]) == (3, 1)
    assert (r["ht_home"], r["ht_away"]) == (2, 0)          # HT derivado do minuto do gol
    assert (r["sot_home"], r["sot_away"]) == (7, 2)
    assert (r["corners_home"], r["corners_away"]) == (6, 1)
    assert (r["possession_home"], r["possession_away"]) == (52, 48)   # 51.7/48.3 arredondados
    assert (r["yellow_home"], r["yellow_away"]) == (0, 1)
    assert (r["red_home"], r["red_away"]) == (0, 0)


def test_vermelho_e_ht_palmeiras():
    p = espn.parse_scoreboard(SCOREBOARD)
    r = next(x for x in p["results"] if x["home"] == "Palmeiras")
    assert (r["home_score"], r["away_score"]) == (1, 0)
    assert (r["ht_home"], r["ht_away"]) == (0, 0)          # gol foi aos 65' (2ºT)
    assert r["red_home"] == 1
    assert r["away"] == "Chapecoense-SC"                    # nome do banco, via ID


def test_fixture_futuro():
    p = espn.parse_scoreboard(SCOREBOARD)
    f = p["fixtures"][0]
    assert f["home"] == "Flamengo RJ" and f["away"] == "Palmeiras"
    assert f["date"] == "2026-08-08" and f["league"] == "BRA"


def test_schema_bate_bra_stats():
    p = espn.parse_scoreboard(SCOREBOARD)
    r = p["results"][0]
    assert set(r.keys()) == set(espn.COLS)                 # mesmo schema do bra_stats.csv
    for k in ("pass_acc_home", "tackles_home", "saves_home"):
        assert r[k] == ""                                  # scoreboard não traz -> em branco, não zero


def _row(**kw):
    r = {c: "" for c in espn.COLS}
    r.update(kw)
    return r


def test_write_results_nao_sobrescreve_completo(tmp_path, monkeypatch):
    import csv
    bra, fix = tmp_path / "bra_stats.csv", tmp_path / "fixtures.csv"
    monkeypatch.setattr(espn, "_paths", lambda: (bra, fix))
    with bra.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=espn.COLS); w.writeheader()
        w.writerow(_row(date="2026-05-31", home="Palmeiras", away="Chapecoense-SC", home_score=9, away_score=9))
    n = espn._write_results([
        _row(date="2026-05-31", home="Palmeiras", away="Chapecoense-SC", home_score=1, away_score=0),  # já completo
        _row(date="2026-06-01", home="Santos", away="Vasco", home_score=2, away_score=1),               # novo
    ])
    by = {(r["home"], r["away"]): r for r in csv.DictReader(bra.open(encoding="utf-8"))}
    assert by[("Palmeiras", "Chapecoense-SC")]["home_score"] == "9"   # NÃO sobrescreveu o completo
    assert ("Santos", "Vasco") in by and n == 1                       # só o novo entrou


def test_write_fixtures_remarca_e_preserva_e0(tmp_path, monkeypatch):
    import csv
    bra, fix = tmp_path / "bra_stats.csv", tmp_path / "fixtures.csv"
    monkeypatch.setattr(espn, "_paths", lambda: (bra, fix))
    with fix.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["league", "round", "date", "home", "away"]); w.writeheader()
        w.writerow({"league": "BRA", "round": "20", "date": "2026-08-01", "home": "Flamengo RJ", "away": "Palmeiras"})
        w.writerow({"league": "E0", "round": "1", "date": "2026-08-15", "home": "Arsenal", "away": "Chelsea"})
    fx = espn._write_fixtures([
        {"league": "BRA", "round": "", "date": "2026-08-08", "home": "Flamengo RJ", "away": "Palmeiras"},  # remarcado
        {"league": "BRA", "round": "", "date": "2026-08-09", "home": "Santos", "away": "Vasco"},           # novo
    ])
    rows = list(csv.DictReader(fix.open(encoding="utf-8")))
    fl = next(r for r in rows if r["home"] == "Flamengo RJ")
    assert fl["date"] == "2026-08-08" and fl["round"] == "20"   # data nova, rodada preservada
    assert any(r["league"] == "E0" for r in rows)               # E0 intacto
    assert any(r["home"] == "Santos" for r in rows) and fx == 2


def test_atualizar_rodada_orquestra(monkeypatch):
    canned = {"results": [_row(date="2026-05-31", home="Palmeiras", away="Chapecoense-SC", home_score=1, away_score=0)],
              "fixtures": [], "cancelados": [{"date": "2026-07-29", "home": "Sao Paulo", "away": "Santos"}],
              "skipped": ["x: fora do mapa"]}
    monkeypatch.setattr(espn, "fetch", lambda *a, **k: canned)
    monkeypatch.setattr(espn, "_write_results", lambda rows, canc=(): len(rows))
    monkeypatch.setattr(espn, "_write_fixtures", lambda fx: 0)
    monkeypatch.setattr(espn, "_remove_cancelados", lambda conn, canc: len(canc))
    import scb.ingest as ing
    import scb.registrar as reg
    monkeypatch.setattr(ing, "load_bra_stats", lambda conn, path: 5)
    monkeypatch.setattr(reg, "settle", lambda conn: {"preenchidos": 3, "em_aberto": 1})

    class FakeConn:
        def commit(self):
            pass

    out = espn.atualizar_rodada(FakeConn())
    assert out["resultados_novos"] == 1 and out["stats_casados"] == 5
    assert out["liquidados"] == 3 and out["em_aberto"] == 1 and out["pulados"] == 1
    assert out["desfeitos_adiados"] == 1                    # o adiado foi desfeito
