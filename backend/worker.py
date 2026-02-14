import asyncio
import time
from db import supabase
from agents.openclaw import OpenClawAgent
# from agents.nuclei import NucleiAgent # Future

# Mapping string agent_type to Class
AGENT_MAP = {
    "exposure": OpenClawAgent, # Using OpenClaw logic for exposure
    "headers_tls": OpenClawAgent, # Reusing for now or specific class
    "auth_abuse": OpenClawAgent,
    "openclaw": OpenClawAgent
}

async def process_run(run_id: str, target_url: str):
    print(f"Processing Run: {run_id} for {target_url}")
    
    # 1. Update Run Status to RUNNING
    supabase.table('security_runs').update({"status": "RUNNING", "started_at": "now()"}).eq("id", run_id).execute()

    # 2. Fetch Queued Sessions
    sessions = supabase.table('agent_sessions').select("*").eq("run_id", run_id).eq("status", "QUEUED").execute()
    
    tasks = []
    
    # 3. Launch Agents
    for session in sessions.data:
        agent_type = session['agent_type']
        session_id = session['id']
        
        # Use OpenClawAgent as default fallback if type not found
        AgentClass = AGENT_MAP.get(agent_type, OpenClawAgent)
        
        agent_instance = AgentClass(run_id, session_id, target_url)
        tasks.append(agent_instance.run()) # buffer the coroutine

    # 4. Wait for all agents
    if tasks:
        await asyncio.gather(*tasks)

    # 5. Update Run Status to COMPLETED
    supabase.table('security_runs').update({"status": "COMPLETED", "ended_at": "now()"}).eq("id", run_id).execute()
    print(f"Run {run_id} Completed")

async def worker_loop():
    print("Worker started. Polling for QUEUED runs...")
    while True:
        try:
            # Poll for 1 queued run
            response = supabase.table('security_runs').select("*").eq("status", "QUEUED").limit(1).execute()
            
            if response.data:
                run = response.data[0]
                await process_run(run['id'], run['target_url'])
            else:
                await asyncio.sleep(2) # Sleep if no work
                
        except Exception as e:
            print(f"Worker Error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(worker_loop())
