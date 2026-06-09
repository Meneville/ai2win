#!/usr/bin/env python3
"""Render a World Cup betting analysis JSON file to a standalone HTML report."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import sys
from pathlib import Path
from typing import Any


def esc(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def money(value: Any, currency: str = "CNY") -> str:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return esc(value)
    symbol = {"CNY": "¥", "USD": "$", "EUR": "€", "GBP": "£"}.get(currency.upper(), "")
    return f"{symbol}{amount:,.0f}" if symbol else f"{amount:,.0f} {esc(currency)}"


def pct(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return esc(value)
    if number <= 1:
        number *= 100
    return f"{number:.1f}%"


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def li(items: Any) -> str:
    values = as_list(items)
    if not values:
        return '<p class="muted">暂无可靠信息</p>'
    return "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in values) + "</ul>"


def source_links(sources: Any) -> str:
    rows = []
    for source in as_list(sources):
        if isinstance(source, dict):
            label = esc(source.get("label") or source.get("url") or "source")
            url = esc(source.get("url") or "")
            note = esc(source.get("note") or "")
            if url:
                rows.append(f'<li><a href="{url}" target="_blank" rel="noreferrer">{label}</a> {note}</li>')
            else:
                rows.append(f"<li>{label} {note}</li>")
        else:
            rows.append(f"<li>{esc(source)}</li>")
    if not rows:
        return '<p class="muted">未记录来源</p>'
    return "<ul>" + "".join(rows) + "</ul>"


def get_any(mapping: Any, *keys: str) -> Any:
    if not isinstance(mapping, dict):
        return None
    for key in keys:
        if key in mapping and mapping[key] not in (None, "", [], {}):
            return mapping[key]
    return None


def render_value(value: Any) -> str:
    if isinstance(value, list):
        return "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in value) + "</ul>"
    if isinstance(value, dict):
        return detail_list(value)
    if value in (None, ""):
        return '<span class="muted">未找到可靠来源</span>'
    return esc(value)


def detail_list(data: Any) -> str:
    if not isinstance(data, dict) or not data:
        return '<p class="muted">未找到可靠来源</p>'
    rows = []
    for key, value in data.items():
        rows.append(
            '<div class="detail-row">'
            f"<b>{esc(key)}</b>"
            f"<span>{render_value(value)}</span>"
            "</div>"
        )
    return '<div class="detail-list">' + "".join(rows) + "</div>"


def render_profile_group(title: str, data: Any) -> str:
    if not isinstance(data, dict) or not data:
        return ""
    units = []
    for unit_title, unit_data in data.items():
        units.append(
            '<div class="unit-block">'
            f"<h5>{esc(unit_title)}</h5>"
            f"{detail_list(unit_data) if isinstance(unit_data, dict) else render_value(unit_data)}"
            "</div>"
        )
    return (
        '<div class="profile-group">'
        f"<h4>{esc(title)}</h4>"
        '<div class="unit-grid">'
        + "".join(units)
        + "</div></div>"
    )


def render_team_reports(match: dict[str, Any]) -> str:
    reports = as_list(get_any(match, "team_reports", "球队报告", "双方详细战术报告"))
    reports = [report for report in reports if isinstance(report, dict)]
    if not reports:
        return ""

    cards = []
    for report in reports:
        team_name = get_any(report, "team", "球队", "name") or "球队"
        personnel = get_any(report, "人员结构", "personnel_structure", "personnel")
        tactical = get_any(report, "战术画像摘要", "tactical_profile", "tactical_summary")
        signals = get_any(report, "主教练与备战信号", "coach_signals", "preparation_signals")
        notes = get_any(report, "综合判断", "summary", "notes")
        cards.append(
            '<article class="team-report">'
            f"<h4>{esc(team_name)}</h4>"
            f'{f"<p>{esc(notes)}</p>" if notes and not isinstance(notes, (dict, list)) else ""}'
            f"{li(notes) if isinstance(notes, list) else ''}"
            f"{render_profile_group('人员结构', personnel)}"
            f"{render_profile_group('战术画像摘要', tactical)}"
            f"{render_profile_group('主教练与备战信号', signals)}"
            "</article>"
        )

    return (
        '<div class="panel tactical-report">'
        "<h3>双方详细战术报告</h3>"
        '<div class="team-report-grid">'
        + "".join(cards)
        + "</div></div>"
    )


def render_matchup_report(match: dict[str, Any]) -> str:
    report = get_any(match, "matchup_report", "对阵双方总体报告", "对阵总体报告")
    if not isinstance(report, dict) or not report:
        return ""
    return (
        '<div class="panel matchup-report">'
        "<h3>对阵双方总体报告</h3>"
        f"{detail_list(report)}"
        "</div>"
    )


def odds_table(odds: Any) -> str:
    rows = []
    for item in as_list(odds):
        if not isinstance(item, dict):
            continue
        rows.append(
            "<tr>"
            f"<td>{esc(item.get('bookmaker'))}</td>"
            f"<td>{esc(item.get('market'))}</td>"
            f"<td>{esc(item.get('home'))}</td>"
            f"<td>{esc(item.get('draw'))}</td>"
            f"<td>{esc(item.get('away'))}</td>"
            f"<td>{esc(item.get('movement'))}</td>"
            f"<td>{esc(item.get('timestamp'))}</td>"
            "</tr>"
        )
    if not rows:
        return '<p class="muted">未记录赔率</p>'
    return (
        '<div class="table-wrap"><table><thead><tr>'
        "<th>公司</th><th>盘口</th><th>主/队A</th><th>平</th><th>客/队B</th><th>水位变化</th><th>时间</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def bets_table(bets: Any, currency: str) -> str:
    rows = []
    for bet in as_list(bets):
        if not isinstance(bet, dict):
            continue
        rows.append(
            "<tr>"
            f"<td>{esc(bet.get('market'))}</td>"
            f"<td><strong>{esc(bet.get('selection'))}</strong></td>"
            f"<td>{esc(bet.get('odds'))}</td>"
            f"<td>{money(bet.get('stake'), currency)}</td>"
            f"<td>{esc(bet.get('limit') or bet.get('acceptable_odds'))}</td>"
            f"<td>{esc(bet.get('rationale'))}</td>"
            "</tr>"
        )
    if not rows:
        return '<p class="muted">本策略建议观望或未给出投注</p>'
    return (
        '<div class="table-wrap"><table><thead><tr>'
        "<th>玩法</th><th>选择</th><th>赔率</th><th>金额</th><th>价格纪律</th><th>理由</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def probability_bar(model: dict[str, Any]) -> str:
    home = float(model.get("home_win") or model.get("team_a_win") or 0)
    draw = float(model.get("draw") or 0)
    away = float(model.get("away_win") or model.get("team_b_win") or 0)
    total = home + draw + away
    if total <= 0:
        return '<p class="muted">未给出概率</p>'
    home_w, draw_w, away_w = (home / total * 100, draw / total * 100, away / total * 100)
    return (
        '<div class="prob-bar" aria-label="probability bar">'
        f'<span class="home" style="width:{home_w:.2f}%"></span>'
        f'<span class="draw" style="width:{draw_w:.2f}%"></span>'
        f'<span class="away" style="width:{away_w:.2f}%"></span>'
        "</div>"
        '<div class="prob-grid">'
        f"<div><b>队A胜</b><strong>{pct(home)}</strong></div>"
        f"<div><b>平局</b><strong>{pct(draw)}</strong></div>"
        f"<div><b>队B胜</b><strong>{pct(away)}</strong></div>"
        "</div>"
    )


def render_match(match: dict[str, Any], idx: int, currency: str) -> str:
    teams = match.get("teams") or {}
    if isinstance(teams, dict):
        home = teams.get("home") or teams.get("team_a") or "队A"
        away = teams.get("away") or teams.get("team_b") or "队B"
    else:
        home, away = "队A", "队B"
    model = match.get("model") or {}
    bets = match.get("bets") or {}
    conservative = bets.get("conservative") if isinstance(bets, dict) else []
    aggressive = bets.get("aggressive") if isinstance(bets, dict) else []

    likely_scorers = model.get("likely_scorers") or match.get("likely_scorers")
    risk = match.get("risks") or match.get("risk_notes")

    return f"""
    <section class="match-card">
      <div class="match-head">
        <div>
          <p class="eyebrow">MATCH {idx} · {esc(match.get('competition'))}</p>
          <h2>{esc(home)} <span>vs</span> {esc(away)}</h2>
          <p class="meta">{esc(match.get('kickoff'))} · {esc(match.get('venue'))}</p>
        </div>
        <div class="score-pill">预期比分 {esc(model.get('expected_score') or match.get('expected_score') or '待定')}</div>
      </div>

      <div class="grid two">
        <div class="panel">
          <h3>模型概率</h3>
          {probability_bar(model)}
          <p><b>置信度：</b>{esc(model.get('confidence') or match.get('confidence') or '未标注')}</p>
          <p><b>可能进球者：</b>{esc(', '.join(map(str, as_list(likely_scorers))) if likely_scorers else '未找到足够证据')}</p>
        </div>
        <div class="panel">
          <h3>积分与背景</h3>
          <p>{esc(match.get('standings_context') or match.get('context') or '暂无')}</p>
          <p><b>地点因素：</b>{esc(match.get('location_factors') or '暂无')}</p>
        </div>
      </div>

      <div class="grid two">
        <div class="panel coach">
          <h3>主教练视角</h3>
          {li(match.get('coach_analysis') or match.get('tactical_analysis'))}
        </div>
        <div class="panel stats">
          <h3>统计学家视角</h3>
          {li(match.get('statistical_analysis') or match.get('market_analysis'))}
        </div>
      </div>

      {render_team_reports(match)}

      {render_matchup_report(match)}

      <div class="panel">
        <h3>赔率与水位</h3>
        {odds_table(match.get('odds'))}
      </div>

      <div class="grid two">
        <div class="panel slip conservative">
          <h3>保守投注单</h3>
          {bets_table(conservative, currency)}
        </div>
        <div class="panel slip aggressive">
          <h3>激进投注单</h3>
          {bets_table(aggressive, currency)}
        </div>
      </div>

      <div class="grid two">
        <div class="panel">
          <h3>主要风险</h3>
          {li(risk)}
        </div>
        <div class="panel">
          <h3>来源</h3>
          {source_links(match.get('sources'))}
        </div>
      </div>
    </section>
    """


def render_report(data: dict[str, Any]) -> str:
    currency = data.get("currency") or "CNY"
    bankroll = data.get("bankroll", 4000)
    generated_at = data.get("generated_at") or dt.datetime.now().astimezone().isoformat(timespec="minutes")
    matches = [m for m in as_list(data.get("matches")) if isinstance(m, dict)]
    portfolio = data.get("portfolio") or {}

    match_html = "\n".join(render_match(match, idx + 1, currency) for idx, match in enumerate(matches))
    if not match_html:
        match_html = '<section class="match-card"><p class="muted">没有可渲染的比赛数据。</p></section>'

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(data.get('title') or '世界杯投注分析报告')}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #17202a;
      --muted: #65707d;
      --line: #d9e0e7;
      --paper: #f6f8fb;
      --panel: #ffffff;
      --accent: #0f766e;
      --accent-2: #7c3aed;
      --warn: #b45309;
      --bad: #b91c1c;
      --good: #166534;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--paper);
      line-height: 1.55;
    }}
    header {{
      padding: 36px min(5vw, 56px) 24px;
      background: #0b1f2a;
      color: white;
    }}
    header h1 {{
      margin: 0 0 10px;
      font-size: clamp(28px, 4vw, 48px);
      letter-spacing: 0;
    }}
    header p {{ max-width: 980px; color: #d7e2ea; margin: 6px 0; }}
    main {{ padding: 24px min(5vw, 56px) 56px; }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 20px;
    }}
    .metric, .panel, .match-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
    }}
    .metric {{ padding: 16px; }}
    .metric b {{ display: block; color: var(--muted); font-size: 13px; font-weight: 650; }}
    .metric strong {{ display: block; margin-top: 4px; font-size: 24px; }}
    .match-card {{ padding: 20px; margin-top: 18px; }}
    .match-head {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: flex-start;
      border-bottom: 1px solid var(--line);
      padding-bottom: 14px;
      margin-bottom: 16px;
    }}
    .eyebrow {{
      margin: 0 0 4px;
      color: var(--accent);
      font-size: 12px;
      font-weight: 750;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    h2 {{ margin: 0; font-size: clamp(22px, 3vw, 34px); letter-spacing: 0; }}
    h2 span {{ color: var(--muted); font-size: 0.72em; }}
    h3 {{ margin: 0 0 10px; font-size: 17px; letter-spacing: 0; }}
    .meta {{ margin: 6px 0 0; color: var(--muted); }}
    .score-pill {{
      white-space: nowrap;
      border: 1px solid #a7f3d0;
      background: #ecfdf5;
      color: var(--good);
      border-radius: 999px;
      padding: 8px 12px;
      font-weight: 750;
    }}
    .grid {{ display: grid; gap: 14px; margin-top: 14px; }}
    .grid.two {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .panel {{ padding: 16px; overflow: hidden; }}
    .muted {{ color: var(--muted); }}
    ul {{ margin: 0; padding-left: 20px; }}
    li + li {{ margin-top: 6px; }}
    h4 {{
      margin: 0 0 10px;
      font-size: 16px;
      letter-spacing: 0;
    }}
    h5 {{
      margin: 0 0 8px;
      font-size: 14px;
      letter-spacing: 0;
      color: #0f172a;
    }}
    .team-report-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }}
    .team-report {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      background: #fbfdff;
    }}
    .profile-group + .profile-group {{ margin-top: 14px; }}
    .profile-group h4 {{
      color: var(--accent);
      border-bottom: 1px solid var(--line);
      padding-bottom: 6px;
    }}
    .unit-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }}
    .unit-block {{
      min-width: 0;
      border: 1px solid #e7edf3;
      border-radius: 8px;
      padding: 10px;
      background: white;
    }}
    .detail-list {{ display: grid; gap: 7px; }}
    .detail-row {{
      display: grid;
      grid-template-columns: minmax(88px, 0.36fr) minmax(0, 1fr);
      gap: 8px;
      padding-bottom: 7px;
      border-bottom: 1px solid #eef2f6;
    }}
    .detail-row:last-child {{ border-bottom: 0; padding-bottom: 0; }}
    .detail-row b {{
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }}
    .detail-row span {{
      min-width: 0;
      overflow-wrap: anywhere;
    }}
    .matchup-report .detail-row {{
      grid-template-columns: minmax(110px, 0.22fr) minmax(0, 1fr);
    }}
    .prob-bar {{
      display: flex;
      height: 12px;
      overflow: hidden;
      border-radius: 999px;
      background: #e5e7eb;
      margin: 8px 0 10px;
    }}
    .prob-bar span {{ display: block; min-width: 2px; }}
    .prob-bar .home {{ background: var(--accent); }}
    .prob-bar .draw {{ background: #64748b; }}
    .prob-bar .away {{ background: var(--accent-2); }}
    .prob-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8px;
      margin-bottom: 10px;
    }}
    .prob-grid div {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 9px;
      background: #fbfdff;
    }}
    .prob-grid b {{ display: block; color: var(--muted); font-size: 12px; }}
    .prob-grid strong {{ display: block; font-size: 18px; }}
    .table-wrap {{ width: 100%; overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 760px; }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 9px 8px;
      text-align: left;
      vertical-align: top;
      font-size: 14px;
    }}
    th {{ color: var(--muted); background: #f8fafc; font-size: 12px; }}
    .conservative h3 {{ color: var(--accent); }}
    .aggressive h3 {{ color: var(--warn); }}
    a {{ color: #075985; }}
    footer {{
      padding: 18px min(5vw, 56px) 36px;
      color: var(--muted);
      font-size: 13px;
    }}
    @media (max-width: 860px) {{
      .summary, .grid.two, .team-report-grid, .unit-grid {{ grid-template-columns: 1fr; }}
      .match-head {{ display: block; }}
      .score-pill {{ display: inline-block; margin-top: 12px; white-space: normal; }}
      .detail-row {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <p class="eyebrow">World Cup Betting Analyst</p>
    <h1>{esc(data.get('title') or '世界杯投注分析报告')}</h1>
    <p>{esc(data.get('subtitle') or '今日最近三场比赛 · 主教练视角 + 统计学家视角')}</p>
    <p>生成时间：{esc(generated_at)} · 时区：{esc(data.get('timezone') or '未标注')}</p>
  </header>
  <main>
    <section class="summary">
      <div class="metric"><b>资金池</b><strong>{money(bankroll, currency)}</strong></div>
      <div class="metric"><b>保守总投入</b><strong>{money(portfolio.get('conservative_total_stake'), currency)}</strong></div>
      <div class="metric"><b>激进总投入</b><strong>{money(portfolio.get('aggressive_total_stake'), currency)}</strong></div>
      <div class="metric"><b>比赛数量</b><strong>{len(matches)}</strong></div>
    </section>
    <section class="panel">
      <h3>组合说明</h3>
      {li(portfolio.get('notes') or data.get('portfolio_notes'))}
    </section>
    {match_html}
  </main>
  <footer>
    本报告是概率与风险管理分析，不构成盈利保证。请遵守所在地法律法规，并只用可承受损失的资金投注。
  </footer>
</body>
</html>
"""


def sample_data() -> dict[str, Any]:
    return {
        "title": "世界杯投注分析报告示例",
        "subtitle": "示例数据，仅用于检查 HTML 样式",
        "generated_at": dt.datetime.now().astimezone().isoformat(timespec="minutes"),
        "timezone": "Asia/Shanghai",
        "bankroll": 4000,
        "currency": "CNY",
        "portfolio": {
            "conservative_total_stake": 240,
            "aggressive_total_stake": 760,
            "notes": [
                "保守方案控制总暴露约 6%。",
                "激进方案提高赔率弹性，但不追损、不使用马丁格尔。",
            ],
        },
        "matches": [
            {
                "competition": "FIFA World Cup",
                "kickoff": "2026-06-11 03:00 Asia/Shanghai",
                "venue": "示例球场，示例城市",
                "teams": {"home": "A队", "away": "B队"},
                "standings_context": "A队需要取胜争取小组第一，B队平局即可接受。",
                "location_factors": "中立场，A队少休一天。",
                "coach_analysis": [
                    "A队边路推进效率更高，但身后空间容易被反击利用。",
                    "B队可能采用低位 5-4-1，重点保护禁区中路。",
                ],
                "statistical_analysis": [
                    "模型认为 A 队胜率高于归一化盘口约 3.2 个百分点。",
                    "大小球 2.5 的即时水位下，进球期望没有足够价值。",
                ],
                "team_reports": [],
                "matchup_report": {
                    "总体判断": ["A队更容易控制球权和场面，B队更容易把比赛拖入低节奏。"],
                    "投注含义": ["A队胜只在赔率不低于模型价格时有价值。"],
                },
                "odds": [
                    {
                        "bookmaker": "示例公司1",
                        "market": "1X2",
                        "home": 1.88,
                        "draw": 3.45,
                        "away": 4.60,
                        "movement": "A胜 1.95 -> 1.88",
                        "timestamp": "示例时间",
                    }
                ],
                "model": {
                    "home_win": 0.54,
                    "draw": 0.27,
                    "away_win": 0.19,
                    "expected_score": "2-1",
                    "likely_scorers": ["A队中锋", "A队点球手"],
                    "confidence": "中",
                },
                "bets": {
                    "conservative": [
                        {
                            "market": "1X2",
                            "selection": "A队胜",
                            "odds": 1.88,
                            "stake": 120,
                            "limit": "低于 1.82 放弃",
                            "rationale": "模型概率略高于市场，且阵容稳定。",
                        }
                    ],
                    "aggressive": [
                        {
                            "market": "正确比分",
                            "selection": "A队 2-1",
                            "odds": 8.50,
                            "stake": 40,
                            "limit": "低于 7.50 放弃",
                            "rationale": "只作为小额高方差补充。",
                        }
                    ],
                },
                "risks": ["临场首发若轮换两名以上核心，A胜价值下降。"],
                "sources": [{"label": "示例来源", "url": "https://www.fifa.com/"}],
            }
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="Input JSON file")
    parser.add_argument("output", nargs="?", help="Output HTML file")
    parser.add_argument("--sample", metavar="PATH", help="Write a sample JSON file and exit")
    args = parser.parse_args()

    if args.sample:
        Path(args.sample).write_text(json.dumps(sample_data(), ensure_ascii=False, indent=2), encoding="utf-8")
        print(args.sample)
        return 0

    if not args.input or not args.output:
        parser.error("input and output are required unless --sample is used")

    input_path = Path(args.input)
    output_path = Path(args.output)
    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 2

    if not isinstance(data, dict):
        print("Input JSON root must be an object", file=sys.stderr)
        return 2

    output_path.write_text(render_report(data), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
