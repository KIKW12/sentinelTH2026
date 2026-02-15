from .base import BaseAgent
from playwright.async_api import async_playwright
import os
import json
from openai import AsyncOpenAI

class LLMAnalysisAgent(BaseAgent):
    def __init__(self, run_id, session_id, target_url):
        super().__init__(run_id, session_id, target_url)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("WARNING: OPENAI_API_KEY not found. LLM Agent will fail.")
        self.client = AsyncOpenAI(api_key=api_key)

    async def execute(self):
        await self.emit_event("INFO", "Starting LLM Logic & PII Analysis...")
        
        async with async_playwright() as p:
            # Headless must be true for Modal environment
            browser = await p.chromium.launch(headless=True)
            # Create a context to support video recording
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                await self.update_progress(10)
                await page.goto(self.target_url)
                
                # Get page content (text only to save tokens)
                content = await page.inner_text("body")
                # Truncate if too long (simple heuristic)
                content = content[:10000] 
                
                await self.emit_event("INFO", "Page content extracted. Sending to 'The Brain' (GPT-4o)...")
                await self.update_progress(40)

                prompt = f"""
                You are a Senior Security Engineer at a top-tier technology company (like Google or Amazon).
                Your goal is to perform a high-signal security analysis of the provided web page content.

                ### Instructions:
                1. Analyze the page for genuine security vulnerabilities, focusing on:
                   - Business Logic Flaws: e.g., price manipulation, unintended access to sensitive data, exposed internal-only links.
                   - Sensitive Data Exposure (PII/Secrets): Look for exposed API keys, private emails (not support contact), phone numbers in debug logs, etc.
                   - Information Leakage: Suspicious developer comments, stack traces, or debug information.
                2. DO NOT flag standard, expected security practices or common public-facing features such as:
                   - Normal login or registration forms.
                   - Standard "Admin" or "Dashboard" links that are expected for authenticated users.
                   - Publicly available support contact information.
                3. Be conservative with severity levels. Only use HIGH or CRITICAL if there is clear evidence of an exploitable vulnerability.

                ### Output Format:
                Return a JSON object with a list of "findings". Each finding MUST include:
                - severity: (LOW, MEDIUM, HIGH, CRITICAL)
                - title: A concise, professional title.
                - evidence: The specific snippet or observation from the page content.
                - justification: A brief explanation of WHY this is a security risk and not a normal feature.
                - recommendation: Actionable steps for the development team.

                If no high-signal issues are found, return an empty list.
                JSON Format: {{ "findings": [ {{ "severity": "...", "title": "...", "evidence": "...", "justification": "...", "recommendation": "..." }} ] }}
                
                You are a Principal Security Engineer conducting a security assessment of {self.target_url}. 
                Your goal is to identify *actionable* security vulnerabilities with high precision and minimal false positives.

                Analyze the extracted page content below for the following categories:

                1. **Business Logic & Authorization Flaws**:
                   - Broken access controls (e.g., visible "Admin" links for non-admins).
                   - Pricing/Payment manipulation risks.
                   - Potentially dangerous debug features exposed in production.

                2. **Sensitive Information Exposure (High Precision)**:
                   - **CRITICAL**: AWS Access Keys (AKIA...), Stripe Secret Keys (sk_live...), Private Keys.
                   - **IGNORE / FALSE POSITIVES**: Do NOT report the following as security issues unless they are explicitly labeled as "secrets":
                     - **Firebase API Keys** (e.g., `AIza...`): These are public by design.
                     - **Google Maps API Keys**: Generally public.
                     - **Stripe Publishable Keys** (`pk_live...`).
                     - **Analytics IDs** (GA, Segment).

                3. **Suspicious Code / Comments**:
                   - Leftover "TODO" comments related to security.
                   - Stack traces or debug information leaked in the DOM.

                ### Context:
                Target URL: {self.target_url}

                ### Page Content (Truncated):
                {content}

                ### Instructions:
                - Think step-by-step about whether a finding is actually a vulnerability.
                - If you find a Firebase Key or other public identifier, IGNORE IT.
                - Return a JSON object with a list of "findings".
                
                JSON Format: {{ "findings": [ {{ "severity": "LOW|MEDIUM|HIGH|CRITICAL", "title": "...", "evidence": "...", "recommendation": "..." }} ] }}
                """

                response = await self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a professional security auditor focusing on high-signal findings."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                result = json.loads(response.choices[0].message.content)
                findings = result.get("findings", [])
                
                await self.emit_event("INFO", f"LLM Analysis complete. Found {len(findings)} high-signal issues.")
                await self.update_progress(80)

                for f in findings:
                    combined_evidence = f"Justification: {f.get('justification', 'N/A')}\n\nEvidence: {f['evidence']}"
                    await self.report_finding(
                        severity=f['severity'],
                        title=f['title'],
                        evidence=combined_evidence,
                        recommendation=f['recommendation']
                    )

                await self.update_progress(100)
                await self.emit_event("SUCCESS", "LLM Analysis finished.")

            except Exception as e:
                await self.emit_event("ERROR", f"LLM Scan failed: {str(e)}")
            finally:
                # Close context to ensure video is saved
                await context.close()
                await browser.close()
