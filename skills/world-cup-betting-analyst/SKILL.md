---
name: world-cup-betting-analyst
description: Analyze FIFA World Cup or Club World Cup schedules, today's nearest three matches, daily detailed tactical reports, personnel structure, goalkeeper/defender/midfielder/forward units, tactical profile, coach preparation signals, odds and water-line movement, win/draw/loss probabilities, expected score, likely scorers, and bankroll-aware betting slips. Use when the user asks in Chinese or English for 世界杯赛程、当天最近三场比赛、每日详细报告、对阵双方总体报告、投注分析、博彩公司赔率/水位、主教练视角技战术分析、统计学家视角概率建模、保守/激进投注策略、HTML 网页投注单, or wants to record actual bet results, profit, or loss for later adjustment.
---

# 世界杯投注分析

## 核心原则

把自己分成两个角色工作：

- **专业主教练**：判断比赛地点、天气/场地、赛程密度、主力球员、伤停、轮换、心理状态、技战术打法、对位优势、积分形势、出线/晋级动机。
- **统计学家**：比较多家博彩公司和赔率聚合站的 1X2、让球、大小球、球员进球等盘口，记录水位变化，去除 overround，估算真实概率和期望价值。

任何投注建议都必须是风险管理建议，不得承诺盈利。默认总财富/资金池为 **4000**，除非用户提供新的资金池、币种、已下注金额或盈亏记录。

## 工作流

1. **确认范围**
   - 默认分析“今天起按开球时间最近的三场世界杯相关比赛”。
   - 如果今天没有三场，就向后顺延到最近的三场，并明确写出日期、时区和筛选逻辑。
   - 使用用户所在时区或请求中的时区；不确定时标注所用时区。

2. **联网核验最新数据**
   - 必须浏览/搜索最新信息。不要依赖记忆中的赛程、伤停、排名、赔率或首发。
   - 赛程、伤停、首发、积分等事实优先使用官方赛程和权威数据源；技战术画像可以参考知名足球战术分析网站和专栏。
   - 赔率至少参考 3 家博彩公司或 1 个赔率聚合站加 2 家博彩公司。
   - 每个关键判断附来源链接和抓取/发布时间；若数据缺失，明确标注不确定性。

3. **收集每场比赛情报**
   - 比赛：赛事、轮次、开球时间、地点、球场、天气/草皮/旅途因素。
   - 球队：积分/排名、晋级形势、近期战绩、进失球、xG/xGA（如可得）、赛程疲劳。
   - 阵容：预计首发、核心球员、伤停停赛、轮换动机、可能替补影响。
   - 技战术：必须为对阵双方分别写出“人员结构”“战术画像摘要”“主教练与备战信号”，再写双方总体对位报告。
   - 裁判：判罚尺度、黄牌/点球倾向（可得时使用，缺失则不臆造）。

4. **每日详细战术报告**
   - 对每支球队分别分析：
     - 人员结构：门将、后卫、中场、前锋四个单元。
     - 战术画像摘要：基础阵型、备选阵型、有球/无球风格、压迫、防线高度、后场出球、机会创造、转换、定位球、优势和弱点。
     - 主教练与备战信号：近期言论、训练营信息、热身赛收获、战术试验、选人信号。
   - 对阵双方总体报告必须回答：
     - 哪支球队的计划更容易落地，原因是什么。
     - 关键对位在哪里，哪一侧会决定比赛走向。
     - A 队如何赢、B 队如何赢、平局路径是什么。
     - 哪些战术判断会转化为投注价值，哪些只适合观望。

5. **赔率与概率建模**
   - 收集 1X2、亚洲让球、大小球、关键球员进球赔率；记录初盘、即时盘和水位变化。
   - 计算博彩公司隐含概率，并归一化去除水钱。
   - 独立给出模型概率：A 胜 / 平 / B 胜、预期比分、可能进球者、主要不确定性。
   - 只在“模型概率 × 可下注赔率”存在正期望或风险补偿足够时推荐投注；否则建议观望。

6. **投注单输出**
   - 给出两套策略：
     - **保守**：更重视本金保护、低相关性、单场小仓位。
     - **激进**：允许更高波动，但仍限制总暴露，不使用马丁格尔或追损。
   - 每个推荐必须写明：玩法、选择、赔率、建议金额、最高可接受赔率/最低可接受赔率、推荐理由、风险点。
   - 把每日详细战术报告合并在投注单同一份 HTML 内；投注建议必须能追溯到战术判断、盘口判断或两者共同支持。
   - 输出每场比赛的投注建议，再输出组合层面的总投入、剩余资金、最大亏损、潜在回报。

7. **HTML 报告**
   - 优先生成结构化 JSON，再用 `scripts/render_betting_report.py` 渲染成 HTML。
   - HTML 应包含摘要、赛程、模型概率、双方详细战术报告、对阵总体报告、赔率表、水位变化、主教练分析、统计学分析、保守/激进投注单、来源列表。

8. **赛后复盘**
   - 如果用户提供实际投注、盈利或亏损，更新分析中的 bankroll、命中率、ROI、最大回撤、策略偏差。
   - 复盘要区分“判断对但赔率无价值”“判断错”“临场信息变化”“仓位过大”等原因。

## 推荐数据源

优先顺序：

- 官方：FIFA 官方赛程/Match Centre、赛事官网、球队官网、官方社媒、赛前发布会。
- 数据：FotMob、Sofascore、WhoScored、FBref、Opta/Stats Perform 转载源、Transfermarkt（身价/伤停作参考）。
- 新闻：Reuters、AP、BBC Sport、ESPN、The Athletic、本地可靠体育媒体。
- 技战术分析：The Coaches' Voice、The Athletic/Tifo Football、Total Football Analysis、Spielverlagerung、Between The Posts、Breaking The Lines、Zonal Marking、StatsBomb、Opta Analyst、Hudl/Wyscout 专栏等。
- 赔率：OddsPortal、OddsChecker、Pinnacle、Bet365、William Hill、DraftKings、FanDuel、Betfair Exchange（按地区可访问性使用）。

博彩网站可能因地区限制不可访问；访问失败时改用赔率聚合站并说明限制。不要伪造赔率。

技战术网站可以提供阵型机制、压迫触发点、出球结构、对位弱点等高价值判断；但它们常带有作者观点。使用时要把“事实”（阵型、球员位置、比赛片段）和“解读”（某队优势、某种打法更有效）分开，并尽量用 2 个以上来源或数据指标交叉验证。

## 资金管理

需要细化仓位时，读取 `references/bankroll-and-odds.md`。默认规则：

- 总资金池：4000。
- 保守策略：单场通常 1%-3%，三场总暴露通常不超过 8%-12%。
- 激进策略：单场通常 3%-7%，三场总暴露通常不超过 20%-25%。
- 单个高不确定性市场（球员进球、比分、半全场）降低仓位。
- 若模型优势不足，投注金额可以为 0，写“观望”。

## 情报清单

需要逐项检查时，读取 `references/research-checklist.md`。不要为了填满清单而编造；缺失项写“未找到可靠来源”。

## 结构化报告字段

生成 HTML 前，建议在每场比赛 JSON 中加入：

```json
{
  "team_reports": [
    {
      "team": "A队",
      "人员结构": {
        "门将": {
          "一号门将": "姓名、状态、脚下能力、扑救特点",
          "替补选择": "替补门将和可用性",
          "优势": "门线/出击/长传等",
          "风险": "伤病、失误、被压迫出球"
        },
        "后卫": {},
        "中场": {},
        "前锋": {}
      },
      "战术画像摘要": {},
      "主教练与备战信号": {}
    }
  ],
  "matchup_report": {
    "总体判断": [],
    "关键对位": [],
    "A队取胜路径": [],
    "B队取胜路径": [],
    "平局路径": [],
    "投注含义": []
  }
}
```

字段可以用中文。`render_betting_report.py` 会把这些内容合并进投注单 HTML。

## HTML 生成

先准备一个 JSON 文件，再运行：

```bash
python3 /Users/chenqh/.codex/skills/world-cup-betting-analyst/scripts/render_betting_report.py input.json output.html
```

可用示例结构：

```bash
python3 /Users/chenqh/.codex/skills/world-cup-betting-analyst/scripts/render_betting_report.py --sample sample.json
python3 /Users/chenqh/.codex/skills/world-cup-betting-analyst/scripts/render_betting_report.py sample.json report.html
```

渲染前检查 JSON 中的金额、赔率、概率加总和来源链接。渲染后给用户 HTML 文件路径；如果用户需要，也可以启动本地静态服务器预览。
