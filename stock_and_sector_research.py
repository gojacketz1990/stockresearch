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
        "required_params": ["sector", "capfocus"]
    },
    {
        "id": "3",
        "name": "Track Smart Money and Influencer Moves",
        "prompt_template": (
            "Search X for recent activity from notable investors regarding {sector}."
        ),
        "params": ["sector"]
    },
    {
        "id": "4",
        "name": "Identify Stocks with Viral Momentum",
        "prompt_template": (
            "Search X for stocks that are gaining viral momentum right now. "
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
        "required_params": []
    },
    {
        "id": "5",
        "name": "Monitor Breaking News and Catalysts",
        "prompt_template": (
            "Search X for breaking news and catalysts related to {stock} in the last 24 hours."
        ),
        "params": ["stock"]
    },
    {
        "id": "6",
        "name": "Gauge Retail vs. Institutional Sentiment",
        "prompt_template": (
            "Analyze the difference between retail and institutional sentiment for {stock} based on X."
        ),
        "params": ["stock"]
    },
    {
        "id": "7",
        "name": "Detect Early Warning Signs and Red Flags",
        "prompt_template": (
            "Search X for red flags, concerns, or negative sentiment about {stock}."
        ),
        "params": ["stock"]
    },
    {
        "id": "8",
        "name": "Create a Real-Time Watchlist Strategy",
        "prompt_template": (
            "Help me build a system to monitor stocks on X for trading opportunities. "
            "My focus: day trading "
            "Sectors: {sector} "
            "Risk tolerance: {risk} "
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
        "required_params": ["sector", "risk"]
    },
        {
        "id": 9,
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
        "required_params": ["sector"]
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
            gr.Markdown("# 📈 AI and X Fueled Stock Research Tool for Research, Trends and Sentiment")
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
                risk_input = gr.Dropdown(choices=["low", "medium", "high"], label="Risk", visible=False)
            
            run_btn = gr.Button("Execute Analysis", variant="primary")

        with gr.Column(scale=2):
            output_display = gr.Markdown("### Analysis Results will appear here...", container=True)

    analysis_type.change(fn=update_visibility, inputs=[analysis_type], outputs=[stock_input, sector_input, cap_input, risk_input])
    run_btn.click(fn=perform_analysis, inputs=[analysis_type, stock_input, sector_input, cap_input, risk_input], outputs=[output_display])

if __name__ == "__main__":
    # In Gradio 6+, theme goes in launch()
    demo.launch(theme=theme)