from .base import BaseAgent
from playwright.async_api import async_playwright
import asyncio

class ExposureAgent(BaseAgent):
    async def execute(self):
        await self.emit_event("INFO", f"Starting Exposure Scan on {self.target_url}")
        
        async with async_playwright() as p:
            # Headless MUST be true for Modal/Linux without Xvfb
            browser = await p.chromium.launch(headless=True)
            # Enable video recording
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                await self.update_progress(10)
                await page.goto(self.target_url, timeout=30000)
                await self.emit_event("INFO", f"Navigated to {self.target_url}")
                await self.update_progress(30)
                
                title = await page.title()
                await self.emit_event("INFO", f"Page Title: {title}")
                
                # Visual Scan
                await self.scroll_and_capture(page, "Exposure Scan")
                
                await self.update_progress(50)
                
                # Check 2: Unsecured Forms / CSRF
                forms = await page.query_selector_all("form")
                if forms:
                    await self.emit_event("INFO", f"Found {len(forms)} forms. Analyzing for CSRF protection...")
                    for form in forms:
                        # Simple heuristic: look for common CSRF token names in hidden inputs
                        # We use a case-insensitive match for 'csrf' or 'token' in the name
                        has_csrf = await form.evaluate("""form => {
                            const inputs = Array.from(form.querySelectorAll("input[type='hidden']"));
                            return inputs.some(i => i.name.toLowerCase().includes('csrf') || i.name.toLowerCase().includes('token'));
                        }""")

                        if not has_csrf:
                            await self.report_finding(
                                severity="LOW",
                                title="Potential Missing CSRF Protection",
                                evidence=f"Form at {self.target_url} appears to lack a hidden CSRF token field.",
                                recommendation="Ensure all state-changing forms implement Anti-CSRF tokens. If using header-based protection (e.g., in SPAs), ensure it is correctly enforced on the backend."
                            )
                            break # Only report once per page to minimize noise
                
                await self.update_progress(90)
                await self.emit_event("SUCCESS", "Scan completed successfully.")
                
            except Exception as e:
                await self.emit_event("ERROR", f"Playwright error: {str(e)}")
                raise e
            finally:
                # Close context to save video
                await context.close()
                await browser.close()
