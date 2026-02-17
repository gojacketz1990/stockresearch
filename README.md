# 📈 xAI Stock Terminal
**Real-time equity analysis powered by Grok-4-1-Fast-Reasoning.**

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The **xAI Stock Terminal** is a professional-grade research tool that leverages live Web and X (Twitter) search to identify emerging trends, track "smart money" moves, and gauge retail sentiment before they hit mainstream headlines.



---

## ✨ Features
- **Live X Integration:** Scans real-time discussions for sentiment and narrative shifts.
- **Advanced Reasoning:** Uses Grok-4-1-Fast-Reasoning to filter noise from actionable signals.
- **Multiple Analysis Modes:** Specialized agents for viral momentum, breaking news, and institutional tracking.
- **Streaming Output:** Instant, token-by-token report generation for a responsive experience.

---

## 🚀 Getting Started

> **System Requirement:** These instructions are for **macOS**. Command syntax for Windows (CMD/PowerShell) will vary.

### 1. Clone & Navigate

git clone [https://github.com/gojacketz1990/stockresearch.git](https://github.com/gojacketz1990/stockresearch.git)
cd stockresearch

### Set Up Virtual Environment

python3 -m venv venv
source venv/bin/activate


### Install Requirements

pip install -r requirements.txt


### Configuration

#### In the project root, create a .env file:

touch .env

#### Past your key into the file:

XAI_API_KEY=your_xai_api_key_here

### Usage

#### Launch the Gradio Interface:

python FINAL_catch_trends_stream.py

Once running, the terminal will provide a local URL (e.g., http://127.0.0.1:7860). Open this in your browser to start your research.


### Security Note

Never commit your .env file to GitHub. Ensure your .gitignore includes:

.env
venv/
__pycache__/

