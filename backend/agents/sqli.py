from .base import BaseAgent
from playwright.async_api import async_playwright
import urllib.parse
import asyncio

class SQLiAgent(BaseAgent):
    SQL_ERRORS = [
        "sql syntax", "mysql_fetch", "ora-", "sqlite3.operationalerror",
        "postgresql query failed", "microsoft ole db provider for sql server",
        "unclosed quotation mark", "jdbc driver", "system.data.sqlclient.sqlexception",
        "dynamic sql error", "valid postgresql result", "pg_query", "db2 sql error"
    ]

    async def execute(self):
        await self.emit_event("INFO", f"Starting Playwright SQLi Hunter on {self.target_url}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Sentinel/1.0"
            )
            page = await context.new_page()

            # Payloads that often trigger errors
            payloads = ["'", "\"", "1' OR '1'='1", "1\" OR \"1\"=\"1", "') OR ('1'='1"]

            try:
                # 1. Test URL Parameters
                parsed = urllib.parse.urlparse(self.target_url)
                params = urllib.parse.parse_qs(parsed.query)

                if params:
                    await self.emit_event("INFO", f"Fuzzing {len(params)} URL parameters for SQL errors...")
                    for param in params.keys():
                        for payload in payloads:
                            fuzzed_params = params.copy()
                            fuzzed_params[param] = [payload]
                            new_query = urllib.parse.urlencode(fuzzed_params, doseq=True)
                            fuzzed_url = parsed._replace(query=new_query).geturl()

                            await page.goto(fuzzed_url)
                            content = await page.content()
                            
                            if any(error in content.lower() for error in self.SQL_ERRORS):
                                await self.save_screenshot(page, f"SQLi Error in Param: {param}")
                                await self.report_finding(
                                    severity="CRITICAL",
                                    title="SQL Injection Detected (Error-Based)",
                                    evidence=f"SQL error signature found in response after injecting `{payload}` into `{param}`.\nURL: {fuzzed_url}",
                                    recommendation="Use parameterized queries (Prepared Statements) for all database interactions. NEVER concatenate user input into SQL strings."
                                )
                                await self.emit_event("SUCCESS", "SQLi VULNERABILITY CONFIRMED!")
                                break # Move to next parameter

                # 2. Test Form Inputs
                await page.goto(self.target_url)
                await self.update_progress(50)

                inputs = await page.query_selector_all("input[type='text'], input:not([type]), textarea")
                if inputs:
                    await self.emit_event("INFO", f"Testing {len(inputs)} form inputs for SQLi...")
                    for i, input_el in enumerate(inputs):
                        for payload in payloads:
                            try:
                                await page.goto(self.target_url) # Reset
                                inputs_retry = await page.query_selector_all("input[type='text'], input:not([type]), textarea")
                                await inputs_retry[i].fill(payload)
                                await inputs_retry[i].press("Enter")
                                await asyncio.sleep(1)
                                
                                content = await page.content()
                                if any(error in content.lower() for error in self.SQL_ERRORS):
                                    await self.save_screenshot(page, f"SQLi Error in Form Input {i}")
                                    await self.report_finding(
                                        severity="CRITICAL",
                                        title="SQL Injection Detected in Form",
                                        evidence=f"SQL error signature found after injecting `{payload}` into form input #{i}.",
                                        recommendation="Ensure all backend queries use database abstractions that handle parameterization automatically."
                                    )
                                    break
                            except:
                                continue

                await self.update_progress(100)
                await self.emit_event("SUCCESS", "SQLi Scan finished.")

            except Exception as e:
                await self.emit_event("ERROR", f"SQLi Agent failed: {str(e)}")
            finally:
                await browser.close()
