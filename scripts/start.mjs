import { spawnSync } from "node:child_process";
import { accessSync, constants } from "node:fs";
import { join } from "node:path";
import process from "node:process";

const root = process.cwd();
const python = join(
  root,
  ".venv",
  process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
);
const frontend = join(root, "frontend", "dist", "index.html");

try {
  accessSync(python, constants.X_OK);
  accessSync(frontend, constants.R_OK);
} catch {
  console.error("\nProduction uygulaması henüz hazır değil.");
  console.error("Önce README'deki ilk kurulum adımlarını uygulayın ve `npm run build` çalıştırın.");
  process.exit(1);
}

console.log("\nYerel RAG açılıyor: http://127.0.0.1:8765\n");
const result = spawnSync(python, ["web_app.py"], {
  cwd: root,
  stdio: "inherit",
});
process.exit(result.status ?? 1);
