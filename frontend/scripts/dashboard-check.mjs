import assert from 'node:assert/strict'
import { readFile, writeFile } from 'node:fs/promises'
import { chromium } from 'playwright-core'
const stage = process.env.CHECK_STAGE || 'before'
const base = process.env.CHECK_URL || 'http://127.0.0.1:8000'
const token = (await readFile('../.env.token.quick-demo.local', 'utf8')).trim()
const browser = await chromium.launch({executablePath:'/usr/bin/google-chrome', headless:true})
const page = await browser.newPage({viewport:{width:1440,height:1000}})
const errors=[]
page.on('pageerror', e=>errors.push(e.message.replaceAll(token,'[redacted]')))
try {
 await page.goto(base)
 await page.getByLabel('Officer token').fill(token)
 await page.getByRole('button',{name:'Open review desk'}).click()
 await page.getByRole('heading',{name:'Comparison request'}).waitFor()
 const inbox = page.locator('.inbox-item').first()
 await inbox.click()
 await page.getByRole('heading',{name:'Draft version 1'}).waitFor()
 await page.getByRole('heading',{name:'Market options'}).waitFor()
 const id=await page.locator('.run-id').innerText()
 const api=async suffix=>page.evaluate(async ({url,token})=>{const r=await fetch(url,{headers:{Authorization:`Bearer ${token}`}}); if(!r.ok)throw Error(`HTTP ${r.status}`);return r.json()}, {url:`/api/v1/runs/${id}${suffix}`,token})
 const run=await api(''), draft=await api('/draft')
 const evidence={stage,workflow_id:id,status:run.status,created_at:draft.created_at,source_date:run.comparison.as_of_date,quantity:draft.content.calculation.quantity,errors}
 if(stage==='copy') {
  assert.equal(await page.locator('.hero h1').innerText(), 'A clearer view of the market.\nOfficer judgement.')
  assert.equal(await page.locator('.appbar-id small').innerText(), 'Market intelligence')
  assert((await page.locator('.hero').innerText()).includes('Compare market options, assess costs, and review the evidence before approving an advisory.'))
  assert((await page.locator('.notice').innerText()).includes('SAMPLE DATA'))
  assert((await page.locator('.notice').innerText()).includes('Illustrative prices and costs'))
  assert(!/synthetic|UI I01\.14/i.test(await page.locator('.hero').innerText()))
 }
 if(stage==='after') {
  assert((await page.locator('.timeline').innerText()).includes('EAT'))
  assert((await page.locator('.timeline').innerText()).includes('not available'))
  const text=await page.locator('.comparison-summary').innerText()
  assert(text.includes(`${draft.content.calculation.quantity} kg`))
  await page.getByLabel('Farmer quantity').fill('17')
  assert.equal(await page.locator('.comparison-summary').innerText(), text)
  for(const row of run.comparison.markets){
   const card=page.locator('article.market').filter({has:page.getByRole('heading',{name:row.market,exact:true})})
   const display=await card.innerText()
   for(const value of [row.gross_proceeds,row.total_cost,row.estimated_net_proceeds,row.sellable_kg])assert(display.includes(value))
   assert.equal(Number(row.gross_proceeds)-Number(row.total_cost),Number(row.estimated_net_proceeds))
  }
  assert(text.includes(run.comparison.winner ? `${run.comparison.winner} leads by ${run.comparison.advantage_kes} KES`:'No defensible net winner'))
  evidence.timestamps={started:run.started_at,completed:run.completed_at,decision:run.officer_decision_at}
 }
 for(const [label,width] of [['desktop',1440],['mobile',390]]){
  await page.setViewportSize({width,height:1000})
  await page.screenshot({path:`../evals/results/I01.14-dashboard/${stage}-${label}.png`,fullPage:true})
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Layout overflow')
 }
 if(stage==='after') {
  // Delay a real old-draft response while selecting a different persisted run.
  let releaseOld, oldBlocked
  const holdOld=new Promise(resolve=>{releaseOld=resolve})
  const blocked=new Promise(resolve=>{oldBlocked=resolve})
  await page.route(`**/api/v1/runs/${id}/draft`,async route=>{
   oldBlocked()
   const response=await route.fetch()
   await holdOld
   await route.fulfill({response})
  })
  await blocked
  const nextItem=page.locator('.inbox-item').nth(2)
  const nextId=await nextItem.locator('strong').innerText()
  await nextItem.click()
  await page.getByText(nextId,{exact:true}).first().waitFor()
  const oldResponse=page.waitForResponse(r=>r.url().endsWith(`/runs/${id}/draft`))
  releaseOld()
  await oldResponse
  const nextDraft=await page.evaluate(async({token,id})=>(await fetch(`/api/v1/runs/${id}/draft`,{headers:{Authorization:`Bearer ${token}`}})).json(),{token,id:nextId})
  await page.getByText(`ID ${nextDraft.draft_id}`,{exact:false}).waitFor()
  assert((await page.locator('.comparison-summary').innerText()).includes(`${nextDraft.content.calculation.quantity} kg`))
  assert.equal(await page.locator('.run-id').innerText(),nextId)
  await page.unroute(`**/api/v1/runs/${id}/draft`)
  evidence.selection_check='passed; delayed real previous-draft response cannot replace the newly selected run'
  // A previously recorded decision, read-only; no reviewer action is taken.
  const reviewedId=process.env.CHECK_REVIEW_ID
  if(reviewedId){
   await page.evaluate(id=>sessionStorage.setItem('sokosignal-demo-workflow-id',id),reviewedId)
   await page.reload()
   await page.getByLabel('Officer token').fill(token)
   await page.getByRole('button',{name:'Open review desk'}).click()
   await page.getByText('Approved for internal review only; nothing was delivered.').waitFor()
   const reviewed=await page.evaluate(async({token,id})=>(await fetch(`/api/v1/runs/${id}`,{headers:{Authorization:`Bearer ${token}`}})).json(),{token,id:reviewedId})
   assert(reviewed.officer_decision_at)
   assert((await page.locator('.timeline').innerText()).includes('Officer decision · approve'))
   assert((await page.locator('.timeline').innerText()).includes('EAT'))
   assert.equal(await page.getByRole('button',{name:'Approve internal review'}).count(),0)
   evidence.historical_decision={id:reviewedId,decided_at:reviewed.officer_decision_at,completed_at:reviewed.completed_at}
   await page.setViewportSize({width:1440,height:1000})
   await page.screenshot({path:'../evals/results/I01.14-dashboard/after-recorded-decision.png',fullPage:true})
  }
  // Explicit browser stub tests polling/progress, separate from real persisted evidence.
  await page.route('**/api/v1/runs/*',async route=>{
   if(new URL(route.request().url()).pathname.split('/').length!==5)return route.continue()
   await route.fulfill({json:{workflow_id:id,status:'RUNNING',started_at:'2026-10-14T22:01:02Z'}})
  })
  await page.route('**/api/v1/runs/*/events',route=>route.fulfill({json:{events:[{timestamp:'2026-10-14T22:01:02Z',tool:'browser-progress-stub',server:'synthetic browser test',phase:'started'}]}}))
  await page.getByText('In progress · browser-progress-stub · started',{exact:true}).waitFor({timeout:15000})
  evidence.progress_check='passed; explicitly stubbed browser polling, not a model run'
 }
 assert.equal(errors.length,0)
 await writeFile(`../evals/results/I01.14-dashboard/${stage}.json`,JSON.stringify(evidence,null,2)+'\n')
 console.log(`${stage}: actual Chrome/API checks passed; no workflow or decisions created`)
} finally {await browser.close()}
