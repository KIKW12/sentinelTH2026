import asyncio
import time
import os
from db import supabase
from dotenv import load_dotenv

load_dotenv()

USE_MODAL = os.getenv("USE_MODAL", "false").lower() == "true"

# ---------- Local agent imports ----------
from agents.exposure_v2 import ExposureAgent
from agents.headers_v2 import HeadersAgent
from agents.auth_abuse import AuthAbuseAgent
from agents.llm_analysis import LLMAnalysisAgent
from agents.sqli import SQLiAgent
from agents.xss import XSSAgent
from agents.red_team import RedTeamAgent
from agents.spider import SpiderAgent
from agents.cors import CORSAgent
from agents.portscan import PortScanAgent

LOCAL_AGENT_MAP = {
    "spider": SpiderAgent,
    "exposure": ExposureAgent,
    "headers_tls": HeadersAgent,
    "cors": CORSAgent,
    "portscan": PortScanAgent,
    "auth_abuse": AuthAbuseAgent,
    "llm_analysis": LLMAnalysisAgent,
    "sqli": SQLiAgent,
    "xss": XSSAgent,
    "red_team": RedTeamAgent,
    "custom": ExposureAgent,
}

# ---------- Modal dispatch ----------
MODAL_AGENT_MAP = {}
if USE_MODAL:
    try:
        import modal
        MODAL_APP_NAME = os.getenv("MODAL_APP_NAME", "sentinel-agents")

        # Map agent_type -> Modal function name (as deployed)
        _MODAL_FUNCTION_NAMES = {
            "spider": "run_spider_agent",
            "exposure": "run_exposure_agent",
            "auth_abuse": "run_auth_abuse_agent",
            "sqli": "run_sqli_agent",
            "xss": "run_xss_agent",
            "llm_analysis": "run_llm_analysis_agent",
            "red_team": "run_red_team_agent",
            "headers_tls": "run_headers_agent",
            "cors": "run_cors_agent",
            "portscan": "run_portscan_agent",
        }

        # Look up each deployed function
        for agent_type, fn_name in _MODAL_FUNCTION_NAMES.items():
            try:
                MODAL_AGENT_MAP[agent_type] = modal.Function.from_name(MODAL_APP_NAME, fn_name)
            except Exception as e:
                print(f"⚠️  Could not find Modal function {fn_name}: {e}")

        print(f"✅ Modal dispatch enabled ({len(MODAL_AGENT_MAP)} functions found)")
    except ImportError as e:
        print(f"⚠️  Modal import failed ({e}), falling back to local execution")
        USE_MODAL = False

SPIDER_AGENTS = {"spider"}
LLM_AGENTS = {"llm_analysis", "red_team"}


async def process_run_modal(run_id: str, target_url: str, sessions_data: list):
    """Dispatch agents to Modal serverless functions."""
    print(f"🚀 Processing run {run_id} via MODAL for {target_url}")

    spider_sessions = []
    non_llm_sessions = []
    llm_sessions = []

    for session in sessions_data:
        agent_type = session["agent_type"]
        if agent_type in SPIDER_AGENTS:
            spider_sessions.append(session)
        elif agent_type in LLM_AGENTS:
            llm_sessions.append(session)
        else:
            non_llm_sessions.append(session)

    # Phase 1: Spider first (maps attack surface)
    for session in spider_sessions:
        agent_type = session["agent_type"]
        session_id = session["id"]
        modal_fn = MODAL_AGENT_MAP.get(agent_type)
        if modal_fn:
            print(f"☁️  [Modal] Launching {agent_type} (session: {session_id})")
            try:
                await modal_fn.remote.aio(run_id, session_id, target_url)
            except Exception as e:
                print(f"❌ Spider agent {agent_type} failed on Modal: {e}")

    # Phase 2: Non-LLM agents concurrently
    if non_llm_sessions:
        tasks = []
        for session in non_llm_sessions:
            agent_type = session["agent_type"]
            session_id = session["id"]
            modal_fn = MODAL_AGENT_MAP.get(agent_type)
            if modal_fn:
                print(f"☁️  [Modal] Launching {agent_type} (session: {session_id})")
                tasks.append(modal_fn.remote.aio(run_id, session_id, target_url))
            else:
                print(f"⚠️  No Modal function for {agent_type}, running locally")
                AgentClass = LOCAL_AGENT_MAP.get(agent_type, ExposureAgent)
                tasks.append(AgentClass(run_id, session_id, target_url).run())
        await asyncio.gather(*tasks, return_exceptions=True)

    # Phase 3: LLM agents sequentially (avoid rate-limit contention)
    for session in llm_sessions:
        agent_type = session["agent_type"]
        session_id = session["id"]
        modal_fn = MODAL_AGENT_MAP.get(agent_type)
        if modal_fn:
            print(f"☁️  [Modal] Launching {agent_type} (session: {session_id})")
            try:
                await modal_fn.remote.aio(run_id, session_id, target_url)
            except Exception as e:
                print(f"❌ LLM agent {agent_type} failed on Modal: {e}")


async def process_run_local(run_id: str, target_url: str, sessions_data: list):
    """Run agents locally (original behavior)."""
    print(f"💻 Processing run {run_id} LOCALLY for {target_url}")

    spider_tasks = []
    non_llm_tasks = []
    llm_sessions_list = []

    for session in sessions_data:
        agent_type = session["agent_type"]
        session_id = session["id"]

        AgentClass = LOCAL_AGENT_MAP.get(agent_type, ExposureAgent)
        agent_instance = AgentClass(run_id, session_id, target_url)

        if agent_type in SPIDER_AGENTS:
            spider_tasks.append(agent_instance)
        elif agent_type in LLM_AGENTS:
            llm_sessions_list.append(agent_instance)
        else:
            non_llm_tasks.append(agent_instance.run())

    # Phase 1: Spider first
    for spider in spider_tasks:
        try:
            await spider.run()
        except Exception as e:
            print(f"Spider Agent failed: {e}")

    # Phase 2: Non-LLM agents concurrently
    if non_llm_tasks:
        await asyncio.gather(*non_llm_tasks)

    # Phase 3: LLM agents sequentially
    for agent in llm_sessions_list:
        try:
            await agent.run()
        except Exception as e:
            print(f"LLM Agent {agent.__class__.__name__} failed: {e}")


async def process_run(run_id: str, target_url: str):
    print(f"Processing Run: {run_id} for {target_url}")

    # 1. Update Run Status to RUNNING
    supabase.table("security_runs").update({"status": "RUNNING", "started_at": "now()"}).eq("id", run_id).execute()

    # 2. Fetch Queued Sessions
    sessions_response = supabase.table("agent_sessions").select("*").eq("run_id", run_id).eq("status", "QUEUED").execute()
    sessions_data = sessions_response.data
    print(f"DEBUG: Found {len(sessions_data)} sessions for run {run_id}")

    # 3. Dispatch
    if USE_MODAL:
        await process_run_modal(run_id, target_url, sessions_data)
    else:
        await process_run_local(run_id, target_url, sessions_data)

    # 4. Update Run Status to COMPLETED
    supabase.table("security_runs").update({"status": "COMPLETED", "ended_at": "now()"}).eq("id", run_id).execute()
    print(f"✅ Run {run_id} Completed")


async def worker_loop():
    mode = "Modal" if USE_MODAL else "Local"
    print(f"Worker started ({mode} Mode). Polling for QUEUED runs...")
    while True:
        try:
            response = supabase.table("security_runs").select("*").eq("status", "QUEUED").limit(1).execute()

            if response.data:
                run = response.data[0]
                await process_run(run["id"], run["target_url"])
            else:
                await asyncio.sleep(2)

        except Exception as e:
            print(f"Worker Error: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(worker_loop())
