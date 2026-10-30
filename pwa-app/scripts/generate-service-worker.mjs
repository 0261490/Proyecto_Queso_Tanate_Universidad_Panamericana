import { createHash } from "node:crypto";
import { readdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const dist = join(root, "dist");

async function filesIn(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = await Promise.all(entries.map((entry) => {
    const path = join(directory, entry.name);
    return entry.isDirectory() ? filesIn(path) : [path];
  }));
  return files.flat();
}

const filePaths = (await filesIn(dist))
  .filter((path) => !path.endsWith("sw.js"))
  .sort();
const files = filePaths.map(
  (path) => `./${relative(dist, path).replaceAll("\\", "/")}`,
);

const cacheHash = createHash("sha256").update(files.join("\n"));
for (const path of filePaths) cacheHash.update(await readFile(path));
const fingerprint = cacheHash.digest("hex").slice(0, 12);
const template = await readFile(join(root, "scripts", "sw-template.js"), "utf8");
const worker = template
  .replace("__CACHE_NAME__", `tenate-${fingerprint}`)
  .replace("__APP_SHELL__", JSON.stringify(files, null, 2));

await writeFile(join(dist, "sw.js"), worker, "utf8");
console.log(`Generated sw.js with ${files.length} precached files.`);
