import asyncio
from abc import ABC, abstractmethod
from db import supabase
import datetime

class BaseAgent(ABC):
    def __init__(self, run_id: str, session_id: str, target_url: str):
        self.run_id = run_id
        self.session_id = session_id
        self.target_url = target_url
        self.log_buffer = []

    async def run(self):
        """Main execution method to be implemented by agents."""
        await self.update_status("RUNNING")
        try:
            await self.execute()
            await self.update_status("COMPLETED")
        except Exception as e:
            await self.emit_event("ERROR", f"Agent failed: {str(e)}")
            await self.update_status("FAILED")

    @abstractmethod
    async def execute(self):
        """Specific logic for the agent."""
        pass

    async def update_status(self, status: str):
        supabase.table('agent_sessions').update({
            "status": status,
            "updated_at": datetime.datetime.now().isoformat()
        }).eq("id", self.session_id).execute()

    async def update_progress(self, progress: int):
        supabase.table('agent_sessions').update({
            "progress": progress
        }).eq("id", self.session_id).execute()

    async def emit_event(self, event_type: str, message: str, data: dict = None):
        event = {
            "run_id": self.run_id,
            "agent_type": self.__class__.__name__,
            "event_type": event_type,
            "message": message,
            "data": data or {}
        }
        # Fire and forget (in a real app, maybe batch or queue)
        # Using Supabase directly here which is IO blocking but okay for prototype
        # Or wrap in run_in_executor if needed, but supabase-py might support async?
        # Actually supabase-py is sync by default unless using an async client?
        # For now we'll assume sync calls are fast enough or wrap them later.
        # Ideally we use an async wrapper or just sync calls in a thread.
        # For simplicity in this Hackathon prototype:
        try:
            supabase.table('run_events').insert(event).execute()
        except Exception as e:
            print(f"Failed to emit event: {e}")

    async def report_finding(self, severity: str, title: str, evidence: str, recommendation: str):
        finding = {
            "run_id": self.run_id,
            "agent_type": self.__class__.__name__,
            "severity": severity,
            "title": title,
            "evidence": evidence,
            "recommendation": recommendation
        }
        supabase.table('findings').insert(finding).execute()

    async def save_screenshot(self, page, title: str):
        """Captures a screenshot and saves it as an event."""
        try:
            # Get bytes for DB/Storage
            screenshot_bytes = await page.screenshot(type='png', full_page=False)
            import base64
            b64_img = base64.b64encode(screenshot_bytes).decode('utf-8')

            # Emit SCREENSHOT event with base64 data
            await self.emit_event(
                "SCREENSHOT",
                f"Screenshot: {title}",
                {"image": f"data:image/png;base64,{b64_img}"}
            )

        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            await self.emit_event("ERROR", f"Failed to capture screenshot: {str(e)}")

    async def scroll_and_capture(self, page, title_prefix: str):
        """Scrolls through the page and captures screenshots at each step."""
        await self.emit_event("INFO", f"Starting visual scroll capture: {title_prefix}")

        try:
            # Get total height
            dimensions = await page.evaluate("""() => {
                return {
                    width: document.documentElement.clientWidth,
                    height: document.documentElement.scrollHeight,
                    vh: window.innerHeight
                }
            }""")

            total_height = dimensions['height']
            viewport_height = dimensions['vh']

            current_scroll = 0
            step = int(viewport_height * 0.8) # 20% overlap

            # Limit screenshots to prevent DB bloat
            max_screenshots = 5
            count = 0

            while current_scroll < total_height and count < max_screenshots:
                await page.evaluate(f"window.scrollTo(0, {current_scroll})")
                await asyncio.sleep(0.8) # Wait for potential lazy loading/animations

                await self.save_screenshot(page, f"{title_prefix} (Scroll {count + 1})")

                current_scroll += step
                count += 1

                # Re-check height in case of lazy loading
                total_height = await page.evaluate("document.documentElement.scrollHeight")

            # Reset scroll
            await page.evaluate("window.scrollTo(0, 0)")

        except Exception as e:
            await self.emit_event("WARNING", f"Scrolling capture failed: {str(e)}")
