from db import supabase

def check_latest_run():
    print("--- Checking Latest Run ---")
    # Get latest run
    res = supabase.table('security_runs').select("*").order("created_at", desc=True).limit(1).execute()
    if not res.data:
        print("No runs found.")
        return

    run = res.data[0]
    print(f"Run ID: {run['id']}")
    print(f"Status: {run['status']}")
    print(f"Target: {run['target_url']}")

    # Get sessions for this run
    sessions = supabase.table('agent_sessions').select("*").eq("run_id", run['id']).execute()
    print(f"Sessions Found: {len(sessions.data)}")
    for s in sessions.data:
        print(f" - {s['agent_type']}: {s['status']}")

if __name__ == "__main__":
    check_latest_run()
