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

# Define the analysis configurations
ANALYSES = [
    {
        "id": "1",
        "name": "Real-Time stock sentiment",
        "prompt_template": (
            "Search X (Twitter) for the latest discussions about {stock} and analyze the sentiment. "
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
        "id": "2",
        "name": "Sudden Attention Spike Detector",
        "prompt_template": (
            "Find stocks that saw a sudden spike in mentions on X in the last 12 hours, excluding major news outlets. "
            "Focus on organic chatter, not headlines."
        ),
        "params": []
    },
    {
        "id": "3",
        "name": "Retail Before Institutions",
        "prompt_template": (
            "Identify stocks where retail traders are accumulating before any analyst upgrades or institutional reports."
        ),
        "params": []
    },
    {
        "id": "4",
        "name": "Narrative Change Tracker",
        "prompt_template": (
            "Track how the narrative around {stock} has changed over the last 30 days."
            "What are people saying now that they weren’t saying before?"
        ),
        "params": ["stock"]
    },
    {
        "id": "5",
        "name": "Influencer Accumulation Signal",
        "prompt_template": (
            "Detect when respected traders, operators, or domain experts start mentioning a stock repeatedly without hyping it."
        ),
        "params": []
    },
        {
        "id": "6",
        "name": "Bear-to-Bull Flip Alert",
        "prompt_template": (
            "Find stocks where historically bearish accounts recently turned neutral or bullish."
            "Highlight exact language changes."
        ),
        "params": ["sector", "risk"]
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