import os
import traceback
from datetime import datetime
import gradio as gr
from xai_sdk import Client
from xai_sdk.chat import user, system
from xai_sdk.tools import web_search, x_search
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
xai_api_key = os.getenv('XAI_API_KEY')

# Define the analysis configurationspip 
ANALYSES = [
    {
        "id": "1",
        "name": "The Tastytrade 0DTE SPX Credit Spread Scanner",
        "prompt_template": (
            "You are a senior options trader at Tastytrade who specializes in 0DTE (zero days to expiration) SPX credit spreads "            
            "— the strategy professional theta traders use to generate daily income from time decay on the S&P 500 index. "
            "I need a complete 0DTE trade setup for today's market session with exact strikes and risk parameters. "
            "Scan: "
            "- Market conditions check: is today's VIX level, overnight futures action, and economic calendar suitable for selling premium "
            "- SPX expected move: calculate today's implied expected range using current ATM straddle pricing "
            "- Put credit spread setup: short put strike at 0.10-0.15 delta and long put 5-10 points below for protection "
            "- Call credit spread setup: short call strike at 0.10-0.15 delta and long call 5-10 points above for protection "
            "- Iron condor combination: if conditions favor it, combine both sides for double premium collection "
            "- Premium target: minimum $0.50-$1.00 credit collected per spread to justify the risk-reward "
            "- Risk-reward ratio: maximum loss vs premium collected with a minimum 1:3 reward-to-risk target "
            "- Entry timing: optimal time of day to enter (typically 9:45-10:30 AM after opening volatility settles) "
            "- Stop-loss rules: close the trade if spread reaches 2x the premium collected or if SPX breaches short strike "
            "- Exit strategy: let expire worthless for full profit, or close at 50% profit if reached before 2 PM "
            "Format as a Tastytrade-style 0DTE trade ticket with exact strikes, entry price, max profit, max loss, and time-based exit rules. "
            "Today's setup: [TODAY'S DATE, CURRENT SPX PRICE, VIX LEVEL, AND ANY MAJOR ECONOMIC EVENTS SCHEDULED TODAY]"
        ),
        "params": []
    },
    {
        "id": "2",
        "name": "The Citadel Market Regime Classifier",
        "prompt_template": (
            "You are a senior quantitative strategist at Citadel who classifies market conditions into specific regimes before"
            "placing any options trade — because the #1 reason theta traders lose is selling premium in the wrong environment."
            "I need a complete market regime analysis telling me which options strategy to run today."
            "Classify:"
            "- VIX regime: low (under 15), normal (15-20), elevated (20-30), or crisis (30+) and what each means for premium sellers"
            "- VIX term structure: is the futures curve in contango (normal, good for selling) or backwardation (danger, stop selling)"
            "- Trend assessment: is SPX trending strongly (bad for iron condors) or range-bound (ideal for selling premium)"
            "- Realized vs implied volatility: is IV overpricing actual movement (edge for sellers) or underpricing (danger zone)"
            "- Correlation regime: are stocks moving together (macro-driven, wider spreads needed) or independently (stock-picking works)"
            "- Overnight gap risk: futures positioning and overseas markets suggesting gap up, gap down, or flat open"
            "- Economic event density: is today a Fed day, CPI release, or earnings-heavy session requiring wider strikes or sitting out"
            "- Put-call ratio reading: extreme readings signaling fear (good for selling puts) or complacency (caution on call side)"
            "- Market breadth: advance-decline line and new highs vs lows confirming or contradicting the index direction"
            "- Regime verdict: GREEN (sell premium aggressively), YELLOW (sell premium conservatively with wider strikes), or RED (sit in cash)"
            "Format as a Citadel-style morning regime report with a dashboard summary and specific strategy recommendation for each regime."
            "Current market: [TODAY'S SPX PRICE, VIX LEVEL, ANY ECONOMIC EVENTS TODAY, AND OVERNIGHT FUTURES DIRECTION]"
        ),
        "params": []
    },
    {
        "id": "3",
        "name": "The SIG Daily Theta Decay Calculator",
        "prompt_template": (
            "You are a senior options market maker at Susquehanna International Group who quantifies exact theta decay profits on short"
            "premium positions hour by hour throughout the trading day."
            "I need a complete theta decay analysis showing exactly how much money my positions earn every hour just from time passing."
            "Calculate:"
            "- Position-level theta: exact dollar amount each open position earns per day from time decay"
            "- Portfolio theta: total daily income across ALL short premium positions combined"
            "- Hourly decay curve: theta doesn't decay evenly — show me which hours of the day I earn the most"
            "- Acceleration zone: when theta decay accelerates dramatically in the final hours before expiration"
            "- Theta-to-delta ratio: am I earning enough theta relative to the directional risk I'm taking"
            "- Weekend theta capture: selling Friday expiration to collect 3 days of theta over the weekend"
            "- Theta vs gamma risk: the exact point where gamma risk outweighs theta income (usually when stock approaches short strike)"
            "- Optimal closing time: the mathematically ideal time to close for profit vs letting positions expire"
            "- Daily income projection: at my current position sizes, expected income per day, per week, and per month"
            "- Compounding model: if I reinvest theta profits into larger positions, projected account growth over 30, 60, and 90 days"
            "Format as a SIG-style theta dashboard with hourly decay schedules, portfolio income summary, and a compounding growth projection."
            "My positions: [LIST YOUR CURRENT SHORT PREMIUM POSITIONS WITH TICKER, STRIKE, EXPIRATION, CREDIT RECEIVED, AND CURRENT VALUE]"
        ),
        "params": []
    },
    {
        "id": "4",
        "name": "The Two Sigma Probability-Based Strike Selection",
        "prompt_template": (
            "You are a senior quantitative researcher at Two Sigma who selects option strikes based purely on statistical "
            " models — removing emotion and replacing gut feeling with math."
            "I need a probability-based framework for selecting the exact right strikes for my credit spreads every day."
            "Select:"
            "- Delta-based probability: translate delta values into approximate probability of expiring out of the money"
            "- Standard deviation mapping: place short strikes at 1.0, 1.5, or 2.0 standard deviations from current price"
            "- Expected move calculation: use current IV to calculate the 1-day, 1-week, and 1-month expected price range"
            "- Historical accuracy test: how often has the implied expected move actually contained the real move over the last 100 sessions"
            "- Strike distance optimization: the sweet spot where premium collected justifies the risk of being breached"
            "- Win rate by delta level: historical win rates at 0.10 delta (90%), 0.15 delta (85%), 0.20 delta (80%), and 0.30 delta (70%)"
            "- Premium decay at each level: how fast premium decays at each delta level (closer = faster decay but higher risk)"
            "- Gap risk adjustment: widen strikes on days with overnight event risk (earnings, Fed, economic data)"
            "- Skew-adjusted selection: when put skew is steep, sell further OTM puts for same premium at wider distance"
            "- Today's exact strikes: based on all factors, the specific short strike and long strike for today's trade"
            "Format as a Two Sigma-style probability matrix with strike recommendations at different confidence levels and today's specific trade setup."
            "Today's trade: [{stock}, CURRENT PRICE, AND 60% WIN RATE]"
        ),
        "params": ["stock"]
    },
    {
        "id": "5",
        "name": "The D.E. Shaw Iron Condor Income Machine",
        "prompt_template": (
            "You are a senior portfolio manager at D.E. Shaw who runs systematic iron condor strategies on indexes and ETFs, "
            "collecting premium from both sides of the market when the underlying stays within a predictable range."
            "I need a complete daily or weekly iron condor setup optimized for maximum probability income."
            "Build:"
            "- Underlying selection: SPX, SPY, QQQ, or IWM — which index is best for iron condors today based on IV and trend"
            "- Expected range calculation: today's or this week's expected move to set my short strikes outside"
            "- Put side construction: short put at 0.10-0.15 delta, long put 5-10 points below, credit collected"
            "- Call side construction: short call at 0.10-0.15 delta, long call 5-10 points above, credit collected"
            "- Total premium collected: combined credit from both sides as my maximum profit"
            "- Maximum loss calculation: width of the wider spread minus total premium collected"
            "- Breakeven prices: the exact upper and lower prices where I start losing money"
            "- Position sizing: number of contracts based on my account size and 2-5% max risk per trade rule"
            "- Adjustment triggers: if the underlying moves to within 30% of a short strike, roll the threatened side"
            "- Profit taking rule: close the entire position at 50% of max profit or manage each side independently"
            "Format as a D.E. Shaw-style iron condor trade plan with a payoff range description, adjustment protocol, and daily income projection."
            "My iron condor: [CURRENT PRICE,  DAILY (0DTE)]"
        ),
        "params": []
    },
        {
        "id": "6",
        "name": "The Jane Street Pre-Market Edge Analyzer",
        "prompt_template": (
            "You are a senior volatility trader at Jane Street who analyzes pre-market conditions every morning at 8 AM to determine "
            "the optimal theta strategy before the opening bell — because the best trades are planned before the market opens."
            "I need a complete pre-market analysis that tells me exactly what to trade and how to trade it today."
            "Analyze:"
            "- Overnight futures movement: how much SPX futures moved overnight and whether the gap will hold or fade"
            "- Pre-market IV levels: are options pricing higher or lower volatility compared to yesterday's close"
            "- Economic calendar impact: what reports are released today and their historical impact on market range"
            "- Earnings exposure: which major companies report today and their potential to move the broader market"
            "- Globex range: the overnight high-to-low range in futures as a guide for today's expected range"
            "- Opening gap strategy: if there's a significant gap, will it fill (sell into it) or extend (stay cautious)"
            "- IV crush opportunity: if yesterday was a high-IV event, are there inflated premiums left to sell this morning"
            "- Previous day's close analysis: did the market close at highs (bearish lean), lows (bullish lean), or middle (neutral)"
            "- Support and resistance for today: the 3 key price levels where SPX is likely to bounce or stall"
            "- Pre-market trade plan: the exact strategy, strikes, expiration, and entry time based on all analysis"
            "Format as a Jane Street-style morning briefing with a market assessment, trade plan, and scenario playbook for bull, bear, and neutral outcomes."
            "Today's pre-market: [CURRENT SPX FUTURES PRICE, VIX LEVEL, AND ANY NEWS OR ECONOMIC EVENTS SCHEDULED FOR TODAY]"
        ),
        "params": []
    },
    {
        "id": "7",
        "name": "The Wolverine Trading Risk Management System",
        "prompt_template": (
            "You are a senior risk manager at Wolverine Trading who monitors options portfolios in real-time and enforces strict "
            "risk rules that prevent catastrophic losses — because surviving bad days is more important than maximizing good ones."
            "I need a complete risk management system for my daily theta income strategy."
            "Protect:"
            "- Daily loss limit: the maximum dollar amount I'm allowed to lose in a single day before closing all positions"
            "- Weekly loss limit: cumulative weekly threshold that triggers a trading pause until next Monday"
            "- Position size cap: maximum number of contracts or dollar risk per individual trade (never exceed 2-5% of account)"
            "- Correlation check: am I accidentally running the same directional bet in multiple positions simultaneously"
            "- Tail risk protection: how to hedge against a 3+ standard deviation move that blows through all my short strikes"
            "- VIX spike protocol: specific actions when VIX jumps 20%+ in a single day (close, hedge, or widen strikes)"
            "- Buying power management: never use more than 50% of total buying power so I always have room to adjust"
            "- Rolling vs closing decision tree: when to roll a losing position for recovery vs cutting the loss immediately"
            "- Recovery protocol: after a max loss day, how to reduce size and rebuild confidence systematically"
            "- Monthly drawdown circuit breaker: if monthly losses hit 10% of account, stop trading for the rest of the month"
            "Format as a Wolverine-style risk management manual with hard rules, decision trees, and a daily risk checklist to review before every trading session."
            "My account: [SMALL ACCOUNT SIZE, $500 DAILY INCOME TARGET, AND $200 MAXIMUM ACCEPTABLE DRAWDOWN]"
        ),
        "params": []
    },
        {
        "id": "8",
        "name": "The Peak6 SPY Weekly Income Calendar",
        "prompt_template": (
            "You are a senior income portfolio manager at Peak6 who runs a systematic weekly options income calendar on SPY — "
            "opening and closing positions on a fixed schedule that compounds premium income week after week."
            "I need a complete weekly trading calendar that tells me exactly what to do each day of the week."
            "Schedule:"
            "- Monday morning: analyze VIX, check economic calendar, set weekly expected range, and identify optimal strikes"
            "- Monday trade: open a weekly put credit spread or iron condor expiring Friday at 0.12-0.15 delta short strikes"
            "- Tuesday management: check positions at 10 AM — if at 30%+ profit already, consider closing early to free capital"
            "- Wednesday midweek review: reassess market direction — if one side is threatened, prepare adjustment or roll"
            "- Thursday acceleration: theta decay accelerates sharply — decide to hold for full decay or close at 65% profit"
            "- Friday morning decision: close all positions by 11 AM to avoid pin risk, or let OTM options expire worthless"
            "- Friday afternoon: review the week's performance, log all trades, and prepare Monday's watchlist"
            "- Position sizing cycle: use fixed percentage of account per week (3-5%) and increase only after 4 consecutive winning weeks"
            "- Loss week protocol: after a losing week, reduce position size by 50% for the following week"
            "- Monthly reconciliation: review all 4 weekly cycles, calculate actual win rate, and adjust delta levels if needed"
            "Format as a Peak6-style weekly trading calendar with exact daily actions, position management checkpoints, and a trade journal template."
            "My account: [SMALL ACCOUNT SIZE, $500 WEEKLY INCOME TARGET, LOW RISK, AND I AM ABLE TO MONITOR MY POSITIONS LIVE]"
        ),
        "params": []
    }
 
]
def perform_analysis(analysis_name, stock, sector, capfocus, risk_level):
    if not xai_api_key:
        yield "### ⚠️ Error\n`XAI_API_KEY` not found in environment variables."
        return

    selected = next((a for a in ANALYSES if a["name"] == analysis_name), None)
    if not selected:
        yield "Invalid Selection."
        return

    format_params = {
        "stock": stock.upper() if stock else "N/A",
        "sector": sector if sector else "unspecified",
        "capfocus": capfocus if capfocus else "unspecified",
        "risk": risk_level if risk_level else "medium"
    }

    try:
        client = Client(api_key=xai_api_key, timeout=300)
        prompt = selected["prompt_template"].format(**format_params)

        chat = client.chat.create(
            model="grok-4-1-fast-reasoning",
            tools=[web_search(), x_search()]
        )

        chat.append(system(
            "You are a senior equity analyst. Format your report for a clean display. "
            "Use # for title, ## for sections, and Markdown TABLES for data comparison. "
            "Bold ticker symbols like **$TSLA**."
        ))

        chat.append(user(prompt))
        
        full_text = ""
        # xAI SDK returns (response, chunk) in stream
        for response, chunk in chat.stream():
            if chunk.content:
                full_text += chunk.content
                yield full_text

    except Exception as e:
        yield f"### ❌ Error\n{str(e)}\n\n```\n{traceback.format_exc()}\n```"

def update_visibility(choice):
    selected = next((a for a in ANALYSES if a["name"] == choice), None)
    params = selected["params"] if selected else []
    
    return [
        gr.update(visible="stock" in params),
        gr.update(visible="sector" in params),
        gr.update(visible="capfocus" in params),
        gr.update(visible="risk" in params)
    ]

# Theme customization
theme = gr.themes.Default(
    primary_hue="indigo",
    secondary_hue="slate",
    neutral_hue="slate",
).set(
    body_background_fill="#fcfcfd",
    block_background_fill="#ffffff",
)

with gr.Blocks(title="xAI Options Research Tool") as demo:
    with gr.Row():
        with gr.Column():
            gr.Markdown("# 📈 Complete Options Research Tool")
            gr.Markdown("Leveraging **Grok-4-1-Fast-Reasoning** with Live Search.")
    
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Group():
                analysis_type = gr.Dropdown(
                    choices=[a["name"] for a in ANALYSES],
                    label="Select Analysis Type",
                    value=ANALYSES[0]["name"]
                )
                stock_input = gr.Textbox(label="Stock Ticker", placeholder="e.g. TSLA", visible=True)
                sector_input = gr.Dropdown(
                        label="Market Sector",
                        choices=[
                            "AI",
                            "Semiconductors",
                            "Information Technology", 
                            "Health Care", 
                            "Financials", 
                            "Consumer Discretionary", 
                            "Communication Services", 
                            "Industrials", 
                            "Consumer Staples", 
                            "Energy", 
                            "Utilities", 
                            "Real Estate", 
                            "Materials",
                            "Pharmaceuticals",
                            "Biotechnology"
                        ],
                        value="Information Technology", # Sets a default starting value
                        multiselect=False,              # Set to True if they can pick more than one
                        visible=False                   # Kept as False per your snippet
                    )
                cap_input = gr.Radio(choices=["small-cap", "mid-cap", "large-cap"], label="Cap Focus", visible=False)
                risk_input = gr.Dropdown(choices=["low", "medium", "high", "very high"], label="Risk", visible=False)
            
            run_btn = gr.Button("Execute Analysis", variant="primary")

        with gr.Column(scale=2):
            output_display = gr.Markdown("### Analysis Results will appear here...", container=True)

    analysis_type.change(fn=update_visibility, inputs=[analysis_type], outputs=[stock_input, sector_input, cap_input, risk_input])
    run_btn.click(fn=perform_analysis, inputs=[analysis_type, stock_input, sector_input, cap_input, risk_input], outputs=[output_display])

if __name__ == "__main__":
    # In Gradio 6+, theme goes in launch()
    demo.launch(theme=theme)