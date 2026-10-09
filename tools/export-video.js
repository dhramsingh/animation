// Export an animation page to MP4 (1280x720, 30 fps) by seeking every frame.
// Needs: Node with the `playwright` package, and ffmpeg on PATH.
// usage: node tools/export-video.js videos/01-query-key-dot-product.html exports/01-query-key-dot-product.mp4 [fps]
// Set CHROME_PATH to use an existing Chromium binary instead of Playwright's bundled one.
const path = require('path');
const { spawn } = require('child_process');
const { once } = require('events');
const { chromium } = require('playwright');

(async () => {
  const [html, out, fpsArg] = process.argv.slice(2);
  if (!html || !out) throw new Error('usage: node tools/export-video.js <page.html> <out.mp4> [fps]');
  const fps = Number(fpsArg || 30);
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--no-sandbox', '--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => console.error('page error:', e.message));
  await page.goto('file://' + path.resolve(html) + '?video=1', { waitUntil: 'load' });
  await page.waitForFunction(() => window.Kit && window.Kit.total > 0);
  const { total, w, h } = await page.evaluate(() => { Kit.seek(0); const c = document.querySelector('canvas'); return { total: Kit.total, w: c.width, h: c.height }; });
  if (w !== 1280 || h !== 720) throw new Error(`unexpected canvas size ${w}x${h}`);

  const frames = Math.ceil((total * fps) / 1000);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '23', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path.resolve(out)],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  const finished = new Promise((res, rej) => ff.on('close', (code) => (code === 0 ? res() : rej(new Error('ffmpeg exited ' + code)))));

  for (let i = 0; i < frames; i++) {
    const ms = (i * 1000) / fps;
    const b64 = await page.evaluate((t) => { Kit.seek(t); return document.querySelector('canvas').toDataURL('image/jpeg', 0.95).split(',')[1]; }, ms);
    if (!ff.stdin.write(Buffer.from(b64, 'base64'))) await once(ff.stdin, 'drain');
  }
  ff.stdin.end();
  await finished;
  await browser.close();
  console.log(`wrote ${out} (${frames} frames)`);
})().catch((e) => { console.error(e); process.exit(1); });
