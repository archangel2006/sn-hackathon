"use client";

import React from "react";
import Icon from "./Icons";
import { PERSONAS, AREA, lvl, studentStatus } from "../lib/data";

function StaffPill({ score }) {
  const l = lvl(score);
  return (
    <span className={`pill ${l.key}`}>
      {score} {l.staff}
    </span>
  );
}

function Meter({ score }) {
  return (
    <div
      className="meter"
      role="img"
      aria-label={`Risk score ${score} out of 100`}
    >
      <div
        className={`fill ${lvl(score).key}`}
        style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
      />
      <span className="tick" style={{ left: "40%" }} />
      <span className="tick" style={{ left: "70%" }} />
    </div>
  );
}

function CaseDetail({ c, update }) {
  if (!c) {
    return (
      <section className="panel">
        <div className="empty">
          <strong>No case selected</strong>
          Select a case to see the evidence, AI domain summary, and audit trace.
        </div>
      </section>
    );
  }

  const domainName = AREA[c.domain] ? AREA[c.domain].toLowerCase() : c.domain;
  const trace = c.trace || {
    tools: ["get_risk_profile", "search_support_kb", "suggest_case", "create_case"],
    retrieved: 4,
    authorized: 3,
    blocked: 1,
    sent: 3,
  };

  return (
    <section className="panel detail" aria-label="Case detail">
      <h2>
        {c.studentName}, {domainName}
      </h2>
      <p className="sub">
        Case {c.no}, opened {c.opened}
      </p>

      <h3>Risk score</h3>
      <div className="scoreline">
        <b>{c.score}</b>
        <StaffPill score={c.score} />
      </div>
      <Meter score={c.score} />

      <h3>Evidence</h3>
      <ul className="evidence">
        {(c.evidence || []).map((e, idx) => (
          <li key={idx}>{e}</li>
        ))}
      </ul>

      <h3>Summary</h3>
      <p>{c.summary}</p>

      <h3>Consent</h3>
      <div className="consentstamp">
        <Icon name="check" size={18} />
        Student agreed to share this at {c.consentAt || c.opened}
      </div>
      <div className="scope">
        This case only includes {domainName} information. Other areas of the
        student&apos;s record aren&apos;t part of it.
      </div>

      <div className="actions">
        {c.state === "New" && (
          <button
            type="button"
            className="btn primary"
            onClick={() => update(c.no, "In Progress")}
          >
            Accept case
          </button>
        )}
        {c.state === "In Progress" && (
          <button
            type="button"
            className="btn primary"
            onClick={() => update(c.no, "Resolved")}
          >
            Mark resolved
          </button>
        )}
        {c.state === "Waiting for Student" && (
          <button
            type="button"
            className="btn primary"
            onClick={() => update(c.no, "In Progress")}
          >
            Resume work
          </button>
        )}
        {(c.state === "New" || c.state === "In Progress") && (
          <button
            type="button"
            className="btn"
            onClick={() => update(c.no, "Waiting for Student")}
          >
            Ask student for more info
          </button>
        )}
      </div>

      <p className="status" aria-live="polite">
        Status: <strong>{c.state}</strong>. The student sees &quot;{studentStatus(c.state)}&quot;.
      </p>

      <details>
        <summary>How this case was created</summary>
        <ul className="trace">
          <li>
            Tools used:{" "}
            {trace.tools.map((t) => (
              <React.Fragment key={t}>
                <code>{t}</code>{" "}
              </React.Fragment>
            ))}
          </li>
          <li>
            Knowledge search: {trace.retrieved} retrieved, {trace.authorized}{" "}
            allowed, {trace.blocked} blocked, {trace.sent} sent to the model
          </li>
          <li>
            Firewall protection: student role prevented leakage of staff triage docs
          </li>
          <li>Case created after the student&apos;s explicit consent, not automatically</li>
        </ul>
      </details>
    </section>
  );
}

export default function StaffPortal({
  cases,
  persona,
  setPersona,
  selected,
  setSelected,
  update,
}) {
  const p = PERSONAS[persona] || PERSONAS.counsellor;
  const list = cases.filter((c) => p.domains.includes(c.domain));
  const chosen = list.find((c) => c.no === selected) || null;
  const count = (s) => list.filter((c) => c.state === s).length;

  return (
    <main className="shell staff">
      <aside className="side">
        <div className="who-card pick">
          <label className="who">
            Signed in as
            <select
              value={persona}
              onChange={(e) => {
                setPersona(e.target.value);
                setSelected(null);
              }}
            >
              {Object.entries(PERSONAS).map(([k, v]) => (
                <option key={k} value={k}>
                  {v.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        <section className="queue" aria-label="Queue summary">
          <span className="tiny">Your queue</span>
          <div className="qn">
            <b>{list.length}</b>
            <span>{list.length === 1 ? "case" : "cases"}</span>
          </div>
          <ul className="qs">
            {["New", "In Progress", "Waiting for Student", "Resolved"].map(
              (s) => (
                <li key={s}>
                  <span>{s}</span>
                  <b>{count(s)}</b>
                </li>
              )
            )}
          </ul>
        </section>
      </aside>

      <div className="main">
        <section className="hero compact">
          <div className="hello">
            <h1>{p.dept}</h1>
            <p>Cases students have chosen to share with you.</p>
          </div>
        </section>

        <section className="panel" aria-label="Case queue">
          {list.length === 0 ? (
            <div className="empty">
              <strong>No cases right now</strong>
              New cases appear here when students share them.
            </div>
          ) : (
            <div className="tablewrap">
              <table>
                <thead>
                  <tr>
                    <th>Case</th>
                    <th>Student</th>
                    <th>Risk</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {list.map((c) => (
                    <tr
                      key={c.no}
                      aria-selected={selected === c.no}
                      tabIndex={0}
                      onClick={() => setSelected(c.no)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          e.preventDefault();
                          setSelected(c.no);
                        }
                      }}
                    >
                      <td className="cn">{c.no}</td>
                      <td>{c.studentName}</td>
                      <td>
                        <StaffPill score={c.score} />
                      </td>
                      <td>{c.state}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>

      <div className="rail">
        <CaseDetail c={chosen} update={update} />
      </div>
    </main>
  );
}
