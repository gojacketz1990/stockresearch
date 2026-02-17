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
        ),
        "params": ["stock"]
    },
    {
        "id": "2",
        "name": "Analyze current discussions on X about emerging trends in sector",
        "prompt_template": (
            "Sector: {sector} Focus: {capfocus} Identify trending stocks and catalysts."
        ),
        "params": ["sector", "capfocus"]
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
            "Search X for stocks gaining viral momentum for market cap {capfocus}."
        ),
        "params": ["capfocus"]
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
            "Help me build a system to monitor {sector} stocks for {capfocus} with {risk} risk."
        ),
        "params": ["capfocus", "sector", "risk"]
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
                sector_input = gr.Textbox(label="Sector", placeholder="e.g. Tech", visible=False)
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