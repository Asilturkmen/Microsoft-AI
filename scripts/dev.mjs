import { spawn } from "node:child_process";
import { accessSync, constants } from "node:fs";
import { join } from "node:path";
import process from "node:process";

const root = process.cwd();
const python = join(
  root,
  ".venv",
  process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
);
const vite = join(
  root,
  "frontend",
  "node_modules",
  ".bin",
  process.platform === "win32" ? "vite.cmd" : "vite",
);

function requireExecutable(path, help) {
  try {
    accessSync(path, constants.X_OK);
  } catch {
    console.error(`\nBaşlatılamadı: ${path} bulunamadı.`);
    console.error(help);
    process.exit(1);
  }
}

requireExecutable(
  python,
  "Önce Python ortamını kurun: python3.12 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt",
);
requireExecutable(vite, "Önce frontend bağımlılıklarını kurun: cd frontend && npm install");

console.log("\nYerel RAG geliştirme ortamı başlatılıyor…");
console.log("API: http://127.0.0.1:8765");
console.log("UI:  http://127.0.0.1:5173\n");

const api = spawn(python, ["web_app.py"], { cwd: root, stdio: "inherit" });
const ui = spawn(vite, [], { cwd: join(root, "frontend"), stdio: "inherit" });
const children = [api, ui];
let stopping = false;

function stop(exitCode = 0) {
  if (stopping) return;
  stopping = true;
  for (const child of children) {
    if (!child.killed) child.kill("SIGTERM");
  }
  process.exitCode = exitCode;
}

process.on("SIGINT", () => stop(0));
process.on("SIGTERM", () => stop(0));

for (const child of children) {
  child.on("error", (error) => {
    console.error(`Geliştirme süreci başlatılamadı: ${error.message}`);
    stop(1);
  });
  child.on("exit", (code, signal) => {
    if (!stopping) {
      if (code !== 0) {
        console.error(`Bir geliştirme süreci beklenmedik biçimde durdu (${signal ?? code}).`);
      }
      stop(code ?? 1);
    }
  });
}
