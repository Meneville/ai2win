# ai2win

Codex skill for World Cup betting analysis, daily tactical reports, odds comparison, bankroll management, and HTML betting slips.

## Skill

The main skill is:

```text
skills/world-cup-betting-analyst/
```

It helps Codex analyze the nearest three FIFA World Cup or Club World Cup matches from today, combining:

- match schedule and venue context
- team news, injuries, likely lineups, and standings
- detailed tactical reports for both teams
- personnel structure by goalkeeper, defenders, midfielders, and forwards
- tactical profile, coach preparation signals, and matchup paths
- multi-bookmaker odds and water-line movement
- win/draw/loss probabilities, expected score, and likely scorers
- conservative and aggressive betting slips based on a bankroll

The default bankroll is `4000`, unless the user provides another value.

## Install Locally

Copy or symlink the skill into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R skills/world-cup-betting-analyst ~/.codex/skills/
```

Then restart Codex or start a new thread so the skill is discovered.

## Use

In Codex, invoke:

```text
用 $world-cup-betting-analyst 分析今天最近三场世界杯比赛。我的总财富是4000，给我每日详细技战术报告，并合成HTML投注单。
```

The skill requires live web verification for current schedules, odds, injuries, lineups, and tactical context. It should not rely on memory for time-sensitive data.

## Generate HTML

The skill includes a renderer:

```bash
python3 skills/world-cup-betting-analyst/scripts/render_betting_report.py input.json output.html
```

Create a sample report:

```bash
python3 skills/world-cup-betting-analyst/scripts/render_betting_report.py --sample sample.json
python3 skills/world-cup-betting-analyst/scripts/render_betting_report.py sample.json sample.html
open sample.html
```

## Report Structure

Each match can include:

- `team_reports`: detailed team tactical reports
- `matchup_report`: overall head-to-head matchup analysis
- `odds`: bookmaker odds and movement
- `model`: model probabilities and expected score
- `bets`: conservative and aggressive staking plans
- `sources`: source links and notes

The renderer accepts Chinese field names used by the skill, such as `人员结构`, `战术画像摘要`, and `主教练与备战信号`.

## Risk Notice

This repository is for probabilistic sports analysis and bankroll planning. It does not guarantee profit. Always verify local laws, final lineups, and live odds before placing any bet, and only risk money you can afford to lose.
