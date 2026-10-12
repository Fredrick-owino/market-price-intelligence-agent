import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { mkdtemp, readFile, writeFile, mkdir, rm } from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright-core'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')
const base = process.env.SOKOSIGNAL_BROWSER_URL || 'http://127.0.0.1:8000'
const output = path.join(root, 'evals/results/I01.13-browser')
const fixture = JSON.parse(await readFile(path.join(root, 'data/synthetic/I01.7-market-comparison.json')))
const token = (await readFile(path.join(root, '.env.token.local'), 'utf8')).trim()
const profile = await mkdtemp(path.join(os.tmpdir(), 'sokosignal-chrome-'))
const result = {
  label: 'Actual local Chrome UI, backend and model; synthetic test officer',
  chrome: '/usr/bin/google-chrome',
  base,
  started_at: new Date().toISOString(),
  scenarios: [],
  expected_http_failures: [],
  unexpected_http_failures: [],
  browser_page_errors: [],
  browser_console_errors: [],
  screenshots: [],
}
let step = 'launch'
let context
let authenticated = false

const quoteRows = fixture.default_request.quote_ids.map(id => fixture.quotes.find(q => q.quote_id === id))
function expected(quantity) {
  const markets = quoteRows.map(q => ({
    market: q.market,
    gross: quantity * Number(q.price),
    cost: Number(q.transport_total) + Number(q.handling_total) + Number(q.market_fees_total),
    net: quantity * Number(q.price) - Number(q.transport_total) - Number(q.handling_total) - Number(q.market_fees_total),
  }))
  return { markets, winner: [...markets].sort((a, b) => b.net - a.net)[0].market }
}
function amount(n) { return n.toFixed(2) }
async function screenshot(page, name) {
  assert(authenticated, 'No screenshots before sign in')
  const file = `${name}.png`
  await page.screenshot({ path: path.join(output, file), fullPage: true })
  result.screenshots.push(file)
}
async function signIn(page) {
  await page.getByLabel('Officer token').fill(token)
  await page.getByRole('button', { name: 'Open review desk' }).click()
  await page.getByRole('heading', { name: 'Comparison request' }).waitFor()
  authenticated = true
}
async function awaitDraft(page, quantity) {
  const start = Date.now()
  await page.getByRole('heading', { name: 'Draft version 1' }).waitFor({ timeout: 900_000 })
  await page.getByText('PENDING REVIEW', { exact: true }).first().waitFor()
  const scenario = { quantity_kg: quantity, pre_review_seconds: (Date.now() - start) / 1000 }
  result.scenarios.push(scenario)
  const exp = expected(quantity)
  for (const market of exp.markets) {
    const card = page.locator('article.market').filter({ has: page.getByRole('heading', { name: market.market }) })
    assert.equal(await card.locator('.market-price').innerText(), `${amount(market.net)} KES net`)
    assert.match(await card.innerText(), new RegExp(amount(market.gross).replace('.', '\\.') ))
    assert.match(await card.innerText(), new RegExp(amount(market.cost).replace('.', '\\.') ))
  }
  const text = await page.locator('section.full').filter({ has: page.getByRole('heading', { name: 'Market options' }) }).innerText()
  assert(text.includes(`${exp.winner} leads by`))
  assert(text.includes('synthetic://sokosignal/I01.7'))
  const grossLeader = [...exp.markets].sort((a, b) => b.gross - a.gross)[0].market
  assert.notEqual(exp.winner, grossLeader, 'Transport should reverse gross ranking')
  await page.getByRole('heading', { name: 'Source & provenance' }).waitFor()
  assert((await page.locator('.evidence').innerText()).includes('actual_public_http_real_mcp'))
  scenario.expected = exp
  scenario.workflow_id = await page.locator('.status').locator('..').locator('.mono').first().innerText()
  scenario.snapshot_sha256 = createHash('sha256').update(await readFile(path.join(root, 'data/synthetic/I01.7-market-comparison.json'))).digest('hex')
  return scenario
}
async function apiDuplicate(page, endpoint, body, acceptedStatus) {
  const response = await page.evaluate(async ({ endpoint, body, token }) => {
    const r = await fetch(endpoint, { method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, body })
    return { status: r.status, value: await r.json() }
  }, { endpoint, body, token })
  assert.equal(response.status, acceptedStatus)
  return response.value
}
try {
  await mkdir(output, { recursive: true })
  context = await chromium.launchPersistentContext(profile, {
    executablePath: '/usr/bin/google-chrome', headless: true,
    viewport: { width: 1440, height: 900 },
    args: ['--no-first-run', '--no-default-browser-check'],
  })
  const page = await context.newPage()
  page.on('pageerror', error => result.browser_page_errors.push(error.name))
  page.on('console', message => { if (message.type() === 'error') result.browser_console_errors.push('console_error') })
  page.on('response', response => {
    if (!response.url().startsWith(`${base}/api/`)) return
    const status = response.status()
    if (status >= 400) {
      const record = { path: new URL(response.url()).pathname, status }
      if ([401, 409].includes(status)) result.expected_http_failures.push(record)
      else result.unexpected_http_failures.push(record)
    }
  })

  step = 'anonymous and invalid authentication'
  await page.goto(base)
  await page.locator('.banner').waitFor()
  await page.getByLabel('Officer token').fill('invalid-browser-test')
  await page.getByRole('button', { name: 'Open review desk' }).click()
  await page.getByRole('alert').getByText('Credential missing or invalid.').waitFor()
  await signIn(page)
  await screenshot(page, '01-desktop-authenticated')

  for (const [index, quantity] of [500, 1000].entries()) {
    step = `start ${quantity} kg actual model workflow`
    if (index) await page.getByRole('button', { name: 'New attempt' }).click()
    await page.getByLabel('Farmer quantity').fill(String(quantity))
    const requestPromise = page.waitForRequest(req => req.url().endsWith('/api/v1/requests') && req.method() === 'POST')
    await page.getByRole('button', { name: 'Start comparison' }).click()
    const request = await requestPromise
    const body = request.postData()
    await page.getByText('The workflow is still running.').waitFor()
    const duplicate = await apiDuplicate(page, '/api/v1/requests', body, 202)
    const scenario = await awaitDraft(page, quantity)
    assert.equal(duplicate.workflow_id, scenario.workflow_id)
    scenario.duplicate_start_status = 202
    await screenshot(page, `${index + 2}-${quantity}kg-draft-desktop`)

    step = `${quantity} kg refresh and review`
    await page.reload()
    authenticated = false
    await signIn(page)
    await page.getByRole('heading', { name: 'Draft version 1' }).waitFor()
    scenario.refresh_restored = true
    const decision = index === 0 ? 'approve' : 'reject'
    const decisionPromise = page.waitForRequest(req => req.url().endsWith('/decisions') && req.method() === 'POST')
    await page.getByRole('button', { name: decision === 'approve' ? 'Approve internal review' : 'Reject draft' }).click()
    const decisionRequest = await decisionPromise
    await page.getByText(decision === 'approve' ? 'Approved for internal review only; nothing was delivered.' : 'Rejected; nothing was delivered.').waitFor({ timeout: 30_000 })
    const duplicateDecision = await apiDuplicate(page, new URL(decisionRequest.url()).pathname, decisionRequest.postData(), 200)
    scenario.decision = decision
    scenario.duplicate_decision_outcome = duplicateDecision.outcome
    await screenshot(page, `${index + 4}-${quantity}kg-${decision}-desktop`)
  }

  step = 'narrow screen and failed retrieval'
  await page.setViewportSize({ width: 390, height: 844 })
  await screenshot(page, '06-narrow-final')
  const dimensions = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, innerWidth }))
  assert(dimensions.scrollWidth <= dimensions.innerWidth + 1, 'Narrow layout overflows viewport')
  result.narrow_viewport = dimensions
  await page.route('**/api/v1/drafts/pending', route => route.abort('failed'))
  await page.reload()
  authenticated = false
  await page.getByLabel('Officer token').fill(token)
  await page.getByRole('button', { name: 'Open review desk' }).click()
  await page.getByRole('alert').waitFor()
  await page.unroute('**/api/v1/drafts/pending')
  await signIn(page)
  result.failed_request_recovered = true
  result.completed_at = new Date().toISOString()
  result.status = 'passed'
} catch (error) {
  result.status = 'failed'
  result.failed_step = step
  result.error_type = error?.name || 'Error'
  result.error_summary = String(error?.message || '').split('\n')[0].replaceAll(token, '[redacted]')
  process.exitCode = 1
} finally {
  if (context) await context.close()
  await rm(profile, { recursive: true, force: true })
  await mkdir(output, { recursive: true })
  await writeFile(path.join(output, 'result.json'), `${JSON.stringify(result, null, 2)}\n`)
  console.log(`Browser check ${result.status} at ${step}; sanitized result: ${path.relative(root, path.join(output, 'result.json'))}`)
}
