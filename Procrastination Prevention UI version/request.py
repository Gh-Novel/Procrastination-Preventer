import base64
import os
import pyautogui
from groq import Groq

class GroqClient:
    def __init__(self):
        self.client = None
        self.user_goal = ""
        self.initialize_client()

    def initialize_client(self):
        try:
            with open("api.txt", "r") as file:
                groq_api_key = file.read().strip()
                os.environ["GROQ_API_KEY"] = groq_api_key
            self.client = Groq()
        except Exception as e:
            raise ConnectionError(f"Groq initialization failed: {str(e)}")

    def set_user_goal(self, goal):
        """Store the user's focus goal for context-aware detection"""
        self.user_goal = goal

    def generate_vision_prompt(self):
        """Generate dynamic prompt based on user goal"""
        base_prompt = """Analyze this screenshot and identify ALL applications/websites. """
        
        if self.user_goal:
            return f"""
{base_prompt}
User's Focus Goal: "{self.user_goal}"
---
Task:
1. Identify if any detected applications/websites conflict with the goal
2. Allow exceptions explicitly mentioned in the goal (e.g., "YouTube for tutorials")
3. For allowed domains, check if content aligns with the goal (e.g., educational vs entertainment)
4. Return ONLY distracting items as a comma-separated list, or an empty string if aligned.
"""
        return base_prompt + "\nReturn ONLY non-work related items."

    def is_distraction(self, domain_list):
        """Fully LLM-based distraction detection"""
        if not domain_list.strip():
            return False

        try:
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze if these activities align with the user's goal. Consider:
1. Explicit allowances in the goal (e.g., "YouTube for learning")
2. Content context (educational vs entertainment)
3. Domain purpose vs stated goal"""
                    },
                    {
                        "role": "user",
                        "content": f"""
User Goal: {self.user_goal}
Detected Activities: {domain_list}

Should any of these trigger a warning? Respond ONLY with:
- 'DISTRACTION' followed by comma-separated items
- 'ALIGNED' if everything is acceptable"""
                    }
                ],
                temperature=0.2,
                max_tokens=100
            )

            result = response.choices[0].message.content.strip()
            return "DISTRACTION" in result.split()[0].upper()

        except Exception as e:
            print(f"LLM analysis failed: {str(e)}")
            return True  # Fail-safe: default to warning

    def get_image_description(self):
        """Capture screen and get description from vision model"""
        try:
            # Capture full screenshot
            screenshot = pyautogui.screenshot()
            
            # Crop the image to remove taskbar (1439x850 instead of 1439x899)
            width, height = screenshot.size
            cropped_screenshot = screenshot.crop((0, 0, width, 850))
            
            temp_path = "temp_screen.png"
            cropped_screenshot.save(temp_path)

            with open(temp_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")

            response = self.client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe active applications/websites in detail:"},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                        ]
                    }
                ],
                temperature=0.3,
                max_tokens=512,
            )
            os.remove(temp_path)
            return response.choices[0].message.content

        except Exception as e:
            raise RuntimeError(f"Vision analysis failed: {str(e)}")

    def get_domains_list(self):
        """Capture screen and extract domain names and application names based on user goal"""
        try:
            # Capture full screenshot
            screenshot = pyautogui.screenshot()
            
            # Crop the image to remove taskbar (1439x850 instead of 1439x899)
            width, height = screenshot.size
            cropped_screenshot = screenshot.crop((0, 0, width, 850))
            
            temp_path = "temp_screen.png"
            cropped_screenshot.save(temp_path)

            with open(temp_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")

            prompt = f"""Analyze this screenshot in the context of:
    User Goal: {self.user_goal}

    Identify:
    1. All open applications/websites
    2. Context clues (e.g., video titles, document content)
    3. Whether activities align with the goal

    Return ONLY problematic items as a comma-separated list, or empty string."""
            
            response = self.client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]}],
                temperature=0.3,
                max_tokens=300
            )

            os.remove(temp_path)
            return response.choices[0].message.content.strip()

        except Exception as e:
            raise RuntimeError(f"Vision analysis failed: {str(e)}")

    def compare_activities(self, user_goal, current_activity):
        """Compare current activity with user goal"""
        try:
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You are evaluating whether current activity matches a focus goal. Be strict about social media - they are always distractions."},
                    {"role": "user", "content": f"""
Goal: {user_goal}
Current Activity: {current_activity}
Respond ONLY with 0 (good) or 1 (distraction)
"""}
                ],
                temperature=0.1,
                max_tokens=2,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"Comparison failed: {str(e)}")
