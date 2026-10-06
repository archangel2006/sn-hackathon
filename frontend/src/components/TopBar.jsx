"use client";

import React from "react";
import Icon from "./Icons";

export default function TopBar({ role, setRole, onReset, isLiveApi }) {
  return (
    <header className="topbar">
      <div className="brand">
        <span className="mark">
          <Icon name="leaf" size={20} />
        </span>
        <div>
          <span className="brand-name">Student Support Agent</span>
          <span className="protonote">
            ServiceNow AI Early-Warning Co-Innovation
          </span>
        </div>
      </div>

      <div className="spacer" />

      {/* Backend connection badge */}
      <div
        className={`apistatus ${isLiveApi ? "" : "offline"}`}
        title={
          isLiveApi
            ? "Connected to FastAPI backend (:8000)"
            : "Running with instant in-memory mock engine"
        }
      >
        <span className="indicator" />
        <span>{isLiveApi ? "FastAPI Live" : "Local Mock Engine"}</span>
      </div>

      <div className="seg" role="group" aria-label="View as">
        <span className="seg-label">Portal view</span>
        <button
          type="button"
          aria-pressed={role === "student"}
          onClick={() => setRole("student")}
        >
          Student
        </button>
        <button
          type="button"
          aria-pressed={role === "staff"}
          onClick={() => setRole("staff")}
        >
          Staff
        </button>
      </div>

      <button
        type="button"
        className="linkbtn"
        onClick={onReset}
        title="Reset demo data to initial state"
      >
        Reset demo
      </button>
    </header>
  );
}
