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
        "name": "Trades for individual stock",
        "prompt_template": (
            "Analyze the current market and identify five high-probability trades for {stock}, "
            "including entry, targets, stop-loss, risk–reward ratio, and brief technical and fundamental "
            "justification."
        ),
        "params": ["stock"]
    },
    {
        "id": "2",
        "name": "Automated Technical Analyst",
        "prompt_template": (
            "Evaluate {stock} using both daily and weekly timeframes. Identify key support and resistance zones, "
            "trendlines, moving averages, and momentum indicators. Then deliver a clear Buy, Hold, or Sell signal "
            "with step-by-step reasoning."
        ),
        "params": ["stock"]
    },
    {
        "id": "3",
        "name": "News-to-Trade Converter",
        "prompt_template": (
            "Summarize the most recent news related to {stock} and convert it into actionable "
            "trading insights. Outline the potential short-term and long-term impact, expected price movement "
            "range, and suggested positioning."
        ),
        "params": ["stock"]
    },
    {
        "id": "4",
        "name": "Strategy Backtester",
        "prompt_template": (
            "Backtest the {strategy} on {stock} "
            "over the past {time_period}. Report the win rate, profit factor, maximum drawdown, and "
            "suggest potential improvements to enhance performance."
        ),
        "params": ["stock", "strategy", "time_period"]
    },
    {
        "id": "5",
        "name": "Portfolio Risk Manager",
        "prompt_template": (
            "Evaluate my portfolio: {portfolio}. Identify areas of overexposure, "
            "weak positions, and hidden correlations. Recommend risk-adjusted rebalancing and hedging strategies "
            "designed to withstand a potential 20% market decline."
        ),
        "params": ["portfolio"]
    },
    {
        "id": "6",
        "name": "Fully Automated Trade Plan",
        "prompt_template": (
            "Create a structured daily trading plan for {sector} with {risk}. Include a pre-market scan, "
            "opening execution strategy, midday adjustments, and closing approach. Present the plan as a "
            "time-stamped checklist I can follow step by step."
        ),
        "params": ["sector", "risk"]
    },
]

def perform_analysis(analysis_name, stock, sector, strategy, time_period, portfolio, risk_level):
    if not xai_api_key:
        yield "### ⚠️ Error\n`XAI_API_KEY` not found in environment variables."
        return

    selected = next((a for a in ANALYSES if a["name"] == analysis_name), None)
    if not selected:
        yield "### ⚠️ Error\nInvalid analysis selection."
        return

    # Basic validation
    required_params = selected["params"]
    if "stock" in required_params and not stock.strip():
        yield "### ⚠️ Error\nStock ticker is required for this analysis."
        return
    if "strategy" in required_params and not strategy.strip():
        yield "### ⚠️ Error\nStrategy description is required."
        return
    if "time_period" in required_params and not time_period.strip():
        yield "### ⚠️ Error\nTime period is required (e.g., '5 years')."
        return
    if "portfolio" in required_params and not portfolio.strip():
        yield "### ⚠️ Error\nPortfolio details are required (e.g., 'AAPL 40%, TSLA 30%, ...')."
        return

    format_params = {
        "stock": stock.upper().strip() if stock else "N/A",
        "sector": sector if sector else "unspecified",
        "strategy": strategy.strip() if strategy else "N/A",
        "time_period": time_period.strip() if time_period else "5 years",
        "portfolio": portfolio.strip() if portfolio else "N/A",
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
        gr.update(visible="stock" in params),       # stock_input
        gr.update(visible="sector" in params),      # sector_input
        gr.update(visible="strategy" in params),    # strategy_input
        gr.update(visible="time_period" in params), # time_period_input
        gr.update(visible="portfolio" in params),   # portfolio_input
        gr.update(visible="risk" in params)         # risk_input
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
                stock_input = gr.Textbox(
                    label="Stock Ticker",
                    placeholder="e.g. TSLA",
                    visible=True
                )
                sector_input = gr.Dropdown(
                    label="Market Sector",
                    choices=[
                        "AI", "Semiconductors", "Information Technology", "Health Care",
                        "Financials", "Consumer Discretionary", "Communication Services",
                        "Industrials", "Consumer Staples", "Energy", "Utilities",
                        "Real Estate", "Materials", "Pharmaceuticals", "Biotechnology"
                    ],
                    value="Information Technology",
                    multiselect=False,
                    visible=False
                )
                strategy_input = gr.Textbox(
                    label="Strategy",
                    placeholder="e.g. moving average crossover",
                    visible=False
                )
                time_period_input = gr.Textbox(
                    label="Time Period (for backtest)",
                    placeholder="e.g. 3 years, 1 year, 6 months",
                    visible=False
                )
                portfolio_input = gr.Textbox(
                    label="Portfolio (ticker % weight, ...)",
                    placeholder="e.g. AAPL 40%, TSLA 30%, SPY 30%",
                    lines=3,
                    visible=False
                )
                risk_input = gr.Dropdown(
                    choices=["low", "medium", "high", "very high"],
                    label="Risk Level",
                    value="medium",
                    visible=False
                )
            
            run_btn = gr.Button("Execute Analysis", variant="primary")

        with gr.Column(scale=2):
            output_display = gr.Markdown("### Analysis Results will appear here...", container=True)

    # Correct order: stock, sector, strategy, time_period, portfolio, risk
    analysis_type.change(
        fn=update_visibility,
        inputs=[analysis_type],
        outputs=[
            stock_input, sector_input, strategy_input,
            time_period_input, portfolio_input, risk_input
        ]
    )

    run_btn.click(
        fn=perform_analysis,
        inputs=[
            analysis_type, stock_input, sector_input,
            strategy_input, time_period_input, portfolio_input, risk_input
        ],
        outputs=[output_display]
    )

if __name__ == "__main__":
    demo.launch(theme=theme)