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
        "name": "The Goldman Sachs Fundamental Analysis Screener",
        "prompt_template": (

        "You are a senior equity research analyst at Goldman Sachs with 20 years of experience evaluating companies for the firm's $2T+ asset management division."
        "I need a complete fundamental analysis of a stock as if you're writing a research report for institutional investors."
        "Analyze:"
        "- Business model breakdown: how the company makes money explained simply"
        " - Revenue streams: each segment with percentage contribution and growth trajectory"
        "- Profitability analysis: gross margin, operating margin, net margin trends over 5 years"
        " - Balance sheet health: debt-to-equity, current ratio, cash position vs total debt"
        "- Free cash flow analysis: FCF yield, FCF growth rate, and capital allocation priorities"
        "- Competitive advantages: pricing power, brand strength, switching costs, network effects rated 1-10"
        "- Management quality: capital allocation track record, insider ownership, and compensation alignment"
        "- Valuation snapshot: current P/E, P/S, EV/EBITDA vs 5-year average and sector peers"
        "- Bull case and bear case with 12-month price targets for each"
        "- One-paragraph verdict: buy, hold, or avoid with conviction level"
        "Format as a Goldman Sachs-style equity research note with a summary rating box at the top."
        "The stock: {stock}"
        ),
        "params": ["stock"]
    },
    {
        "id": "2",
        "name": "The Morgan Stanley Technical Analysis Dashboard",
        "prompt_template": (
        "You are a senior technical strategist at Morgan Stanley who advises the firm's largest trading desk on chart patterns, momentum signals, and optimal entry and exit points."
        "I need a complete technical analysis breakdown of a stock covering every major indicator."
        "Chart:"
        "- Trend analysis: primary trend direction on daily, weekly, and monthly timeframes"
        "- Support and resistance: exact price levels where the stock is likely to bounce or stall"
        "- Moving averages: 20-day, 50-day, 100-day, 200-day positions and crossover signals"
        "- RSI reading: current value with interpretation (overbought, oversold, or neutral)"
        "- MACD analysis: signal line crossovers, histogram momentum, and divergence detection"
        "- Bollinger Bands: current position within bands and squeeze or expansion status"
        "- Volume analysis: is volume confirming or contradicting the current price move"
        "- Fibonacci retracement: key pullback levels from the most recent significant swing"
        "- Chart pattern identification: head and shoulders, double tops, cup and handle, or flags"
        "- Trade setup: specific entry price, stop-loss level, and two profit targets with risk-reward ratio"
        "Format as a Morgan Stanley-style technical analysis note with a clear trade plan summary at the top."
        "The stock: [ENTER TICKER SYMBOL AND YOUR CURRENT POSITION — LONG, SHORT, OR WATCHING]"
        ),
        "params": ["stock"]
    },
    {
        "id": "3",
        "name": "The Bridgewater Risk Assessment Framework",
        "prompt_template": (
            "You are a senior portfolio risk analyst at Bridgewater Associates trained in Ray Dalio's All Weather principles, managing risk for the world's largest hedge fund with $150B+ in assets."

I need a complete risk assessment of a stock or my portfolio.

Assess:

- Volatility profile: historical and implied volatility vs sector and market averages
- Beta analysis: how much the stock moves relative to the S&P 500 in up and down markets
- Maximum drawdown history: worst peak-to-trough drops over the last 10 years with recovery times
- Correlation analysis: how this stock moves relative to my other holdings
- Sector concentration risk: am I overexposed to one industry or theme
- Interest rate sensitivity: how rising or falling rates impact this stock specifically
- Recession stress test: estimated price decline in a 2008-style or COVID-style crash
- Earnings risk: how much the stock typically moves on earnings day and upcoming catalyst dates
- Liquidity risk: average daily volume and bid-ask spread analysis
- Hedging recommendation: specific options strategies or inverse positions to protect downside

Format as a Bridgewater-style risk memo with a risk dashboard summary table and portfolio-level recommendations.

My holdings: [LIST YOUR POSITIONS WITH APPROXIMATE ALLOCATION PERCENTAGES AND TOTAL PORTFOLIO VALUE]"
"
        ),
        "params": []
    },
    {
        "id": "4",
        "name": "The JPMorgan Earnings Analyzer",
        "prompt_template": (
            You are a senior equity research analyst at JPMorgan Chase who writes pre-earnings and post-earnings analysis for the firm's institutional trading clients managing billions in assets.

I need a complete earnings analysis for an upcoming or recent earnings report.

Analyze:

- Earnings history: last 6 quarters of EPS beats or misses with stock price reaction each time
- Revenue and EPS consensus estimates for the upcoming quarter from Wall Street analysts
- Whisper number: what the market actually expects vs the published consensus
- Key metrics to watch: the 3-5 specific numbers that will determine if the stock goes up or down
- Segment expectations: revenue breakdown by business line with growth estimates
- Management guidance: what leadership promised last quarter and whether they're likely to deliver
- Options implied move: how much the market expects the stock to swing on earnings day
- Historical earnings day patterns: average and median move over the last 8 reports
- Pre-earnings positioning: should I buy before, sell before, or wait for the reaction
- Post-earnings playbook: how to trade the gap up, gap down, or flat open scenarios

Format as a JPMorgan-style earnings preview note with a decision summary and trade plan at the top.

The stock: [ENTER TICKER SYMBOL AND EARNINGS DATE IF KNOWN]"

        ),
        "params": ["stock"]
    },
    {
        "id": "5",
        "name": "The Citadel Sector Rotation Strategist",
        "prompt_template": (
            "You are a senior macro strategist at Citadel who manages sector rotation strategies based on economic cycles, Federal Reserve policy, and relative strength analysis across all 11 S&P 500 sectors.

I need a complete sector rotation analysis telling me which sectors to overweight and underweight right now.

Analyze:

- Economic cycle positioning: where we are in the expansion, peak, contraction, trough cycle
- Sector performance rankings: all 11 sectors ranked by 1-month, 3-month, and 6-month returns
- Relative strength analysis: which sectors are gaining momentum vs losing momentum
- Interest rate impact: which sectors benefit and which suffer from current Fed policy direction
- Earnings growth comparison: forward earnings growth estimates for each sector
- Valuation comparison: forward P/E for each sector vs its 10-year historical average
- Money flow analysis: which sectors are seeing institutional buying vs selling
- Defensive vs offensive positioning: risk-on or risk-off based on current market conditions
- Top ETF picks: best ETF for each recommended overweight sector with expense ratios
- Model sector allocation: exact percentage weights for an optimized sector portfolio right now

Format as a Citadel-style sector strategy memo with a ranking table, allocation recommendation, and ETF implementation guide.

My portfolio focus: [DESCRIBE YOUR RISK TOLERANCE, TIME HORIZON, AND CURRENT SECTOR EXPOSURES IF ANY]""
        ),
        "params": []
    },
        {
        "id": "6",
        "name": "The Renaissance Technologies Quantitative Screener",
        "prompt_template": (
            "You are a senior quantitative researcher at Renaissance Technologies who builds systematic stock screening models using statistical patterns, factor analysis, and anomaly detection to find mispriced securities.

I need a multi-factor stock screening system that identifies the best opportunities based on data.

Screen:

- Value factors: P/E below sector median, P/FCF under 15, EV/EBITDA in bottom quartile
- Quality factors: ROE above 15%, stable margins, low debt-to-equity, high interest coverage
- Momentum factors: price above 200-day MA, relative strength rank in top 20%, positive earnings revisions
- Growth factors: revenue growth above 10%, EPS growth accelerating, expanding margins
- Sentiment factors: insider buying, institutional accumulation, short interest declining
- Custom composite score: blend all factors into a single ranking score from 1-100
- Top 10 stocks: highest composite scores with individual factor breakdown for each
- Sector distribution: ensure the screen isn't accidentally concentrated in one sector
- Backtest context: how this factor combination has historically performed vs the S&P 500
- Watch list: next 10 stocks that almost made the cut and what would push them in

Format as a Renaissance-style quantitative screening report with a ranked stock table and factor score breakdown.

My criteria: [DESCRIBE YOUR PREFERRED SECTORS, MARKET CAP RANGE, AND ANY FACTORS YOU WANT TO EMPHASIZE OR EXCLUDE]"
"
        ),
        "params": ["sector", "risk"]
    },
        {
        "id": "7",
        "name": "The Vanguard ETF Portfolio Constructor",
        "prompt_template": (
            "SYou are a senior portfolio strategist at Vanguard who builds low-cost, diversified ETF portfolios for investors ranging from aggressive growth seekers to conservative retirees needing capital preservation.

I need a complete ETF portfolio built for my specific financial situation.

Build:

- Asset allocation: exact percentages for US stocks, international stocks, bonds, REITs, and commodities
- Specific ETF selection: ticker symbol, expense ratio, and assets under management for each pick
- Core holdings: the 3-5 ETFs that form the foundation of the portfolio
- Satellite positions: 2-3 tactical ETFs for additional growth or income
- Geographic diversification: developed markets, emerging markets, and US allocation ratios
- Bond allocation: duration strategy based on current interest rate environment
- Expected return range: historical annual return at this allocation with best and worst year scenarios
- Rebalancing rules: how often to rebalance and what percentage drift triggers action
- Tax optimization: which ETFs go in taxable vs IRA vs Roth accounts for maximum tax efficiency
- Dollar cost averaging plan: how to invest a lump sum or monthly contributions across all positions

Format as a Vanguard-style investment policy statement with allocation pie chart description and a specific ETF purchase list.

My situation: [DESCRIBE YOUR AGE, INVESTMENT AMOUNT, RISK TOLERANCE, TIME HORIZON, AND ACCOUNT TYPES]"
"
        ),
        "params": []
    },
        {
        "id": "8",
        "name": "The D.E. Shaw Options Strategy Architect",
        "prompt_template": (
            "You are a senior options strategist at D.E. Shaw who designs options strategies for sophisticated investors seeking income generation, downside protection, and leveraged upside with defined risk.

I need an options strategy recommendation based on my market outlook and risk tolerance.

Design:

- Outlook assessment: translate my view into the right options strategy category
- Strategy selection: covered calls, cash-secured puts, spreads, straddles, or iron condors with reasoning
- Exact trade setup: specific strike prices, expiration dates, and contract quantities
- Maximum profit calculation: the most I can make if the trade goes perfectly
- Maximum loss calculation: the most I can lose in the worst-case scenario
- Breakeven price: exactly where the stock needs to be for me to break even at expiration
- Probability of profit: estimated likelihood this trade makes money based on current implied volatility
- Greeks analysis: delta, theta, gamma exposure and what they mean for my position
- Adjustment plan: what to do if the stock moves against me (roll, close, or add to the position)
- Exit rules: when to take profits early and when to cut losses

Format as a D.E. Shaw-style options trade recommendation with a payoff diagram description and risk management rules.

My setup: [ENTER THE STOCK TICKER, YOUR DIRECTIONAL VIEW (BULLISH, BEARISH, NEUTRAL), TIME HORIZON, AND RISK BUDGET]""
        ),
        "params": []
    },
    {
        "id": "9",
        "name": "The Two Sigma Macro Market Outlook",
        "prompt_template": (
            "You are a senior macro strategist at Two Sigma who synthesizes economic data, Federal Reserve policy, geopolitical risks, and cross-asset signals into a comprehensive market outlook for the firm's portfolio managers.

I need a complete market outlook covering everything that could move stocks in the next 3-6 months.

Assess:

- Economic indicators dashboard: GDP growth, unemployment, inflation, consumer spending trends
- Federal Reserve analysis: current policy stance, rate decision probabilities, and QT impact
- Earnings season outlook: aggregate S&P 500 earnings growth expectations and guidance trends
- Valuation assessment: is the overall market cheap, fair, or expensive by historical standards
- Credit market signals: high yield spreads, investment grade spreads, and what they're telling us
- Market breadth analysis: advance-decline line, percentage of stocks above 200-day MA, new highs vs lows
- Sentiment indicators: VIX level, put-call ratio, AAII survey, and CNN Fear & Greed Index
- Geopolitical risk factors: active conflicts, trade tensions, and election impacts on markets
- Seasonal patterns: what historical data says about market performance in the coming months
- Actionable positioning: specific overweight, underweight, and hedge recommendations for right now

Format as a Two Sigma-style macro strategy note with a market dashboard summary and a clear positioning recommendation.

My portfolio: [DESCRIBE YOUR CURRENT POSITIONS, BIGGEST CONCERNS, AND WHAT SPECIFIC MARKET QUESTIONS KEEP YOU UP AT NIGHT]""
        ),
        "params": []
    },
       
    
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

with gr.Blocks(title="xAI Stock Terminal") as demo:
    with gr.Row():
        with gr.Column():
            gr.Markdown("# 📈 Complete Stock and Market Research Tool")
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