import os
import json
import base64
import io
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# =====================================================
# Setup
# =====================================================

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =====================================================
# OpenAI Vision Analysis
# =====================================================

def analyze_chart_with_openai(image: Image.Image):

    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": """
You are an expert institutional-level technical analyst.

Analyze the chart image and detect classical patterns such as:
- Falling Wedge
- Rising Wedge
- Ascending Triangle
- Descending Triangle
- Bullish Pennant
- Bearish Pennant
- Head and Shoulders
- Double Top / Double Bottom

Return ONLY valid JSON in this structure:

{
  "analysis": "Detailed technical explanation",
  "patterns": [
    {
      "name": "Pattern Name",
      "confidence": 0.85,
      "breakout_bias": "bullish or bearish",
      "trendlines": [
        {"x1": 100, "y1": 200, "x2": 400, "y2": 150}
      ]
    }
  ]
}

Coordinates should be approximate pixel positions relative to the image.
"""
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this stock chart."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=1200
    )

    return json.loads(response.choices[0].message.content)

# =====================================================
# Draw Trendlines
# =====================================================

def draw_annotations(image: Image.Image, analysis_json):

    fig, ax = plt.subplots(figsize=(8,6))
    ax.imshow(image)
    ax.axis("off")

    if "patterns" in analysis_json:
        for pattern in analysis_json["patterns"]:
            for line in pattern.get("trendlines", []):
                ax.plot(
                    [line["x1"], line["x2"]],
                    [line["y1"], line["y2"]],
                    linewidth=3
                )

    fig.canvas.draw()

    buffer = np.asarray(fig.canvas.buffer_rgba())
    annotated_image = Image.fromarray(buffer[:, :, :3])

    plt.close(fig)

    return annotated_image

# =====================================================
# Main Processing
# =====================================================

def process_image(image):

    analysis = analyze_chart_with_openai(image)
    annotated_image = draw_annotations(image, analysis)

    explanation = analysis.get("analysis", "No analysis returned.")

    return explanation, annotated_image

# =====================================================
# Gradio Interface
# =====================================================

demo = gr.Interface(
    fn=process_image,
    inputs=gr.Image(type="pil"),
    outputs=[
        gr.Textbox(label="Technical Analysis"),
        gr.Image(label="Annotated Chart")
    ],
    title="AI Stock Chart Pattern Detector (Vision-Based)",
    description="Upload a stock chart image. The AI will detect patterns and annotate trendlines."
)

if __name__ == "__main__":
    demo.launch()
