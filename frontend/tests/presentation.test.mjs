import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import ts from 'typescript'
const source = await readFile(new URL('../src/presentation.ts', import.meta.url), 'utf8')
const js = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext } }).outputText
const { workflowTime, sourceDate, recordedQuantity } = await import(`data:text/javascript;base64,${Buffer.from(js).toString('base64')}`)
test('UTC rollover and explicit offsets use Africa/Nairobi independent of browser timezone', () => {
 for (const zone of ['America/Los_Angeles','UTC','Asia/Tokyo']) {
  process.env.TZ = zone
  assert.equal(workflowTime('2026-10-14T22:01:02.662836+00:00'), '15 Oct 2026, 01:01:02 EAT')
  assert.equal(workflowTime('2026-10-15T01:01:02+03:00'), '15 Oct 2026, 01:01:02 EAT')
  assert.equal(workflowTime('2026-10-14T22:01:02Z'), '15 Oct 2026, 01:01:02 EAT')
 }
})
test('missing, invalid or naive timestamps never use current/browser time', () => {
 for (const value of [null, undefined, '', 'bad', '2026-10-10', '2026-10-14T22:01:02', '2026-02-30T22:01:02Z']) assert.equal(workflowTime(value), 'not available')
})
test('source dates remain date-only historical evidence', () => {
 assert.equal(sourceDate('2026-10-10'), '10 Oct 2026')
 assert.equal(sourceDate('2026-02-30'), 'not available')
})
test('comparison quantity comes from the immutable draft, with no editable input fallback', () => {
 assert.equal(recordedQuantity({content:{calculation:{quantity:'650',unit:'kg'}}}), '650 kg')
 assert.equal(recordedQuantity(null), 'not available')
})
