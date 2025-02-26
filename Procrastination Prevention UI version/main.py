import customtkinter as ctk
import threading
import time
import os
import json
from datetime import datetime
from tkinter import messagebox
from request import GroqClient
from alert import AlertSystem
from analysis import AnalysisWindow

class FocusApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Focus - Procrastination Preventer")
        self.geometry("600x400")
        self.configure_app()
        self.create_widgets()
        self.groq_client = GroqClient()
        self.session_data = []
        self.load_sessions()
        self.current_session = None
        self.start_time = None
        self.total_focused_time = 0
        self.current_streak = 0
        self.longest_streak = 0
        self.achievements = {
            'no_distraction_1h': False,
            'coding_marathon': False,
            'perfect_session': False,
            'streak_master': False
        }

    def configure_app(self):
        """Initialize app configuration"""
        self.distraction_count = 0
        self.is_tracking = False
        self.user_goal = ""
        self.distraction_threshold = 3
        self.focus_mode_enabled = False
        self.last_check_time = 0
        self.check_interval = 5
        ctk.set_appearance_mode("dark")

    def create_widgets(self):
        """Create all GUI components"""
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.goal_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="Enter your focus goal (e.g.: 'I need to code in VS Code and research in Chrome')",
            width=400
        )
        self.goal_entry.pack(pady=10)

        examples_label = ctk.CTkLabel(
            self.main_frame,
            text="Example: 'I'm coding in VS Code and researching documentation'",
            font=("Arial", 10),
            text_color="#888888"
        )
        examples_label.pack(pady=(0, 10))

        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(pady=10)

        self.start_button = ctk.CTkButton(
            button_frame,
            text="Start Focus Session",
            command=self.start_tracking
        )
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ctk.CTkButton(
            button_frame,
            text="Stop Focus Session",
            command=self.stop_tracking,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)

        self.analysis_button = ctk.CTkButton(
            button_frame,
            text="View Analysis",
            command=self.show_analysis
        )
        self.analysis_button.pack(side="left", padx=5)

        settings_frame = ctk.CTkFrame(self.main_frame)
        settings_frame.pack(pady=10)

        interval_label = ctk.CTkLabel(settings_frame, text="Check Interval (seconds):")
        interval_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.interval_slider = ctk.CTkSlider(
            settings_frame, 
            from_=5, 
            to=60,
            number_of_steps=11,
            command=self.update_interval
        )
        self.interval_slider.set(self.check_interval)
        self.interval_slider.grid(row=0, column=1, padx=10, pady=5)
        
        self.interval_value = ctk.CTkLabel(settings_frame, text=f"{self.check_interval}s")
        self.interval_value.grid(row=0, column=2, padx=10, pady=5)

        toggle_frame = ctk.CTkFrame(self.main_frame)
        toggle_frame.pack(pady=10)

        self.dark_mode = ctk.BooleanVar(value=True)
        self.dark_mode_switch = ctk.CTkSwitch(
            toggle_frame,
            text="Dark Mode",
            variable=self.dark_mode,
            command=self.toggle_dark_mode
        )
        self.dark_mode_switch.pack(side="left", padx=10)

        self.focus_mode = ctk.BooleanVar()
        self.focus_mode_switch = ctk.CTkSwitch(
            toggle_frame,
            text="Focus Mode (Auto-block)",
            variable=self.focus_mode,
            command=self.toggle_focus_mode
        )
        self.focus_mode_switch.pack(side="left", padx=10)

        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Status: Idle",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=10)

        self.log_text = ctk.CTkTextbox(self.main_frame, width=550, height=150)
        self.log_text.pack(pady=10)
        self.log_text.insert("end", "Activity Log:\n")

    def show_analysis(self):
        """Show analysis window"""
        self.update_achievements()
        AnalysisWindow(self, self.session_data, self.achievements, self.longest_streak)

    def update_interval(self, value):
        self.check_interval = int(value)
        self.interval_value.configure(text=f"{self.check_interval}s")
        self.log(f"Check interval updated to {self.check_interval} seconds")

    def log(self, message):
        self.log_text.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see("end")

    def toggle_dark_mode(self):
        current_mode = ctk.get_appearance_mode()
        new_mode = "light" if current_mode == "Dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        self.log(f"Switched to {new_mode} mode")

    def toggle_focus_mode(self):
        self.focus_mode_enabled = self.focus_mode.get()
        status = "ON" if self.focus_mode_enabled else "OFF"
        self.log(f"Super Focus Mode {status} - Auto-block after {self.distraction_threshold} warnings")

    def start_tracking(self):
        if not self.goal_entry.get().strip():
            messagebox.showerror("Error", "Please enter your focus goal!")
            return

        self.user_goal = self.goal_entry.get()
        self.groq_client.set_user_goal(self.user_goal)
        self.is_tracking = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_label.configure(text="Status: Actively monitoring")

        # Initialize session data
        self.current_session = {
            "start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end": None,
            "goal": self.user_goal,
            "distractions": [],
            "total_time": 0
        }
        self.start_time = datetime.now()
        self.current_streak = 0
        
        tracking_thread = threading.Thread(target=self.monitor_activity, daemon=True)
        tracking_thread.start()
        self.log(f"Focus tracking started with goal: {self.user_goal}")

    def stop_tracking(self):
        if self.is_tracking and self.current_session:
            self.is_tracking = False
            end_time = datetime.now()
            self.current_session["end"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Calculate total session time in seconds
            session_duration = (end_time - self.start_time).total_seconds()
            self.current_session["total_time"] = session_duration
            self.total_focused_time += session_duration
            
            # Update longest streak
            self.longest_streak = max(self.longest_streak, self.current_streak)
            
            # Add to session history
            self.session_data.append(self.current_session)
            self.save_sessions()
            
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.status_label.configure(text="Status: Stopped")
            self.log(f"Focus tracking stopped. Session duration: {session_duration/60:.1f} minutes")
        else:
            self.is_tracking = False
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.status_label.configure(text="Status: Stopped")
            self.log("Focus tracking stopped")

    def monitor_activity(self):
        last_distraction_time = None
        
        while self.is_tracking:
            current_time = time.time()
            if current_time - self.last_check_time >= self.check_interval:
                self.last_check_time = current_time
                try:
                    self.log("Checking current applications against focus goal...")
                    domains = self.groq_client.get_domains_list()

                    if domains and domains.strip():
                        self.log(f"Detected potential distractions: {domains}")
                        if self.groq_client.is_distraction(domains):
                            self.after(0, self.handle_distraction, domains)
                            
                            # Reset streak on distraction
                            current_time = datetime.now()
                            if last_distraction_time is not None:
                                streak_duration = (current_time - last_distraction_time).total_seconds()
                                self.current_streak = max(self.current_streak, streak_duration)
                            last_distraction_time = current_time
                        else:
                            self.log("Aligned with focus goal - productive activity detected")
                    else:
                        self.log("On track - productive activity detected")

                except Exception as e:
                    self.log(f"Error: {str(e)}")

            time.sleep(1)

    def handle_distraction(self, domains):
        try:
            if domains.strip():
                # Record the distraction in the current session
                if self.current_session:
                    distraction_data = {
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "domains": domains
                    }
                    self.current_session["distractions"].append(distraction_data)
                
                if self.focus_mode_enabled:
                    self.distraction_count += 1
                    alert_text = f"[Super Focus] Warning {self.distraction_count}/{self.distraction_threshold}"
                    self.log(f"{alert_text}: {domains}")
                    AlertSystem.show_warning(self, domains)
                    if self.distraction_count >= self.distraction_threshold:
                        self.close_distraction(domains)
                        self.distraction_count = 0
                else:
                    self.log(f"[Normal Mode] Distraction detected: {domains}")
                    AlertSystem.show_warning(self, domains)
        except Exception as e:
            self.log(f"Error in handle_distraction: {str(e)}")

    def close_distraction(self, domains):
        try:
            domain_list = [d.strip() for d in domains.split(',') if d.strip()]
            self.log(f"Closing distracting websites: {', '.join(domain_list)}")

            if os.name == 'nt':  # Windows
                for domain in domain_list:
                    if 'youtube' in domain.lower() or 'instagram' in domain.lower():
                        os.system("taskkill /f /im chrome.exe")
                        self.log("Closed Chrome browser")
                        break
                    elif 'facebook' in domain.lower() or 'twitter' in domain.lower() or 'instagram' in domain.lower():
                        os.system("taskkill /f /im msedge.exe")
                        self.log("Closed Edge browser")
                        break
            else:  # macOS/Linux
                for domain in domain_list:
                    if any(site in domain.lower() for site in ['youtube', 'facebook', 'twitter', 'instagram']):
                        os.system("pkill -f firefox")
                        os.system("pkill -f chrome")
                        os.system("pkill -f safari")
                        self.log("Closed browser processes")
                        break

            import pyautogui
            pyautogui.hotkey('alt', 'f4')
            self.log("Closed active window")

        except Exception as e:
            self.log(f"Error closing window: {str(e)}")

    def save_sessions(self):
        try:
            with open("sessions.json", "w") as f:
                json.dump(self.session_data, f, indent=2)
        except Exception as e:
            self.log(f"Error saving sessions: {str(e)}")

    def load_sessions(self):
        try:
            if os.path.exists("sessions.json"):
                with open("sessions.json", "r") as f:
                    self.session_data = json.load(f)
        except Exception as e:
            self.log(f"Error loading sessions: {str(e)}")

    def update_achievements(self):
        total_focused = sum(session["total_time"] for session in self.session_data)
        total_distractions = sum(len(session["distractions"]) for session in self.session_data)
        
        self.achievements['no_distraction_1h'] = any(
            session["total_time"] >= 3600 and len(session["distractions"]) == 0 
            for session in self.session_data
        )
        
        self.achievements['coding_marathon'] = total_focused >= 5*3600
        self.achievements['perfect_session'] = any(
            len(session["distractions"]) == 0 and session["total_time"] >= 1800  # At least 30 minutes
            for session in self.session_data
        )
        self.achievements['streak_master'] = self.longest_streak >= 3600

if __name__ == "__main__":
    app = FocusApp()
    app.mainloop()