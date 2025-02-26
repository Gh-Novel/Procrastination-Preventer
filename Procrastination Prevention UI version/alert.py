import customtkinter as ctk
import tkinter as tk

class AlertSystem:
    @staticmethod
    def show_warning(parent, domains):
        """Display custom warning popup with domain information"""
        popup = ctk.CTkToplevel(parent)
        popup.title("⚠️ Focus Alert")
        popup.geometry("400x250")
        popup.attributes('-topmost', True)  # Ensure the alert stays on top

        try:
            popup.bell()
        except:
            pass

        warning_frame = ctk.CTkFrame(popup)
        warning_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Format the domains string
        if isinstance(domains, str):
            domain_list = [d.strip() for d in domains.split(',') if d.strip()]
            formatted_domains = ", ".join(domain_list)
        else:
            formatted_domains = ", ".join(domains)

        # Build a dynamic warning message including the user's focus goal
        warning_text = f"""The system detected potential distractions:
{formatted_domains}

These appear unrelated to your stated goal:
"{parent.user_goal}" """

        ctk.CTkLabel(warning_frame, 
                     text="Potential Distraction Detected:",
                     font=("Arial", 16, "bold"),
                     text_color="#ff4444").pack(pady=(10, 5))

        ctk.CTkLabel(warning_frame,
                     text=warning_text,
                     font=("Arial", 14),
                     text_color="#ff8888").pack(pady=5)

        ctk.CTkLabel(warning_frame,
                     text="This activity doesn't align with your focus goal.",
                     font=("Arial", 12),
                     text_color="#ff8888").pack(pady=5)

        button_frame = ctk.CTkFrame(warning_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame,
                      text="Stay Focused",
                      command=popup.destroy,
                      fg_color="#4CAF50",
                      hover_color="#45a049").pack(side=tk.LEFT, padx=5)

        ctk.CTkButton(button_frame,
                      text="Dismiss Warning",
                      command=popup.destroy,
                      fg_color="#ff4444",
                      hover_color="#cc0000").pack(side=tk.LEFT, padx=5)

        popup.grab_set()  # Make the popup modal
        popup.after(15000, popup.destroy)  # Auto-close after 15 seconds
