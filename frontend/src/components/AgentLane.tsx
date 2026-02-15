"use client";

import { motion } from "framer-motion";
import { AgentSession, Finding } from "@/lib/types";
import { ShieldAlert, CheckCircle, Terminal, Loader2, Eye, Key, Shield } from "lucide-react";

interface AgentLaneProps {
    session: AgentSession;
    findings: Finding[];
}

const AGENT_ICON_MAP: Record<string, any> = {
    exposure: Eye,
    headers_tls: Shield,
    auth_abuse: Key,
    llm_analysis: Terminal,
    sqli: ShieldAlert,
    xss: ShieldAlert,
    red_team: ShieldAlert // Or a robot icon if available, reusing ShieldAlert for now or importing Bot
};

export default function AgentLane({ session, findings }: AgentLaneProps) {
    const Icon = AGENT_ICON_MAP[session.agent_type] || Terminal;
    const isRunning = session.status === "RUNNING";
    const isCompleted = session.status === "COMPLETED";
    const isFailed = session.status === "FAILED";

    let statusColor = "border-gray-700";
    if (isRunning) statusColor = "border-cyber-blue shadow-[0_0_15px_rgba(0,240,255,0.3)]";
    if (isCompleted) statusColor = "border-success-green shadow-[0_0_10px_rgba(0,255,159,0.2)]";
    if (isFailed) statusColor = "border-danger-red";

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className={`relative p-4 rounded-lg bg-black/40 border ${statusColor} backdrop-blur-sm transition-all duration-300 min-h-[120px]`}
        >
            <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                    <Icon className={`w-5 h-5 ${isRunning ? 'animate-pulse text-cyber-blue' : 'text-gray-400'}`} />
                    <span className="font-mono text-sm uppercase tracking-wider text-gray-200">
                        {session.agent_type.replace('_', ' ')}
                    </span>
                </div>
                {isRunning && <Loader2 className="w-4 h-4 animate-spin text-cyber-blue" />}
                {isCompleted && <CheckCircle className="w-4 h-4 text-success-green" />}
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-gray-800 h-1.5 rounded-full mt-2 mb-3 overflow-hidden">
                <motion.div
                    className="h-full bg-gradient-to-r from-cyber-blue to-purple-500"
                    initial={{ width: 0 }}
                    animate={{ width: `${session.progress}%` }}
                    transition={{ ease: "linear" }}
                />
            </div>

            {/* Stats */}
            <div className="flex justify-between items-end text-xs font-mono text-gray-400">
                <span>{session.status}</span>
                <div className="flex items-center gap-1 text-danger-red">
                    {findings.length > 0 && (
                        <>
                            <ShieldAlert className="w-3 h-3" />
                            <span>{findings.length} ISSUES</span>
                        </>
                    )}
                </div>
            </div>

            {/* Finding Dots */}
            <div className="flex gap-1 mt-2 flex-wrap">
                {findings.map((f, i) => (
                    <motion.div
                        key={f.id}
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className={`w-2 h-2 rounded-full ${f.severity === 'CRITICAL' ? 'bg-red-600 animate-ping' :
                            f.severity === 'HIGH' ? 'bg-orange-500' : 'bg-yellow-400'
                            }`}
                        title={f.title}
                    />
                ))}
            </div>
        </motion.div>
    );
}
