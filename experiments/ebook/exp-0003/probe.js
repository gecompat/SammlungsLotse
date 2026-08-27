"use strict";

const childProcess = require("child_process");
const fs = require("fs");
const path = require("path");

const OUTPUT = "/output";
const ACE = "/opt/ace/node_modules/.bin/ace-puppeteer";

function writeJson(name, value) {
  fs.mkdirSync(OUTPUT, { recursive: true });
  fs.writeFileSync(path.join(OUTPUT, name), `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

function run(command, args) {
  return childProcess.spawnSync(command, args, {
    encoding: "utf8",
    env: process.env,
    maxBuffer: 1024 * 1024,
    stdio: ["ignore", "pipe", "pipe"],
  });
}

function toolVersion() {
  const ace = run(ACE, ["--version"]);
  const node = run("node", ["--version"]);
  const chrome = run(process.env.PUPPETEER_EXECUTABLE_PATH, ["--version"]);
  writeJson("tool-version.json", {
    ace: (ace.stdout || ace.stderr || "").trim(),
    ace_exit_code: ace.status,
    chrome: (chrome.stdout || chrome.stderr || "").trim(),
    chrome_exit_code: chrome.status,
    node: (node.stdout || node.stderr || "").trim(),
    node_exit_code: node.status,
  });
  return ace.status || node.status || chrome.status || 0;
}

function checkEpub() {
  const reportRoot = "/tmp/ace-report";
  const tempRoot = "/tmp/ace-work";
  fs.rmSync(reportRoot, { recursive: true, force: true });
  fs.rmSync(tempRoot, { recursive: true, force: true });
  const completed = run(ACE, [
    "--silent",
    "--force",
    "--doNotReportMedia",
    "--exiterror2",
    "--timeout",
    "30000",
    "--outdir",
    reportRoot,
    "--tempdir",
    tempRoot,
    "/input/input.epub",
  ]);
  const report = path.join(reportRoot, "report.json");
  if (fs.existsSync(report)) {
    fs.writeFileSync(path.join(OUTPUT, "report.json"), fs.readFileSync(report));
  }
  writeJson("control.json", {
    browser_internal_sandbox: false,
    command_profile: "ace-puppeteer-json/v1",
    exit_code: completed.status,
    report_created: fs.existsSync(report),
    stderr_tail: (completed.stderr || "").slice(-5000),
    stdout_tail: (completed.stdout || "").slice(-5000),
  });
  return completed.status === 0 || completed.status === 2 ? 0 : completed.status || 1;
}

let status = 2;
if (process.argv.length === 3 && process.argv[2] === "tool-version") {
  status = toolVersion();
} else if (process.argv.length === 3 && process.argv[2] === "check") {
  status = checkEpub();
}
writeJson("probe-complete.json", { exit_code: status });
// Keep tmpfs evidence available until the host copies it and terminates the
// disposable container, matching the already-qualified EXP-0005 pattern.
Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 300000);
process.exit(status);
