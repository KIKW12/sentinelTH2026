"""
Modal functions for running security agents in the cloud.
Each agent runs as a serverless function on Modal's infrastructure.

SETUP:
1. Authenticate: modal token new
2. Deploy: modal deploy modal_agents.py
3. Set USE_MODAL=true in .env
4. Worker will auto-dispatch to Modal
"""
import modal
import os
from dotenv import load_dotenv

load_dotenv()

# Create Modal app
MODAL_APP_NAME = os.getenv('MODAL_APP_NAME', 'sentinel-agents')
app = modal.App(MODAL_APP_NAME)

# ---------- Images ----------

# Heavy image: Playwright + all deps (for browser-based agents)
heavy_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "playwright",
        "aiohttp",
        "beautifulsoup4",
        "openai",
        "google-genai",
        "supabase",
        "python-dotenv",
    )
    .run_commands("playwright install chromium", "playwright install-deps chromium")
    .add_local_dir("agents", remote_path="/root/agents")
    .add_local_file("db.py", remote_path="/root/db.py")
)

# Light image: HTTP-only agents (no Playwright)
light_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "aiohttp",
        "beautifulsoup4",
        "supabase",
        "python-dotenv",
    )
    .add_local_dir("agents", remote_path="/root/agents")
    .add_local_file("db.py", remote_path="/root/db.py")
)

# ---------- Secrets ----------

secrets = modal.Secret.from_dict({
    "SUPABASE_URL": os.getenv("SUPABASE_URL", ""),
    "SUPABASE_SERVICE_KEY": os.getenv("SUPABASE_SERVICE_KEY", ""),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
})

# =====================================================
# HEAVY (Playwright) agents
# =====================================================

@app.function(image=heavy_image, secrets=[secrets], timeout=600, cpu=2.0, memory=2048)
async def run_spider_agent(run_id: str, session_id: str, target_url: str, config: dict = None):
    """Run SpiderAgent on Modal — maps attack surface first."""
    from agents.spider import SpiderAgent
    agent = SpiderAgent(run_id, session_id, target_url)
    await agent.run()
    return {"status": "completed", "session_id": session_id}


@app.function(image=heavy_image, secrets=[secrets], timeout=600, cpu=2.0, memory=2048)
async def run_exposure_agent(run_id: str, session_id: str, target_url: str, config: dict = None):
    """Run ExposureAgent (v2) on Modal."""
    from agents.exposure_v2 import ExposureAgent
    agent = ExposureAgent(run_id, session_id, target_url)
    await agent.run()
    return {"status": "completed", "session_id": session_id}


@app.function(image=heavy_image, secrets=[secrets], timeout=600, cpu=2.0, memory=2048)
async def run_auth_abuse_agent(run_id: str, session_id: str, target_url: str, config: dict = None):
    """Run AuthAbuseAgent on Modal."""
    from agents.auth_abuse import AuthAbuseAgent
    agent = AuthAbuseAgent(run_id, session_id, target_url)
    await agent.run()
    return {"status": "completed", "session_id": session_id}


@app.function(image=heavy_image, secrets=[secrets], timeout=600, cpu=2.0, memory=2048)
async def run_sqli_agent(run_id: str, session_id: str, target_url: str, config: dict = None):
    """Run SQLiAgent on Modal."""
    from agents.sqli import SQLiAgent
    agent = SQLiAgent(run_id, session_id, target_url)
    await agent.run()
    return {"status": "completed", "session_id": session_id}


@app.function(image=heavy_image, secrets=[secrets], timeout=600, cpu=2.0, memory=2048)
async def run_xss_agent(run_id: str, session_id: str, target_url: str, config: dict = None):
    """Run XSSAgent on Modal."""
    from agents.xss import XSSAgent
    agent = XSSAgent(run_id, session_id, target_url)
    await agent.run()
    return {"status": "completed", "session_id": session_id}


@app.function(image=heavy_image, secrets=[secrets], timeout=900, cpu=2.0, memory=2048)
async def run_llm_analysis_agent(run_id: str, session_id: str, target_url: str, config: dict = None):
    """Run LLMAnalysisAgent on Modal (longer timeout for AI processing)."""
    from agents.llm_analysis import LLMAnalysisAgent
    agent = LLMAnalysisAgent(run_id, session_id, target_url)
    await agent.run()
    return {"status": "completed", "session_id": session_id}


@app.function(image=heavy_image, secrets=[secrets], timeout=1200, cpu=2.0, memory=4096)
async def run_red_team_agent(run_id: str, session_id: str, target_url: str, config: dict = None):
    """Run RedTeamAgent on Modal (extra memory + timeout)."""
    from agents.red_team import RedTeamAgent
    agent = RedTeamAgent(run_id, session_id, target_url)
    await agent.run()
    return {"status": "completed", "session_id": session_id}


# =====================================================
# LIGHT (HTTP-only) agents
# =====================================================

@app.function(image=light_image, secrets=[secrets], timeout=300, cpu=1.0, memory=512)
async def run_headers_agent(run_id: str, session_id: str, target_url: str, config: dict = None):
    """Run HeadersAgent (v2) on Modal."""
    from agents.headers_v2 import HeadersAgent
    agent = HeadersAgent(run_id, session_id, target_url)
    await agent.run()
    return {"status": "completed", "session_id": session_id}


@app.function(image=light_image, secrets=[secrets], timeout=300, cpu=1.0, memory=512)
async def run_cors_agent(run_id: str, session_id: str, target_url: str, config: dict = None):
    """Run CORSAgent on Modal."""
    from agents.cors import CORSAgent
    agent = CORSAgent(run_id, session_id, target_url)
    await agent.run()
    return {"status": "completed", "session_id": session_id}


@app.function(image=light_image, secrets=[secrets], timeout=300, cpu=1.0, memory=512)
async def run_portscan_agent(run_id: str, session_id: str, target_url: str, config: dict = None):
    """Run PortScanAgent on Modal."""
    from agents.portscan import PortScanAgent
    agent = PortScanAgent(run_id, session_id, target_url)
    await agent.run()
    return {"status": "completed", "session_id": session_id}


# =====================================================
# Agent dispatch map (used by worker.py)
# =====================================================

MODAL_AGENT_MAP = {
    "spider": run_spider_agent,
    "exposure": run_exposure_agent,
    "auth_abuse": run_auth_abuse_agent,
    "sqli": run_sqli_agent,
    "xss": run_xss_agent,
    "llm_analysis": run_llm_analysis_agent,
    "red_team": run_red_team_agent,
    "headers_tls": run_headers_agent,
    "cors": run_cors_agent,
    "portscan": run_portscan_agent,
}
