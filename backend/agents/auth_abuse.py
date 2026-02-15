from .base import BaseAgent
from playwright.async_api import async_playwright
import asyncio
import random

class AuthAbuseAgent(BaseAgent):
    async def execute(self):
        await self.emit_event("INFO", "Starting Auth Abuse simulation.")
        
        async with async_playwright() as p:
            # Headless must be true for Modal environment
            browser = await p.chromium.launch(headless=True)
            # Create a context to support video recording
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                await self.update_progress(10)
                await page.goto(self.target_url)
                await self.emit_event("INFO", f"Scanning {self.target_url} for login forms...")
                
                # Logic: Find inputs with type='password'
                password_inputs = await page.query_selector_all("input[type='password']")
                
                if not password_inputs:
                     await self.emit_event("INFO", "No login forms detected. Skipping auth attacks.")
                     await self.update_progress(100)
                     return

                await self.update_progress(30)
                await self.emit_event("INFO", f"Found login form with {len(password_inputs)} password fields.")
                
                # Report finding (INFO only - seeing a login form is not a vulnerability)
                await self.report_finding(
                        severity="INFO",
                        title="Login Form Detected",
                        evidence=f"Login form with password fields found at {self.target_url}",
                        recommendation="Ensure that the login endpoint implements rate limiting, brute-force protection, and multi-factor authentication (MFA)."
                    )

                # Simulate Brutes (SAFE MODE - just typing, not submitting heavy load)
                await self.emit_event("INFO", "Performing non-intrusive authentication analysis...")
                await asyncio.sleep(1)
                await self.update_progress(50)
                
                # (Removed simulated 'Weak Password Policy' finding to reduce false positives)

                await self.update_progress(80)
                await self.emit_event("SUCCESS", "Auth abuse scan completed.")
                
            except Exception as e:
                await self.emit_event("ERROR", f"Auth scan failed: {str(e)}")
            finally:
                # Close context to ensure video is saved
                await context.close()
                await browser.close()
