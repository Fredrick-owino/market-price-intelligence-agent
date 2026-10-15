// Actual isolated public-demo login; no requests, model runs or review decisions.
import assert from 'node:assert/strict'
import { mkdir, writeFile } from 'node:fs/promises'
import { chromium } from 'playwright-core'

const base = 'http://127.0.0.1:8002'
const output = '../evals/results/I01.16-public-demo'
await mkdir(output, { recursive: true })
const browser = await chromium.launch({ executablePath: '/usr/bin/google-chrome', headless: true })
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } })
const errors = []
page.on('pageerror', error => errors.push(error.name))
try {
  await page.goto(base)
  await page.getByRole('button', { name: 'Try the demo' }).waitFor()
  assert.equal(await page.getByRole('button', { name: 'Use demo token' }).count(), 0)
  await page.getByLabel('Officer token').focus()
  await page.getByText('Demo token: SOKO-DEMO', { exact: true }).waitFor()
  await page.getByText('Demo decisions are not verified officer approvals.', { exact: false }).waitFor()
  for (const width of [1440, 390]) {
    await page.setViewportSize({ width, height: 1000 })
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth))
    await page.screenshot({ path: `${output}/help-${width}.png`, fullPage: true })
  }
  await page.getByRole('button', { name: 'Use demo token' }).click()
  assert.equal(await page.getByLabel('Officer token').inputValue(), 'SOKO-DEMO')
  await page.getByRole('button', { name: 'Open review desk' }).click()
  await page.getByRole('heading', { name: 'Comparison request' }).waitFor()
  await page.getByText('test:public-demo', { exact: true }).waitFor()
  await page.getByText('No pending drafts in your permitted workflows.', { exact: true }).waitFor()
  assert.equal((await page.request.get(`${base}/api/v1/drafts/pending`)).status(), 401)
  assert.equal((await page.request.get(`${base}/api/v1/runs/quick-demo-private`, { headers: { Authorization: 'Bearer SOKO-DEMO' } })).status(), 403)
  await page.reload()
  await page.getByLabel('Officer token').waitFor()
  assert.equal(await page.getByLabel('Officer token').inputValue(), '')
  assert.equal(errors.length, 0)
  await writeFile(`${output}/checks.json`, JSON.stringify({
    label: 'Actual isolated local demo login; no model run, request or reviewer decision',
    checked_at: new Date().toISOString(),
    checks: ['Focus reveals sample code and instructions', 'Click fills public demo token', 'Real API login under test:public-demo', 'No existing private drafts visible', 'Anonymous access 401; private workflow 403', 'Refresh clears entered token', 'Desktop/mobile no horizontal overflow'],
    errors,
  }, null, 2) + '\n')
  console.log('Public demo helper: actual Chrome/login/isolation checks passed')
} finally { await browser.close() }
