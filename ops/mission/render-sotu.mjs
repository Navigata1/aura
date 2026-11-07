#!/usr/bin/env node
/**
 * render_sotu.mjs — Mission Control State of the Union renderer.
 *
 * Reads state.json (+ journal.md if present) from its own directory and writes
 * state-of-the-union.html next to them. Dependency-free, Node >= 18.
 *
 * Usage:  node ops/mission/render-sotu.mjs [--enhanced]
 * The HTML is GENERATED — never hand-edit it. Change state.json and re-render.
 *
 * Two presentations share one state parser and one set of generated prompts:
 *   standard (default)  the original heartbeat, unchanged.
 *   --enhanced          the Signal build: Signal layout grammar, a theme derived from the
 *                       subject (optional state.theme, else neutral placeholders), a
 *                       dark/light switch, a data-bound "mission orbit" canvas hero,
 *                       charts and tables. Zero external requests.
 *
 * The renderer degrades gracefully on missing fields (it does NOT validate the
 * schema — the model maintaining state.json is the validator) and warns on
 * stderr when it defaults something important. Every state string is untrusted
 * input: it is escaped with esc() for HTML, linked only through safeUrl(),
 * embedded in JSON with `<`, `>`, `&` unicode-escaped, and theme tokens are
 * accepted only as `--name: #hex | rgb[a](...)` pairs.
 */
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const statePath = join(here, "state.json");
const journalPath = join(here, "journal.md");
const outPath = join(here, "state-of-the-union.html");
const enhanced = process.argv.includes("--enhanced");

if (!existsSync(statePath)) {
  console.error(`No state.json found at ${statePath}`);
  process.exit(1);
}

let state;
try {
  // Strip a UTF-8 BOM if present — PowerShell 5.1's `-Encoding utf8` writes one,
  // and JSON.parse rejects it. Windows sessions hit this constantly.
  state = JSON.parse(readFileSync(statePath, "utf8").replace(/^﻿/, ""));
} catch (e) {
  console.error(`state.json is not valid JSON: ${e.message}`);
  process.exit(1);
}

// ---------- helpers ----------
const esc = (s) =>
  String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

// Only http(s) URLs become links; anything else renders as text.
const safeUrl = (u) => (/^https?:\/\//i.test(String(u ?? "")) ? esc(u) : null);

// JSON for an inline <script type="application/json">: no character in the
// payload can close the script element or open a comment.
const jsonForScript = (value) =>
  JSON.stringify(value)
    .replace(/</g, "\\u003c")
    .replace(/>/g, "\\u003e")
    .replace(/&/g, "\\u0026")
    .replace(/\u2028/g, "\\u2028")
    .replace(/\u2029/g, "\\u2029");

const warn = (msg) => console.error(`[render-sotu] warning: ${msg}`);

// Look up a value in a fixed map; untrusted keys (incl. "__proto__") fall back.
const toneOf = (map, key, fallback = "gray") => (Object.hasOwn(map, String(key)) ? map[String(key)] : fallback);

// ---------- state (shared by both presentations) ----------
// state.json is untrusted: a null root, null entries or wrong types must degrade, never crash.
const isObj = (x) => x !== null && typeof x === "object" && !Array.isArray(x);
if (!isObj(state)) {
  warn("state.json root is not an object; rendering an empty mission");
  state = {};
}
const objs = (arr) => (Array.isArray(arr) ? arr.filter(isObj) : []);
const m = isObj(state.mission) ? state.mission : {};
const phases = objs(state.phases);
const metrics = objs(state.metrics);
const risks = objs(state.risks);
const prLog = objs(state.prLog);
const resume = isObj(state.resume) ? state.resume : {};
const policies = isObj(state.policies) ? state.policies : {};
const nextActions = Array.isArray(resume.nextActions) ? resume.nextActions : [];
const blockers = Array.isArray(resume.blockers) ? resume.blockers : [];
const tasksOf = (p) => objs(p.tasks);
const gatesOf = (p) => objs(p.gates);

for (const p of phases) {
  if (!p.status) warn(`phase ${p.id ?? "?"} has no status — defaulting to "pending"`);
}

const allTasks = phases.flatMap(tasksOf);
const doneTasks = allTasks.filter((t) => t.status === "done").length;
const allGates = phases.flatMap(gatesOf);
const passedGates = allGates.filter((g) => g.status === "passed").length;
const pct = allTasks.length ? Math.round((doneTasks / allTasks.length) * 100) : 0;

function journalTail(n = 12) {
  if (!existsSync(journalPath)) return [];
  const entries = readFileSync(journalPath, "utf8")
    .split(/^## /m)
    .filter((s) => s.trim())
    .map((s) => "## " + s.trim());
  return entries.slice(-n).reverse();
}

// ---------- resume prompt generation (identical in both presentations) ----------
function coldStartChecklist() {
  return [
    `Read ops/mission/state.json FIRST — it is the source of truth, not this prompt.`,
    `Verify reality matches state: git log --oneline -5, and re-run the active phase's gate commands.`,
    `Follow the loop: pick next unblocked task -> branch ${policies.branchPrefix ?? "mission/"}<phase>-<slug> -> implement -> run gates -> PR -> merge per policy '${policies.merge ?? "review"}' -> update state.json -> node ops/mission/render-sotu.mjs -> commit state+journal+html.`,
    `Never hand-edit state-of-the-union.html. Never merge without fresh gate evidence in ops/mission/evidence/.`,
    `End of session: update resume.nextActions for a stranger, append journal entry, render, commit.`,
  ];
}

// Sections are null when skipped; empty strings are intentional blank-line spacers.
function joinPrompt(lines) {
  return lines.filter((l) => l !== null).join("\n");
}

function conventionLines() {
  const conv = Array.isArray(resume.conventions) ? resume.conventions : [];
  if (!conv.length) return null;
  return `Mission conventions:\n${conv.map((c) => `  - ${c}`).join("\n")}`;
}

function resumePromptFor(phase) {
  const gatesTodo = gatesOf(phase)
    .filter((g) => g.status !== "passed")
    .map((g) => `  - [${g.status ?? "pending"}] ${g.title ?? g.id ?? "?"}  ->  ${g.command ?? "(no command recorded)"}`);
  const tasksTodo = tasksOf(phase)
    .filter((t) => t.status !== "done")
    .map((t) => `  - [${t.status ?? "pending"}] ${t.id ?? "?"}: ${t.title ?? ""}${t.notes ? ` (${t.notes})` : ""}`);
  const isActive = resume.activePhase === phase.id;
  const next = (isActive ? nextActions : []).map((a) => `  - ${a}`);
  const blocks = (isActive ? blockers : []).map((b) => `  - ${b}`);

  return joinPrompt([
    `You are resuming the "${m.name ?? "mission"}" mission at phase ${phase.id ?? "?"}: ${phase.title ?? ""}.`,
    ``,
    `Mission: ${m.tagline ?? ""}`,
    `North star: ${m.northStar ?? ""}`,
    `Repo: ${m.repo ?? "?"} (local: ${m.repoPath ?? "?"}), default branch: ${m.defaultBranch ?? "main"}.`,
    `Governing plan: ${m.planDoc ?? "?"}`,
    ``,
    `Phase goal: ${phase.goal ?? ""}`,
    tasksTodo.length ? `Remaining tasks:\n${tasksTodo.join("\n")}` : `All tasks in this phase are done.`,
    gatesTodo.length ? `Gates not yet passed:\n${gatesTodo.join("\n")}` : `All gates passed — close the phase and advance.`,
    next.length ? `Next actions (from last session):\n${next.join("\n")}` : null,
    blocks.length ? `Known blockers:\n${blocks.join("\n")}` : null,
    conventionLines(),
    ``,
    `Operating procedure:`,
    ...coldStartChecklist().map((c) => `  ${c}`),
  ]);
}

const globalPrompt = joinPrompt([
  `You are cold-starting the "${m.name ?? "mission"}" mission with zero prior context.`,
  ``,
  `Local repo: ${m.repoPath ?? "?"}  (${m.repo ?? "?"}, default branch ${m.defaultBranch ?? "main"})`,
  `Governing plan: ${m.planDoc ?? "?"}`,
  `Mission status: ${m.status ?? "?"} — active phase: ${resume.activePhase ?? "?"}`,
  ``,
  conventionLines(),
  conventionLines() ? `` : null,
  `Operating procedure:`,
  ...coldStartChecklist().map((c) => `  ${c}`),
]);

/**
 * Metric coloring honors metrics[].direction ("up"|"down" = which way is improvement):
 *   green = target reached; blue = moved toward target; amber = unchanged from baseline;
 *   red = moved AWAY from target (a regression must never look like progress).
 * Non-numeric values fall back to: green at target, amber otherwise.
 */
function metricTone(x) {
  const num = (v) => {
    const n = parseFloat(String(v).replace(/[^0-9.eE+-]/g, ""));
    return Number.isFinite(n) ? n : null;
  };
  const b = num(x.baseline), c = num(x.current), t = num(x.target);
  if (c === null || b === null || t === null) {
    return String(x.current) === String(x.target) ? "green" : "amber";
  }
  if (c === t || (x.direction === "down" && c < t) || (x.direction === "up" && c > t)) return "green";
  if (c === b) return "amber";
  const improving = x.direction === "down" ? c < b : x.direction === "up" ? c > b : Math.abs(c - t) < Math.abs(b - t);
  return improving ? "blue" : "red";
}

// =====================================================================================
// STANDARD presentation: the original heartbeat. Its output must stay byte-identical to
// the pre-Signal renderer for the same state.json (apart from the generated timestamp).
// =====================================================================================
function renderStandard() {
  const phaseTone = { pending: "", in_progress: "amber", blocked: "red", done: "green" };
  const gateTone = { pending: "", passed: "green", failed: "red", waived: "amber" };
  const taskMark = { pending: "&#9675;", in_progress: "&#9689;", blocked: "&#9888;", done: "&#9679;" };
  const sevTone = { high: "red", critical: "red", medium: "amber", low: "blue" };

  const chip = (text, tone = "") => `<span class="chip ${tone}">${esc(text)}</span>`;

  function metricsTable() {
    if (!metrics.length) return "";
    const rows = metrics
      .map(
        (x) =>
          `<tr><td><b>${esc(x.label)}</b></td><td>${esc(x.baseline)}</td><td><span class="chip ${metricTone(x)}">${esc(x.current)}</span></td><td>${esc(x.target)}</td></tr>`
      )
      .join("");
    return `<section aria-labelledby="metrics"><h2 id="metrics">Scoreboard: Baseline &rarr; Current &rarr; Target</h2>
  <div class="table-wrap"><table><thead><tr><th>Metric</th><th>Baseline</th><th>Current</th><th>Target</th></tr></thead><tbody>${rows}</tbody></table></div>
  <p class="small muted" style="margin-top:6px">green = at/past target &middot; blue = moving toward target &middot; amber = unchanged &middot; red = moving away</p></section>`;
  }

  function gateRows(gates) {
    return gates
      .map((g) => {
        const status = g.status ?? "pending";
        const notes = g.notes ? `<br><span class="small">${esc(g.notes)}</span>` : "";
        return `<tr>
      <td><span class="chip ${toneOf(gateTone, status, "")}">${esc(status)}</span></td>
      <td><b>${esc(g.title ?? g.id ?? "?")}</b>${notes}</td>
      <td>${g.command ? `<code>${esc(g.command)}</code>` : "&mdash;"}</td>
      <td>${g.evidence ? esc(g.evidence) : "&mdash;"}</td>
      <td>${g.lastRun ? esc(g.lastRun) : "&mdash;"}</td></tr>`;
      })
      .join("");
  }

  function taskList(tasks) {
    return tasks
      .map((t) => {
        const status = t.status ?? "pending";
        const url = safeUrl(t.pr?.url);
        const prLabel = t.pr?.number != null ? `PR #${esc(t.pr.number)}` : null;
        const pr = prLabel
          ? ` &mdash; ${url ? `<a href="${url}">${prLabel}</a>` : prLabel}${t.pr.mergedAt ? ` merged ${esc(t.pr.mergedAt)}` : ""}`
          : "";
        return `<li class="task-${esc(status)}"><span class="mark">${toneOf(taskMark, status, "&#9675;")}</span> <b>${esc(t.id ?? "?")}</b> ${esc(t.title ?? "")}${pr}${t.notes ? `<br><span class="muted small">${esc(t.notes)}</span>` : ""}</li>`;
      })
      .join("");
  }

  function phaseCards() {
    return phases
      .map((p) => {
        const status = p.status ?? "pending";
        const tasks = tasksOf(p);
        const gates = gatesOf(p);
        const done = tasks.filter((t) => t.status === "done").length;
        const ppct = tasks.length ? Math.round((done / tasks.length) * 100) : status === "done" ? 100 : 0;
        const active = resume.activePhase === p.id ? " active" : "";
        return `<article class="phase${active}">
      <header>
        <span class="chip ${toneOf(phaseTone, status, "")}">${esc(String(status).replace("_", " "))}</span>
        <h3>${esc(p.id ?? "?")} &middot; ${esc(p.title ?? "")}</h3>
        ${p.sessionsEstimate ? `<span class="muted small">est. sessions: ${esc(p.sessionsEstimate)}</span>` : ""}
      </header>
      <p class="muted">${esc(p.goal ?? "")}</p>
      <div class="bar"><div class="fill" style="width:${ppct}%"></div></div>
      <p class="small muted">${done}/${tasks.length} tasks &middot; ${ppct}%</p>
      ${tasks.length ? `<ul class="tasks">${taskList(tasks)}</ul>` : ""}
      ${gates.length ? `<div class="table-wrap"><table><thead><tr><th>Gate</th><th>Check</th><th>Command</th><th>Evidence</th><th>Last run</th></tr></thead><tbody>${gateRows(gates)}</tbody></table></div>` : ""}
      <details class="resume"><summary>Resume prompt for ${esc(p.id ?? "?")} (copy into a fresh session)</summary>
        <div class="prompt-box"><button class="copy" type="button">Copy</button><pre>${esc(resumePromptFor(p))}</pre></div>
      </details>
    </article>`;
      })
      .join("");
  }

  function risksPanel() {
    const blockerItems = blockers.map((b) => `<li><span class="chip red">blocker</span> ${esc(b)}</li>`).join("");
    const riskItems = risks
      .map((r) => `<li><span class="chip ${toneOf(sevTone, r.severity, "")}">${esc(r.severity ?? "?")}</span> <b>${esc(r.title)}</b>${r.note ? ` &mdash; <span class="muted">${esc(r.note)}</span>` : ""}</li>`)
      .join("");
    if (!blockerItems && !riskItems) return "";
    return `<section aria-labelledby="risks"><h2 id="risks">Risks &amp; Blockers</h2><div class="panel"><ul class="bare">${blockerItems}${riskItems}</ul></div></section>`;
  }

  function prTimeline() {
    if (!prLog.length) return "";
    const rows = [...prLog]
      .reverse()
      .map((p) => {
        const url = safeUrl(p.url);
        return `<article class="tl-item"><time>#${esc(p.number ?? "?")}</time><p><b>${esc(p.title ?? "")}</b> &mdash; ${esc(p.phase ?? "?")}${p.mergedAt ? `, merged ${esc(p.mergedAt)}` : ""} ${url ? `&middot; <a href="${url}">view</a>` : ""}</p></article>`;
      })
      .join("");
    return `<section aria-labelledby="prs"><h2 id="prs">Merged Work (${prLog.length} PRs)</h2><div class="timeline">${rows}</div></section>`;
  }

  function journalSection() {
    const tail = journalTail();
    if (!tail.length) return "";
    const items = tail
      .map((e) => {
        const [head, ...rest] = e.replace(/^## /, "").split("\n");
        return `<article class="tl-item"><time>&#9998;</time><p><b>${esc(head)}</b><br>${rest.map((l) => esc(l)).join("<br>")}</p></article>`;
      })
      .join("");
    return `<section aria-labelledby="journal"><h2 id="journal">Journal (latest first)</h2><div class="timeline">${items}</div></section>`;
  }

  const statusTone = m.status === "complete" ? "green" : m.status === "paused" ? "amber" : "blue";
  const gatesChipTone = !allGates.length ? "" : passedGates === allGates.length ? "green" : "amber";

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(m.name ?? "Mission")} — State of the Union</title>
<style>
:root{color-scheme:dark;--bg:#070f1c;--paper:#0d1b2f;--paper-2:#10243b;--ink:#eef6ff;--muted:#a9bdd3;--line:rgba(169,189,211,.18);--accent:#58d7b3;--blue:#77b7ff;--amber:#ffd166;--red:#ff8f8f;--good:#8ef2c0}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(circle at top left,rgba(88,215,179,.15),transparent 30rem),radial-gradient(circle at top right,rgba(119,183,255,.13),transparent 32rem),var(--bg);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,"Segoe UI",sans-serif;line-height:1.55}
main{width:min(1180px,calc(100% - 32px));margin:0 auto;padding:40px 0 60px}
h1,h2,h3{margin:0;line-height:1.12}
h1{font-size:clamp(2rem,5vw,3.8rem);letter-spacing:-.04em;max-width:900px;margin-top:10px}
h2{margin-bottom:14px;font-size:clamp(1.4rem,2.6vw,2rem)}
h3{font-size:1.02rem;color:#fff}
p{margin:0}
a{color:var(--blue)}
code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.85em;color:#dff7ef;overflow-wrap:anywhere}
.eyebrow{color:var(--accent);font-size:.78rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase}
.muted{color:var(--muted)}
.small{font-size:.85rem}
section{padding-top:34px}
.hero{padding:20px 0 26px;border-bottom:1px solid var(--line)}
.hero .tagline{max-width:760px;margin-top:14px;color:var(--muted);font-size:1.06rem}
.chip{display:inline-flex;align-items:center;border:1px solid var(--line);border-radius:999px;padding:3px 10px;margin:2px 6px 2px 0;background:rgba(255,255,255,.05);color:var(--muted);font-size:.78rem;font-weight:800}
.chip.green{color:var(--good);border-color:rgba(142,242,192,.4)}
.chip.amber{color:var(--amber);border-color:rgba(255,209,102,.4)}
.chip.red{color:var(--red);border-color:rgba(255,143,143,.4)}
.chip.blue{color:var(--blue);border-color:rgba(119,183,255,.4)}
.panel,.phase{border:1px solid var(--line);border-radius:16px;background:linear-gradient(180deg,rgba(16,36,59,.95),rgba(13,27,47,.95));box-shadow:0 18px 46px rgba(0,0,0,.25);padding:20px}
.phase{margin-top:14px}
.phase.active{border-color:rgba(88,215,179,.45)}
.phase header{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-bottom:8px}
.bar{height:10px;border-radius:999px;background:rgba(255,255,255,.07);margin-top:12px;overflow:hidden}
.bar .fill{height:100%;border-radius:999px;background:linear-gradient(90deg,var(--accent),var(--blue))}
.bar.big{height:16px}
ul.tasks,ul.bare{list-style:none;margin:12px 0 0;padding:0}
ul.tasks li,ul.bare li{padding:8px 0;border-top:1px solid var(--line);color:var(--muted)}
ul.tasks li:first-child,ul.bare li:first-child{border-top:0}
ul.tasks .mark{margin-right:6px;color:var(--accent)}
li.task-done{opacity:.75}
li.task-blocked .mark{color:var(--red)}
table{width:100%;border-collapse:collapse;margin-top:12px;font-size:.9rem}
th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
th{background:rgba(255,255,255,.05);color:#fff;font-size:.76rem;letter-spacing:.06em;text-transform:uppercase}
td{color:var(--muted)}
td b{color:#fff}
.table-wrap{overflow-x:auto;border-radius:12px}
.timeline{display:grid;gap:10px}
.tl-item{display:grid;grid-template-columns:72px 1fr;gap:14px;border:1px solid var(--line);border-radius:12px;padding:12px 14px;background:rgba(255,255,255,.035)}
.tl-item time{color:var(--accent);font-size:.8rem;font-weight:900}
.tl-item p{color:var(--muted)}
details.resume{margin-top:14px;border:1px dashed rgba(88,215,179,.4);border-radius:12px;padding:10px 14px}
details.resume summary{cursor:pointer;color:var(--accent);font-weight:800}
.prompt-box{position:relative;margin-top:10px}
.prompt-box pre{margin:0;border:1px solid var(--line);border-radius:10px;background:#081120;color:#dff7ef;padding:14px;font-size:.82rem;white-space:pre-wrap;overflow-wrap:anywhere;max-height:420px;overflow:auto}
button.copy{position:absolute;top:8px;right:8px;border:1px solid var(--line);border-radius:8px;background:rgba(255,255,255,.08);color:var(--ink);font-weight:700;padding:4px 12px;cursor:pointer}
button.copy:hover{background:rgba(88,215,179,.2)}
.footer{margin-top:40px;border-top:1px solid var(--line);padding-top:16px;color:var(--muted);font-size:.9rem}
@media(max-width:900px){main{width:min(100% - 24px,760px)}.tl-item{grid-template-columns:56px 1fr}}

</style>
</head>
<body>

<main>
  <header class="hero">
    <p class="eyebrow">Mission Control &middot; State of the Union &middot; generated ${esc(new Date().toISOString().slice(0, 16).replace("T", " "))}Z</p>
    <h1>${esc(m.name ?? "Mission")}</h1>
    <p class="tagline">${esc(m.tagline ?? "")}</p>
    <div style="margin-top:14px">
      ${chip(`mission: ${m.status ?? "?"}`, statusTone)}
      ${chip(`active phase: ${resume.activePhase ?? "?"}`, "green")}
      ${chip(`${doneTasks}/${allTasks.length} tasks`, "blue")}
      ${chip(`${passedGates}/${allGates.length} gates passed`, gatesChipTone)}
      ${chip(`${prLog.length} PRs merged`)}
      ${chip(`sessions: ${m.sessionCount ?? 1}`)}
      ${chip(`updated: ${m.updated ?? "?"}`)}
    </div>
    <div class="bar big" role="img" aria-label="Overall progress ${pct}%"><div class="fill" style="width:${pct}%"></div></div>
    <p class="small muted" style="margin-top:6px">Overall: ${pct}% of tasks complete &middot; repo ${esc(m.repo ?? "?")} &middot; plan: ${esc(m.planDoc ?? "?")}</p>
  </header>

  <section aria-labelledby="coldstart">
    <h2 id="coldstart">Cold-Start Prompt (any new session, zero context)</h2>
    <div class="panel">
      <div class="prompt-box"><button class="copy" type="button">Copy</button><pre>${esc(globalPrompt)}</pre></div>
    </div>
  </section>

  ${metricsTable()}
  ${risksPanel()}

  <section aria-labelledby="phases">
    <h2 id="phases">Phases</h2>
    ${phaseCards()}
  </section>

  ${prTimeline()}
  ${journalSection()}

  <p class="footer">GENERATED by ops/mission/render-sotu.mjs from state.json — do not hand-edit.
  To update: edit state.json, run <code>node ops/mission/render-sotu.mjs</code>, commit both.</p>
</main>
<script>
document.querySelectorAll("button.copy").forEach((b) => {
  b.addEventListener("click", async () => {
    const text = b.parentElement.querySelector("pre").innerText;
    try { await navigator.clipboard.writeText(text); b.textContent = "Copied!"; }
    catch { const r = document.createRange(); r.selectNodeContents(b.parentElement.querySelector("pre")); const s = getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent = "Select+Ctrl C"; }
    setTimeout(() => (b.textContent = "Copy"), 1600);
  });
});
</script>

</body>
</html>
`;
}

// =====================================================================================
// ENHANCED presentation: the Signal build with a theme derived from the subject.
// =====================================================================================

// Neutral placeholder tokens (copied from flagship-report's enhanced-report-shell.html).
// They are only the fallback: a real heartbeat carries a derived theme in state.theme.
const NEUTRAL_TOKENS = {
  dark: {
    "--bg": "#0d0d10", "--panel": "#141418", "--panel-2": "#1a1a1f",
    "--border": "rgba(236,235,232,.09)", "--border-soft": "rgba(236,235,232,.055)", "--grid": "rgba(236,235,232,.03)", "--tick": "rgba(236,235,232,.2)",
    "--text": "#ecebe8", "--muted": "#a6a5ae", "--dim": "#8a8994",
    "--a1": "#8fb3ff", "--a2": "#c4a7ff",
    "--good": "#20ad7a", "--warn": "#e2a20b", "--bad": "#ee4d6f", "--info": "#67c1f5",
    "--neutral": "#6b6f7b", "--cell-off": "#2c2f38", "--dot-off": "#3a3d4a",
    "--hue-1": "#3987e5", "--hue-2": "#d95926", "--hue-3": "#199e70", "--hue-4": "#c98500", "--hue-5": "#d55181", "--hue-6": "#008300", "--hue-7": "#9085e9",
    "--tip-bg": "#1a1a1f", "--shadow": "rgba(0,0,0,.45)",
  },
  light: {
    "--bg": "#f7f6f3", "--panel": "#ffffff", "--panel-2": "#efeee9",
    "--border": "rgba(20,20,24,.11)", "--border-soft": "rgba(20,20,24,.07)", "--grid": "rgba(20,20,24,.04)", "--tick": "rgba(20,20,24,.25)",
    "--text": "#151517", "--muted": "#47474f", "--dim": "#5e5e68",
    "--a1": "#2459c8", "--a2": "#6a3fd6",
    "--good": "#0f8a5f", "--warn": "#b47d00", "--bad": "#981c3b", "--info": "#1f6fa8",
    "--neutral": "#868892", "--cell-off": "#dcdbd5", "--dot-off": "#cfcec8",
    "--hue-1": "#2a78d6", "--hue-2": "#eb6834", "--hue-3": "#1baf7a", "--hue-4": "#eda100", "--hue-5": "#e87ba4", "--hue-6": "#008300", "--hue-7": "#4a3aa7",
    "--tip-bg": "#ffffff", "--shadow": "rgba(30,35,50,.14)",
  },
};
const MODES = ["dark", "light"];
// A token key is a lowercase custom property; a value is a hex or rgb()/rgba() color. Nothing
// else is accepted, so no theme value can carry `;`, `{`, `}`, `<`, `>`, url() or expressions.
const TOKEN_KEY = /^--[a-z0-9-]{1,40}$/;
const TOKEN_HEX = /^#(?:[0-9a-f]{3}|[0-9a-f]{4}|[0-9a-f]{6}|[0-9a-f]{8})$/i;
const TOKEN_HEX_OPAQUE = /^#(?:[0-9a-f]{3}|[0-9a-f]{6})$/i;
const TOKEN_RGB = /^rgba?\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*(?:,\s*(?:0|1|0?\.\d{1,4}|1\.0{1,4})\s*)?\)$/i;
const RESERVED_TOKENS = new Set(["--mono", "--sans", "--display", "--ease"]);
// The Signal gate computes contrast from these slots, so they must be opaque #rgb/#rrggbb.
const HEX_ONLY_TOKENS = new Set(["--bg", "--panel", "--text", "--muted", "--dim", "--a1", "--good", "--warn", "--bad"]);
const MAX_THEME_TOKENS = 64;
const MAX_THEME_SOURCES = 20;
const THEME_TEXT_MAX = 600;

const themeText = (v) => (typeof v === "string" ? v.trim().slice(0, THEME_TEXT_MAX) : "");

function cleanTokens(raw, mode) {
  if (raw === undefined) return {};
  if (!isObj(raw)) {
    warn(`state.theme.${mode} is not an object of tokens; using the neutral ${mode} set`);
    return {};
  }
  const out = {};
  for (const [key, value] of Object.entries(raw).slice(0, MAX_THEME_TOKENS)) {
    const v = typeof value === "string" ? value.trim() : "";
    if (!TOKEN_KEY.test(key) || RESERVED_TOKENS.has(key)) {
      warn(`state.theme.${mode}: rejected token key ${JSON.stringify(key).slice(0, 60)} (want --lowercase-name, not a font/ease slot)`);
    } else if (HEX_ONLY_TOKENS.has(key) ? !TOKEN_HEX_OPAQUE.test(v) : !TOKEN_HEX.test(v) && !TOKEN_RGB.test(v)) {
      warn(`state.theme.${mode}: rejected value for ${key} ${JSON.stringify(value).slice(0, 60)} (want ${HEX_ONLY_TOKENS.has(key) ? "#rgb or #rrggbb: contrast is computed from it" : "#hex or rgb()/rgba()"})`);
    } else {
      out[key] = v;
    }
  }
  return out;
}

function readTheme(raw) {
  const derived = isObj(raw);
  if (!derived) {
    warn(
      raw === undefined || raw === null
        ? "state.theme is absent: rendering neutral placeholder tokens. Derive a theme from the subject with flagship-report's theme forge (references/theme-forge.md) and record it in state.theme."
        : "state.theme is not an object: rendering neutral placeholder tokens. Derive one with flagship-report's theme forge (references/theme-forge.md)."
    );
  }
  const t = derived ? raw : {};
  let defaultMode = "dark";
  if (MODES.includes(t.defaultMode)) defaultMode = t.defaultMode;
  else if (derived && t.defaultMode !== undefined) warn(`state.theme.defaultMode must be "dark" or "light"; using "dark"`);
  const tokens = {};
  for (const mode of MODES) tokens[mode] = { ...NEUTRAL_TOKENS[mode], ...cleanTokens(t[mode], mode) };
  const personality = {};
  if (isObj(t.personality)) {
    for (const axis of ["warm_cool", "quiet_loud", "organic_engineered", "luminous_grounded"]) {
      const n = Number(t.personality[axis]);
      if (Number.isFinite(n)) personality[axis] = Math.max(0, Math.min(1, n));
    }
  }
  const sources = objs(t.sources)
    .slice(0, MAX_THEME_SOURCES)
    .map((s) => ({ kind: themeText(s.kind), ref: themeText(s.ref), note: themeText(s.note) }))
    .filter((s) => s.ref || s.note);
  const name = themeText(t.name) || (derived ? "Unnamed derived theme" : "Neutral placeholder (no theme derived)");
  return {
    derived,
    name,
    ethos: themeText(t.ethos),
    defaultMode,
    modeReason: themeText(t.modeReason),
    personality,
    sources,
    tokens,
    paletteId: name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 48) || "neutral",
  };
}

function renderEnhanced() {
  const theme = readTheme(state.theme);
  if (!m.name) warn(`mission.name is missing — defaulting to "Mission"`);

  const PHASE_STATUSES = ["pending", "in_progress", "blocked", "done"];
  const GATE_STATUSES = ["pending", "passed", "failed", "waived"];
  const phaseStatus = (s) => (PHASE_STATUSES.includes(s) ? s : "pending");
  const gateStatus = (s) => (GATE_STATUSES.includes(s) ? s : "pending");

  const evidencedGates = allGates.filter((g) => g.evidence).length;
  const donePhases = phases.filter((p) => phaseStatus(p.status) === "done").length;
  const missionName = m.name ?? m.tagline ?? "Mission";

  // Active phase: resume.activePhase, else first in_progress, else first unfinished.
  // A finished mission has no active node; the orbit's landing marker takes the flow.
  const allPhasesDone = phases.length > 0 && donePhases === phases.length;
  let activeIdx = phases.findIndex((p) => resume.activePhase != null && p.id === resume.activePhase);
  if (resume.activePhase != null && activeIdx < 0 && phases.length) {
    warn(`resume.activePhase "${resume.activePhase}" matches no phase id — highlighting the first unfinished phase`);
  }
  if (activeIdx < 0) activeIdx = phases.findIndex((p) => phaseStatus(p.status) === "in_progress");
  if (activeIdx < 0) activeIdx = phases.findIndex((p) => phaseStatus(p.status) !== "done");
  if (allPhasesDone || m.status === "complete") activeIdx = -1;
  const activeLabel = resume.activePhase ?? (activeIdx >= 0 ? phases[activeIdx].id : null) ?? "none";

  const phasePill = { pending: "gray", in_progress: "info", blocked: "bad", done: "ok" };
  const gatePill = { pending: "gray", passed: "ok", failed: "bad", waived: "warn" };
  const gateExit = { pending: "pending", passed: "", failed: "bad", waived: "warn" };
  const gateMark = { pending: "&#9675;", passed: "&#10003;", failed: "&#10007;", waived: "~" };
  const sevPill = { critical: "bad", high: "bad", medium: "warn", med: "warn", low: "info" };
  const metricPill = { green: "ok", blue: "info", amber: "warn", red: "bad" };
  const sourceKind = { repo: "Build folder", reference: "Reference", external: "External", subject: "Subject", validation: "Validation" };

  const pill = (text, tone = "gray") => `<span class="pill ${tone}">${esc(text)}</span>`;

  /** A stat value whose markup already holds the true value; JS only replays it. */
  function countValue(value) {
    const s = String(value ?? "");
    const parts = s.match(/^(\D*?)(-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d+))?)([\s\S]*)$/);
    if (!parts) return esc(s || "—");
    const [, prefix, number, decimals = "", suffix] = parts;
    const grouped = number.includes(",") ? ` data-group="1"` : "";
    return `<span class="count" data-target="${esc(number.replace(/,/g, ""))}" data-decimals="${decimals.length}"${grouped} data-prefix="${esc(prefix)}" data-suffix="${esc(suffix)}">${esc(s)}</span>`;
  }

  function stat(value, label, tone = "", sub = "") {
    return `<div class="stat reveal"><div class="val${tone ? ` ${tone}` : ""}">${countValue(value)}</div><div class="lbl">${label}</div>${sub ? `<div class="sub">${sub}</div>` : ""}</div>`;
  }

  /**
   * Signal bar chart. Callers pass already-escaped label/val/tip strings; v is a
   * percentage of the axis and is clamped to 0-100 so a bar can never leave its track.
   */
  function barChart(id, title, sub, rows, axis) {
    const clamp = (x) => Math.max(0, Math.min(100, Number.isFinite(x) ? x : 0));
    const bars = rows
      .map((r) => {
        const v = clamp(r.v).toFixed(1);
        return `<span class="bar-lbl" title="${r.tip}">${r.label}</span><div class="bar-track"><span class="bar${r.neutral ? " neutral" : ""}" style="--v:${v}%" tabindex="0" data-tip="${r.tip}"></span><span class="bar-val${Number(v) > 85 ? " in" : ""}" style="--v:${v}%">${r.val}</span></div>`;
      })
      .join("");
    return `<div class="chart reveal" role="figure" aria-labelledby="${id}">
      <div class="chart-title" id="${id}">${title}</div>
      <div class="chart-sub">${sub}</div>
      <div class="bars" style="--ticks:${axis.length - 1}">${bars}</div>
      <div class="axis"><span></span><div class="axis-ticks">${axis.map((a) => `<span>${a}</span>`).join("")}</div></div>
    </div>`;
  }

  const numOf = (v) => {
    const x = parseFloat(String(v ?? "").replace(/[^0-9.eE+-]/g, ""));
    return Number.isFinite(x) ? x : null;
  };

  function terminal(title, text) {
    return `<div class="terminal">
      <div class="term-bar"><span class="dot"></span><span class="dot"></span><span class="dot"></span><span class="ttl">${title}</span><button class="copy" type="button">COPY</button></div>
<pre>${esc(text)}</pre>
    </div>`;
  }

  function sectionShell(id, num, title, lede, body) {
    return `<section id="${id}" aria-labelledby="h-${id}">
  <div class="wrap">
    <div class="sec-num reveal">SECTION ${num}</div>
    <h2 class="reveal" id="h-${id}">${title}</h2>
    ${lede ? `<p class="sec-lede reveal">${lede}</p>` : ""}
    ${body}
  </div>
</section>`;
  }

  function overviewSection() {
    const lede = [
      m.northStar ? `<b>North star:</b> ${esc(m.northStar)}` : null,
      `Repo <code>${esc(m.repo ?? "?")}</code> on <code>${esc(m.defaultBranch ?? "main")}</code> &middot; plan <code>${esc(m.planDoc ?? "?")}</code> &middot; merge policy <code>${esc(policies.merge ?? "review")}</code>.`,
    ].filter(Boolean).join("<br>");
    const next = nextActions.length
      ? `<ol class="next">${nextActions.map((a) => `<li>${esc(a)}</li>`).join("")}</ol>`
      : `<p class="note">No next actions recorded in resume.nextActions.</p>`;
    const phaseRows = phases.map((p) => {
      const tasks = tasksOf(p);
      const done = tasks.filter((t) => t.status === "done").length;
      const gates = gatesOf(p);
      const gp = gates.filter((g) => g.status === "passed").length;
      const frac = tasks.length ? done / tasks.length : phaseStatus(p.status) === "done" ? 1 : 0;
      return { label: esc(p.id ?? "?"), v: frac * 100, val: `${done}/${tasks.length}`, tip: esc(`${p.id ?? "?"} · ${p.title ?? ""} · ${done}/${tasks.length} tasks · ${gp}/${gates.length} gates passed`) };
    });
    const phaseChart = phases.length
      ? barChart("ct-phases", "Task completion by phase", "PERCENT OF TASKS DONE &middot; FROM STATE.JSON", phaseRows, ["0%", "20%", "40%", "60%", "80%", "100%"])
      : "";
    const body = `<div class="stat-row">
      ${stat(`${pct}%`, "of all tasks complete")}
      ${stat(`${doneTasks}/${allTasks.length}`, "tasks done")}
      ${stat(`${passedGates}/${allGates.length}`, "gates passed", allGates.length && passedGates === allGates.length ? "ok" : "")}
      ${stat(`${donePhases}/${phases.length}`, "phases closed")}
      ${stat(prLog.length, "PRs merged")}
      ${stat(blockers.length, "open blockers", blockers.length ? "bad" : "ok")}
    </div>
    ${phaseChart}
    <div class="verdict-banner reveal">
      <p><b>Active phase ${esc(activeLabel)}.</b> Next actions for a cold start:</p>
      ${next}
      <div class="meter big" role="img" aria-label="Overall progress ${pct}%"><span style="width:${pct}%"></span></div>
      <div class="meter-lbl">OVERALL ${pct}% &middot; ${doneTasks}/${allTasks.length} TASKS &middot; MISSION ${esc(m.status ?? "?")}</div>
    </div>`;
    return { id: "status", nav: "Status", render: (n) => sectionShell("status", n, `Status: <span class="accent">${pct}% of tasks complete.</span>`, lede, body) };
  }

  function coldStartSection() {
    const body = `<div class="reveal">${terminal("cold-start prompt &middot; paste into any new session", globalPrompt)}</div>`;
    return {
      id: "coldstart",
      nav: "Cold start",
      render: (n) => sectionShell("coldstart", n, `Cold-Start Prompt: <span class="accent">any new session, zero context.</span>`, `Generated from state.json on every render. It is exactly as fresh as the last heartbeat commit.`, body),
    };
  }

  function metricsSection() {
    if (!metrics.length) return null;
    const cards = metrics
      .slice(0, 6)
      .map((x) => stat(x.current, esc(x.label), toneOf(metricPill, metricTone(x)), `BASE ${esc(x.baseline)} &rarr; TARGET ${esc(x.target)}`))
      .join("");
    const rows = metrics
      .map((x) => {
        const tone = metricTone(x);
        return `<tr><td>${esc(x.label)}</td><td>${esc(x.baseline)}</td><td>${pill(x.current, toneOf(metricPill, tone))}</td><td>${esc(x.target)}</td><td class="mono">${x.direction === "down" ? "&darr; lower" : x.direction === "up" ? "&uarr; higher" : "&mdash;"}</td></tr>`;
      })
      .join("");
    const progressRows = metrics
      .map((x) => {
        const b = numOf(x.baseline), c = numOf(x.current), t = numOf(x.target);
        if (b === null || c === null || t === null || b === t) return null;
        const frac = (b - c) / (b - t);
        return { label: esc(x.label), v: frac * 100, val: esc(x.current), neutral: frac <= 0, tip: esc(`${x.label} · baseline ${x.baseline} → current ${x.current} → target ${x.target}`) };
      })
      .filter(Boolean);
    const progressChart = progressRows.length
      ? barChart("ct-metrics", "Progress to target", "SHARE OF THE BASELINE &rarr; TARGET GAP CLOSED &middot; NEUTRAL = NO PROGRESS OR REGRESSION", progressRows, ["0%", "25%", "50%", "75%", "100%"])
      : "";
    const body = `<div class="stat-row">${cards}</div>
    ${progressChart}
    <div class="tbl-wrap reveal"><table><thead><tr><th style="width:36%">Metric</th><th>Baseline</th><th>Current</th><th>Target</th><th>Better</th></tr></thead><tbody>${rows}</tbody></table></div>
    <p class="note reveal">ok = at/past target &middot; info = moving toward target &middot; warn = unchanged &middot; bad = moving away</p>`;
    return { id: "scoreboard", nav: "Scoreboard", render: (n) => sectionShell("scoreboard", n, `Scoreboard: <span class="accent">baseline &rarr; current &rarr; target.</span>`, "", body) };
  }

  function risksSection() {
    if (!blockers.length && !risks.length) return null;
    const blockerRows = blockers.map((b) => `<tr><td>${esc(b)}</td><td>${pill("BLOCKER", "bad")}</td><td>Open blocker from resume.blockers.</td></tr>`).join("");
    const riskRows = risks
      .map((r) => `<tr><td>${esc(r.title)}</td><td>${pill(String(r.severity ?? "?").toUpperCase(), toneOf(sevPill, String(r.severity ?? "").toLowerCase()))}</td><td>${r.note ? esc(r.note) : "&mdash;"}</td></tr>`)
      .join("");
    const body = `<div class="tbl-wrap reveal"><table><thead><tr><th style="width:38%">Risk or blocker</th><th style="width:14%">Severity</th><th>Note</th></tr></thead><tbody>${blockerRows}${riskRows}</tbody></table></div>`;
    return {
      id: "risks",
      nav: "Risks",
      render: (n) => sectionShell("risks", n, `Risks &amp; <span class="accent">blockers.</span>`, `${blockers.length} open blocker${blockers.length === 1 ? "" : "s"} &middot; ${risks.length} tracked risk${risks.length === 1 ? "" : "s"}.`, body),
    };
  }

  function exitChip(g) {
    const st = gateStatus(g.status);
    return `<span class="exit-chip ${gateExit[st]}"><b>EXIT ${gateMark[st]}</b>${esc(g.title ?? g.id ?? "?")}</span>`;
  }

  function gateTable(gates) {
    const rows = gates
      .map((g) => {
        const st = gateStatus(g.status);
        const notes = g.notes ? `<span class="why">${esc(g.notes)}</span>` : "";
        return `<tr><td>${esc(g.title ?? g.id ?? "?")}${notes}</td><td>${pill(g.status ?? "pending", gatePill[st])}</td><td>${g.command ? `<code>${esc(g.command)}</code>` : "&mdash;"}</td><td>${g.evidence ? `<code>${esc(g.evidence)}</code>` : "&mdash;"}</td><td class="mono">${g.lastRun ? esc(g.lastRun) : "&mdash;"}</td></tr>`;
      })
      .join("");
    return `<div class="tbl-wrap"><table><thead><tr><th style="width:28%">Gate</th><th>Status</th><th>Command</th><th>Evidence</th><th>Last run</th></tr></thead><tbody>${rows}</tbody></table></div>`;
  }

  function taskList(tasks) {
    return tasks
      .map((t) => {
        const st = phaseStatus(t.status);
        const url = safeUrl(t.pr?.url);
        const prLabel = t.pr?.number != null ? `PR #${esc(t.pr.number)}` : null;
        const pr = prLabel
          ? `<span class="tpr">${url ? `<a href="${url}">${prLabel}</a>` : prLabel}${t.pr.mergedAt ? ` &middot; merged ${esc(t.pr.mergedAt)}` : ""}</span>`
          : "";
        return `<li class="task-${st}">${pill(String(t.status ?? "pending").replace("_", " "), phasePill[st])}<span class="tid">${esc(t.id ?? "?")}</span><span class="tt">${esc(t.title ?? "")}</span>${pr}${t.notes ? `<span class="tnote">${esc(t.notes)}</span>` : ""}</li>`;
      })
      .join("");
  }

  function phaseItem(p, i) {
    const st = phaseStatus(p.status);
    const tasks = tasksOf(p);
    const gates = gatesOf(p);
    const done = tasks.filter((t) => t.status === "done").length;
    const passed = gates.filter((g) => g.status === "passed").length;
    const ppct = tasks.length ? Math.round((done / tasks.length) * 100) : st === "done" ? 100 : 0;
    const active = i === activeIdx;
    const est = p.sessionsEstimate ? ` &middot; est. ${esc(p.sessionsEstimate)} sessions` : "";
    return `<div class="phase reveal st-${st}${active ? " active" : ""}" id="phase-${i}">
        <div class="ph">${esc(p.id ?? "?")}${est}</div>
        <h4>${esc(p.title ?? "")} ${pill(String(p.status ?? "pending").replace("_", " "), phasePill[st])}${active ? ` <span class="pill live">ACTIVE</span>` : ""}</h4>
        ${p.goal ? `<p>${esc(p.goal)}</p>` : ""}
        <div class="meter" role="img" aria-label="${esc(p.id ?? "phase")} ${ppct}% of tasks complete"><span style="width:${ppct}%"></span></div>
        <div class="meter-lbl">${done}/${tasks.length} TASKS &middot; ${ppct}% &middot; ${passed}/${gates.length} GATES PASSED</div>
        ${gates.length ? `<div class="exits">${gates.map(exitChip).join("")}</div>` : ""}
        <details class="phase-detail"${st === "done" ? "" : " open"}>
          <summary>Tasks, gates &amp; resume prompt</summary>
          ${tasks.length ? `<ul class="task-list">${taskList(tasks)}</ul>` : `<p class="note">No tasks recorded.</p>`}
          ${gates.length ? gateTable(gates) : ""}
          <details class="resume"><summary>Resume prompt for ${esc(p.id ?? "?")} (copy into a fresh session)</summary>
            ${terminal(`resume &middot; ${esc(p.id ?? "?")}`, resumePromptFor(p))}
          </details>
        </details>
      </div>`;
  }

  function phasesSection() {
    const fill = phases.length ? (activeIdx >= 0 ? (activeIdx + 1) / phases.length : 1) : 0;
    const body = phases.length
      ? `<div class="v-timeline" style="--fill:${fill.toFixed(3)}"><span class="v-fill"></span>${phases.map(phaseItem).join("")}</div>`
      : `<p class="callout reveal">No phases recorded in state.json.</p>`;
    return {
      id: "phases",
      nav: "Phases",
      render: (n) => sectionShell("phases", n, `Phases: <span class="accent">${donePhases} of ${phases.length} closed.</span>`, `Exit chips are the phase gates. A phase closes only when every gate passes with fresh evidence from the current default branch.`, body),
    };
  }

  function prSection() {
    if (!prLog.length) return null;
    const items = [...prLog]
      .reverse()
      .map((p) => {
        const url = safeUrl(p.url);
        return `<li class="tl-item"><div class="tl-k">#${esc(p.number ?? "?")}</div><h4>${esc(p.title ?? "")}</h4><div class="tl-meta">${pill(p.phase ?? "?", "gray")}${p.mergedAt ? `<span>merged ${esc(p.mergedAt)}</span>` : ""}${url ? `<a href="${url}">view &#8599;</a>` : ""}</div></li>`;
      })
      .join("");
    return {
      id: "prs",
      nav: "Merged",
      render: (n) => sectionShell("prs", n, `Merged work: <span class="accent">${prLog.length} PR${prLog.length === 1 ? "" : "s"}.</span>`, "", `<ol class="tl reveal">${items}</ol>`),
    };
  }

  function journalSection() {
    const tail = journalTail();
    if (!tail.length) return null;
    const items = tail
      .map((e) => {
        const [head, ...rest] = e.replace(/^## /, "").split("\n");
        const lines = rest.map((l) => l.trim()).filter(Boolean);
        return `<li class="tl-item"><div class="tl-k">&#9998; JOURNAL</div><h4>${esc(head)}</h4>${lines.length ? `<p>${lines.map((l) => esc(l)).join("<br>")}</p>` : ""}</li>`;
      })
      .join("");
    return {
      id: "journal",
      nav: "Journal",
      render: (n) => sectionShell("journal", n, `Journal: <span class="accent">latest first.</span>`, "", `<ol class="tl reveal">${items}</ol>`),
    };
  }

  /** Method: where this heartbeat's look came from (only when the theme names its sources). */
  function methodSection() {
    if (!theme.sources.length) return null;
    const rows = theme.sources
      .map((s) => `<tr><td>${esc(toneOf(sourceKind, s.kind.toLowerCase(), s.kind || "Source"))}</td><td>${esc(s.ref) || "&mdash;"}</td><td>${esc(s.note) || "&mdash;"}</td></tr>`)
      .join("");
    const lede = [
      theme.ethos ? `<b>${esc(theme.ethos)}</b>` : null,
      `Default reading mode: <b>${theme.defaultMode}</b>${theme.modeReason ? `. ${esc(theme.modeReason)}` : "."} The switch in the nav overrides it and is remembered per page.`,
    ].filter(Boolean).join(" ");
    const body = `<h3 class="reveal"><span class="tag">THEME</span>Where this look came from</h3>
    <div class="tbl-wrap reveal"><table><thead><tr><th style="width:18%">Source</th><th style="width:34%">Reference</th><th>What it contributed</th></tr></thead><tbody>${rows}</tbody></table></div>`;
    return { id: "method", nav: "Method", render: (n) => sectionShell("method", n, `Method: <span class="accent">${esc(theme.name)}.</span>`, lede, body) };
  }

  // ---------- hero data (bound to the canvas) ----------
  const heroData = {
    mission: String(missionName),
    activeIndex: activeIdx,
    prs: prLog.length,
    tasksDone: doneTasks,
    phases: phases.map((p) => {
      const tasks = tasksOf(p);
      const done = tasks.filter((t) => t.status === "done").length;
      const st = phaseStatus(p.status);
      return {
        id: String(p.id ?? "?"),
        title: String(p.title ?? ""),
        status: st,
        done,
        total: tasks.length,
        frac: tasks.length ? +(done / tasks.length).toFixed(4) : st === "done" ? 1 : 0,
        gates: gatesOf(p).map((g) => gateStatus(g.status)),
      };
    }),
  };

  const themeSpec = {
    name: theme.name,
    ethos: theme.ethos,
    defaultMode: theme.defaultMode,
    modeReason: theme.modeReason || (theme.derived ? "" : "No state.theme was recorded; neutral placeholder tokens are shown. Derive a theme with flagship-report's theme forge."),
    derived: theme.derived,
    ...(Object.keys(theme.personality).length ? { personality: theme.personality } : {}),
    sources: theme.sources,
    modes: theme.tokens,
  };

  // ---------- page ----------
  const sections = [overviewSection(), coldStartSection(), metricsSection(), risksSection(), phasesSection(), prSection(), journalSection(), methodSection()]
    .filter(Boolean)
    .map((s, i) => ({ ...s, num: String(i).padStart(2, "0") }));
  const navLinks = sections.map((s) => `<a href="#${s.id}">${s.num} ${s.nav}</a>`).join("\n      ");
  const sectionsHtml = sections.map((s) => s.render(s.num)).join("\n\n");
  const generated = new Date().toISOString().slice(0, 16).replace("T", " ");
  const lastGateRun = allGates.map((g) => String(g.lastRun ?? "")).filter(Boolean).sort().pop();
  const isDark = theme.defaultMode === "dark";
  const other = isDark ? "light" : "dark";
  const tokenDecls = (mode) => `color-scheme:${mode};\n  ${Object.entries(theme.tokens[mode]).map(([k, v]) => `${k}:${v};`).join("")}`;
  const tokenCss = `/* theme "${esc(theme.name).replace(/\*\//g, "* /")}" · default mode (${theme.defaultMode}) also lives on bare :root so the page is themed with JavaScript off */
:root,:root[data-mode="${theme.defaultMode}"]{
  ${tokenDecls(theme.defaultMode)}
}
:root[data-mode="${other}"]{
  ${tokenDecls(other)}
}`;
  const orbitLabel = `Mission orbit: ${phases.length} phases from launch to landing, ${donePhases} closed, active phase ${activeLabel}, ${prLog.length} merged PRs.`;

  const signalCss = String.raw`
/* Signal · generated heartbeat: data hero, then numbered evidence sections. Colors come only from theme tokens. */
:root{
  --mono:ui-monospace,"SF Mono","Cascadia Mono",Menlo,Consolas,monospace;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --display:"SF Pro Display","Helvetica Neue","Arial Black",Arial,system-ui,sans-serif;
  --ease:cubic-bezier(.22,.61,.36,1);
}
${tokenCss}
/* terminals stay dark in both modes, with their own fixed ink */
.terminal{--term-bg:#0c0d11;--term-bar:#14161c;--term-line:rgba(255,255,255,.08);--term-text:#d6d9e0;--term-accent:#7fb0ff;--term-good:#3ccf95;--term-dim:#8b909c}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;background:var(--bg)}
body{background:var(--bg);color:var(--text);font-family:var(--sans);font-size:16px;line-height:1.65;-webkit-font-smoothing:antialiased;overflow-x:hidden;transition:background-color .35s,color .35s}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;background-image:radial-gradient(var(--grid) 1px,transparent 1px);background-size:4px 4px}
::selection{background:color-mix(in srgb,var(--a1) 30%,transparent)}
a{color:var(--a1);text-decoration:none}
a:hover{color:var(--a2)}
a:focus-visible,button:focus-visible,summary:focus-visible,[tabindex]:focus-visible{outline:2px solid var(--a1);outline-offset:3px;border-radius:6px}
.wrap{max-width:1200px;margin:0 auto;padding-inline:28px;position:relative;z-index:1}
code,.mono{font-family:var(--mono);font-size:.86em}
code{color:var(--text);background:color-mix(in srgb,var(--text) 6%,transparent);border:1px solid var(--border-soft);border-radius:5px;padding:1px 6px;overflow-wrap:anywhere}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
#progress{position:fixed;top:0;left:0;height:3px;width:100%;transform:scaleX(0);transform-origin:left;z-index:60;background:linear-gradient(90deg,var(--a1),var(--a2))}
nav.top{position:sticky;top:env(safe-area-inset-top,0px);z-index:50;background:color-mix(in srgb,var(--bg) 95%,transparent);border-bottom:1px solid var(--border-soft)}
.nav-inner{max-width:1200px;margin:0 auto;padding:12px 28px;display:flex;align-items:center;gap:20px}
.brand{font-family:var(--mono);font-size:13px;letter-spacing:.22em;color:var(--a1);font-weight:700;white-space:nowrap}
.brand span{color:var(--dim);letter-spacing:.1em;font-weight:500}
.nav-links{display:flex;flex-wrap:wrap;gap:2px;min-width:0;flex:1}
.nav-links::-webkit-scrollbar{display:none}
.nav-links a{font-family:var(--mono);font-size:11px;color:var(--muted);padding:5px 8px;border-radius:6px;letter-spacing:.04em;white-space:nowrap;transition:color .2s,background .2s}
.nav-links a:hover{color:var(--a1);background:color-mix(in srgb,var(--a1) 9%,transparent)}
.nav-links a.active{color:var(--a1);background:color-mix(in srgb,var(--a1) 13%,transparent)}
.mode-toggle{flex:none;font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;color:var(--text);background:var(--panel);border:1px solid var(--border);border-radius:999px;padding:6px 12px;cursor:pointer;white-space:nowrap;display:inline-flex;align-items:center;gap:7px}
.mode-toggle:hover{border-color:var(--a1);color:var(--a1)}
.mode-toggle i{width:10px;height:10px;border-radius:50%;background:linear-gradient(90deg,var(--text) 50%,transparent 50%);border:1px solid var(--text);display:inline-block}
.hero{position:relative;min-height:100vh;min-height:100svh;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;overflow:hidden;z-index:1}
#hero-canvas{position:absolute;inset:0;width:100%;height:100%;z-index:0}
.hero-fade{position:absolute;inset:0;z-index:1;pointer-events:none;background:radial-gradient(ellipse 46% 40% at 50% 50%,color-mix(in srgb,var(--bg) 88%,transparent),color-mix(in srgb,var(--bg) 35%,transparent) 62%,color-mix(in srgb,var(--bg) 18%,transparent) 78%,color-mix(in srgb,var(--bg) 92%,transparent) 100%)}
.hero-content{position:relative;z-index:2;padding:96px 24px 120px;max-width:980px;min-width:0}
.hero-eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.32em;color:var(--a1);text-transform:uppercase;margin-bottom:22px;overflow-wrap:anywhere}
.hero h1{font-family:var(--display);font-size:clamp(40px,7.4vw,94px);font-weight:900;letter-spacing:-.025em;line-height:1.02;text-wrap:balance;overflow-wrap:anywhere;color:var(--text)}
.hero-sub{margin:24px auto 0;font-size:clamp(15px,2.1vw,20px);color:var(--muted);max-width:760px;text-wrap:balance;overflow-wrap:anywhere}
.hero-sub b{color:var(--text);font-weight:600}
.hero-meta{margin-top:34px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
.hero-chip{font-family:var(--mono);font-size:11.5px;color:var(--muted);border:1px solid var(--border);border-radius:999px;padding:7px 15px;background:color-mix(in srgb,var(--panel) 82%,transparent);letter-spacing:.06em;max-width:100%;overflow-wrap:anywhere}
.hero-chip em{font-style:normal;color:var(--a1)}
.hero-chip em.bad{color:var(--bad)}
.hero-legend{position:absolute;left:28px;bottom:30px;z-index:2;font-family:var(--mono);font-size:10.5px;color:var(--dim);letter-spacing:.08em;text-align:left;line-height:1.9;max-width:320px}
.hero-legend b{color:var(--muted);font-weight:600}
.hero-legend i{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:8px;vertical-align:middle;font-style:normal}
.scroll-cue{position:absolute;bottom:30px;left:50%;transform:translateX(-50%);z-index:2;display:flex;flex-direction:column;align-items:center;gap:10px;color:var(--dim);font-family:var(--mono);font-size:10.5px;letter-spacing:.3em}
.scroll-cue .line{width:1px;height:44px;background:linear-gradient(180deg,var(--a1),transparent);animation:cue 2.2s ease-in-out infinite;transform-origin:top}
@keyframes cue{0%{transform:scaleY(0)}45%{transform:scaleY(1)}100%{transform:scaleY(1);opacity:0}}
.motion-toggle{position:absolute;right:28px;bottom:30px;z-index:3;font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;color:var(--muted);background:color-mix(in srgb,var(--panel) 85%,transparent);border:1px solid var(--border);border-radius:999px;padding:7px 14px;cursor:pointer}
.motion-toggle:hover{color:var(--a1);border-color:var(--a1)}
main{position:relative;z-index:1}
section{padding-block:96px 72px;border-top:1px solid var(--border-soft);position:relative}
.sec-num{font-family:var(--mono);font-size:13px;letter-spacing:.3em;color:var(--a1);margin-bottom:14px}
.sec-num::before{content:"";display:inline-block;width:34px;height:1px;background:var(--a1);vertical-align:middle;margin-right:12px;opacity:.7}
h2{font-family:var(--display);font-size:clamp(30px,4.4vw,50px);font-weight:900;letter-spacing:-.02em;line-height:1.06;margin-bottom:14px;text-wrap:balance;overflow-wrap:anywhere}
h2 .accent{color:var(--a1)}
h3{font-size:20px;font-weight:700;margin:8px 0 18px;letter-spacing:-.005em;text-wrap:balance}
h3 .tag{font-family:var(--mono);font-size:11px;color:var(--a1);letter-spacing:.15em;vertical-align:middle;margin-right:10px;font-weight:600}
.sec-lede{color:var(--muted);font-size:17px;max-width:820px;margin-bottom:44px;overflow-wrap:anywhere}
.sec-lede b{color:var(--text)}
.note{font-family:var(--mono);font-size:12px;color:var(--dim);margin-top:14px;line-height:1.7}
.reveal{transition:opacity .8s var(--ease),transform .8s var(--ease)}
body.armed .reveal:not(.in){opacity:0;transform:translateY(26px)}
.stat-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(165px,100%),1fr));gap:14px;margin:8px 0 8px}
.stat{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:22px 18px;text-align:center;position:relative;overflow:hidden;min-width:0}
.stat::after{content:"";position:absolute;top:0;left:20%;right:20%;height:2px;background:var(--a1);opacity:.7}
.stat .val{font-family:var(--mono);font-size:clamp(24px,3vw,32px);font-weight:700;color:var(--text);letter-spacing:-.02em;line-height:1.1;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
.stat .val.ok{color:var(--good)}.stat .val.warn{color:var(--warn)}.stat .val.bad{color:var(--bad)}.stat .val.info{color:var(--info)}.stat .val.gray{color:var(--muted)}
.stat .lbl{font-size:12.5px;color:var(--muted);margin-top:9px;line-height:1.45;overflow-wrap:anywhere}
.stat .sub{font-family:var(--mono);font-size:10.5px;color:var(--dim);letter-spacing:.06em;margin-top:6px;overflow-wrap:anywhere}
.verdict-banner{margin-top:40px;background:var(--panel);border:1px solid color-mix(in srgb,var(--a1) 35%,transparent);border-left:3px solid var(--a1);border-radius:14px;padding:28px 32px}
.verdict-banner p{font-size:17px;color:var(--text)}
.verdict-banner p b{color:var(--a1)}
ol.next{margin:12px 0 0 20px;color:var(--muted);font-size:15px;overflow-wrap:anywhere}
ol.next li{padding:4px 0}
.meter{height:6px;border-radius:999px;background:color-mix(in srgb,var(--text) 8%,transparent);overflow:hidden;margin-top:14px}
.meter span{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,var(--a1),var(--a2))}
.meter.big{height:10px;margin-top:22px}
.meter-lbl{font-family:var(--mono);font-size:11px;color:var(--dim);letter-spacing:.08em;margin-top:8px;overflow-wrap:anywhere}
.tbl-wrap{overflow-x:auto;border:1px solid var(--border);border-radius:14px;background:var(--panel)}
table{width:100%;border-collapse:collapse;font-size:14px;min-width:680px}
th{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--dim);text-align:left;padding:14px 18px;border-bottom:1px solid var(--border);background:var(--panel-2);white-space:nowrap}
td{padding:14px 18px;border-bottom:1px solid var(--border-soft);vertical-align:top;color:var(--muted)}
td:first-child{color:var(--text)}
tr:last-child td{border-bottom:none}
tbody tr{transition:background .2s}
tbody tr:nth-child(even){background:color-mix(in srgb,var(--text) 2%,transparent)}
tbody tr:hover{background:color-mix(in srgb,var(--a1) 6%,transparent)}
td .mono,td.mono{color:var(--text);font-family:var(--mono);font-size:12px}
.why{display:block;font-size:12px;color:var(--dim);margin-top:4px;line-height:1.45}
.pill{display:inline-block;font-family:var(--mono);font-size:10.5px;font-weight:700;letter-spacing:.08em;padding:4px 11px;border-radius:999px;white-space:nowrap;text-transform:uppercase;border:1px solid}
.pill.ok{color:var(--good);background:color-mix(in srgb,var(--good) 11%,transparent);border-color:color-mix(in srgb,var(--good) 38%,transparent)}
.pill.warn{color:var(--warn);background:color-mix(in srgb,var(--warn) 11%,transparent);border-color:color-mix(in srgb,var(--warn) 38%,transparent)}
.pill.bad{color:var(--bad);background:color-mix(in srgb,var(--bad) 11%,transparent);border-color:color-mix(in srgb,var(--bad) 40%,transparent)}
.pill.info{color:var(--info);background:color-mix(in srgb,var(--info) 9%,transparent);border-color:color-mix(in srgb,var(--info) 32%,transparent)}
.pill.gray{color:var(--muted);background:color-mix(in srgb,var(--text) 5%,transparent);border-color:var(--border)}
.pill.live{color:var(--a1);background:color-mix(in srgb,var(--a1) 10%,transparent);border-color:color-mix(in srgb,var(--a1) 40%,transparent)}
.v-timeline{position:relative;margin:36px 0 0;padding-left:44px}
.v-timeline::before{content:"";position:absolute;left:14px;top:8px;bottom:8px;width:2px;background:var(--border)}
.v-fill{position:absolute;left:14px;top:8px;width:2px;height:calc((100% - 16px) * var(--fill,1));transform:scaleY(0);transform-origin:top;background:linear-gradient(180deg,var(--a1),var(--a2));transition:transform 2.6s var(--ease)}
.v-timeline.in .v-fill{transform:scaleY(1)}
.phase{position:relative;padding:0 0 44px;min-width:0}
.phase:last-child{padding-bottom:0}
.phase::before{content:"";position:absolute;left:-36px;top:6px;width:13px;height:13px;border-radius:50%;border:2px solid var(--a1);background:var(--bg);transition:background .4s .3s,box-shadow .4s .3s}
.v-timeline.in .phase::before{background:var(--a1);box-shadow:0 0 12px color-mix(in srgb,var(--a1) 50%,transparent)}
.phase.st-done::before{border-color:var(--good)}
.v-timeline.in .phase.st-done::before{background:var(--good);box-shadow:0 0 12px color-mix(in srgb,var(--good) 50%,transparent)}
.phase.st-blocked::before{border-color:var(--bad)}
.v-timeline.in .phase.st-blocked::before{background:var(--bad);box-shadow:0 0 12px color-mix(in srgb,var(--bad) 50%,transparent)}
.phase.st-pending::before,.v-timeline.in .phase.st-pending::before{border-color:var(--dot-off);background:var(--bg);box-shadow:none}
.v-timeline.in .phase.active::before{animation:beacon 2.4s var(--ease) infinite}
@keyframes beacon{0%{box-shadow:0 0 0 0 color-mix(in srgb,var(--a1) 55%,transparent)}70%{box-shadow:0 0 0 12px color-mix(in srgb,var(--a1) 0%,transparent)}100%{box-shadow:0 0 0 0 color-mix(in srgb,var(--a1) 0%,transparent)}}
.phase .ph{font-family:var(--mono);font-size:11px;letter-spacing:.24em;color:var(--a1);text-transform:uppercase;overflow-wrap:anywhere}
.phase h4{font-size:19px;margin:5px 0 7px;display:flex;flex-wrap:wrap;align-items:center;gap:8px 10px;overflow-wrap:anywhere}
.phase>p{font-size:14px;color:var(--muted);max-width:820px;overflow-wrap:anywhere}
.exits{display:flex;flex-wrap:wrap}
.exit-chip{display:inline-block;font-family:var(--mono);font-size:11px;color:var(--good);background:color-mix(in srgb,var(--good) 8%,transparent);border:1px solid color-mix(in srgb,var(--good) 32%,transparent);border-radius:7px;padding:4px 11px;margin:10px 8px 0 0;max-width:100%;overflow-wrap:anywhere}
.exit-chip b{font-weight:600;letter-spacing:.12em;margin-right:8px;opacity:.85}
.exit-chip.bad{color:var(--bad);background:color-mix(in srgb,var(--bad) 8%,transparent);border-color:color-mix(in srgb,var(--bad) 32%,transparent)}
.exit-chip.warn{color:var(--warn);background:color-mix(in srgb,var(--warn) 8%,transparent);border-color:color-mix(in srgb,var(--warn) 32%,transparent)}
.exit-chip.pending{color:var(--muted);background:transparent;border:1px dashed var(--tick)}
details.phase-detail{margin-top:18px;background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:2px 20px 18px;min-width:0}
.phase.active details.phase-detail{border-color:color-mix(in srgb,var(--a1) 35%,transparent)}
details summary{cursor:pointer;font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);padding:13px 0;list-style:none}
details summary::-webkit-details-marker{display:none}
details summary::before{content:"\25B8";display:inline-block;margin-right:10px;color:var(--a1);transition:transform .2s}
details[open]>summary::before{transform:rotate(90deg)}
details summary:hover{color:var(--a1)}
details.resume{margin-top:16px;border-top:1px dashed var(--border)}
ul.task-list{list-style:none}
ul.task-list li{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 10px;padding:10px 0;border-top:1px solid var(--border-soft);font-size:14px;color:var(--muted);overflow-wrap:anywhere}
ul.task-list li:first-child{border-top:0}
.tid{font-family:var(--mono);font-size:12px;color:var(--text)}
.tt{color:var(--text);min-width:0}
li.task-done .tt{color:var(--muted)}
.tpr{font-family:var(--mono);font-size:11.5px;color:var(--dim)}
.tnote{flex-basis:100%;font-size:12.5px;color:var(--dim)}
.phase-detail .tbl-wrap{margin-top:16px}
.terminal{background:var(--term-bg);border:1px solid var(--border);border-radius:14px;overflow:hidden;margin:14px 0 0}
.term-bar{display:flex;align-items:center;gap:8px;padding:10px 12px 10px 18px;background:var(--term-bar);border-bottom:1px solid var(--term-line)}
.term-bar .dot{width:11px;height:11px;border-radius:50%;background:#3a3d4a;flex:none}
.term-bar .ttl{font-family:var(--mono);font-size:11px;color:var(--term-dim);margin-left:10px;letter-spacing:.1em;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.terminal pre{padding:22px 24px;font-family:var(--mono);font-size:12.6px;line-height:1.75;color:var(--term-text);white-space:pre-wrap;overflow-wrap:anywhere;max-height:460px;overflow:auto}
button.copy{margin-left:auto;flex:none;font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;color:var(--term-dim);background:rgba(255,255,255,.04);border:1px solid var(--term-line);border-radius:999px;padding:5px 13px;cursor:pointer;transition:color .2s,border-color .2s,background .2s}
button.copy:hover{color:var(--term-accent);border-color:var(--term-accent)}
button.copy.copied{color:var(--term-good);border-color:var(--term-good)}
.tl{list-style:none;position:relative;margin:12px 0 0;padding-left:44px}
.tl::before{content:"";position:absolute;left:14px;top:8px;bottom:8px;width:2px;background:var(--border)}
.tl-item{position:relative;padding:0 0 26px;min-width:0}
.tl-item:last-child{padding-bottom:0}
.tl-item::before{content:"";position:absolute;left:-34px;top:7px;width:9px;height:9px;border-radius:50%;background:var(--a1);box-shadow:0 0 10px color-mix(in srgb,var(--a1) 45%,transparent)}
.tl-k{font-family:var(--mono);font-size:11px;letter-spacing:.2em;color:var(--a1)}
.tl-item h4{font-size:16px;margin:4px 0 6px;overflow-wrap:anywhere}
.tl-item p{font-size:14px;color:var(--muted);overflow-wrap:anywhere}
.tl-meta{font-family:var(--mono);font-size:11.5px;color:var(--dim);display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center}
.callout{border-left:3px solid var(--a1);background:color-mix(in srgb,var(--a1) 6%,transparent);border-radius:0 10px 10px 0;padding:16px 22px;margin-top:18px;font-size:14px;color:var(--muted)}
.chart{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:22px 24px 18px;min-width:0;margin:22px 0 4px}
.chart-title{font-weight:700;font-size:15px}
.chart-sub{font-family:var(--mono);font-size:11px;color:var(--dim);letter-spacing:.06em;margin:2px 0 16px}
.bars{display:grid;grid-template-columns:minmax(64px,auto) 1fr;column-gap:14px;row-gap:9px;align-items:center}
.bar-lbl{font-family:var(--mono);font-size:12px;color:var(--text);white-space:nowrap;max-width:34vw;overflow:hidden;text-overflow:ellipsis}
.bar-track{position:relative;height:22px;background-image:linear-gradient(90deg,var(--border) 1px,transparent 1px);background-size:calc(100% / var(--ticks,5)) 100%;background-position:-1px 0;border-left:1px solid var(--tick)}
.bar{position:absolute;left:0;top:5px;height:12px;width:var(--v);border-radius:0 4px 4px 0;background:var(--a1);outline:none}
.bar.neutral{background:var(--neutral)}
.bar:hover,.bar:focus-visible{filter:brightness(1.12);box-shadow:0 0 0 2px var(--panel),0 0 0 3px var(--a1)}
.bar-val{position:absolute;top:1px;left:calc(var(--v) + 8px);font-family:var(--mono);font-size:11.5px;color:var(--text);white-space:nowrap;font-variant-numeric:tabular-nums}
.bar-val.in{left:auto;right:calc(100% - var(--v) + 8px);color:var(--bg);font-weight:700}
.axis{display:grid;grid-template-columns:minmax(64px,auto) 1fr;column-gap:14px;margin-top:6px}
.axis-ticks{display:flex;justify-content:space-between;font-family:var(--mono);font-size:10px;color:var(--dim);font-variant-numeric:tabular-nums}
#tip{position:fixed;z-index:80;pointer-events:none;background:var(--tip-bg);border:1px solid var(--border);border-radius:8px;padding:8px 11px;font-family:var(--mono);font-size:11.5px;color:var(--text);max-width:280px;box-shadow:0 10px 30px var(--shadow);opacity:0;transform:translateY(4px);transition:opacity .15s,transform .15s}
#tip.on{opacity:1;transform:none}
footer{border-top:1px solid var(--border-soft);padding-block:60px 50px;text-align:center;position:relative;z-index:1}
footer .f-line{font-family:var(--mono);font-size:12px;color:var(--dim);letter-spacing:.06em;line-height:2;overflow-wrap:anywhere}
footer .f-line em{font-style:normal;color:var(--a1)}
footer .f-mark{font-family:var(--display);font-size:26px;font-weight:900;letter-spacing:.3em;margin-bottom:16px;color:var(--text)}
@media (max-width:820px){
  .wrap,.nav-inner{padding-inline:16px}
  .nav-inner{gap:12px}
  .brand span{display:none}
  .nav-links{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none}
  section{padding-block:64px 52px}
  .hero-legend,.motion-toggle{display:none}
  .verdict-banner{padding:22px 20px}
  .stat-row{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
  .stat{padding:18px 12px}
  .v-timeline,.tl{padding-left:34px}
  .phase::before{left:-27px}
  .tl-item::before{left:-24px}
  .v-timeline::before,.v-fill,.tl::before{left:9px}
  details.phase-detail{padding:2px 14px 14px}
  .terminal pre{padding:16px}
}
@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{animation-duration:.001s!important;animation-iteration-count:1!important;transition-duration:.001s!important}
  html{scroll-behavior:auto}
}
@media print{
  body.armed .reveal:not(.in){opacity:1;transform:none}
  .v-fill{transform:none}
  nav.top,#progress,.scroll-cue,.motion-toggle,.mode-toggle,#hero-canvas,button.copy{display:none!important}
  .hero{min-height:auto}
  .terminal pre{max-height:none;overflow:visible}
}
`;

  const clientScript = String.raw`
(function(){
  "use strict";
  var root = document.documentElement;
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var noanim = location.hash === "#noanim";
  var clamp = function(v, a, b){ return Math.max(a, Math.min(b, v)); };

  /* ---- dark / light switch: the default comes from the theme, a viewer's choice wins ---- */
  var modeBtn = document.getElementById("mode-toggle");
  function paintModeButton(){
    if(!modeBtn) return;
    var dark = root.getAttribute("data-mode") !== "light";
    modeBtn.setAttribute("aria-pressed", String(dark));
    modeBtn.setAttribute("aria-label", dark ? "Dark mode on. Switch to light mode" : "Light mode on. Switch to dark mode");
    modeBtn.lastChild.textContent = dark ? " DARK" : " LIGHT";
  }
  paintModeButton();
  if(modeBtn) modeBtn.addEventListener("click", function(){
    var next = root.getAttribute("data-mode") === "light" ? "dark" : "light";
    root.setAttribute("data-mode", next);
    try { localStorage.setItem("signal-mode:" + location.pathname, next); } catch(e) {}
    paintModeButton();
    window.dispatchEvent(new CustomEvent("signal-mode", {detail:{mode: next}}));
  });

  /* ---- tooltips on chart marks ---- */
  var tip = document.getElementById("tip");
  function showTip(el){ var r = el.getBoundingClientRect(); tip.textContent = el.getAttribute("data-tip"); tip.classList.add("on");
    var x = Math.min(Math.max(8, r.left + r.width/2 - tip.offsetWidth/2), window.innerWidth - tip.offsetWidth - 8);
    var y = r.top - tip.offsetHeight - 10; if(y < 8) y = r.bottom + 10; tip.style.left = x + "px"; tip.style.top = y + "px"; }
  function hideTip(){ if(tip) tip.classList.remove("on"); }
  if(tip) document.querySelectorAll("[data-tip]").forEach(function(el){
    el.addEventListener("pointerenter", function(){ showTip(el); });
    el.addEventListener("pointerleave", hideTip);
    el.addEventListener("focus", function(){ showTip(el); });
    el.addEventListener("blur", hideTip);
  });

  /* ---- reading progress: the page's only scroll listener, batched into one rAF ---- */
  var prog = document.getElementById("progress"), pending = 0;
  function readScroll(){ pending = 0; var max = Math.max(1, root.scrollHeight - window.innerHeight); if(prog) prog.style.transform = "scaleX(" + clamp(window.scrollY / max, 0, 1) + ")"; }
  window.addEventListener("scroll", function(){ hideTip(); if(!pending) pending = requestAnimationFrame(readScroll); }, {passive:true});
  readScroll();

  /* ---- copy buttons: clipboard inside the click, select-the-text fallback ---- */
  document.querySelectorAll("button.copy").forEach(function(b){
    b.addEventListener("click", function(){
      var pre = b.closest(".terminal").querySelector("pre");
      function show(label, ok){
        b.textContent = label; b.classList.toggle("copied", ok);
        clearTimeout(b._t); b._t = setTimeout(function(){ b.textContent = "COPY"; b.classList.remove("copied"); }, 1800);
      }
      function fallback(){
        var r = document.createRange(); r.selectNodeContents(pre);
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        show("SELECTED · CTRL/CMD+C", false);
      }
      try {
        navigator.clipboard.writeText(pre.textContent).then(function(){ show("COPIED", true); }).catch(fallback);
      } catch(e){ fallback(); }
    });
  });

  /* ---- scroll reveal: anything already on screen is never hidden.
     Threshold 0 (not a ratio) so a timeline taller than the viewport still reveals. ---- */
  var revealEls = Array.prototype.slice.call(document.querySelectorAll(".reveal"));
  var parents = new Map();
  revealEls.forEach(function(el){ var p=el.parentNode, i=parents.get(p)||0; parents.set(p,i+1); el.style.transitionDelay=(i%8)*70+"ms"; });
  var watched = revealEls.concat(Array.prototype.slice.call(document.querySelectorAll(".v-timeline:not(.reveal)")));
  if("IntersectionObserver" in window && !reduced && !noanim){
    var vh = window.innerHeight || 800;
    watched.forEach(function(el){ if(el.getBoundingClientRect().top < vh) el.classList.add("in"); });
    document.body.classList.add("armed");
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add("in"); io.unobserve(e.target); } });
    }, {threshold:0, rootMargin:"0px 0px -10% 0px"});
    watched.forEach(function(el){ if(!el.classList.contains("in")) io.observe(el); });
  } else {
    watched.forEach(function(el){ el.classList.add("in"); });
  }

  /* ---- counters: markup holds the true value; animation only replays it ---- */
  function fmt(v, el){
    var dec = parseInt(el.getAttribute("data-decimals")||"0",10), s = v.toFixed(dec);
    if(el.getAttribute("data-group")) s = Number(s).toLocaleString("en-US", {minimumFractionDigits:dec, maximumFractionDigits:dec});
    return (el.getAttribute("data-prefix")||"") + s + (el.getAttribute("data-suffix")||"");
  }
  function animateCount(el){
    var target = parseFloat(el.getAttribute("data-target"))||0, finalText = el.textContent, t0=null, dur=1400;
    function frame(t){ if(!t0) t0=t; var k=Math.min((t-t0)/dur,1); el.textContent = k<1 ? fmt(target*(1-Math.pow(1-k,3)), el) : finalText; if(k<1) requestAnimationFrame(frame); }
    requestAnimationFrame(frame);
  }
  if("IntersectionObserver" in window && !reduced && !noanim){
    var cio = new IntersectionObserver(function(en){ en.forEach(function(e){ if(e.isIntersecting){ animateCount(e.target); cio.unobserve(e.target); } }); }, {threshold:.4});
    document.querySelectorAll(".count").forEach(function(c){ cio.observe(c); });
  }

  /* ---- scrollspy ---- */
  var navLinks = Array.prototype.slice.call(document.querySelectorAll(".nav-links a"));
  var secs = navLinks.map(function(a){ return document.querySelector(a.getAttribute("href")); }).filter(Boolean);
  if("IntersectionObserver" in window && secs.length){
    var spy = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if(!e.isIntersecting) return;
        navLinks.forEach(function(a){
          var on = a.getAttribute("href") === "#" + e.target.id;
          a.classList.toggle("active", on);
          if(on && a.parentNode.scrollWidth > a.parentNode.clientWidth){ a.parentNode.scrollLeft = a.offsetLeft - a.parentNode.offsetLeft - 40; }
        });
      });
    }, {rootMargin:"-30% 0px -60% 0px"});
    secs.forEach(function(s){ spy.observe(s); });
  }

  initHero();

  /* ---- HERO: mission orbit ----
     Bound to #hero-data: one node per phase along an open orbit (launch -> landing);
     ring arc = that phase's task completion; the active phase pulses; particles leave
     done phases for the active one at a rate proportional to merged PRs.
     Every color is read from the theme tokens and re-read when the reading mode changes. */
  function initHero(){
    var canvas = document.getElementById("hero-canvas");
    var data; try { data = JSON.parse(document.getElementById("hero-data").textContent); } catch(e){ data = null; }
    if(!canvas || !canvas.getContext || !data || !Array.isArray(data.phases)) return;
    var ctx = canvas.getContext("2d"), dpr = Math.min(window.devicePixelRatio||1, 2);
    var phases = data.phases, n = phases.length, active = typeof data.activeIndex === "number" ? data.activeIndex : -1;
    var W=0, H=0, cx=0, cy=0, rx=0, ry=0, narrow=false;
    var A0 = Math.PI*0.78, SWEEP = Math.PI*1.44;
    var rate = Math.min(36, (data.prs||0)*1.2);
    var particles = [], cells = [], quiet = [], flash = 0, t = 0;
    var running = true, paused = false, raf = 0, last = 0;

    function tok(name){ return getComputedStyle(root).getPropertyValue(name).trim(); }
    function rgbOf(v){
      var m = /^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/i.exec(v);
      if(m) return m[1] + "," + m[2] + "," + m[3];
      var h = String(v).replace("#", "");
      if(h.length === 3 || h.length === 4) h = h.slice(0, 3).split("").map(function(c){ return c + c; }).join("");
      h = h.slice(0, 6); var x = parseInt(h, 16);
      if(h.length !== 6 || !isFinite(x)) return "128,128,128";
      return ((x >> 16) & 255) + "," + ((x >> 8) & 255) + "," + (x & 255);
    }
    var P = {}, tone = {}, gateTone = {};
    function readPalette(){
      ["a1","a2","good","warn","bad","dim","muted","text","bg"].forEach(function(k){ P[k] = rgbOf(tok("--" + k)); });
      tone = {done:P.good, in_progress:P.a1, blocked:P.bad, pending:P.dim};
      gateTone = {passed:P.good, failed:P.bad, waived:P.warn, pending:P.dim};
    }
    readPalette();

    function sOf(i){ return (i+1)/(n+1); }
    var targetS = active >= 0 && active < n ? sOf(active) : 1;
    var sources = [], totalW = 0;
    phases.forEach(function(p, i){ if(p.status === "done" && i !== active){ var w = Math.max(1, p.done||0); sources.push({s:sOf(i), w:w}); totalW += w; } });
    function pickSource(){ if(!sources.length) return 0; var r = Math.random()*totalW; for(var i=0;i<sources.length;i++){ r -= sources[i].w; if(r<=0) return sources[i].s; } return sources[0].s; }
    function pt(s, lift){ var a = A0 + s*SWEEP, k = 1 + (lift||0); return {x: cx + Math.cos(a)*rx*k, y: cy + Math.sin(a)*ry*k, a: a}; }
    function spawn(u){ particles.push({s0:pickSource(), u:u||0, sp:.26+Math.random()*.22, w:.6+Math.random()*1.1, lift:(Math.random()-.5)*.09}); }

    function measureQuiet(){
      quiet = []; var base = canvas.getBoundingClientRect();
      document.querySelectorAll(".hero-content > *, .hero-legend").forEach(function(el){
        var r = el.getBoundingClientRect(); if(!r.width) return;
        quiet.push({x:r.left-base.left-18, y:r.top-base.top-14, w:r.width+36, h:r.height+28});
      });
    }
    function inQuiet(x,y){ for(var i=0;i<quiet.length;i++){ var q=quiet[i]; if(x>q.x&&x<q.x+q.w&&y>q.y&&y<q.y+q.h) return true; } return false; }
    function resize(){
      W = canvas.clientWidth; H = canvas.clientHeight;
      canvas.width = Math.max(1, W*dpr); canvas.height = Math.max(1, H*dpr); ctx.setTransform(dpr,0,0,dpr,0,0);
      narrow = W < 700; cx = W/2; cy = H*0.54;
      rx = Math.min(W*0.43, 640); ry = Math.min(H*0.38, narrow ? 270 : 330);
      cells = []; var g = narrow ? 22 : 18;
      for(var x=0;x<W;x+=g){ for(var y=0;y<H;y+=g){ if(Math.random()<.14) cells.push({x:x,y:y,p:Math.random()*6.28,s:.3+Math.random()*1.2}); } }
      measureQuiet();
    }
    function arc(s0, s1){ ctx.beginPath(); ctx.ellipse(cx,cy,rx,ry,0,A0+s0*SWEEP,A0+s1*SWEEP); ctx.stroke(); }
    function ring(x,y,r){ ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); }
    function rgba(c, a){ return "rgba(" + c + "," + a + ")"; }

    function draw(time, still){
      ctx.clearRect(0,0,W,H);
      for(var k=0;k<cells.length;k++){ var c=cells[k], al=.03+.04*(Math.sin(time*c.s+c.p)*.5+.5); ctx.fillStyle=rgba(P.dim, al.toFixed(3)); ctx.fillRect(c.x,c.y,2,2); }
      /* the orbit: faint full ellipse, travelled arc lit, remaining arc dashed */
      ctx.lineWidth=1; ctx.setLineDash([2,6]); ctx.strokeStyle=rgba(P.a1,".12"); ctx.beginPath(); ctx.ellipse(cx,cy,rx,ry,0,0,Math.PI*2); ctx.stroke();
      ctx.setLineDash([4,7]); ctx.strokeStyle=rgba(P.dim,".45"); arc(targetS, 1); ctx.setLineDash([]);
      ctx.lineWidth=1.6; ctx.strokeStyle=rgba(P.a1,".5"); arc(0, targetS);
      var L=pt(0), E=pt(1);
      ctx.fillStyle=rgba(P.a1,".8"); ctx.fillRect(L.x-3,L.y-3,6,6);
      ctx.setLineDash([3,3]); ctx.lineWidth=1.4; ctx.strokeStyle= active<0 ? rgba(P.good,".9") : rgba(P.dim,".7"); ring(E.x,E.y,7); ctx.stroke(); ctx.setLineDash([]);
      /* particles: merged work flowing toward the active phase */
      for(var j=0;j<particles.length;j++){
        var p=particles[j], e=p.u<.5?2*p.u*p.u:1-Math.pow(-2*p.u+2,2)/2, u0=Math.max(0,p.u-.05), e0=u0<.5?2*u0*u0:1-Math.pow(-2*u0+2,2)/2;
        var a1=pt(p.s0+(targetS-p.s0)*e, Math.sin(p.u*Math.PI)*p.lift), a0=pt(p.s0+(targetS-p.s0)*e0, Math.sin(u0*Math.PI)*p.lift);
        var fade = Math.sin(p.u*Math.PI) * (inQuiet(a1.x,a1.y) ? .3 : 1);
        ctx.strokeStyle=rgba(P.a2,(fade*.6).toFixed(3)); ctx.lineWidth=p.w; ctx.beginPath(); ctx.moveTo(a0.x,a0.y); ctx.lineTo(a1.x,a1.y); ctx.stroke();
        ctx.fillStyle=rgba(P.a2,(fade*.95).toFixed(3)); ring(a1.x,a1.y,p.w*.9+.4); ctx.fill();
      }
      /* phase nodes */
      var pulse = still ? .5 : (Math.sin(time*1.6)*.5+.5);
      ctx.font = (narrow?"10px ":"11px ") + "ui-monospace,Menlo,monospace"; ctx.textAlign="center"; ctx.textBaseline="middle";
      for(var i=0;i<n;i++){
        var ph=phases[i], pos=pt(sOf(i)), r=narrow?8:11, col=tone[ph.status]||P.dim, isA=i===active, hush=inQuiet(pos.x,pos.y);
        ctx.globalAlpha = hush ? .28 : 1;
        if(isA){ for(var q=0;q<2;q++){ var w=((still?.35:time*.45)+q*.5)%1; ctx.strokeStyle=rgba(P.a1,((1-w)*.55).toFixed(3)); ctx.lineWidth=1.4; ring(pos.x,pos.y,r+7+w*30); ctx.stroke(); } }
        ctx.fillStyle=rgba(P.bg,".94"); ring(pos.x,pos.y,r+5); ctx.fill();
        ctx.strokeStyle=rgba(P.text,".14"); ctx.lineWidth=2; ring(pos.x,pos.y,r+5); ctx.stroke();
        if(ph.frac>0){ ctx.strokeStyle=rgba(col,".95"); ctx.lineWidth=2.6; ctx.beginPath(); ctx.arc(pos.x,pos.y,r+5,-Math.PI/2,-Math.PI/2+Math.PI*2*Math.min(1,ph.frac)); ctx.stroke(); }
        var glow = isA ? .4+pulse*.25+flash*.35 : (ph.status==="done" ? .5 : .28);
        ctx.fillStyle=rgba(isA?P.a2:col, Math.min(1,glow).toFixed(3)); ring(pos.x,pos.y,r*.5+(isA?flash*3:0)); ctx.fill();
        var gs = ph.gates||[];
        for(var g=0;g<gs.length&&g<9;g++){ var ga=Math.PI/2+(g-(Math.min(gs.length,9)-1)/2)*.36; ctx.fillStyle=rgba(gateTone[gs[g]]||P.dim,".95"); ring(pos.x+Math.cos(ga)*(r+11),pos.y+Math.sin(ga)*(r+11),1.8); ctx.fill(); }
        if(!hush){
          var lx=Math.max(18, Math.min(W-18, pos.x+Math.cos(pos.a)*(r+30))), ly=Math.max(14, Math.min(H-24, pos.y+Math.sin(pos.a)*(r+26)));
          ctx.fillStyle=rgba(P.text,".9"); ctx.fillText(ph.id, lx, ly);
          if(!narrow){ ctx.fillStyle=rgba(P.muted,".9"); ctx.fillText(ph.done+"/"+ph.total+" tasks", lx, ly+14); }
        }
      }
      ctx.globalAlpha = 1;
    }

    function step(dt){
      t += dt;
      if(rate>0 && Math.random() < rate*dt) spawn(0);
      for(var j=particles.length-1;j>=0;j--){ var p=particles[j]; p.u += p.sp*dt; if(p.u>=1){ flash=Math.min(1,flash+.3); particles.splice(j,1); } }
      flash = Math.max(0, flash-dt*1.4);
    }
    function staticFrame(){ particles.length=0; var count=Math.min(40, Math.round(rate*1.5)); for(var i=0;i<count;i++){ spawn(.1+.8*(i+.5)/count); } draw(1.7,true); }
    function loop(now){
      raf = 0; var dt = Math.min(.05, (now-last)/1000); last = now;
      step(dt); draw(t,false);
      if(running && !paused && !document.hidden) raf = requestAnimationFrame(loop);
    }
    function wake(){ if(!raf && running && !paused && !document.hidden){ last = performance.now(); raf = requestAnimationFrame(loop); } }
    function sleep(){ if(raf){ cancelAnimationFrame(raf); raf = 0; } }

    resize();
    setTimeout(function(){ measureQuiet(); if(reduced||noanim) staticFrame(); }, 300);
    var btn = document.getElementById("motion-toggle");
    window.addEventListener("resize", function(){ resize(); if(reduced||noanim) staticFrame(); else if(paused||!running) draw(t,false); });
    /* the reading mode changed: re-read the tokens and repaint at once, even when paused */
    window.addEventListener("signal-mode", function(){ readPalette(); if(reduced||noanim) staticFrame(); else draw(t,false); });
    if(reduced || noanim){ staticFrame(); if(btn) btn.hidden = true; return; }
    if(btn) btn.addEventListener("click", function(){
      paused = !paused; btn.setAttribute("aria-pressed", String(paused)); btn.textContent = paused ? "PLAY MOTION" : "PAUSE MOTION";
      window.dispatchEvent(new CustomEvent("enhanced-report-motion", {detail:{paused: paused}}));
      if(paused) sleep(); else wake();
    });
    var hero = document.querySelector(".hero");
    if("IntersectionObserver" in window && hero){ new IntersectionObserver(function(en){ running = en[0].isIntersecting; if(running) wake(); else sleep(); }, {threshold:0}).observe(hero); }
    document.addEventListener("visibilitychange", function(){ if(document.hidden) sleep(); else wake(); });
    for(var w=0; w<120; w++) step(1/60);
    draw(t,false); /* one populated frame at rest, even in a hidden tab or a thumbnail capture */
    wake();
  }
})();
`;

  return `<!doctype html>
<html lang="en" data-mode="${theme.defaultMode}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="signal-kind" content="sotu">
<title>${esc(missionName)} State of the Union</title>
<!-- DEFAULT_MODE equals state.theme.defaultMode (the theme-spec default). A viewer's saved choice wins. -->
<script>(function(){var DEFAULT_MODE="${theme.defaultMode}",m=DEFAULT_MODE;try{var v=localStorage.getItem("signal-mode:"+location.pathname);if(v==="dark"||v==="light")m=v;}catch(e){}document.documentElement.setAttribute("data-mode",m);})();</script>
<style>${signalCss}</style>
<noscript><style>.reveal{opacity:1!important;transform:none!important}</style></noscript>
</head>
<body class="enhanced" data-palette-id="${esc(theme.paletteId)}">
<div id="progress" aria-hidden="true"></div>
<nav class="top" aria-label="Report sections">
  <div class="nav-inner">
    <div class="brand">MISSION CONTROL <span>/ STATE OF THE UNION</span></div>
    <div class="nav-links">
      ${navLinks}
    </div>
    <button class="mode-toggle" id="mode-toggle" type="button" aria-pressed="${isDark}" aria-label="${isDark ? "Dark mode on. Switch to light mode" : "Light mode on. Switch to dark mode"}"><i aria-hidden="true"></i> ${isDark ? "DARK" : "LIGHT"}</button>
  </div>
</nav>

<!-- HERO: mission orbit, bound to #hero-data (built from state.phases + prLog) -->
<header class="hero" id="top">
  <canvas id="hero-canvas" role="img" aria-label="${esc(orbitLabel)}" data-visual-thesis="Mission orbit: one node per phase from launch to landing; ring = task completion, pulse = active phase, particle rate = merged PRs."></canvas>
  <div class="hero-fade" aria-hidden="true"></div>
  <div class="hero-content">
    <div class="hero-eyebrow">State of the Union &middot; ${esc(missionName)}</div>
    <h1>${esc(missionName)}</h1>
    <p class="hero-sub">${m.tagline ? `<b>${esc(m.tagline)}</b> ` : ""}Mission ${esc(m.status ?? "?")} &middot; ${pct}% of tasks complete &middot; ${passedGates}/${allGates.length} gates passed.</p>
    <div class="hero-meta">
      <span class="hero-chip">UPDATED <em>${esc(m.updated ?? "?")}</em></span>
      <span class="hero-chip">SESSIONS <em>${esc(m.sessionCount ?? 1)}</em></span>
      <span class="hero-chip">ACTIVE <em>${esc(activeLabel)}</em></span>
      <span class="hero-chip">BLOCKERS <em${blockers.length ? ' class="bad"' : ""}>${blockers.length}</em></span>
    </div>
  </div>
  <div class="hero-legend" aria-hidden="true">
    <div><i style="background:var(--good)"></i><b>Node ring</b> = phase task completion</div>
    <div><i style="background:var(--a2)"></i><b>Particle rate</b> = ${prLog.length} merged PRs</div>
    <div><i style="background:var(--a1)"></i><b>Pulse</b> = active phase</div>
  </div>
  <button class="motion-toggle" id="motion-toggle" type="button" aria-pressed="false">PAUSE MOTION</button>
  <div class="scroll-cue" aria-hidden="true"><span>SCROLL</span><span class="line"></span></div>
</header>

<script type="application/json" id="hero-data">${jsonForScript(heroData)}</script>
<script type="application/json" id="theme-spec">${jsonForScript(themeSpec)}</script>

<main>
${sectionsHtml}
</main>

<footer>
  <div class="wrap">
    <div class="f-mark">IDC</div>
    <div class="f-line">Generated <em>${esc(generated)}Z</em> &middot; Evidence: <em>${evidencedGates}/${allGates.length} gates carry evidence &middot; ${passedGates} passed${lastGateRun ? ` &middot; last run ${esc(lastGateRun)}` : ""}</em> &middot; Design system: <em>Signal</em> &middot; Theme: <em>${esc(theme.name)}</em><br>GENERATED by ops/mission/render-sotu.mjs from state.json — do not hand-edit.
    To update: edit state.json, run <code>node ops/mission/render-sotu.mjs --enhanced</code>, commit both.</div>
  </div>
</footer>

<div id="tip" role="status" aria-live="polite"></div>

<script>
/* fail-safe: if anything below throws, never leave content hidden */
window.addEventListener("error", function(){
  document.body.classList.remove("armed");
  document.querySelectorAll(".reveal,.v-timeline").forEach(function(e){ e.classList.add("in"); });
});
</script>
<script>${clientScript}</script>
</body>
</html>
`;
}

const html = enhanced ? renderEnhanced() : renderStandard();
writeFileSync(outPath, html.replace(/[\t ]+$/gm, ""));
console.log(`Rendered ${outPath}`);
console.log(`  presentation: ${enhanced ? "enhanced" : "standard"}`);
console.log(`  phases: ${phases.length}, tasks: ${doneTasks}/${allTasks.length}, gates passed: ${passedGates}/${allGates.length}, PRs: ${prLog.length}`);
