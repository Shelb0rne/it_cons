import http from "http";
import { readFileSync, existsSync } from "fs";
import { resolve } from "path";

const PORT = process.env.PORT || 5173;
const INDEX = resolve(".", "index.html");

const server = http.createServer((req, res) => {
  if (!existsSync(INDEX)) {
    res.writeHead(500, { "Content-Type": "text/plain" });
    res.end("index.html not found");
    return;
  }

  const html = readFileSync(INDEX, "utf8");
  res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
  res.end(html);
});

server.listen(PORT, () => {
  console.log(`Frontend listening on http://localhost:${PORT}`);
});
