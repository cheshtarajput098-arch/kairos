import fs from 'fs';
import http from 'http';
import lighthouse from 'lighthouse';
import puppeteer from 'puppeteer-core';

const targetUrl = process.argv[2] || 'http://host.docker.internal:8765';
const formFactor = process.argv[3] || 'desktop';
const outPath = process.argv[4] || `./docs/lighthouse/${formFactor}`;

console.log(`Auditing ${targetUrl} for ${formFactor}...`);

// 1. Fetch browser version from host with Host: localhost header
function fetchVersion() {
  return new Promise((resolve, reject) => {
    const req = http.request({
      host: 'host.docker.internal',
      port: 9222,
      path: '/json/version',
      headers: { Host: '127.0.0.1:9222' }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(new Error(`Failed to parse: ${data}`));
        }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

const versionData = await fetchVersion();
let wsEndpoint = versionData.webSocketDebuggerUrl;
// Ensure port 9222 is present and host is host.docker.internal
wsEndpoint = wsEndpoint.replace('ws://localhost/', 'ws://localhost:9222/');
wsEndpoint = wsEndpoint.replace(/localhost|127\.0\.0\.1/, 'host.docker.internal');
console.log(`Connecting to Chrome at ${wsEndpoint}...`);

const browser = await puppeteer.connect({
  browserWSEndpoint: wsEndpoint,
  defaultViewport: null,
  headers: { Host: '127.0.0.1:9222' },
});

try {
  const flags = {
    port: 9222,
    output: ['json', 'html'],
    onlyCategories: ['performance', 'accessibility', 'best-practices'],
    formFactor: formFactor,
    screenEmulation: formFactor === 'desktop'
      ? { mobile: false, width: 1350, height: 940, deviceScaleFactor: 1, disabled: false }
      : { mobile: true, width: 390, height: 844, deviceScaleFactor: 2, disabled: false },
  };

  const runnerResult = await lighthouse(targetUrl, flags, undefined, browser.pages ? (await browser.pages())[0] : undefined);

  if (runnerResult) {
    const reportJson = runnerResult.report[0];
    const reportHtml = runnerResult.report[1];
    fs.writeFileSync(`${outPath}.report.json`, reportJson);
    fs.writeFileSync(`${outPath}.report.html`, reportHtml);

    const scores = runnerResult.lhr.categories;
    console.log(`\nLighthouse Scores for ${formFactor}:`);
    console.log(`  Performance:    ${Math.round((scores.performance?.score || 0) * 100)}/100`);
    console.log(`  Accessibility:  ${Math.round((scores.accessibility?.score || 0) * 100)}/100`);
    console.log(`  Best Practices: ${Math.round((scores['best-practices']?.score || 0) * 100)}/100`);
  }
} finally {
  await browser.disconnect();
}
