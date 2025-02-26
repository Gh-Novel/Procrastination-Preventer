# Procrastination Prevention: Your AI-Powered Productivity Ally

Focus Guardian is an intelligent, AI-driven tool designed to help you overcome procrastination and reclaim your focus. By dynamically analyzing your screen activity and translating your personal work goals into actionable rules, it acts as your digital guardian against distractions.

## Key Features

- **Real-Time Monitoring**: Continuously captures and analyzes your screen to detect unproductive activities.
- **Dynamic Goal Parsing**: Converts your productivity goals into tailored rules for permitted applications and usage.
- **Multi-Modal Alerts**: Issues friendly sound notifications, pop-up warnings, and system alerts to keep you on track.
- **Distraction Blocking**: Optionally intervenes by closing distracting applications after repeated warnings.
- **Insightful Analytics**: Provides comprehensive session reports, including productivity rates, top activities, and distraction patterns.

## Getting Started

Run Focus Guardian from the command line with your work goal:

```bash
python procrastination_preventer.py "Your work goal here"
```

## Available Flags

- `--sfm` - Enable Super Focus Mode (3-strike rule).
- `--no-sound` - Disable warning sounds.
- `--no-popup` - Disable popup warnings.
- `--interval` - Adjust the monitoring interval (default: 10 seconds).

## How It Works

1. **Screen Capture & Analysis**: Focus Guardian captures your screen and uses AI to identify the active application or website.
2. **Activity Validation**: It validates whether the current activity aligns with your productivity goal using dynamically generated rules.
3. **Real-Time Alerts**: When a distraction is detected, Focus Guardian alerts you via sound notifications, pop-up warnings, and system alerts.
4. **Session Analytics**: It logs your activities and provides detailed session reports, helping you understand and improve your productivity.

## Why Use Focus Guardian?

- **Stay Focused**: Eliminate distractions and maintain productivity.
- **Actionable Insights**: Get detailed reports to analyze your work habits.
- **Customizable**: Tailor the tool to match your personal productivity goals.
- **User-Friendly**: Easy to set up and run from the command line.

## Join the Movement

Focus Guardian is more than just a productivity tool—it's a revolution in work efficiency. Embrace a smarter way to work and say **goodbye to procrastination**. Join us in the movement towards better focus and enhanced productivity!
