# Focus Guardian

An AI-powered productivity assistant that helps you stay focused on your work by monitoring your screen activity and providing real-time feedback.

## Overview

Focus Guardian is a Python-based application that uses computer vision and natural language processing to:

1. Monitor your screen activity in real-time
2. Compare your activities against your stated productivity goals
3. Alert you when you drift off task with customizable notifications
4. Provide session analytics to help improve your productivity

The system uses Groq's LLM models for intelligent activity analysis and adaptive rule generation based on your specific goals.

## Features

- **Goal-Based Monitoring**: Define your work goals in natural language
- **Dynamic Rule Generation**: AI-generated rules based on your specific goals
- **Real-Time Activity Analysis**: Computer vision-based screen monitoring
- **Multi-Modal Alerts**: Sound, popup, and system notifications
- **Super Focus Mode (SFM)**: Three-strike system with option to block distractions
- **Session Analytics**: Comprehensive productivity reports
- **Cross-Platform Support**: Works on Windows, macOS, and Linux

## Requirements

### Python Version
- Python 3.7+

### Required Libraries
- `groq`: Groq API client for LLM access
- `pyautogui`: For screen capture functionality
- `pillow`: For image processing
- `tkinter`: For popup notifications (usually included with Python)
- `plyer`: For system notifications (optional)

### Optional Libraries
- `pydub`: For cross-platform sound alerts (recommended for macOS/Linux)
- `winsound`: For sound alerts on Windows (included with Python on Windows)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/focus-guardian.git
cd focus-guardian
```

2. Install required dependencies:
```bash
pip install groq pyautogui pillow plyer
```

3. Install optional dependencies based on your platform:

For cross-platform sound support:
```bash
pip install pydub
```

4. Create an API key file:
   - Create a file named `api.txt` in the application directory
   - Paste your Groq API key in this file

## Usage

### Basic Usage

```bash
python procrastination_preventer.py "Work on my thesis for 2 hours"
```

### With Super Focus Mode (SFM)

```bash
python procrastination_preventer.py "Study for my exam" --sfm
```

### Customizing the Monitoring Interval

```bash
python procrastination_preventer.py "Code a new feature" --interval 20
```

### Disable Sound or Popup Alerts

```bash
python procrastination_preventer.py "Write an essay" --no-sound
python procrastination_preventer.py "Design website mockups" --no-popup
```

### Analyze Previous Session

```bash
python procrastination_preventer.py --analyze focus_session_20250225_143022.json
```

## Command Line Arguments

| Argument | Description |
|----------|-------------|
| `goal` | Your work goal in natural language (required unless using --analyze) |
| `--sfm` | Enable Super Focus Mode (3 warnings then block) |
| `--interval` | Monitoring interval in seconds (default: 10) |
| `--no-sound` | Disable warning sounds |
| `--no-popup` | Disable popup warnings |
| `--analyze` | Analyze a previous session JSON file |

## How It Works

1. **Goal Analysis**: When you start Focus Guardian, it uses a LLM to analyze your goal and generate appropriate monitoring rules
2. **Screen Monitoring**: At regular intervals, it captures your screen and uses vision models to identify active applications
3. **Activity Validation**: Each detected activity is validated against your goals and rules
4. **Notifications**: If distractions are detected, you receive customized alerts
5. **Session Analytics**: When you finish a session, a detailed productivity report is generated

## Troubleshooting

### API Key Issues
- Ensure your `api.txt` file contains a valid Groq API key with no extra spaces or lines
- Check API key permissions if you experience authorization errors

### Screen Capture Issues
- On macOS, you may need to grant screen recording permissions to your terminal application
- On Linux, ensure you have the required X11 dependencies installed

### Sound Alert Issues
- On non-Windows platforms, install `pydub` for better sound support
- Check system volume and notification settings

## Future Plans

- Mobile companion app with remote monitoring capabilities
- Integration with productivity tools like Pomodoro timers
- Machine learning-based personalization of distraction detection
- Cloud sync for multi-device productivity tracking

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Groq for providing powerful LLM APIs
- The open-source libraries that made this project possible

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.