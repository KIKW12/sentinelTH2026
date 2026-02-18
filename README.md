<div align="center">

# 🛡️ SENTINEL

### AI-Powered Autonomous Security Scanner

**Deploy a swarm of 10 AI agents to find vulnerabilities in your web app — before attackers do.**

[![Built at TreeHacks](https://img.shields.io/badge/Built%20at-TreeHacks%202026-6366f1?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPjxwYXRoIGQ9Ik0xMiAyTDIgN2w1IDUgNS01IDUtNSA1IDV6Ii8+PC9zdmc+)](https://www.treehacks.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![Gemini](https://img.shields.io/badge/Gemini-2.0--flash-4285f4?style=for-the-badge&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Supabase](https://img.shields.io/badge/Supabase-Realtime-3ecf8e?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)

<br/>

*Traditional scanners check boxes. Sentinel **thinks**.*

</div>

---

## ⚡ The Problem

Penetration testing is **expensive** ($5K–$30K per engagement), **slow** (weeks to schedule), and **inaccessible** to indie developers, startups, and small teams. Meanwhile, automated scanners run rigid, predefined checks — they can't *reason* about what they find.

**Sentinel bridges the gap.** It combines the systematic coverage of automated scanning with the adaptive reasoning of a human pen tester — powered by LLMs that observe, think, and act.

---

## 🧬 How It Works

Sentinel deploys a coordinated **swarm of 10 specialized AI agents** against your target, each attacking a different surface. Agents run concurrently, share reconnaissance data, and report findings in real-time.

```
                                 ┌──────────────────────────────────┐
                                 │         SENTINEL ENGINE          │
                                 │                                  │
   ┌──────────┐    ┌─────────┐   │  Phase 1 ─ Recon                │
   │  Target  │───►│  Flask  │──►│  └── 🕷️  Spider Agent            │
   │   URL    │    │   API   │   │                                  │
   └──────────┘    └────┬────┘   │  Phase 2 ─ Concurrent Scanners  │
                        │        │  ├── 🔍 Exposure   ├── 🌐 CORS  │
   ┌──────────┐    ┌────▼────┐   │  ├── 🛡️  Headers   ├── 🔌 Ports │
   │  Next.js │◄───│Supabase │◄──│  ├── 💉 SQLi      ├── ⚡ XSS   │
   │   Live   │    │Realtime │   │  └── 🔐 Auth Abuse              │
   │Dashboard │    └─────────┘   │                                  │
   └──────────┘                  │  Phase 3 ─ AI Deep Analysis     │
                                 │  ├── 🤖 Red Team (Autonomous)   │
                                 │  └── 🧠 LLM Analysis            │
                                 │                                  │
                                 │  ══════════════════════════════  │
                                 │  📊 Gemini Remediation Report   │
                                 └──────────────────────────────────┘
```

---

## 🤖 The Agent Swarm

<table>
<tr>
<td width="50%">

### 🕷️ Spider Agent
Crawls the target to **map the full attack surface** — pages, forms, API endpoints, JavaScript files, and linked resources. Feeds recon data to all downstream agents.

### 🔍 Exposure Agent
Hunts for **leaked secrets**: exposed `.env` files, API keys in JavaScript, directory listings, `.git` folders, backup files, and sensitive endpoints like `/wp-admin`.

### 🛡️ Headers & TLS Agent
Audits every HTTP security header (`CSP`, `HSTS`, `X-Frame-Options`, etc.) and evaluates the **TLS configuration** — cipher suites, certificate validity, and protocol versions.

### 🌐 CORS Agent
Probes **Cross-Origin Resource Sharing** policies for dangerous misconfigurations: wildcard origins, null origin reflection, credential exposure, and subdomain trust issues.

### 🔌 Port Scan Agent
Discovers **open ports and services** on the target host, fingerprinting running software and flagging unnecessary exposed services that expand the attack surface.

</td>
<td width="50%">

### 🔐 Auth Abuse Agent
Tests **authentication and authorization** boundaries: brute-force protections, session fixation, IDOR vulnerabilities, privilege escalation, and JWT misconfigurations.

### 💉 SQLi Agent
Attempts **SQL injection** across all discovered input vectors — URL parameters, form fields, cookies, and headers — using both error-based and blind injection techniques.

### ⚡ XSS Agent
Tests for **Cross-Site Scripting** with payload injection across reflected, stored, and DOM-based contexts. Verifies findings by confirming actual script execution in the DOM.

### 🤖 Red Team Agent
The crown jewel — an **autonomous AI pen tester** with full browser control via Playwright. Uses Gemini to run an observe → think → act loop, deciding which tools to invoke (click, type, JS execution, API calls, screenshots) in real-time.

### 🧠 LLM Analysis Agent
Performs **contextual AI analysis** of all collected data — discovering patterns, chaining low-severity findings into high-impact attack paths, and identifying logic flaws that traditional scanners miss.

</td>
</tr>
</table>

---

## 📊 Risk Scoring

Every finding is severity-weighted to produce a composite security score and letter grade:

<div align="center">

$$S = \max\!\Big(0,\;\; 100 - \sum_{i=1}^{n} w(s_i)\Big)$$

| Severity | Penalty | Example |
|:---:|:---:|:---|
| 🔴 **CRITICAL** | **−25** | Remote Code Execution, SQL Injection with data exfil |
| 🟠 **HIGH** | **−10** | Stored XSS, Authentication Bypass |
| 🟡 **MEDIUM** | **−3** | Missing CSP, Insecure CORS |
| 🟢 **LOW** | **−1** | Missing `X-Content-Type-Options` |

| Grade | Score Range | Meaning |
|:---:|:---:|:---|
| **A** | 90 – 100 | Excellent — minimal risk |
| **B** | 75 – 89 | Good — minor issues |
| **C** | 50 – 74 | Moderate — action needed |
| **D** | 25 – 49 | Poor — significant risk |
| **F** | 0 – 24 | Critical — immediate action |

</div>

The final report is generated by **Gemini**, providing code-level fix instructions, OWASP references, and prioritized remediation steps.

---

## 🏗️ Architecture

```
sentinel/
├── backend/                  # Python Backend
│   ├── agents/               # 10 Specialized Security Agents
│   │   ├── base.py           #   └── BaseAgent ABC (lifecycle, events, findings)
│   │   ├── spider.py         #   └── Attack Surface Mapper
│   │   ├── exposure.py       #   └── Secret & File Leak Detection
│   │   ├── headers.py        #   └── HTTP Header & TLS Auditor
│   │   ├── cors.py           #   └── CORS Misconfiguration Tester
│   │   ├── portscan.py       #   └── Port & Service Discovery
│   │   ├── auth_abuse.py     #   └── Auth & Authz Bypass Engine
│   │   ├── sqli.py           #   └── SQL Injection Fuzzer
│   │   ├── xss.py            #   └── XSS Payload Engine
│   │   ├── red_team.py       #   └── Autonomous AI Pen Tester
│   │   └── llm_analysis.py   #   └── Contextual AI Analyzer
│   ├── app.py                # Flask API (Control Plane)
│   ├── worker.py             # Agent Orchestrator (Execution Plane)
│   ├── report_generator.py   # Gemini-Powered Report Engine
│   ├── summary_generator.py  # Executive Summary Generator
│   └── modal_agents.py       # Modal Cloud Agent Runners
│
├── frontend/                 # Next.js 16 Dashboard
│   └── src/
│       ├── app/page.tsx      # Scan launcher & homepage
│       └── app/runs/         # Real-time scan monitoring
│
└── supabase/
    └── schema.sql            # Database schema + RLS policies
```

### Tech Stack

| Layer | Technology | Purpose |
|:---|:---|:---|
| **Frontend** | Next.js 16, TypeScript, Tailwind CSS, Framer Motion | Real-time dashboard with dark cyber aesthetic |
| **Backend** | Python, Flask, asyncio | REST API + async agent orchestration |
| **AI Engine** | Google Gemini (`gemini-2.0-flash`) | Red Team reasoning, LLM analysis, report generation |
| **Browser Automation** | Playwright (headless Chromium) | Red Team agent DOM interaction |
| **Database** | Supabase (PostgreSQL + Realtime) | Live event streaming & finding storage |
| **HTTP Probing** | aiohttp, BeautifulSoup | Async HTTP requests & HTML parsing |
| **Cloud Compute** | Modal *(optional)* | Offload Playwright agents to serverless GPU |
| **Deployment** | Render | Single-process API + worker |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** & **Node.js 18+**
- **Supabase** project ([create one free](https://supabase.com))
- **Google AI API key** for Gemini ([get one](https://aistudio.google.com/app/apikey))

### 1. Clone & Install

```bash
git clone https://github.com/EKasuti/sentinel.git
cd sentinel
```

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

```bash
# Frontend
cd ../frontend
npm install
```

### 2. Configure Environment

```bash
# Backend — backend/.env
cp backend/.env.example backend/.env
```
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
OPENAI_API_KEY=your_gemini_api_key
ALLOWED_ORIGINS=http://localhost:3000
```

```bash
# Frontend — frontend/.env
cp frontend/.env.example frontend/.env
```
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 3. Set Up Database

Run the SQL in `supabase/schema.sql` in your Supabase SQL Editor, then enable **Realtime** for:
- `agent_sessions`
- `run_events`
- `findings`

### 4. Launch

```bash
# Terminal 1 — Backend
cd backend
python main.py
# API running on http://localhost:5000

# Terminal 2 — Frontend
cd frontend
npm run dev
# Dashboard on http://localhost:3000
```

**Enter a URL → Hit Scan → Watch the agents work in real-time.** 🎯

---

## 🔬 Agent Framework

Every agent extends a `BaseAgent` abstract class providing:

```python
class BaseAgent(ABC):
    """
    Lifecycle:  QUEUED → RUNNING → COMPLETED / FAILED
    Events:     Structured events → Supabase Realtime → Dashboard
    Findings:   Severity-tagged vulnerabilities with reproduction steps
    Progress:   Percentage updates for the UI
    """

    @abstractmethod
    async def run(self, target_url: str, context: dict) -> list[Finding]:
        ...
```

### Phased Orchestration

Agents run in **three phases** to balance thoroughness with rate limits:

```
Phase 1  ──────────────►  Spider (maps attack surface)
                              │
Phase 2  ──────────────►  7 Scanner agents run concurrently
          asyncio.gather()    │  via asyncio.gather()
                              │
Phase 3  ──────────────►  Red Team → LLM Analysis
          sequential          │  (avoids API rate contention)
                              ▼
                         📊 Report Generation
```

---

## 🧪 Challenges & Lessons

<details>
<summary><b>🔄 LLM Rate Limits vs. Agent Concurrency</b></summary>

Running all agents in parallel — including multiple LLM-powered ones — immediately hit Gemini's RPM limits. **Fix:** Phased orchestration model separating fast scanners from LLM agents.
</details>

<details>
<summary><b>🎯 Making the Red Team Agent Actually Useful</b></summary>

Early versions were random clickers. We needed careful prompt engineering to teach the LLM to **prioritize** (check `.env` before fuzzing forms), **stay on-domain** (domain guard), and **avoid infinite loops** (capping the observe-think-act cycle).
</details>

<details>
<summary><b>📡 Keeping 10 Agents in Sync with the UI</b></summary>

With agents emitting events at different rates, keeping the frontend in sync required a structured event schema — every event carries `run_id`, `agent_type`, and structured `data` — routed to the correct agent lane via Supabase Realtime.
</details>

<details>
<summary><b>🚨 Taming False Positives</b></summary>

Initial XSS and SQLi agents flagged every reflected parameter. We added **verification** — confirming that injected JavaScript actually executes in the DOM before reporting — to maintain signal-to-noise ratio.
</details>

<details>
<summary><b>📦 Single-Process Deployment</b></summary>

Render's free tier means running Flask API + async worker in one process. Python's `multiprocessing` spawns the worker as a child with graceful shutdown. Not elegant, but the entire backend deploys with a single `python main.py`.
</details>

---

## 🗺️ Roadmap

- [ ] **Authentication & multi-tenancy** — user accounts with scan history
- [ ] **Scheduled recurring scans** — continuous security monitoring
- [ ] **Custom agent configuration** — choose which agents to run per scan
- [ ] **CI/CD integration** — run Sentinel as a GitHub Action on every deploy
- [ ] **PDF report export** — downloadable security assessment reports
- [ ] **API endpoint** — headless scanning via REST API

---

## 🏆 Built At

<div align="center">

**[TreeHacks 2026](https://www.treehacks.com)** — Stanford University's flagship hackathon.

Track: **AI × Cybersecurity**

</div>

---

<div align="center">

**[⬆ Back to Top](#-sentinel)**

</div>
