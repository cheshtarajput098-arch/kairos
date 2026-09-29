import fs from 'fs';
import http from 'http';
import puppeteer from 'puppeteer-core';

function fetchVersion() {
  return new Promise((resolve, reject) => {
    const req = http.request(
      {
        host: 'host.docker.internal',
        port: 9222,
        path: '/json/version',
        headers: { Host: '127.0.0.1:9222' },
      },
      (res) => {
        let data = '';
        res.on('data', (chunk) => (data += chunk));
        res.on('end', () => {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(new Error(`Failed to parse: ${data}`));
          }
        });
      }
    );
    req.on('error', reject);
    req.end();
  });
}

const versionData = await fetchVersion();
let wsEndpoint = versionData.webSocketDebuggerUrl;
wsEndpoint = wsEndpoint.replace('ws://localhost/', 'ws://localhost:9222/');
wsEndpoint = wsEndpoint.replace(/localhost|127\.0\.0\.1/, 'host.docker.internal');
console.log(`Connecting to Chrome at ${wsEndpoint}...`);

const browser = await puppeteer.connect({
  browserWSEndpoint: wsEndpoint,
  defaultViewport: null,
  headers: { Host: '127.0.0.1:9222' },
});

const baseUrl = process.argv[2] || 'http://127.0.0.1:8765';
const outDir = '/app/docs/screenshots';
fs.mkdirSync(outDir, { recursive: true });

const axeScript = fs.readFileSync('/app/web/node_modules/axe-core/axe.min.js', 'utf8');

const screenshots = [
  { name: 'board_06_home_desktop.png', url: `${baseUrl}/?tab=ask`, width: 1440, height: 900 },
  { name: 'board_06_home_mobile.png', url: `${baseUrl}/?tab=ask`, width: 390, height: 844 },
  { name: 'board_07_conversation_desktop.png', url: `${baseUrl}/?mode=conversation`, width: 1440, height: 900 },
  { name: 'board_07_conversation_mobile.png', url: `${baseUrl}/?mode=conversation`, width: 390, height: 844 },
  { name: 'board_08_sources_desktop.png', url: `${baseUrl}/?tab=sources`, width: 1440, height: 900 },
  { name: 'board_08_sources_mobile.png', url: `${baseUrl}/?tab=sources`, width: 390, height: 844 },
  { name: 'board_09_traces_desktop.png', url: `${baseUrl}/?tab=traces`, width: 1440, height: 900 },
  { name: 'board_09_traces_mobile.png', url: `${baseUrl}/?tab=traces`, width: 390, height: 844 },
  { name: 'mid_answer_scenario_1.png', url: `${baseUrl}/?mid_answer=true`, width: 1440, height: 900 },
];

let axeViolationsTotal = 0;

for (const item of screenshots) {
  const page = await browser.newPage();
  await page.setViewport({ width: item.width, height: item.height });
  await page.goto(item.url, { waitUntil: 'networkidle2' });
  await new Promise((r) => setTimeout(r, 600));

  // Run Axe accessibility check on desktop screens
  if (item.width === 1440 && !item.name.includes('mid_answer')) {
    await page.evaluate(axeScript);
    const axeResults = await page.evaluate(() =>
      axe.run({ runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa'] } })
    );
    const violations = axeResults.violations || [];
    console.log(`Axe check on ${item.name}: ${violations.length} violations`);
    if (violations.length > 0) {
      console.error(violations.map((v) => `${v.id}: ${v.description}`));
      // Filter out non-serious issues if any
      const serious = violations.filter(
        (v) => v.impact === 'serious' || v.impact === 'critical'
      );
      axeViolationsTotal += serious.length;
    }
  }

  const dest = `${outDir}/${item.name}`;
  await page.screenshot({ path: dest });
  console.log(`Saved screenshot: ${dest} (${item.width}x${item.height})`);
  await page.close();
}

await browser.disconnect();

console.log(`\nAll screenshots captured. Total axe-core violations: ${axeViolationsTotal}`);
if (axeViolationsTotal > 0) {
  process.exit(1);
}
