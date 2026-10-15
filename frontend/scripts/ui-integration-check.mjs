// Read-only real persisted API checks, then explicitly stubbed failure/progress checks.
import assert from 'node:assert/strict'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { chromium } from 'playwright-core'

const base = process.env.CHECK_URL || 'http://127.0.0.1:5174'
const output = '../evals/results/I01.16-ui'
const token = (await readFile('../.env.token.quick-demo.local', 'utf8')).trim()
const result = { label: 'Actual Chrome and read-only persisted synthetic API; labelled browser stubs; no model run or decisions', base, checks: [], errors: [] }
await mkdir(output, { recursive: true })
const browser = await chromium.launch({ executablePath: '/usr/bin/google-chrome', headless: true })
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } })
page.on('pageerror', error => result.errors.push(error.name))
try {
  await page.goto(base)
  await page.getByText('SAMPLE DATA', { exact: true }).waitFor()
  await page.getByLabel('Officer token').fill('invalid-ui-check')
  await page.getByRole('button', { name: 'Open review desk' }).click()
  await page.getByRole('alert').filter({ hasText: 'Credential missing or invalid' }).waitFor()
  assert.equal(await page.getByRole('button', { name: 'Refresh status' }).count(), 0)
  await page.getByLabel('Officer token').fill(token)
  await page.getByRole('button', { name: 'Open review desk' }).click()
  await page.getByRole('heading', { name: 'Comparison request' }).waitFor()
  await page.locator('.inbox-item').first().click()
  await page.getByRole('heading', { name: 'Draft version 1' }).waitFor()
  const id = await page.locator('.run-id').innerText()
  const get = suffix => page.evaluate(async ({ id, token, suffix }) => {
    const r = await fetch(`/api/v1/runs/${id}${suffix}`, { headers: { Authorization: `Bearer ${token}` } })
    if (!r.ok) throw new Error(`HTTP ${r.status}`)
    return r.json()
  }, { id, token, suffix })
  const run = await get(''), draft = await get('/draft')
  assert.equal(run.status, 'PENDING_REVIEW')
  assert((await page.locator('.timeline').innerText()).includes('EAT'))
  assert((await page.locator('.draft-meta').innerText()).includes(draft.content_hash))
  const summary = await page.locator('.comparison-summary').innerText()
  assert(summary.includes(`${draft.content.calculation.quantity} kg`))
  await page.getByLabel('Farmer quantity').fill('17')
  assert.equal(await page.locator('.comparison-summary').innerText(), summary)
  for (const market of run.comparison.markets) {
    const card = page.locator('article.market').filter({ has: page.getByRole('heading', { name: market.market, exact: true }) })
    for (const value of [market.gross_proceeds, market.total_cost, market.estimated_net_proceeds]) assert((await card.innerText()).includes(value))
    assert.equal(Number(market.gross_proceeds) - Number(market.total_cost), Number(market.estimated_net_proceeds))
  }
  await page.getByText('Demo reviewer identity:', { exact: true }).waitFor()
  result.checks.push('Real API: invalid/valid authentication, pending draft, exact hash, EAT timestamps, server monetary values, recorded quantity independent of request input')
  assert.equal(await page.locator('.execution-trace').getAttribute('open'), null)
  await page.getByText(`Execution trace ·`, { exact: false }).click()
  await page.locator('.tool-event').first().waitFor()
  await page.getByText(`Execution trace ·`, { exact: false }).click()
  assert((await page.getByRole('heading', { name: 'Draft version 1' }).boundingBox()).y < (await page.getByRole('heading', { name: 'Live tool activity' }).boundingBox()).y)
  result.checks.push('Persisted trace expands on demand; draft review appears before completed tool log')
  for (const width of [1440, 1024, 768, 390, 320]) {
    await page.setViewportSize({ width, height: 1000 })
    await page.evaluate(() => document.fonts.ready)
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `Overflow at ${width}`)
    if (width <= 900) {
      assert((await page.locator('.pending-panel').boundingBox()).y > (await page.getByRole('heading', { name: 'Market options' }).boundingBox()).y)
    }
    await page.screenshot({ path: `${output}/workspace-${width}.png`, fullPage: true })
  }
  result.checks.push('Actual Chrome responsive layout at 1440/1024/768/390/320; no horizontal overflow; mobile results before inbox')
  // Stub only reads; never send a workflow/decision mutation to the actual backend.
  await page.route(`**/api/v1/runs/${id}`, route => route.fulfill({ json: { workflow_id: id, status: 'FAILED', error_code: 'ui-check-service-unavailable' } }))
  await page.getByText('ui-check-service-unavailable', { exact: true }).waitFor({ timeout: 15000 })
  assert.equal(await page.getByRole('button', { name: 'Approve internal review' }).count(), 0)
  await page.unroute(`**/api/v1/runs/${id}`)
  await page.route(`**/api/v1/runs/${id}`, route => route.fulfill({ json: { workflow_id: id, status: 'RUNNING' } }))
  await page.getByRole('status').filter({ hasText: 'RUNNING' }).first().waitFor({ timeout: 15000 })
  assert(await page.getByRole('button', { name: 'Start comparison' }).isDisabled())
  result.checks.push('Explicit browser stubs: failed run removes stale approval controls; running state disables start')
  await page.emulateMedia({ reducedMotion: 'reduce' })
  assert.equal(await page.locator('.skeleton').first().evaluate(el => getComputedStyle(el).animationName), 'none')
  result.checks.push('Reduced motion disables loading animation')
  assert.equal(result.errors.length, 0)
  await writeFile(`${output}/checks.json`, JSON.stringify(result, null, 2) + '\n')
  console.log('UI integration: real read-only API and labelled browser checks passed')
} finally { await browser.close() }
