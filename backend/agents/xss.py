from .base import BaseAgent
from playwright.async_api import async_playwright
import random
import string
import asyncio
import urllib.parse

class XSSAgent(BaseAgent):
    async def execute(self):
        await self.emit_event("INFO", f"Starting Playwright XSS Auditor on {self.target_url}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Sentinel/1.0"
            )
            page = await context.new_page()

            # Detection state
            self.vulnerable = False
            self.detected_payload = ""

            async def handle_dialog(dialog):
                if "Sent" in dialog.message:
                    self.vulnerable = True
                    self.detected_payload = dialog.message
                    await self.emit_event("SUCCESS", f"XSS CONFIRMED: Alert dialog triggered with message: {dialog.message}")
                await dialog.dismiss()

            page.on("dialog", lambda d: asyncio.create_task(handle_dialog(d)))

            try:
                # 1. Test URL Parameters
                parsed = urllib.parse.urlparse(self.target_url)
                params = urllib.parse.parse_qs(parsed.query)
                
                if params:
                    await self.emit_event("INFO", f"Testing {len(params)} URL parameters for Reflected XSS...")
                    for param in params.keys():
                        canary = "Sent" + ''.join(random.choices(string.ascii_letters, k=6))
                        payload = f"<script>alert('{canary}')</script>"

                        fuzzed_params = params.copy()
                        fuzzed_params[param] = [payload]
                        new_query = urllib.parse.urlencode(fuzzed_params, doseq=True)
                        fuzzed_url = parsed._replace(query=new_query).geturl()
                        
                        await page.goto(fuzzed_url)
                        await asyncio.sleep(1) # Wait for execution

                        if self.vulnerable:
                            await self.save_screenshot(page, f"XSS Found in Param: {param}")
                            await self.report_finding(
                                severity="HIGH",
                                title="Reflected XSS in URL Parameter",
                                evidence=f"Vulnerability found in `{param}` parameter.\nURL: {fuzzed_url}\nPayload: {payload}",
                                recommendation="Sanitize all user inputs, use innerText instead of innerHTML, and implement a strong CSP."
                            )
                            self.vulnerable = False # Reset

                # 2. Test Form Inputs
                await page.goto(self.target_url)
                await self.update_progress(50)

                inputs = await page.query_selector_all("input[type='text'], input:not([type]), textarea")
                if inputs:
                    await self.emit_event("INFO", f"Found {len(inputs)} input fields. Testing for XSS...")
                    for i, input_el in enumerate(inputs):
                        canary = "Sent" + ''.join(random.choices(string.ascii_letters, k=6))
                        payload = f"<script>alert('{canary}')</script>"

                        # Try to fill and submit
                        try:
                            await input_el.fill(payload)
                            await input_el.press("Enter")
                            await asyncio.sleep(1.5)

                            if self.vulnerable:
                                await self.save_screenshot(page, f"XSS Found in Form Input {i}")
                                await self.report_finding(
                                    severity="HIGH",
                                    title="Stored or Reflected XSS in Form",
                                    evidence=f"Vulnerability found in form input field #{i}.\nPayload: {payload}",
                                    recommendation="Apply context-aware output encoding and use modern web frameworks that auto-escape data."
                                )
                                self.vulnerable = False
                        except:
                            continue

                await self.update_progress(100)
                await self.emit_event("SUCCESS", "XSS Scan completed.")

            except Exception as e:
                await self.emit_event("ERROR", f"XSS Agent failed: {str(e)}")
            finally:
                await browser.close()
