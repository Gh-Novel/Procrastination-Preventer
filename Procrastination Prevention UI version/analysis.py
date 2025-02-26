import customtkinter as ctk
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

class AnalysisWindow(ctk.CTkToplevel):
    def __init__(self, parent, session_data, achievements, longest_streak):
        super().__init__(parent)
        self.title("Session Analysis")
        self.geometry("1000x600")
        self.session_data = session_data
        self.achievements = achievements
        self.longest_streak = longest_streak

        self.create_widgets()
        self.update_achievements_display()

    def create_widgets(self):
        """Create analysis window components"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Session List
        session_frame = ctk.CTkFrame(main_frame, width=300)
        session_frame.pack(side="left", fill="y", padx=5, pady=5)

        ctk.CTkLabel(session_frame, text="Session History", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.session_listbox = tk.Listbox(session_frame, width=40, height=20)
        self.session_listbox.pack(padx=10, pady=10, fill="both", expand=True)
        
        for idx, session in enumerate(self.session_data):
            start_time = session["start"][11:19]
            duration = f"{session['total_time']//3600:.0f}h {(session['total_time']%3600)//60:.0f}m"
            self.session_listbox.insert(tk.END, f"Session {idx+1} | {start_time} | {duration}")

        # Graph Frame
        graph_frame = ctk.CTkFrame(main_frame)
        graph_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Achievements Frame
        achievements_frame = ctk.CTkFrame(main_frame, width=200)
        achievements_frame.pack(side="left", fill="y", padx=5, pady=5)

        ctk.CTkLabel(achievements_frame, text="Achievements", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.achievements_text = ctk.CTkTextbox(achievements_frame, width=180, height=400)
        self.achievements_text.pack(padx=10, pady=10)

        # Bind selection event
        self.session_listbox.bind("<<ListboxSelect>>", self.plot_session_data)

    def plot_session_data(self, event):
        selection = self.session_listbox.curselection()
        if not selection:
            return
            
        session_idx = selection[0]
        session = self.session_data[session_idx]
        
        self.ax.clear()
        
        # Plot timeline with distraction points
        start_time = datetime.strptime(session["start"], "%Y-%m-%d %H:%M:%S")
        times = [start_time]
        distractions = [0]
        
        for d in session["distractions"]:
            dt = datetime.strptime(d["time"], "%Y-%m-%d %H:%M:%S")
            times.append(dt)
            distractions.append(1)
            times.append(dt)
            distractions.append(0)
        
        times.append(datetime.strptime(session["end"], "%Y-%m-%d %H:%M:%S"))
        distractions.append(0)
        
        self.ax.step(times, distractions, where="post")
        self.ax.set_title(f"Session {session_idx+1} Focus Timeline")
        self.ax.set_yticks([0, 1])
        self.ax.set_yticklabels(["Focused", "Distracted"])
        self.ax.set_xlabel("Time")
        self.figure.autofmt_xdate()
        self.canvas.draw()

    def update_achievements_display(self):
        self.achievements_text.delete("1.0", "end")
        self.achievements_text.insert("end", "🏆 Earned Achievements:\n\n")
        
        if self.achievements['no_distraction_1h']:
            self.achievements_text.insert("end", "✅ 1 Hour Focused (No Distractions)\n")
        if self.achievements['coding_marathon']:
            self.achievements_text.insert("end", "✅ 5 Hour Coding Marathon\n")
        if self.achievements['perfect_session']:
            self.achievements_text.insert("end", "✅ Perfect Session (No Distractions)\n")
        if self.achievements['streak_master']:
            self.achievements_text.insert("end", f"✅ Focus Streak Master ({self.longest_streak//3600}hr+)\n")