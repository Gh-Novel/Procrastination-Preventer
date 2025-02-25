# Focus - Procrastination Prevention System

A smart productivity tool that monitors your computer activity using AI vision models, helps maintain focus through alerts, and provides detailed session analytics.

## Features

- **Goal-Oriented Monitoring**: Set a focus goal and get alerts when distracted
- **AI-Powered Analysis**: Uses Groq's LLMs and vision models to detect distractions
- **Focus Timeline Visualization**: See your focus patterns with interactive charts
- **Achievement System**: Earn badges for focused work sessions
- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **Focus Mode**: Auto-block distracting websites after configurable warnings

## Installation

### Prerequisites
- Python 3.8+
- Groq API key (free trial available)
- Supported browsers (Chrome, Firefox, Edge)

### Setup
1. Clone repository:
   ```bash
   git clone https://github.com/Gh-Novel/Procrastination-Preventer.git
   cd focus-system
2. Install dependencies:
   ```bash
   pip install customtkinter matplotlib pyautogui groq pillow
3. Create api.txt in root directory and paste your Groq API key
4. (Optional) For Linux/macOS users:
   ```bash
   sudo apt-get install scrot  # For screenshot functionality

# Usage

1. Start the application:
   ```bash
   python main.py
2. Set your focus goal (e.g., "Coding in VS Code and researching in Chrome")
3. Adjust settings:
