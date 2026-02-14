from flask import Flask, request, jsonify
from flask_cors import CORS
from db import supabase
import uuid

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/runs/start', methods=['POST'])
def start_run():
    data = request.json
    target_url = data.get('target_url')
    agents = data.get('agents', ['exposure', 'headers_tls']) # Default agents
    
    if not target_url:
        return jsonify({"error": "target_url is required"}), 400

    # 1. Create Run
    run_data = {
        "target_url": target_url,
        "status": "QUEUED"
    }
    
    try:
        run_res = supabase.table('security_runs').insert(run_data).execute()
        run_id = run_res.data[0]['id']

        # 2. Create Agent Sessions
        sessions = []
        for agent in agents:
            sessions.append({
                "run_id": run_id,
                "agent_type": agent,
                "status": "QUEUED"
            })
        
        supabase.table('agent_sessions').insert(sessions).execute()
        
        return jsonify({"run_id": run_id, "status": "QUEUED"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/runs/<run_id>/cancel', methods=['POST'])
def cancel_run(run_id):
    try:
        # Cancel run
        supabase.table('security_runs').update({"status": "CANCELLED"}).eq("id", run_id).execute()
        # Cancel sessions
        supabase.table('agent_sessions').update({"status": "CANCELLED"}).eq("run_id", run_id).execute()
        
        return jsonify({"status": "CANCELLED"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
