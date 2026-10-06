const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const defaultHeaders = {
    "Content-Type": "application/json",
  };

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 4000);
  config.signal = controller.signal;

  try {
    const res = await fetch(url, config);
    clearTimeout(timeoutId);
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    clearTimeout(timeoutId);
    throw err;
  }
}

export async function checkBackendHealth() {
  try {
    const res = await request("/health", { method: "GET" });
    return res && res.status === "ok";
  } catch {
    return false;
  }
}

export async function getOverview(userId = "S001") {
  return request("/me/overview", {
    method: "GET",
    headers: { "X-User-Id": userId, "X-Role": "student" },
  });
}

export async function postChat(text, userId = "S001") {
  return request("/chat", {
    method: "POST",
    headers: { "X-User-Id": userId, "X-Role": "student" },
    body: JSON.stringify({ message: text }),
  });
}

export async function createCaseApi(casePayload, userId = "S001") {
  return request("/cases", {
    method: "POST",
    headers: { "X-User-Id": userId, "X-Role": "student" },
    body: JSON.stringify(casePayload),
  });
}

export async function getMyCases(userId = "S001") {
  return request("/me/cases", {
    method: "GET",
    headers: { "X-User-Id": userId, "X-Role": "student" },
  });
}

export async function getStaffCases(role = "counsellor", userId = "counsellor_01") {
  return request("/staff/cases", {
    method: "GET",
    headers: { "X-User-Id": userId, "X-Role": role },
  });
}

export async function getStaffCaseDetail(caseId, role = "counsellor") {
  return request(`/staff/cases/${caseId}`, {
    method: "GET",
    headers: { "X-User-Id": "staff_user", "X-Role": role },
  });
}

export async function patchStaffCaseState(caseId, state, role = "counsellor") {
  return request(`/staff/cases/${caseId}`, {
    method: "PATCH",
    headers: { "X-User-Id": "staff_user", "X-Role": role },
    body: JSON.stringify({ state }),
  });
}

export async function triggerRiskScan(studentId = "S001") {
  return request(`/admin/risk-scan/${studentId}`, {
    method: "POST",
  });
}

export async function getAuditTrace(traceId) {
  return request(`/audit/${traceId}`, {
    method: "GET",
  });
}
