# procrastination_preventer.py
import argparse
import time
import json
import base64
import os
import platform
import pyautogui
import threading
import datetime
from PIL import Image
from groq import Groq
try:
    from plyer import notification
except ImportError:
    notification = None

# Add imports for sound functionality
try:
    import winsound  # For Windows
except ImportError:
    winsound = None

try:
    from pydub import AudioSegment
    from pydub.playback import play
    has_pydub = True
except ImportError:
    has_pydub = False

# Add imports for GUI popup window
try:
    import tkinter as tk
    from tkinter import font as tkFont
    has_tkinter = True
except ImportError:
    has_tkinter = False

class ProcrastinationPreventer:
    def __init__(self, api_key_path="api.txt"):
        self.client = self.initialize_groq_client(api_key_path)
        self.user_goal = ""
        self.dynamic_rules = {}
        self.sfm_mode = False
        self.distraction_count = 0
        self.interval = 10
        self.running = True
        self.blocked = False
        self.sound_enabled = True  # Enable sound by default
        self.popup_enabled = True  # Enable popup by default
        
        # Session analytics data
        self.session_start_time = datetime.datetime.now()
        self.session_log = []
        self.productive_time = 0
        self.distraction_time = 0
        self.current_activity = None
        self.current_activity_start = None
        
        # Store active popup windows
        self.active_popups = []

    def initialize_groq_client(self, api_key_path):
        """Initialize Groq client with API key"""
        try:
            with open(api_key_path, "r") as f:
                api_key = f.read().strip()
            return Groq(api_key=api_key)
        except Exception as e:
            print(f"Error initializing Groq client: {str(e)}")
            exit(1)

    def play_warning_sound(self, severity="medium"):
        """Play a warning sound based on severity level"""
        if not self.sound_enabled:
            return
            
        try:
            # Windows implementation
            if winsound:
                # Different frequencies based on severity
                frequencies = {
                    "low": 440,    # A4 note
                    "medium": 880,  # A5 note
                    "high": 1760   # A6 note
                }
                duration = 500  # milliseconds
                
                frequency = frequencies.get(severity, frequencies["medium"])
                winsound.Beep(frequency, duration)
                return
                
            # Cross-platform implementation using pydub
            if has_pydub:
                # Generate different tones based on severity
                duration = 500  # milliseconds
                
                # Different frequencies based on severity
                frequencies = {
                    "low": 440,    # A4 note
                    "medium": 880,  # A5 note
                    "high": 1760   # A6 note
                }
                
                frequency = frequencies.get(severity, frequencies["medium"])
                
                # Generate a sine wave tone
                sample_rate = 44100
                sine_wave = AudioSegment.silent(duration=duration)
                
                # This is a simple way to generate a tone - in a real implementation
                # you would use numpy to generate proper sine waves
                sine_wave = sine_wave.set_frame_rate(sample_rate)
                
                # Play the sound
                play(sine_wave)
                return
                
            # Fallback for Unix-like systems using system bell
            print('\a')
            
        except Exception as e:
            print(f"Sound error: {str(e)}")

    def show_warning_popup(self, title, message, severity="medium"):
        """Display a warning popup window"""
        if not self.popup_enabled or not has_tkinter:
            return
            
        # Define colors based on severity
        colors = {
            "low": {"bg": "#FFF3CD", "fg": "#856404", "border": "#FFEEBA"},     # Yellow (warning)
            "medium": {"bg": "#F8D7DA", "fg": "#721C24", "border": "#F5C6CB"},  # Red (danger)
            "high": {"bg": "#CC0000", "fg": "#FFFFFF", "border": "#990000"}     # Bright Red (severe)
        }
        
        color_scheme = colors.get(severity, colors["medium"])
        
        # Create popup window in a separate thread to not block main app
        def create_popup():
            # Create the popup window
            popup = tk.Tk()
            popup.title("Focus Guardian Alert")
            popup.attributes("-topmost", True)  # Keep window on top
            
            # Get screen width and height
            screen_width = popup.winfo_screenwidth()
            screen_height = popup.winfo_screenheight()
            
            # Set window size and position (top right corner)
            window_width = 350
            window_height = 200
            x_position = screen_width - window_width - 20
            y_position = 40
            
            # Position the window
            popup.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
            
            # Configure the window
            popup.configure(bg=color_scheme["bg"])
            popup.overrideredirect(True)  # Remove window decorations
            
            # Add a border
            frame = tk.Frame(popup, bg=color_scheme["border"], padx=3, pady=3)
            frame.pack(fill="both", expand=True)
            
            inner_frame = tk.Frame(frame, bg=color_scheme["bg"], padx=10, pady=10)
            inner_frame.pack(fill="both", expand=True)
            
            # Add title
            title_font = tkFont.Font(family="Arial", size=14, weight="bold")
            title_label = tk.Label(inner_frame, text=title, font=title_font, 
                                 bg=color_scheme["bg"], fg=color_scheme["fg"])
            title_label.pack(pady=(10, 5))
            
            # Add message
            message_font = tkFont.Font(family="Arial", size=12)
            message_label = tk.Label(inner_frame, text=message, font=message_font, 
                                   bg=color_scheme["bg"], fg=color_scheme["fg"],
                                   wraplength=320, justify="center")
            message_label.pack(pady=10)
            
            # Add dismiss button
            button_font = tkFont.Font(family="Arial", size=10, weight="bold")
            dismiss_button = tk.Button(inner_frame, text="I'll Focus Now", font=button_font,
                                     command=popup.destroy, bg="#007BFF", fg="white",
                                     activebackground="#0069D9", activeforeground="white",
                                     padx=15, pady=5, border=0)
            dismiss_button.pack(pady=10)
            
            # Store reference to popup
            self.active_popups.append(popup)
            
            # Auto-close after 10 seconds
            popup.after(10000, lambda: self.close_popup(popup))
            
            # Start popup
            popup.mainloop()
            
        # Create and start popup thread
        popup_thread = threading.Thread(target=create_popup)
        popup_thread.daemon = True
        popup_thread.start()
        
    def close_popup(self, popup):
        """Safely close a popup window"""
        if popup in self.active_popups:
            try:
                popup.destroy()
                self.active_popups.remove(popup)
            except Exception:
                pass

    def close_all_popups(self):
        """Close all active popup windows"""
        for popup in self.active_popups[:]:  # Create a copy of the list to iterate over
            self.close_popup(popup)

    def show_progress_bar(self, seconds):
        """Display animated progress bar"""
        for i in range(seconds):
            if not self.running:
                break
            progress = (i + 1) / seconds
            bar_length = 40
            filled = int(round(bar_length * progress))
            bar = '█' * filled + '-' * (bar_length - filled)
            print(f'\r\033[94mScanning: [{bar}] {int(progress*100)}%\033[0m', end='', flush=True)
            time.sleep(1)
        print('\r' + ' ' * 60 + '\r', end='')

    def parse_user_goal(self, goal_text):
        """Dynamically generate rules from user goal using LLM"""
        self.user_goal = goal_text
        try:
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{
                    "role": "user",
                    "content": f"""Analyze this productivity goal and create enforcement rules:
                    Goal: "{goal_text}"
                    
                    Return JSON with:
                    - allowed_resources: list of allowed apps/websites
                    - allowed_purposes: specific usage purposes
                    - content_rules: content validation criteria
                    - strictness: level of enforcement (1-5)
                    
                    Example response for "Study ML on YouTube":
                    {{
                        "allowed_resources": ["youtube.com"],
                        "allowed_purposes": {{
                            "youtube.com": "machine learning tutorials"
                        }},
                        "content_rules": {{
                            "youtube.com": "Video titles must contain ML/AI keywords"
                        }},
                        "strictness": 4
                    }}"""
                }],
                temperature=0.2,
                max_tokens=400,
                response_format={"type": "json_object"}
            )
            self.dynamic_rules = json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Goal parsing error: {str(e)}")
            exit(1)

    def capture_and_analyze(self):
        """Capture screen and analyze activities with improved vision prompt"""
        temp_path = "temp_screen.png"
        try:
            # Capture and crop screenshot
            screenshot = pyautogui.screenshot()
            width, height = screenshot.size
            crop_height = int(height * 0.95)
            screenshot = screenshot.crop((0, 0, width, crop_height))
            screenshot.save(temp_path)

            with open(temp_path, "rb") as f:
                base64_image = base64.b64encode(f.read()).decode("utf-8")

            vision_prompt = """Analyze ONLY the active window and Identify primary application
            
            Return JSON with confidence scores (1-100):
            {
                "activities": [
                    {
                        "name": "exact-app-or-domain",
                        "type": "work|education|entertainment|other",
                        "content": "visible text/title",
                        "confidence": 75
                    }
                ]
            }"""

            response = self.client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": vision_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response.choices[0].message.content)
            # Filter low-confidence detections
            return {
                "activities": [
                    a for a in data.get("activities", [])
                    if a.get("confidence", 0) > 65
                ]
            }
        except Exception as e:
            return {"activities": []}
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def validate_activity(self, activity):
        """Context-aware validation using LLM"""
        try:
            prompt = f"""Verify if this activity aligns with the user's goal:
            User Goal: "{self.user_goal}"
            Activity: {json.dumps(activity)}
            Rules: {json.dumps(self.dynamic_rules)}
            
            Consider:
            1. Resource allowlist
            2. Purpose matching
            3. Content relevance
            4. Current context
            
            Return JSON response:
            {{
                "allowed": boolean,
                "reason": "explanation",
                "suggestion": "productivity tip",
                "severity": "low|medium|high"
            }}"""

            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"allowed": True, "reason": "Validation failed"}

    def update_session_analytics(self, activity, validation_result):
        """Update session analytics with current activity"""
        now = datetime.datetime.now()
        
        # If there's an ongoing activity, log it
        if self.current_activity and self.current_activity_start:
            duration = (now - self.current_activity_start).total_seconds()
            
            log_entry = {
                "activity": self.current_activity,
                "start_time": self.current_activity_start.strftime("%H:%M:%S"),
                "end_time": now.strftime("%H:%M:%S"),
                "duration_seconds": duration,
                "productive": self.current_activity.get("is_productive", False)
            }
            
            self.session_log.append(log_entry)
            
            # Update productivity counters
            if log_entry["productive"]:
                self.productive_time += duration
            else:
                self.distraction_time += duration
        
        # Set the new current activity
        if activity:
            activity_copy = activity.copy()
            activity_copy["is_productive"] = validation_result.get("allowed", True)
            self.current_activity = activity_copy
            self.current_activity_start = now

    def handle_validation_result(self, result, activity):
        """Handle validation results with dynamic responses"""
        # Update session analytics
        self.update_session_analytics(activity, result)
        
        if not result.get("allowed", True):
            # Build warning message
            warning_msg = f"\033[91m⚠️ {result.get('reason', 'Unproductive activity detected')}\033[0m"
            if "suggestion" in result:
                warning_msg += f"\n\033[93m💡 {result['suggestion']}\033[0m"
            
            # Get severity level for sound and popup
            severity = result.get("severity", "medium")
            
            # Play warning sound
            self.play_warning_sound(severity)
            
            # Show popup window with warning
            title = "⚠️ Focus Alert"
            if severity == "high":
                title = "🚨 URGENT FOCUS ALERT"
            elif severity == "low":
                title = "⚠️ Mild Focus Alert"
                
            popup_message = f"{result.get('reason', 'Potential distraction detected')}"
            if "suggestion" in result:
                popup_message += f"\n\n💡 {result['suggestion']}"
                
            self.show_warning_popup(title, popup_message, severity)
            
            # Show system notification as a backup
            if notification:
                try:
                    notification.notify(
                        title="Focus Alert",
                        message=result.get("reason", "Potential distraction detected"),
                        timeout=10
                    )
                except Exception as e:
                    pass
            
            print(warning_msg)
            
            # Handle SFM mode
            if self.sfm_mode:
                self.distraction_count += 1
                print(f"SFM Warnings: {self.distraction_count}/3")
                if self.distraction_count >= 3:
                    self.block_distraction(result.get("reason", "Repeated distractions"))

    def block_distraction(self, reason):
        """Take action against distractions"""
        try:
            # Cross-platform process termination
            if platform.system() == "Windows":
                os.system("taskkill /f /im chrome.exe")
            else:
                os.system("pkill -f chrome")
            print(f"\n\033[91m🚫 Blocked browser due to: {reason}\033[0m")
            # Play a more severe sound when blocking
            self.play_warning_sound("high")
            
            # Show critical popup when blocking
            self.show_warning_popup("🚫 DISTRACTION BLOCKED", 
                                  f"Browser has been closed.\n\n{reason}\n\nTime to refocus on your goal.", 
                                  "high")
            
            self.blocked = True
        except Exception as e:
            print(f"Blocking error: {str(e)}")

    def generate_session_analysis(self):
        """Generate an analysis of the focus session"""
        # Finalize the current activity if there is one
        if self.current_activity and self.current_activity_start:
            now = datetime.datetime.now()
            duration = (now - self.current_activity_start).total_seconds()
            
            log_entry = {
                "activity": self.current_activity,
                "start_time": self.current_activity_start.strftime("%H:%M:%S"),
                "end_time": now.strftime("%H:%M:%S"),
                "duration_seconds": duration,
                "productive": self.current_activity.get("is_productive", False)
            }
            
            self.session_log.append(log_entry)
            
            # Update productivity counters
            if log_entry["productive"]:
                self.productive_time += duration
            else:
                self.distraction_time += duration
        
        # Calculate session statistics
        session_duration = (datetime.datetime.now() - self.session_start_time).total_seconds()
        productive_percentage = (self.productive_time / session_duration * 100) if session_duration > 0 else 0
        
        # Get most common activities
        activity_counts = {}
        for entry in self.session_log:
            activity_name = entry["activity"].get("name", "Unknown")
            if activity_name in activity_counts:
                activity_counts[activity_name] += entry["duration_seconds"]
            else:
                activity_counts[activity_name] = entry["duration_seconds"]
        
        # Sort activities by time spent
        sorted_activities = sorted(activity_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Generate activity distribution
        top_activities = []
        for activity, duration in sorted_activities[:5]:  # Top 5 activities
            percentage = (duration / session_duration * 100) if session_duration > 0 else 0
            top_activities.append({
                "name": activity,
                "duration_minutes": round(duration / 60, 1),
                "percentage": round(percentage, 1)
            })
        
        # Count distractions
        distraction_entries = [entry for entry in self.session_log if not entry["productive"]]
        
        # Format results
        analysis = {
            "session_summary": {
                "goal": self.user_goal,
                "start_time": self.session_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "duration_minutes": round(session_duration / 60, 1),
                "productivity_rate": round(productive_percentage, 1),
                "distraction_count": len(distraction_entries),
                "blocks_triggered": 1 if self.blocked else 0
            },
            "time_distribution": {
                "productive_minutes": round(self.productive_time / 60, 1),
                "distracted_minutes": round(self.distraction_time / 60, 1),
                "productivity_percentage": round(productive_percentage, 1)
            },
            "top_activities": top_activities,
            "distraction_patterns": {}
        }
        
        # If we have enough data, let's analyze patterns
        if len(distraction_entries) > 2:
            # Simplified pattern detection using time-of-day
            morning_distractions = 0
            afternoon_distractions = 0
            evening_distractions = 0
            
            for entry in distraction_entries:
                hour = int(entry["start_time"].split(":")[0])
                if 5 <= hour < 12:
                    morning_distractions += 1
                elif 12 <= hour < 18:
                    afternoon_distractions += 1
                else:
                    evening_distractions += 1
            
            analysis["distraction_patterns"] = {
                "morning_count": morning_distractions,
                "afternoon_count": afternoon_distractions,
                "evening_count": evening_distractions,
                "peak_time": "Morning" if morning_distractions > afternoon_distractions and morning_distractions > evening_distractions else
                            "Afternoon" if afternoon_distractions > morning_distractions and afternoon_distractions > evening_distractions else
                            "Evening"
            }
        
        return analysis

    def print_session_analysis(self):
        """Print a formatted analysis of the focus session"""
        analysis = self.generate_session_analysis()
        
        # Save analysis to JSON file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"focus_session_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(analysis, f, indent=2)
        
        # Print formatted analysis
        print("\n" + "="*60)
        print("\033[1m\033[95m📊 FOCUS SESSION ANALYSIS 📊\033[0m")
        print("="*60)
        
        # Session summary
        summary = analysis["session_summary"]
        print(f"\033[1m\033[96m🎯 Goal:\033[0m {summary['goal']}")
        print(f"\033[1m\033[96m⏱️ Duration:\033[0m {summary['duration_minutes']} minutes")
        print(f"\033[1m\033[96m📈 Productivity Rate:\033[0m {summary['productivity_rate']}%")
        
        # Time distribution
        dist = analysis["time_distribution"]
        print("\n\033[1m\033[96m⏰ TIME DISTRIBUTION\033[0m")
        print(f"  Productive Time: {dist['productive_minutes']} minutes ({dist['productivity_percentage']}%)")
        print(f"  Distracted Time: {dist['distracted_minutes']} minutes ({100-dist['productivity_percentage']}%)")
        
        # Top activities
        print("\n\033[1m\033[96m🔍 TOP ACTIVITIES\033[0m")
        for idx, activity in enumerate(analysis["top_activities"], 1):
            print(f"  {idx}. {activity['name']}: {activity['duration_minutes']} min ({activity['percentage']}%)")
        
        # Distraction summary
        print(f"\n\033[1m\033[96m⚠️ DISTRACTIONS\033[0m")
        print(f"  Total Count: {summary['distraction_count']}")
        
        if "peak_time" in analysis["distraction_patterns"]:
            print(f"  Peak Distraction Time: {analysis['distraction_patterns']['peak_time']}")
        
        print(f"  Blocks Triggered: {summary['blocks_triggered']}")
        
        # Final output
        print("\n" + "="*60)
        print(f"\033[1m\033[92m💾 Full analysis saved to: {filename}\033[0m")
        print("="*60 + "\n")

    def monitor(self, interval):
        """Main monitoring loop"""
        print(f"\n\033[92mStarting Focus Guardian\033[0m")
        print(f"User Goal: {self.user_goal}")
        print(f"SFM Mode: {'ENABLED (3-strike rule)' if self.sfm_mode else 'DISABLED'}")
        print(f"Sound Alerts: {'ENABLED' if self.sound_enabled else 'DISABLED'}")
        print(f"Popup Alerts: {'ENABLED' if self.popup_enabled else 'DISABLED'}")
        
        try:
            while self.running:
                progress_thread = threading.Thread(target=self.show_progress_bar, args=(interval,))
                progress_thread.start()
                
                # Capture and analyze screen
                activities = self.capture_and_analyze().get("activities", [])
                
                # Validate each activity
                for activity in activities:
                    validation = self.validate_activity(activity)
                    self.handle_validation_result(validation, activity)
                
                progress_thread.join()
                
        except KeyboardInterrupt:
            self.running = False
            print("\n\033[93mMonitoring stopped\033[0m")
            # Close all popup windows on exit
            self.close_all_popups()
            # Show session analysis on exit
            self.print_session_analysis()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI-Powered Focus Guardian")
    parser.add_argument("goal", type=str, help="Your work goal in natural language", nargs='?')
    parser.add_argument("--sfm", action="store_true", 
                       help="Enable Super Focus Mode (3 warnings then block)")
    parser.add_argument("--interval", type=int, default=10,
                       help="Monitoring interval in seconds (default: 10)")
    parser.add_argument("--no-sound", action="store_true",
                       help="Disable warning sounds")
    parser.add_argument("--no-popup", action="store_true",
                       help="Disable popup warnings")
    parser.add_argument("--analyze", type=str,
                       help="Analyze a previous session JSON file")
    args = parser.parse_args()
    
    # Check if we're just analyzing a previous session
    if args.analyze:
        try:
            with open(args.analyze, "r") as f:
                analysis_data = json.load(f)
            
            # Print analysis header
            print("\n" + "="*60)
            print("\033[1m\033[95m📊 FOCUS SESSION ANALYSIS 📊\033[0m")
            print("="*60)
            
            # Session summary
            summary = analysis_data["session_summary"]
            print(f"\033[1m\033[96m🎯 Goal:\033[0m {summary['goal']}")
            print(f"\033[1m\033[96m⏱️ Duration:\033[0m {summary['duration_minutes']} minutes")
            print(f"\033[1m\033[96m📈 Productivity Rate:\033[0m {summary['productivity_rate']}%")
            
            # Time distribution
            dist = analysis_data["time_distribution"]
            print("\n\033[1m\033[96m⏰ TIME DISTRIBUTION\033[0m")
            print(f"  Productive Time: {dist['productive_minutes']} minutes ({dist['productivity_percentage']}%)")
            print(f"  Distracted Time: {dist['distracted_minutes']} minutes ({100-dist['productivity_percentage']}%)")
            
            # Top activities
            print("\n\033[1m\033[96m🔍 TOP ACTIVITIES\033[0m")
            for idx, activity in enumerate(analysis_data["top_activities"], 1):
                print(f"  {idx}. {activity['name']}: {activity['duration_minutes']} min ({activity['percentage']}%)")
            
            # Distraction summary
            print(f"\n\033[1m\033[96m⚠️ DISTRACTIONS\033[0m")
            print(f"  Total Count: {summary['distraction_count']}")
            
            if "peak_time" in analysis_data["distraction_patterns"]:
                print(f"  Peak Distraction Time: {analysis_data['distraction_patterns']['peak_time']}")
            
            print(f"  Blocks Triggered: {summary['blocks_triggered']}")
            
            print("\n" + "="*60 + "\n")
            exit(0)
        except Exception as e:
            print(f"Error analyzing session file: {str(e)}")
            exit(1)
    
    # Check if we have a goal
    if not args.goal:
        print("Error: Please provide a work goal or use --analyze to review a previous session")
        print("Example: python procrastination_preventer.py 'Work on my thesis for 2 hours'")
        exit(1)

    guardian = ProcrastinationPreventer()
    guardian.parse_user_goal(args.goal)
    guardian.sfm_mode = args.sfm
    guardian.sound_enabled = not args.no_sound
    guardian.popup_enabled = not args.no_popup
    guardian.monitor(args.interval)