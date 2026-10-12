// Native continuous recording. No trimming, frame substitution or acceleration.
import assert from 'node:assert/strict'
import { readFile, mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright-core'
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..')
const stamp=new Date().toISOString().replaceAll(':','-').replaceAll('.','-')
const output=path.join(root,'.state/continuous-video',stamp)
await mkdir(output,{recursive:true,mode:0o700})
const token=(await readFile(path.join(root,'.env.token.local'),'utf8')).trim()
const browser=await chromium.launch({executablePath:'/usr/bin/google-chrome',headless:true})
const context=await browser.newContext({viewport:{width:1440,height:1000},recordVideo:{dir:output,size:{width:1440,height:1000}}})
// Conceal sign-in before first document paint. Auth still goes to the real API.
await context.route('http://127.0.0.1:8001/',async route=>{
 const response=await route.fetch()
 const html=(await response.text()).replace('<head>','<head><style id="private-signin-curtain">html{opacity:0!important}</style>')
 await route.fulfill({response,body:html})
})
let record={label:'Actual continuous local synthetic model/MCP and authenticated demo approval; no independent practitioner',started_at:new Date().toISOString(),quantity_kg:650,edited:false,model_warming:'Existing pinned model reused after measured rehearsal; no tool results cached or replayed',cuts:0,time_compression:false,substituted_footage:false,uploaded:false,submitted:false}
const start=Date.now()
const page=await context.newPage()
let phase='private sign-in'
try{
 await page.goto('http://127.0.0.1:8001/')
 await page.getByLabel('Officer token').fill(token)
 await page.getByRole('button',{name:'Open review desk'}).click()
 await page.getByRole('heading',{name:'Comparison request'}).waitFor()
 assert.equal(await page.getByLabel('Officer token').count(),0)
 await page.evaluate(()=>document.querySelector('#private-signin-curtain').remove())
 await page.getByLabel('Farmer quantity').fill('650')
 await page.getByLabel('Farmer quantity').scrollIntoViewIfNeeded()
 await page.waitForTimeout(3000)
 phase='actual request/model/tools'
 const responsePromise=page.waitForResponse(r=>r.url().endsWith('/api/v1/requests')&&r.request().method()==='POST')
 const requestStart=Date.now()
 await page.getByRole('button',{name:'Start comparison'}).click()
 const response=await responsePromise
 assert.equal(response.status(),202)
 record.workflow_id=(await response.json()).workflow_id
 const deadline=Date.now()+900000
 while(Date.now()<deadline){
  const events=page.locator('.tool-event')
  if(await events.count())await events.last().scrollIntoViewIfNeeded()
  if(await page.getByRole('heading',{name:'Draft version 1'}).count())break
  if(await page.getByText('The run stopped:').count())throw new Error('Actual workflow failed')
  await page.waitForTimeout(700)
 }
 await page.getByRole('heading',{name:'Draft version 1'}).waitFor({timeout:1000})
 record.request_to_review_seconds=(Date.now()-requestStart)/1000
 phase='comparison and exact pending draft'
 await page.locator('.tool-event').last().evaluate(el=>el.scrollIntoView({block:'center'}))
 await page.waitForTimeout(4000)
 await page.locator('.market-grid').evaluate(el=>el.scrollIntoView({block:'start'}))
 assert.match(await page.locator('.market-grid').innerText(),/24000.00/)
 assert.match(await page.locator('.market-grid').innerText(),/21250.00/)
 await page.waitForTimeout(5000)
 await page.getByRole('heading',{name:'Draft version 1'}).evaluate(el=>el.scrollIntoView({block:'start'}))
 await page.waitForTimeout(5000)
 await page.getByRole('button',{name:'Approve internal review'}).scrollIntoViewIfNeeded()
 phase='authenticated demo approval'
 const decisionPromise=page.waitForResponse(r=>r.url().endsWith('/decisions')&&r.request().method()==='POST')
 await page.getByRole('button',{name:'Approve internal review'}).click()
 const decided=await decisionPromise
 assert.equal(decided.status(),200)
 const decision=await decided.json()
 assert.equal(decision.outcome,'approved_internal_review')
 assert.equal(decision.decision.reviewer_id,'test:local-demo-officer')
 record.authenticated_decision=decision
 record.request_to_approval_seconds=(Date.now()-requestStart)/1000
 await page.getByText('Approved for internal review only; nothing was delivered.').waitFor()
 await page.getByRole('heading',{name:'Run status'}).scrollIntoViewIfNeeded()
 await page.waitForTimeout(5000)
 const result=await context.request.get(`http://127.0.0.1:8001/api/v1/runs/${record.workflow_id}/events`,{headers:{Authorization:`Bearer ${token}`}})
 record.sanitized_tool_events=(await result.json()).events
 const tools=record.sanitized_tool_events.filter(e=>e.phase==='completed'&&e.server!=='local pinned Qwen').map(e=>e.tool)
 assert.deepEqual(tools,['fetch','search_market_quotes','compare_market_options','save_advisory_draft'])
 record.status='completed'
}catch(error){record.status='failed';record.failed_phase=phase;record.error_type=error.name;process.exitCode=1}
finally{
 record.recording_wall_seconds=(Date.now()-start)/1000
 const video=page.video()
 await context.close()
 const native=await video.path()
 record.video_local_path=path.relative(root,native)
 record.credential_content_visible=false
 record.completed_at=new Date().toISOString()
 await browser.close()
 await writeFile(path.join(root,`evals/results/I01.13-continuous-video-${stamp}.json`),JSON.stringify(record,null,2)+'\n')
 console.log(JSON.stringify({status:record.status,wall_seconds:record.recording_wall_seconds,request_to_review:record.request_to_review_seconds,video:record.video_local_path}))
}
