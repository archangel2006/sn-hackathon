export const DEPT_OF = {
  wellbeing: "Counselling Service",
  financial: "Scholarships & Financial Aid",
  academic: "Academic Advising",
  engagement: "Academic Advising"
};

export const AREA = {
  wellbeing: "Wellbeing",
  financial: "Money",
  academic: "Studies",
  engagement: "Attendance"
};

export const PERSONAS = {
  counsellor: {
    label: "Counsellor",
    dept: "Counselling Service",
    domains: ["wellbeing"]
  },
  finaid: {
    label: "Scholarship and financial aid officer",
    dept: "Scholarships & Financial Aid",
    domains: ["financial"]
  },
  advisor: {
    label: "Academic advisor",
    dept: "Academic Advising",
    domains: ["academic", "engagement"]
  }
};

export const ME = {
  id: "S001",
  name: "Student 001",
  course: "Computer Science, year 2",
  areas: [
    {
      key: "academic",
      title: "Studies",
      score: 48,
      note: "Marks have dipped over the last three assessments.",
      ask: "Can I get help with my studies? What support exists?"
    },
    {
      key: "engagement",
      title: "Attendance",
      score: 28,
      note: "Steady at 91% this term.",
      ask: "Check my attendance"
    },
    {
      key: "financial",
      title: "Money",
      score: 74,
      note: "Tuition fees are 18 days overdue.",
      ask: "Help with fees"
    },
    {
      key: "wellbeing",
      title: "Wellbeing",
      score: 63,
      note: "Your check-ins have been lower this week.",
      ask: "I've been feeling stressed lately"
    }
  ]
};

export const SCORE = Object.fromEntries(ME.areas.map(a => [a.key, a.score]));

export const EVIDENCE = {
  wellbeing: [
    "Mood check-ins averaged 2.1 out of 5 over 7 days",
    "Stress rated 4 or 5 on 5 of the last 7 days",
    "3 assignments missed this month"
  ],
  financial: [
    "Tuition fees are 18 days overdue",
    "Available funds are below monthly need",
    "May qualify for the Merit Support Grant"
  ],
  academic: [
    "Marks: 68, 61, 54 across the last three assessments",
    "3 assignments missed this month"
  ]
};

export const SUMMARY = {
  wellbeing: "Sustained low mood alongside falling academic activity. The student asked to be connected and agreed to share this summary.",
  financial: "Overdue fees and limited funds, with likely eligibility for hardship support. The student agreed to share this summary.",
  academic: "Declining marks and missed work over the past month. The student agreed to share this summary."
};

export const SHARE = {
  wellbeing: {
    summary: "Lower mood check-ins for a week, alongside missed coursework.",
    shared: ["Mood check-ins from the last 7 days", "Number of missed assignments"],
    notShared: ["Your finances", "Your marks and attendance", "This chat"]
  },
  financial: {
    summary: "Fees are overdue and available funds look tight.",
    shared: ["Fee status and days overdue", "Scholarship eligibility"],
    notShared: ["Your wellbeing check-ins", "Your marks and attendance", "This chat"]
  },
  academic: {
    summary: "Marks have dipped and a few assignments were missed.",
    shared: ["Marks for the last three assessments", "Number of missed assignments"],
    notShared: ["Your finances", "Your wellbeing check-ins", "This chat"]
  }
};

export const TRACE_TOOLS = ["get_risk_profile", "search_support_kb", "suggest_case", "create_case"];

export function seedCases() {
  const mk = (no, name, domain, score, state, opened) => ({
    no,
    studentId: name.replace("Student ", "S"),
    studentName: name,
    domain,
    dept: DEPT_OF[domain],
    score,
    state,
    opened,
    consentAt: opened,
    evidence: EVIDENCE[domain] || ["Routine signal observation"],
    summary: SUMMARY[domain] || "Automated check-in review.",
    trace: { tools: TRACE_TOOLS, retrieved: 4, authorized: 3, blocked: 1, sent: 3 }
  });

  return [
    mk("WEL0000122", "Student 031", "financial", 66, "In Progress", "Yesterday, 16:20"),
    mk("WEL0000121", "Student 014", "wellbeing", 71, "New", "Today, 08:40"),
    mk("WEL0000119", "Student 009", "academic", 47, "In Progress", "Yesterday, 11:05"),
    mk("WEL0000118", "Student 022", "financial", 58, "New", "Yesterday, 09:32")
  ];
}

let _id = 100;
export const uid = () => "m" + (++_id);
export const nowTime = () => new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

export function lvl(score) {
  if (score >= 70) return { key: "high", staff: "High", student: "Could use support", icon: "heart" };
  if (score >= 40) return { key: "med", staff: "Medium", student: "Worth watching", icon: "eye" };
  return { key: "low", staff: "Low", student: "Doing well", icon: "check" };
}

export const studentStatus = s => ({
  "New": "Received",
  "In Progress": "In progress",
  "Waiting for Student": "Action needed from you",
  "Resolved": "Resolved"
}[s] || s);

export const stepIndex = s => ({
  "New": 0,
  "In Progress": 1,
  "Waiting for Student": 1,
  "Resolved": 2
}[s] ?? 0);

export function getProposal(domain, ctx) {
  const exists = (ctx.cases || []).some(c => c.studentId === ME.id && c.domain === domain) ||
                 (ctx.messages || []).some(m => m.type === "consent" && m.domain === domain && m.status === "pending");
  if (exists) return [];
  return [{
    id: uid(),
    role: "agent",
    type: "consent",
    domain,
    dept: DEPT_OF[domain],
    status: "pending",
    ...SHARE[domain]
  }];
}

export function localRespond(text, ctx) {
  const t = (text || "").toLowerCase();
  const say = o => ({ id: uid(), role: "agent", type: "message", ...o });

  if (/(hurt myself|end it all|suicid|self.?harm|no point|don't want to be here)/.test(t)) {
    return [{ id: uid(), role: "agent", type: "escalation" }];
  }

  if (/(staff|triage|internal|other student|another student|someone else)/.test(t)) {
    return [{ id: uid(), role: "agent", type: "blocked" }];
  }

  if (/\bfees?\b|money|\bpay|scholar|\bfunds?\b|tuition|grant|afford/.test(t)) {
    return [
      say({
        text: "Two things can help right now. You can ask for a short payment plan, and your results may make you eligible for the Merit Support Grant. The Scholarships and Financial Aid team can walk you through both.",
        sources: ["Fee payment support", "Scholarships overview"],
        blocked: 1
      }),
      ...getProposal("financial", ctx)
    ];
  }

  if (/attend|\bclass/.test(t)) {
    return [
      say({
        text: "Your attendance is 91% this term, which is steady. Nothing to worry about there.",
        sources: ["Your attendance record"],
        blocked: 0
      })
    ];
  }

  if (/\b(lot|yes|sad|low)\b|stress|overwhelm|anxious|tired|struggl|talk|hard|feeling/.test(t)) {
    return [
      say({
        text: "That sounds like a lot, and it's good that you said something. Your check-ins have been lower this week and a few assignments have slipped. The Counselling Service offers short first conversations, and there are options for easing your workload too.",
        sources: ["Counselling Service intro", "Academic Support Guide"],
        blocked: 0
      }),
      ...getProposal("wellbeing", ctx)
    ];
  }

  if (/support|option|help|what/.test(t)) {
    return [
      say({
        text: "Here's what's available: academic advising to plan around deadlines, free peer tutoring, and extension requests. An advisor can look at your recent marks with you.",
        sources: ["Academic Support Guide", "Tutoring FAQ"],
        blocked: 1
      }),
      ...getProposal("academic", ctx)
    ];
  }

  return [
    say({
      text: "I can talk through your studies, attendance, fees, or how you're feeling. Which would you like to start with?",
      sources: []
    })
  ];
}

export const firstMessage = () => [
  {
    id: uid(),
    role: "agent",
    type: "message",
    text: "Hi Student 001. I noticed you've missed a few assignments and your check-ins have been low this week. Want to talk about it?"
  }
];
