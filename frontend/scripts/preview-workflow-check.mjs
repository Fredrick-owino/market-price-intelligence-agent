// Actual local model/MCP verification. No routes, mocks, replay or cached tool outputs.
import assert from 'node:assert/strict'
import {readFile, writeFile} from 'node:fs/promises'
import {randomUUID} from 'node:crypto'
import {chromium} from 'playwright-core'
const base='http://127.0.0.1:8001'
const token=(await readFile('../.env.token.quick-demo.local','utf8')).trim()
const stamp=new Date().toISOString().replaceAll(':','-')
const output=`../evals/results/I01.14-preview-workflow/${stamp}`
const record={label:'Actual Qwen/model and real borrowed/own MCP; automated authenticated demo-officer verification, no independent human review',base,started_at:new Date().toISOString(),quantity_kg:650,submitted:false,committed:false,phase:'launch',screenshots:[],progress:[]}
const browser=await chromium.launch({executablePath:'/usr/bin/google-chrome',headless:true})
const context=await browser.newContext({viewport:{width:1440,height:1000}})
const page=await context.newPage()
const errors=[]
page.on('pageerror',e=>errors.push(e.name))
const api=async(path,options={},credential=token)=>{
 const response=await context.request.fetch(`${base}${path}`,{...options,headers:{Authorization:`Bearer ${credential}`,'Content-Type':'application/json'}})
 return {status:response.status(),value:await response.json()}
}
const screenshot=async(label)=>{
 assert.equal(await page.getByLabel('Officer token').count(),0)
 const filename=`${output}-${label}.png`
 await page.screenshot({path:filename,fullPage:true})
 record.screenshots.push(filename.replace('../',''))
}
const eat=value=>new Intl.DateTimeFormat('en-GB',{day:'2-digit',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23',timeZone:'Africa/Nairobi'}).format(new Date(value))+' EAT'
try{
 record.phase='authentication'
 assert.equal((await api('/api/v1/drafts/pending',{},'invalid-preview-test')).status,401)
 await page.goto(base)
 await page.getByLabel('Officer token').fill(token)
 await page.getByRole('button',{name:'Open review desk'}).click()
 await page.getByRole('heading',{name:'Comparison request'}).waitFor()
 const identity=await api('/api/v1/drafts/pending')
 assert.equal(identity.status,200)
 assert.equal(identity.value.reviewer.demo,true)
 record.reviewer=identity.value.reviewer
 record.phase='fresh model/MCP request'
 await page.getByLabel('Farmer quantity').fill('650')
 const started=Date.now()
 const startResponse=page.waitForResponse(r=>r.url().endsWith('/api/v1/requests')&&r.request().method()==='POST')
 await page.getByRole('button',{name:'Start comparison'}).click()
 const response=await startResponse
 assert.equal(response.status(),202)
 const start=await response.json()
 record.workflow_id=start.workflow_id
 const path=`/api/v1/runs/${start.workflow_id}`
 const deadline=Date.now()+900000
 let count=-1, pending
 while(Date.now()<deadline){
  const run=await api(path),activity=await api(`${path}/events`)
  assert.equal(run.status,200)
  assert(run.value.started_at)
  if(activity.value.events.length!==count){
   count=activity.value.events.length
   const latest=activity.value.events.at(-1)
   record.progress.push({status:run.value.status,event_count:count,latest:latest?{tool:latest.tool,phase:latest.phase,timestamp:latest.timestamp}:null})
   console.log(`Preview verification: ${run.value.status}; ${count} real events${latest?`; ${latest.tool} ${latest.phase}`:''}`)
  }
  if(run.value.status==='FAILED'){record.failed_run=run.value;throw Error(`Workflow failed: ${run.value.error_code}`)}
  if(run.value.status==='PENDING_REVIEW'){pending=run.value;break}
  await page.waitForTimeout(1000)
 }
 assert(pending,'No review pause before deadline')
 record.request_to_review_seconds=(Date.now()-started)/1000
 record.phase='pending draft and actual events'
 const draft=(await api(`${path}/draft`)).value
 assert.equal(draft.status,'PENDING_REVIEW')
 assert.equal(pending.advisory_created_at,draft.created_at)
 assert.equal(pending.completed_at,null)
 assert.equal(pending.officer_decision_at,null)
 const activity=(await api(`${path}/events`)).value.events
 const tools=activity.filter(e=>e.phase==='completed'&&e.server!=='local pinned Qwen').map(e=>e.tool)
 assert.deepEqual(tools,['fetch','search_market_quotes','compare_market_options','save_advisory_draft'])
 const choices=activity.filter(e=>e.tool==='model selection'&&e.phase==='completed').map(e=>e.output.selected_tool)
 assert.deepEqual(choices,['search_market_quotes','compare_market_options','save_advisory_draft'])
 for(const event of activity)assert(Number.isFinite(Date.parse(event.timestamp)))
 assert.equal(pending.comparison.retrieval_provenance.evidence_mode,'actual_public_http_real_mcp')
 assert.equal(pending.comparison.as_of_date,'2026-10-10')
 record.pending=pending
 record.draft={draft_id:draft.draft_id,version:draft.version,content_hash:draft.content_hash,created_at:draft.created_at}
 record.events=activity
 await page.getByRole('heading',{name:'Draft version 1'}).waitFor({timeout:15000})
 const timeline=await page.locator('.timeline').innerText()
 assert(timeline.includes(eat(pending.started_at)))
 assert(timeline.includes(eat(draft.created_at)))
 assert((await page.locator('.comparison-summary').innerText()).includes('Recorded input: 650 kg'))
 for(const [market,gross,cost,net] of [['Market A','26000.00','2000.00','24000.00'],['Market B','29250.00','8000.00','21250.00']]){
  const card=page.locator('article.market').filter({has:page.getByRole('heading',{name:market,exact:true})})
  for(const amount of [gross,cost,net])assert((await card.innerText()).includes(amount))
 }
 await screenshot('pending-desktop')
 record.phase='approval safeguards and authenticated exact draft approval'
 const decisionBody={draft_id:draft.draft_id,version:draft.version,content_hash:draft.content_hash,decision:'approve',idempotency_key:`preview-check-${randomUUID()}`,note:'Automated preview verification; internal demo review only.'}
 assert.equal((await api(`${path}/decisions`,{method:'POST',data:decisionBody},'invalid-preview-test')).status,401)
 assert.equal((await api(`${path}/decisions`,{method:'POST',data:{...decisionBody,content_hash:'0'.repeat(64)}})).status,409)
 assert.equal((await api(`${path}/draft`)).value.status,'PENDING_REVIEW')
 await page.getByLabel('Decision note').fill(decisionBody.note)
 const decisionResponse=page.waitForResponse(r=>r.url().endsWith(`${path}/decisions`)&&r.request().method()==='POST')
 await page.getByRole('button',{name:'Approve internal review'}).click()
 const decided=await decisionResponse
 assert.equal(decided.status(),200)
 const decision=await decided.json()
 assert.equal(decision.decision.reviewer_id,record.reviewer.id)
 assert.equal(decision.decision.content_hash,draft.content_hash)
 assert.equal(decision.decision.version,draft.version)
 assert.equal(decision.outcome,'approved_internal_review')
 await page.getByText('Approved for internal review only; nothing was delivered.').waitFor()
 const completed=(await api(path)).value
 assert.equal(completed.status,'COMPLETED')
 assert(completed.completed_at)
 assert.equal(completed.started_at,pending.started_at)
 assert.equal(completed.advisory_created_at,draft.created_at)
 assert.equal(completed.officer_decision_at,decision.decision.decided_at)
 assert(Date.parse(completed.started_at)<=Date.parse(draft.created_at))
 assert(Date.parse(draft.created_at)<=Date.parse(completed.officer_decision_at))
 assert(Date.parse(completed.officer_decision_at)<=Date.parse(completed.completed_at))
 assert.equal((await api(path)).value.completed_at,completed.completed_at)
 const completedTimeline=await page.locator('.timeline').innerText()
 assert(completedTimeline.includes(eat(completed.completed_at)))
 assert(completedTimeline.includes(eat(completed.officer_decision_at)))
 assert.equal(await page.getByRole('button',{name:'Approve internal review'}).count(),0)
 record.completed=completed
 record.decision=decision
 record.request_to_approval_seconds=(Date.now()-started)/1000
 record.errors=errors
 assert.equal(errors.length,0)
 await screenshot('approved-desktop')
 await page.setViewportSize({width:390,height:1000})
 await screenshot('approved-mobile')
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth))
 record.status='passed'
 record.phase='completed actual verification'
 console.log(`Preview verified: ${record.workflow_id}; review ${record.request_to_review_seconds}s; approval ${record.request_to_approval_seconds}s`)
}catch(error){
 record.status='failed'
 record.error_type=error.name
 record.error_summary=String(error.message).split('\n')[0].replaceAll(token,'[redacted]')
 process.exitCode=1
 console.log(`Preview verification failed at ${record.phase}: ${record.error_summary}`)
}finally{
 record.finished_at=new Date().toISOString()
 await browser.close()
 await writeFile(`${output}.json`,JSON.stringify(record,null,2)+'\n')
 console.log(`Sanitized evidence: ${output}.json`)
}
