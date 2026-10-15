// Local-only edited evidence video. Auth happens before any captured frame.
import assert from 'node:assert/strict'
import { readFile, writeFile, mkdir } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { spawn, execFileSync } from 'node:child_process'
import { once } from 'node:events'
import { chromium } from 'playwright-core'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')
const attempt = new Date().toISOString().replaceAll(':', '-').replaceAll('.', '-')
const out = path.join(root, `.state/video/I01.13-local-demo-${attempt}`)
await mkdir(out, { recursive: true, mode: 0o700 })
const frames = path.join(out, 'frames')
await mkdir(frames, { mode: 0o700 })
const token = (await readFile(path.join(root, '.env.token.quick-demo.local'), 'utf8')).trim()
const base = 'http://127.0.0.1:8000'
const apiLog = path.join(root, '.state/api-restored.local.log')
const ffmpeg = path.join(root, '.cache/playwright/ffmpeg-1013/ffmpeg-linux')
const fps = 4
let index = 0, liveStart = 0, workflow = '', requestBody = null, logOffset = 0
const scenes = [], trace = [], pageErrors = []
const revision = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim()
const browser = await chromium.launch({ executablePath: '/usr/bin/google-chrome', headless: true })
const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } })
const page = await context.newPage()
page.on('pageerror', error => pageErrors.push(error.name))
async function caption(title, text, tool = '') {
  await page.evaluate(({ title, text, tool, elapsed }) => {
    document.querySelector('#record-title').textContent = title
    document.querySelector('#record-text').textContent = text
    document.querySelector('#record-tool').textContent = tool
    document.querySelector('#record-time').textContent = elapsed === null ? 'Before request start' : `Actual elapsed since request: ${elapsed.toFixed(1)} seconds`
  }, { title, text, tool, elapsed: liveStart ? (Date.now() - liveStart) / 1000 : null })
}
async function capture(seconds, title, text, tool = '') {
  const first = index
  for (let n = 0; n < seconds * fps; n++) {
    await caption(title, text, tool)
    await page.screenshot({ path: path.join(frames, `${String(index++).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 85 })
    await page.waitForTimeout(1000 / fps)
  }
  scenes.push({ title, first_frame: first, last_frame: index - 1 })
}
function events(raw) {
  return raw.split('\n').filter(x => x.startsWith('{')).flatMap(x => { try { return [JSON.parse(x)] } catch { return [] } })
}
let result
try {
  await page.goto(base)
  await page.getByLabel('Officer token').fill(token)
  await page.getByRole('button', { name: 'Open review desk' }).click()
  await page.getByRole('heading', { name: 'Comparison request' }).waitFor()
  // Sign-in form is absent before recording. Never capture credentials or headers.
  assert.equal(await page.getByLabel('Officer token').count(), 0)
  await page.evaluate(() => {
    const box = document.createElement('div')
    box.id = 'record-caption'
    box.style.cssText = 'position:fixed;bottom:0;left:0;right:0;height:232px;padding:18px 34px;background:#102d29;color:#fff;z-index:9999;font:20px/1.45 Arial;box-sizing:border-box;border-top:4px solid #e4b66a'
    box.innerHTML = '<div style="color:#f3d89d;font-size:16px;font-weight:bold">LOCAL SYNTHETIC DEMO · EDITED: WAITING SHORTENED · NO REMOTE EXPOSURE</div><div id="record-title" style="font-size:25px;font-weight:bold"></div><div id="record-text"></div><div id="record-tool" style="font:16px/1.5 monospace;color:#c9ede3"></div><div id="record-time" style="font-size:15px;color:#c9ede3"></div>'
    document.body.append(box)
    document.body.style.paddingBottom = '260px'
  })
  await page.getByLabel('Farmer quantity').fill('500')
  await capture(10, 'SokoSignal — Agriculture market comparison', 'Actual local browser, pinned Qwen model and MCP servers. Markets, maize prices, costs and capacity are invented. Partner institution and practitioner remain unconfirmed.')
  await page.getByRole('heading', { name: 'Comparison request' }).scrollIntoViewIfNeeded()
  await capture(8, 'One bounded 500 kg request', 'Software calculates comparable gross and net proceeds. A local synthetic test officer can review an exact draft; the model cannot approve it. Sign-in was completed before capture.')
  const responsePromise = page.waitForResponse(r => r.url() === `${base}/api/v1/requests` && r.request().method() === 'POST')
  logOffset = (await readFile(apiLog, 'utf8')).length
  liveStart = Date.now()
  await page.getByRole('button', { name: 'Start comparison' }).click()
  const response = await responsePromise
  assert.equal(response.status(), 202)
  workflow = (await response.json()).workflow_id
  requestBody = response.request().postDataJSON()
  await page.getByText('The workflow is still running.').waitFor()
  // Verify identical retry and rejection of a distinct overlapping request privately.
  const retry = await context.request.post(`${base}/api/v1/requests`, { headers: { Authorization: `Bearer ${token}` }, data: requestBody })
  assert.equal(retry.status(), 202)
  assert.equal((await retry.json()).workflow_id, workflow)
  const overlapping = await context.request.post(`${base}/api/v1/requests`, { headers: { Authorization: `Bearer ${token}` }, data: { ...requestBody, idempotency_key: requestBody.idempotency_key + '-overlap' } })
  assert.equal(overlapping.status(), 409)
  await capture(8, 'Actual retrieval and model execution', 'One model workflow is active. This run uses real public borrowed Fetch and three own MCP tools. Duplicate start: 202, same run. New overlapping start: 409, no new run.')
  const seen = new Set()
  let completedAt
  while (Date.now() - liveStart < 900000) {
    const logEvents = events((await readFile(apiLog, 'utf8')).slice(logOffset))
    for (const row of logEvents) {
      const key = row.event === 'borrowed_retrieval_verified' ? 'borrowed-fetch' : row.event === 'mcp_call' && !row.is_error ? row.tool : null
      if (!key || seen.has(key)) continue
      seen.add(key)
      const summary = key === 'borrowed-fetch' ? 'Borrowed Fetch: public synthetic fixture hash verified.' : `Own MCP: ${row.tool} returned its actual result.`
      await capture(4, 'Executed tool evidence from this run', summary + ' Intervening waiting is omitted in this edited video.', `${key} · ${row.timestamp} · Actual output: ${JSON.stringify(key === 'borrowed-fetch' ? row.provenance?.sha256 || row.sha256 || 'verified public fixture' : row.output).slice(0, 150)}`)
    }
    if (await page.getByRole('heading', { name: 'Draft version 1' }).count()) {
      completedAt = Date.now()
      break
    }
    if (await page.getByText('The run stopped:').count()) throw new Error('Actual model workflow failed')
    await page.waitForTimeout(1000)
  }
  assert(completedAt, 'No draft within bounded wait')
  const measured = (completedAt - liveStart) / 1000
  const statusResponse = await context.request.get(`${base}/api/v1/runs/${workflow}`, { headers: { Authorization: `Bearer ${token}` } })
  result = await statusResponse.json()
  assert.equal(result.status, 'PENDING_REVIEW')
  assert.equal(result.comparison.markets[0].estimated_net_proceeds, '18000.00')
  assert.equal(result.comparison.markets[1].estimated_net_proceeds, '14500.00')
  for (const tool of ['borrowed-fetch', 'search_market_quotes', 'compare_market_options', 'save_advisory_draft']) assert(seen.has(tool), `Missing actual tool ${tool}`)
  await page.locator('.markets').evaluate(el => el.scrollIntoView({ block: 'start' }))
  await capture(10, `Measured request-to-review: ${measured.toFixed(3)} seconds`, 'Waiting was shortened. This is an edited local demonstration, not an uninterrupted sub-three-minute agent run. Previous browser measurements: 234.38 s and 246.07 s.')
  await capture(14, 'Higher gross does not imply higher net', '500 kg: A gross KES 20,000 − transport 2,000 = net 18,000. B gross 22,500 − transport 8,000 = net 14,500. Market A leads by KES 3,500; fees, handling and loss are explicit zero assumptions.')
  await page.getByRole('heading', { name: 'Draft version 1' }).evaluate(el => el.scrollIntoView({ block: 'start' }))
  await capture(12, 'Private draft, immutable version and source provenance', 'Version 1 is bound to the displayed SHA-256 and pinned fixture. Borrowed retrieval and own tools ran through actual MCP. Values are synthetic; no current-price or buyer-demand claim.')
  await page.getByRole('button', { name: 'Approve internal review' }).scrollIntoViewIfNeeded()
  await capture(12, 'Human review remains pending', 'Approval or rejection requires an authenticated decision on this exact version and hash. No approval is performed in this recording. The earlier owner-test draft also remains untouched. Nothing is delivered to farmers.')
  await capture(10, 'Verified local success; remote completion remains unverified', 'Earlier Chrome tests verified synthetic approval, rejection and refresh. Phone email login was owner-reported; remote officer completion was not verified. The one-hour connector expired and has not been relaunched.')
  await capture(10, 'Remaining submission requirements', 'Named institution and practitioner; eight diverse live evaluations and independent review; fresh-clone setup; exact official cutoff; qualifying video and durable public demonstration link. This file stays local, with no upload or submission.')
  assert.equal(pageErrors.length, 0)
  trace.push(...events((await readFile(apiLog, 'utf8')).slice(logOffset)))
  const sanitized = JSON.stringify(trace)
  assert(!sanitized.includes(token))
  await writeFile(path.join(root, 'evals/results/I01.13-recorded-local-trace.jsonl'), trace.map(x => JSON.stringify(x)).join('\n') + '\n')
  const videoPath = path.join(out, 'sokosignal-local-demo-edited.webm')
  const encoder = spawn(ffmpeg, ['-hide_banner', '-loglevel', 'error', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-r', String(fps), '-i', 'pipe:0', '-c:v', 'libvpx-vp9', '-b:v', '1600k', '-deadline', 'realtime', '-cpu-used', '6', '-an', videoPath], { stdio: ['pipe', 'ignore', 'pipe'] })
  let encoderError = ''
  encoder.stderr.on('data', x => { encoderError += x.toString() })
  const exit = once(encoder, 'close')
  for (let n = 0; n < index; n++) {
    const frame = await readFile(path.join(frames, `${String(n).padStart(5, '0')}.jpg`))
    if (!encoder.stdin.write(frame)) await once(encoder.stdin, 'drain')
  }
  encoder.stdin.end()
  const [code] = await exit
  assert.equal(code, 0, encoderError)
  const evidence = { label: 'Actual local browser/model/MCP; synthetic officer; edited waiting, no decisions', revision, workflow_id: workflow, recorded_at: new Date().toISOString(), quantity_kg: 500, measured_request_to_review_seconds: measured, encoded_duration_seconds: index / fps, frames: index, fps, edited_waiting: true, uninterrupted_competition_video_requirement_met: false, video_local_path: path.relative(root, videoPath), actual_tools: [...seen], identical_retry_status: 202, overlapping_start_status: 409, draft_id: result.draft_id, version: result.version, content_hash: result.content_hash, status: result.status, original_pending_draft_approved: false, decisions_performed: 0, scenes, uploaded: false, submitted: false, audio: 'None; on-screen narration captions' }
  assert(evidence.encoded_duration_seconds < 180)
  await writeFile(path.join(root, 'evals/results/I01.13-local-video.json'), JSON.stringify(evidence, null, 2) + '\n')
  console.log(`Local edited video: ${videoPath}; ${evidence.encoded_duration_seconds}s; actual review latency ${measured}s`)
} catch (error) {
  const failure = { label: 'Failed actual local recording attempt; no success claimed', revision, workflow_id: workflow, recorded_at: new Date().toISOString(), captured_frames: index, error_type: error.name, decision_count: 0, local_frames: path.relative(root, frames), uploaded: false }
  await writeFile(path.join(out, 'failure.local.json'), JSON.stringify(failure, null, 2) + '\n')
  throw error
} finally {
  await context.close()
  await browser.close()
}
