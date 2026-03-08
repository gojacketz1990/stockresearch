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
        "name": "Hidden Catalyst Discovery",
        "prompt_template": (
            "Scan X for subtle mentions of upcoming catalysts (contracts, regulation changes, pilots, partnerships) that are not in mainstream news."
        ),
        "params": []
    },
        {
        "id": "8",
        "name": "Insider Language Pattern Scan",
        "prompt_template": (
            "Analyze posts from employees, ex-employees, or contractors casually referencing their companys momentum or workload."
        ),
        "params": []
    },
    {
        "id": "9",
        "name": "Volume Without News",
        "prompt_template": (
            "Identify stocks with unusual trading volume today but no major news."
            "Cross-check with X sentiment for possible early explanations."
        ),
        "params": []
    },
        {
        "id": "10",
        "name": "Sector Rotation Early Signal",
        "prompt_template": (
            "Detect early chatter suggesting capital rotating into a specific sector before ETFs or analysts mention it."
            "Rotations start on X, not Bloomberg."
        ),
        "params": []
    },
        {
        "id": "11",
        "name": "Earnings Whisper Analysis",
        "prompt_template": (
            "Analyze pre-earnings discussions on X to extract ‘whisper numbers’ and expectations versus consensus."
        ),
        "params": []
    },
        {
        "id": "12",
        "name": "Crowded Trade Exit Signal",
        "prompt_template": (
            "Find stocks where bullish sentiment is becoming repetitive, meme-like, or overly confident."
        ),
        "params": []
    },
    {
        "id": "13",
        "name": "Small-Cap Smart Money Trail",
        "prompt_template": (
            "Identify small-cap stocks being discussed by hedge fund analysts, ex-bankers, or finance PhDs on X."
        ),
        "params": []
    },
        {
        "id": "14",
        "name": "Fear Compression Scan",
        "prompt_template": (
            "Find stocks where fear-driven language is declining even though price hasn’t moved yet."
        ),
        "params": []
    },
        {
        "id": "15",
        "name": "Macro-to-Micro Translation",
        "prompt_template": (
            "Translate current macro events into specific stocks that might benefit before the connection becomes obvious."
        ),
        "params": []
    },
        {
        "id": "16",
        "name": "Management Credibility Signal",
        "prompt_template": (
            "Analyze CEO or CFO posts for changes in tone, confidence, or specificity over time."
        ),
        "params": []
    },
    {
        "id": "17",
        "name": "Early Meme Formation Detector",
        "prompt_template": (
            "Identify stocks transitioning from serious discussion to early meme language but still low market cap."
        ),
        "params": []
    },
        {
        "id": "18",
        "name": "Regulatory Tailwind Radar",
        "prompt_template": (
            "Scan policy, legal, or regulatory discussions on X that could quietly favor specific companies."
        ),
        "params": []
    },
        {
        "id": "19",
        "name": "Global Edge Finder",
        "prompt_template": (
            "Track non-US accounts discussing US stocks before US traders notice."
        ),
        "params": []
    },
    {
        "id": "20",
        "name": "Future Price Path Simulation",
        "prompt_template": (
            "Based on current sentiment, narratives, and catalysts, simulate 3 possible price paths for {stock} over the next 3–6 months."
        ),
        "params": ["stock"]
    },
        {
        "id": "21",
        "name": "Analyze current discussions on X about emerging trends in sector",
        "prompt_template": (
            "Analyze current discussions on X about emerging trends in {sector}. "
            "Sector: {sector} "
            "Focus: {capfocus} "
            "Identify: "
            "1. What trends are gaining traction right now "
            "2. Stocks being mentioned repeatedly "
            "3. New products, technologies, or catalysts "
            "4. Sentiment shift patterns "
            "5. Early-stage companies getting attention "
            "6. Comparison to mainstream media coverage (are we early?) "
            "7. Key opinion leaders driving the narrative "
            "8. Stocks positioned to benefit most "
            "Show me what's trending NOW, not last quarter."
        ),
        "params": ["sector", "capfocus"]
    },
        {
        "id": "22",
        "name": "Identify Stocks with Viral Momentum",
        "prompt_template": (
            "Search X for stocks that are gaining viral momentum right now. "
            "Focus: {capfocus} "
            "Criteria: "
            "- Sudden spike in mentions "
            "- Increasing engagement on posts "
            "- Multiple accounts discussing simultaneously "
            "- Market cap: [your preference] "
            "For each stock gaining traction, analyze: "
            "1. Why it's trending (catalyst, news, hype?) "
            "2. Quality of the narrative (substance vs. pump) "
            "3. Who's driving the conversation "
            "4. Fundamental backing (does it deserve attention?) "
            "5. Risk of being too late "
            "6. Historical pattern (does viral = gains for this stock?) "
            "7. Entry/exit strategy if momentum is real "
            "8. Red flags suggesting pump and dump "
            "Separate real opportunities from noise."
        ),
        "params": ["capfocus"]
    },
        {
        "id": "23",
        "name": "Monitor Breaking News and Catalysts",
        "prompt_template": (
            "Search X for breaking news and catalysts related to {stock} in the last 24 hours."
            "Focus on actionable insights, not noise."
            "Based on what you find, provide: "
            "Overall sentiment (bullish/neutral/bearish) "
            "Key themes and narratives emerging "
            "Notable investors or analysts discussing it "
            "Any breaking news or catalysts mentioned "
            "Shift in sentiment compared to last week "
            "Retail vs. institutional sentiment indicators "
            "Hype level assessment (organic vs. pump) "
            "Momentum prediction: Building or fading?"
        ),
        "params": ["stock"]
    },
    {
        "id": "24",
        "name": "Gauge Retail vs. Institutional Sentiment",
        "prompt_template": (
            "Analyze the difference between retail and institutional sentiment for {stock} based on X."
        ),
        "params": ["stock"]
    },
        {
        "id": "25",
        "name": "Detect Early Warning Signs and Red Flags",
        "prompt_template": (
            "Search X for red flags, concerns, or negative sentiment about {stock}."
        ),
        "params": ["stock"]
    },
    {
        "id": "26",
        "name": "Create a Real-Time Watchlist Strategy",
        "prompt_template": (
            "Help me build a system to monitor stocks on X for trading opportunities. "
            "My focus: day trading "
            "Sectors: {sector} "
            "Risk tolerance: {risk} "
            "Focus: {capfocus} "
            "Create a framework for: "
            "1. Which accounts and hashtags to monitor daily "
            "2. Sentiment indicators that signal buy/sell "
            "3. How to filter noise from actionable signals "
            "4. Tools and search strategies for X "
            "5. How to validate X sentiment with fundamentals "
            "6. Entry and exit triggers based on momentum "
            "7. Risk management when trading on sentiment "
            "8. Daily routine to stay ahead of the market "
            "Make it systematic and repeatable."
        ),
        "params": ["sector", "risk","capfocus"]
    },
            {
        "id": 27,
        "name": "Recent Activity by Sector",
        "prompt_template": (
            "Search X for recent activity from notable investors and analysts regarding {sector} "
            "Focus on: "
            "Prominent investors (e.g., [specific names if known]) "
            "Verified analysts and researchers "
            "Hedge fund managers with public presence "
            "Analyze: "
            "1. What stocks they're discussing or buying "
            "2. Their thesis and reasoning "
            "3. Timing of their posts (recent accumulation?) "
            "4. Engagement and agreement from others "
            "5. Contrarian vs. consensus views "
            "6. Track record of their past calls "
            "7. Any disclosed positions or conflicts "
            "8. Should I follow this move? Why or why not? "
            "Help me follow smart money in real-time."
        ),
        "params": ["sector"]
    },
                {
        "id": 28,
        "name": "Why is this stock moving",
        "prompt_template": (
            "Analyze the main drivers behind {stock}'s price action since [specific time/date or 'market open today']. Focus especially on:"
            "Categorize and roughly weight the drivers as:"
            "Fundamental news / earnings surprise / guidance change (weight %)"
            "Analyst upgrades/downgrades / price target changes"
            "Technical / momentum factors"
            "Macro / interest rate / commodity / FX crossover effects"
            "Sentiment / flow / positioning (institutional, retail, options gamma)"
            "Idiosyncratic (M&A rumor, legal, product launch, etc.)"
            "End with your best judgment of whether the current move looks sustainable or likely to reverse in the short term, and why."
        ),
        "params": ["stock"]
    },
    {
        "id": "29",
        "name": "Generate a Real-Time Watchlist by Risk Level for Stocks Under $10",
        "prompt_template": (
            "Search X and use web search to create a real-time watchlist of stocks currently trading under $10 that are suitable for day trading or short-term momentum plays. "
            "Focus on low-priced stocks (under $10/share) with potential for volatility, volume spikes, or emerging buzz. "
            "Use up-to-date market information as of today. "
            "Prioritize stocks that show: "
            "- High relative volume or unusual volume surges "
            "- Recent price momentum (e.g., big % moves in the last 1 to 5 days) "
            "- Positive chatter, catalysts, or hype on X/Twitter, Reddit, or financial news "
            "Only include stocks where the key risk level matches the user's risk tolerance: {risk} (e.g., if {risk} is 'medium', filter for medium-risk stocks only). "
            "Define risk levels as: Low (stable with low volatility), Medium (moderate volatility and some uncertainty), High (high volatility, speculative, or significant downside potential). "
            "For each stock in the watchlist (aim for 8 to 15 tickers that fit the risk filter), include: "
            "1. Ticker symbol and company name "
            "2. Current price (approximate, under $10) "
            "3. Today's % change and volume vs average "
            "4. Why it's on the watchlist (e.g., recent catalyst, X mentions, sector heat, technical breakout) "
            "5. Key risk level (must match {risk}) "
            "6. Suggested watch levels (e.g., breakout above X, support at Y) "
            "Structure the output as a clean markdown table or bulleted list for easy scanning. "
            "At the end, explain your screening criteria and any sources/tools you used to compile this real-time list. "
            "Remind that this is not financial advice — always do your own due diligence, use level 2/data, and manage risk tightly on sub-$10 names."        ),
        "params": ["risk"]
    },
    {
        "id": "30",
        "name": "Company and Stock Strength Assessment",
        "prompt_template": (
            "Always convert and report ALL financial and valuation metrics (market cap, revenue, profit, debt, cash, EBITDA, etc.) exclusively in United States Dollars (USD), using the most recent reliable exchange rate. Never show values in GBP, EUR, JPY, CAD, or any other currency — only USD equivalents. "
            "Conduct thorough research on company (ticker: {stock}) using Web Search, Browse Page, X Keyword Search, X Semantic Search, and other relevant tools. "
            "Assess the overall strength of the company and its stock, focusing on fundamentals, market position, risks, and investment potential. "
            "Gather data from reliable sources like financial news sites, SEC filings, analyst reports, X discussions, and company websites. "
            "Based on what you find, provide a structured analysis including: "
            "Company overview: Core business, market cap (in USD), recent revenue/profit trends (in USD), key products/services "
            "Financial health: Debt levels (in USD), cash flow (in USD), profitability metrics (e.g., ROE, margins), latest earnings surprises (in USD), all values strictly in USD "
            "Competitive position: Market share, moat (e.g., brand, tech, barriers), peers comparison "
            "Growth prospects: Upcoming catalysts (e.g., product launches, expansions), industry trends, analyst forecasts "
            "Risks and challenges: Regulatory issues, competition threats, macroeconomic sensitivities "
            "Stock assessment: Current valuation (P/E, EV/EBITDA vs. peers — all in USD terms), price performance YTD, technical indicators (e.g., support/resistance) "
            "Sentiment analysis: Overall X/social media vibe (bullish/neutral/bearish), notable mentions from investors/analysts "
            "Investment thesis: Strengths/weaknesses summary, buy/hold/sell rationale with 12-month outlook "
            "Sources: List key references with links where possible. "
            "Output Rules: All monetary amounts MUST be in USD only (e.g., $1.25B USD). Do NOT include original non-USD amounts or conversions in parentheses. Remain objective and data-driven."
        ),
        "params": ["stock"]
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