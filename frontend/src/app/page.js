"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import TopBar from "../components/TopBar";
import StudentPortal from "../components/StudentPortal";
import StaffPortal from "../components/StaffPortal";
import {
  seedCases,
  firstMessage,
  ME,
  SCORE,
  EVIDENCE,
  SUMMARY,
  TRACE_TOOLS,
  uid,
  nowTime,
  localRespond,
} from "../lib/data";
import {
  checkBackendHealth,
  postChat,
  createCaseApi,
  patchStaffCaseState,
} from "../lib/api";

export default function App() {
  const [role, setRole] = useState("student");
  const [tab, setTab] = useState("home");
  const [persona, setPersona] = useState("counsellor");
  const [selected, setSelected] = useState(null);
  const [cases, setCases] = useState(seedCases);
  const [messages, setMessages] = useState(firstMessage);
  const [typing, setTyping] = useState(false);
  const [isLiveApi, setIsLiveApi] = useState(false);

  const nextNo = useRef(124);
  const liveRef = useRef({});
  liveRef.current = { cases, messages, typing, isLiveApi };

  // Check backend health periodically
  useEffect(() => {
    let mounted = true;
    const probe = async () => {
      const alive = await checkBackendHealth();
      if (mounted) setIsLiveApi(alive);
    };
    probe();
    const interval = setInterval(probe, 8000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const send = useCallback(async (text) => {
    const q = (text || "").trim();
    if (!q || liveRef.current.typing) return;

    const userMsgId = uid();
    setMessages((m) => [...m, { id: userMsgId, role: "user", text: q }]);
    setTyping(true);

    const ctx = {
      cases: liveRef.current.cases,
      messages: liveRef.current.messages,
    };

    if (liveRef.current.isLiveApi) {
      try {
        const resp = await postChat(q, ME.id);
        if (resp && resp.type) {
          if (resp.type === "consent_request" && resp.consent_request) {
            const cr = resp.consent_request;
            setMessages((ms) => [
              ...ms,
              {
                id: uid(),
                role: "agent",
                type: "message",
                text: resp.text,
                sources: (resp.sources || []).map((s) => s.title || s.doc_id),
                blocked: resp.blocked_count || 0,
              },
              {
                id: uid(),
                role: "agent",
                type: "consent",
                domain: cr.domain,
                dept: cr.department,
                status: "pending",
                summary: cr.shared_summary,
                shared: cr.shared_fields || [],
                notShared: cr.not_shared || [],
              },
            ]);
          } else {
            setMessages((ms) => [
              ...ms,
              {
                id: uid(),
                role: "agent",
                type: resp.type === "escalation" ? "escalation" : resp.type === "blocked" ? "blocked" : "message",
                text: resp.text,
                sources: (resp.sources || []).map((s) => s.title || s.doc_id),
                blocked: resp.blocked_count || 0,
              },
            ]);
          }
          setTyping(false);
          return;
        }
      } catch (err) {
        console.warn("Backend chat call failed, falling back to local engine:", err);
      }
    }

    // Local engine fallback
    setTimeout(() => {
      const replies = localRespond(q, ctx);
      setMessages((m) => [...m, ...replies]);
      setTyping(false);
    }, 700);
  }, []);

  const onConsent = useCallback(async (id, accepted) => {
    const m = liveRef.current.messages.find((x) => x.id === id);
    if (!m || m.status !== "pending") return;

    if (!accepted) {
      setMessages((ms) => [
        ...ms.map((x) => (x.id === id ? { ...x, status: "declined" } : x)),
        {
          id: uid(),
          role: "agent",
          type: "message",
          text: "No problem. Nothing was shared, and I'm here if you change your mind.",
        },
      ]);
      return;
    }

    const no = "WEL" + String(nextNo.current++).padStart(7, "0");
    const domain = m.domain;
    const newCase = {
      no,
      studentId: ME.id,
      studentName: ME.name,
      domain,
      dept: m.dept,
      score: SCORE[domain] || 50,
      state: "New",
      opened: "Today, " + nowTime(),
      consentAt: nowTime(),
      evidence: EVIDENCE[domain] || ["Routine signal observation"],
      summary: SUMMARY[domain] || "The student agreed to share this domain summary.",
      trace: {
        tools: TRACE_TOOLS,
        retrieved: 4,
        authorized: 3,
        blocked: 1,
        sent: 3,
      },
    };

    if (liveRef.current.isLiveApi) {
      try {
        await createCaseApi({
          student_id: ME.id,
          domain: domain,
          category: domain.charAt(0).toUpperCase() + domain.slice(1),
          priority: (SCORE[domain] || 50) >= 70 ? "High" : "Medium",
          risk_score: SCORE[domain] || 50,
          risk_level: (SCORE[domain] || 50) >= 70 ? "HIGH" : "MEDIUM",
          evidence: EVIDENCE[domain] || [],
          ai_summary: SUMMARY[domain] || "",
          consent: {
            given: true,
            timestamp: new Date().toISOString(),
            scope: domain,
          },
          trace_id: "T-" + Math.floor(1000 + Math.random() * 9000),
        });
      } catch (e) {
        console.warn("ServiceNow backend sync notice:", e);
      }
    }

    setCases((cs) => [newCase, ...cs]);
    setMessages((ms) => [
      ...ms.map((x) =>
        x.id === id ? { ...x, status: "accepted", caseNo: no } : x
      ),
      {
        id: uid(),
        role: "agent",
        type: "message",
        text: `Done. Case ${no} is with the ${m.dept}. You can follow it under My support.`,
      },
    ]);
  }, []);

  const update = useCallback(async (no, state) => {
    setCases((cs) => cs.map((c) => (c.no === no ? { ...c, state } : c)));

    if (liveRef.current.isLiveApi) {
      try {
        await patchStaffCaseState(no, state);
      } catch (e) {
        console.warn("Backend state sync notice:", e);
      }
    }
  }, []);

  const reset = useCallback(() => {
    setCases(seedCases());
    setMessages(firstMessage());
    setTyping(false);
    setTab("home");
    setSelected(null);
    nextNo.current = 124;
  }, []);

  return (
    <div>
      <TopBar
        role={role}
        setRole={setRole}
        onReset={reset}
        isLiveApi={isLiveApi}
      />
      {role === "student" ? (
        <StudentPortal
          cases={cases}
          messages={messages}
          typing={typing}
          send={send}
          onConsent={onConsent}
          tab={tab}
          setTab={setTab}
        />
      ) : (
        <StaffPortal
          cases={cases}
          persona={persona}
          setPersona={setPersona}
          selected={selected}
          setSelected={setSelected}
          update={update}
        />
      )}
    </div>
  );
}
