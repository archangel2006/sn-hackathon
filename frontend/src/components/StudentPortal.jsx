"use client";

import React, { useState, useRef, useEffect } from "react";
import Icon from "./Icons";
import { ME, AREA, lvl, studentStatus, stepIndex, SHARE } from "../lib/data";

function StudentPill({ score }) {
  const l = lvl(score);
  return (
    <span className={`pill ${l.key}`}>
      <Icon name={l.icon} size={14} />
      {l.student}
    </span>
  );
}

function StudentHome({ cases, openChat, ask, goSupport }) {
  const mine = cases.filter((c) => c.studentId === ME.id);

  return (
    <>
      <section className="hero">
        <span className="badge" aria-hidden="true">
          <Icon name="leaf" size={44} />
        </span>
        <div className="hello">
          <h1>Hi {ME.name}</h1>
          <p>{ME.course}</p>
        </div>
        <div className="note">
          <span className="spark" aria-hidden="true">
            <Icon name="spark" size={18} />
          </span>
          <div className="txt">
            <strong>Your support agent left a note</strong>
            A few things are worth a conversation. Nothing has been shared with anyone.
          </div>
          <button type="button" className="btn primary" onClick={openChat}>
            Open chat
          </button>
        </div>
      </section>

      <section aria-labelledby="how-section">
        <div className="sechead">
          <h2 id="how-section">How you&apos;re doing</h2>
          <span className="chip-count">{ME.areas.length} areas</span>
        </div>
        <div className="tiles">
          {ME.areas.map((a) => (
            <article className="tile" key={a.key}>
              <div className="tile-top">
                <span className="t">{a.title}</span>
                <StudentPill score={a.score} />
              </div>
              <p className="d">{a.note}</p>
              <button
                type="button"
                className="askbtn"
                onClick={() => ask(a.ask)}
              >
                Ask about this
                <Icon name="arrow" size={14} />
              </button>
            </article>
          ))}
        </div>
      </section>

      <section className="panel" aria-labelledby="sup-section">
        <h2 id="sup-section">Your support</h2>
        {mine.length === 0 ? (
          <div className="empty">
            <strong>Nothing shared yet</strong>
            Nothing goes to a department unless you say yes in the chat.
          </div>
        ) : (
          <ul className="rows">
            {mine.map((c) => (
              <li key={c.no}>
                <span className="t">{AREA[c.domain]} support</span>
                <span className="d">{c.dept}</span>
                <span className="a">
                  <span className="pill neutral">{studentStatus(c.state)}</span>
                  <button
                    type="button"
                    className="btn small"
                    onClick={goSupport}
                  >
                    View
                  </button>
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </>
  );
}

function ConsentCard({ m, onConsent }) {
  if (m.status !== "pending") {
    return (
      <div className="consent done">
        <div className="doneline">
          <Icon name={m.status === "accepted" ? "check" : "shield"} size={18} />
          {m.status === "accepted"
            ? `Shared with the ${m.dept}. Case ${m.caseNo} is open.`
            : `Not shared. Nothing was sent to the ${m.dept}.`}
        </div>
      </div>
    );
  }

  return (
    <div className="consent" role="group" aria-label="Sharing request">
      <h3>
        <Icon name="shield" size={18} />
        Share this with the {m.dept}?
      </h3>
      <p>{m.summary} Nothing is sent unless you say yes.</p>
      <div className="shareGrid">
        <div className="yes">
          <h4>Will be shared</h4>
          <ul>
            {m.shared.map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ul>
        </div>
        <div className="no">
          <h4>Stays private</h4>
          <ul>
            {m.notShared.map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ul>
        </div>
      </div>
      <div className="actions">
        <button
          type="button"
          className="btn primary"
          onClick={() => onConsent(m.id, true)}
        >
          Yes, share
        </button>
        <button
          type="button"
          className="btn"
          onClick={() => onConsent(m.id, false)}
        >
          Not now
        </button>
      </div>
    </div>
  );
}

function Message({ m, onConsent }) {
  if (m.role === "user") {
    return (
      <div className="msg user">
        <div className="bubble">{m.text}</div>
      </div>
    );
  }

  if (m.type === "consent") {
    return (
      <div className="msg agent">
        <ConsentCard m={m} onConsent={onConsent} />
      </div>
    );
  }

  if (m.type === "blocked") {
    return (
      <div className="msg agent">
        <div className="bubble">
          I can&apos;t help with that. It&apos;s restricted to staff, and I didn&apos;t use it in this conversation.
          <div className="blockednote">
            <Icon name="shield" size={15} />
            1 restricted source was blocked
          </div>
        </div>
      </div>
    );
  }

  if (m.type === "escalation") {
    return (
      <div className="msg agent">
        <div className="esc" role="alert">
          <h3>Let&apos;s get you to a person</h3>
          <p>
            If you might be in danger, call your local emergency number now. A member of the counselling team has been alerted and will reach out today.
          </p>
          <ul>
            <li>Campus crisis line, open 24 hours: 0800 000 0000 (demo number)</li>
            <li>You can keep chatting here while you wait.</li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="msg agent">
      <div className="bubble">
        {m.text}
        {m.sources && m.sources.length > 0 && (
          <div className="sources">
            Sources{" "}
            {m.sources.map((s) => (
              <span className="chip" key={s}>
                {s}
              </span>
            ))}
          </div>
        )}
        {Boolean(m.blocked) && (
          <div className="blockednote">
            <Icon name="shield" size={15} />
            {m.blocked} restricted source was blocked before I answered
          </div>
        )}
      </div>
    </div>
  );
}

function Chat({ messages, typing, send, onConsent }) {
  const [draft, setDraft] = useState("");
  const logRef = useRef(null);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [messages, typing]);

  const handleSend = () => {
    if (!draft.trim()) return;
    send(draft);
    setDraft("");
  };

  const quick = [
    "I've been feeling stressed lately",
    "Help with fees",
    "What support is there?",
    "Check my attendance",
  ];

  return (
    <div className="chatwrap">
      <section className="panel chat" aria-label="Chat with your support agent">
        <div className="chathead">
          <div className="l">
            <span className="dotlive" aria-hidden="true" />
            <div>
              <div className="tiny">Support agent</div>
              <h2>How can I help?</h2>
            </div>
          </div>
          <span className="tag">Student</span>
        </div>

        <div className="log" ref={logRef} role="log" aria-live="polite">
          {messages.map((m) => (
            <Message key={m.id} m={m} onConsent={onConsent} />
          ))}
          {typing && (
            <div className="msg agent">
              <div className="bubble typing" aria-label="Agent is typing">
                <i />
                <i />
                <i />
              </div>
            </div>
          )}
        </div>

        <div className="quick">
          {quick.map((q) => (
            <button
              key={q}
              type="button"
              onClick={() => send(q)}
              disabled={typing}
            >
              {q}
            </button>
          ))}
        </div>

        <div className="composer">
          <input
            value={draft}
            placeholder="Write a message"
            aria-label="Message"
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSend();
            }}
          />
          <button
            type="button"
            className="btn primary"
            onClick={handleSend}
            disabled={typing || !draft.trim()}
          >
            <Icon name="send" size={15} />
            Send
          </button>
        </div>
      </section>
    </div>
  );
}

function Support({ cases, goChat }) {
  const mine = cases.filter((c) => c.studentId === ME.id);
  const steps = ["Received", "In progress", "Resolved"];

  return (
    <div className="chatwrap">
      <section className="panel" aria-labelledby="ms-heading">
        <h2 id="ms-heading">My support</h2>
        {mine.length === 0 ? (
          <div className="empty">
            <strong>You haven&apos;t shared anything yet</strong>
            When you agree to share something in the chat, you can follow it here.
            <div style={{ marginTop: 12 }}>
              <button type="button" className="btn" onClick={goChat}>
                Open chat
              </button>
            </div>
          </div>
        ) : (
          mine.map((c) => {
            const idx = stepIndex(c.state);
            const domainShare = SHARE[c.domain] || {
              shared: ["Signals and check-ins"],
            };
            return (
              <div className="case" key={c.no}>
                <h3>{AREA[c.domain]} support</h3>
                <p className="meta">
                  {c.dept}, case {c.no}
                </p>
                <div className="steps" role="list">
                  {steps.map((s, i) => (
                    <React.Fragment key={s}>
                      <div
                        role="listitem"
                        className={`step ${
                          i < idx ? "done" : i === idx ? "now done" : ""
                        }`}
                      >
                        <span className="dot" />
                        {s}
                      </div>
                      {i < steps.length - 1 && (
                        <span
                          className={`bar ${i < idx ? "done" : ""}`}
                        />
                      )}
                    </React.Fragment>
                  ))}
                </div>
                {c.state === "Waiting for Student" && (
                  <div className="callout">
                    Action needed from you: the team has asked for a little more information.
                  </div>
                )}
                <p className="sharedwith">
                  Shared with the {c.dept}:{" "}
                  {domainShare.shared.join(", ").toLowerCase()}.
                </p>
                <p className="sharedwith">
                  {c.state === "Resolved"
                    ? "This case is resolved."
                    : "Next step: someone from the team will get in touch."}
                </p>
              </div>
            );
          })
        )}
      </section>
    </div>
  );
}

function StudentRail({ cases }) {
  const mine = cases.filter((c) => c.studentId === ME.id).length;
  const steps = [
    ["Ask in chat", "Say what is on your mind."],
    [
      "Choose what to share",
      "You see exactly what is shared before anything is sent.",
    ],
    ["Follow it", "Track progress under My support."],
  ];

  return (
    <aside className="rail" aria-label="Your workspace">
      <section className="railcard">
        <div className="tiny">Your workspace</div>
        <div className="ws">
          <span className="ni" aria-hidden="true">
            <Icon name="shield" size={20} />
          </span>
          <div>
            <b>Student workspace</b>
            <span className="s">Private to you</span>
          </div>
        </div>
        <div className="stats">
          <div className="stat">
            <b>{ME.areas.length}</b>
            <span>areas we look at</span>
          </div>
          <div className="stat">
            <b>{mine}</b>
            <span>{mine === 1 ? "case shared" : "cases shared"}</span>
          </div>
        </div>
        <div className="checks">
          {ME.areas.map((a) => (
            <span key={a.key}>
              <Icon name="check" size={14} />
              {a.title}
            </span>
          ))}
        </div>
        <div className="privnote">
          <strong>Sharing stays with you</strong>
          Nothing goes to a department unless you say yes in the chat.
        </div>
      </section>

      <section className="railcard">
        <div className="tiny">How sharing works</div>
        <ol className="how">
          {steps.map((s, i) => (
            <li key={s[0]}>
              <span className="n">{i + 1}</span>
              <div>
                <b>{s[0]}</b>
                <span className="s">{s[1]}</span>
              </div>
            </li>
          ))}
        </ol>
      </section>
    </aside>
  );
}

export default function StudentPortal({
  cases,
  messages,
  typing,
  send,
  onConsent,
  tab,
  setTab,
}) {
  const mine = cases.filter((c) => c.studentId === ME.id).length;
  const items = [
    ["home", "Home", "Your overview", "home"],
    ["chat", "Chat", "Talk to your agent", "chat"],
    ["support", "My support", "Follow shared cases", "folder"],
  ];

  return (
    <main className="shell">
      <aside className="side">
        <div className="who-card">
          <span className="avatar" aria-hidden="true">
            {ME.name.charAt(0)}
          </span>
          <div>
            <span className="tiny">Signed in as</span>
            <b>{ME.name}</b>
          </div>
        </div>
        <div className="navwrap">
          <span className="tiny">Menu</span>
          <nav className="nav" aria-label="Student">
            {items.map(([k, label, desc, icon]) => (
              <button
                key={k}
                type="button"
                aria-current={tab === k ? "page" : undefined}
                onClick={() => setTab(k)}
              >
                <span className="ni" aria-hidden="true">
                  <Icon name={icon} size={18} />
                </span>
                <span>
                  <span className="nt">{label}</span>
                  <span className="nd">{desc}</span>
                </span>
                {k === "support" && mine > 0 ? (
                  <span className="count">{mine}</span>
                ) : null}
              </button>
            ))}
          </nav>
        </div>
      </aside>

      <div className="main">
        {tab === "home" && (
          <StudentHome
            cases={cases}
            openChat={() => setTab("chat")}
            goSupport={() => setTab("support")}
            ask={(q) => {
              setTab("chat");
              send(q);
            }}
          />
        )}
        {tab === "chat" && (
          <Chat
            messages={messages}
            typing={typing}
            send={send}
            onConsent={onConsent}
          />
        )}
        {tab === "support" && (
          <Support cases={cases} goChat={() => setTab("chat")} />
        )}
      </div>

      <StudentRail cases={cases} />
    </main>
  );
}
