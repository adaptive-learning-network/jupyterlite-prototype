import {expect,Page,test} from '@playwright/test';
import {readFileSync} from 'node:fs';
import {ACTION,Catalog,LearnerRecord,OUTCOME} from '../src/engine';
import {encryptBackup} from '../src/portability/crypto';
import {portableRecord} from '../src/portability/record';

const key='al-engine:learner-record:v0.1';
const password='A long test-only backup password';
const panel=(p:Page)=>p.locator('#al-engine-learning');
const read=(p:Page)=>p.evaluate(key=>JSON.parse(localStorage.getItem(key)!),key);
async function open(page:Page,path='u00-n00-start-here.ipynb') {
 await page.goto('/lab/index.html?path=notebooks/'+path);await expect(panel(page)).toBeVisible();
 // Workspace restoration can expose the previous notebook before the requested
 // document finishes opening. Do not run cells in that restored notebook.
 await expect(page.getByRole('tab',{name:path,exact:false})).toHaveAttribute('aria-selected','true');
}
async function preview(page:Page,file:string|{name:string;mimeType:string;buffer:Buffer},pw=password) {
 await panel(page).getByRole('button',{name:'Import learner backup',exact:true}).click();
 const d=page.getByRole('dialog');await d.getByLabel('Learner backup file').setInputFiles(file);
 await d.getByLabel('Backup password',{exact:true}).fill(pw);await d.getByRole('button',{name:'Preview backup',exact:true}).click();
}
async function runAll(page:Page) {
 await expect(page.locator('.jp-Notebook-ExecutionIndicator[data-status="idle"]:visible')).toHaveCount(1,{timeout:180000});
 await page.getByRole('menuitem',{name:'Run',exact:true}).click();await page.getByRole('menuitem',{name:'Run All Cells',exact:true}).click();
}
test('encrypted transfer restores actual practice, different-case state and reflections in a fresh browser',async({page,browser},info)=>{
 test.setTimeout(480000);
 await open(page,'u03-n06-case-or-aggregate.ipynb');await runAll(page);
 await expect(page.getByRole('radio')).toHaveCount(10);
 const submit=page.getByRole('button',{name:'Submit',exact:true});await expect(submit).toBeEnabled();
 await page.getByRole('button',{name:'Show a hint',exact:true}).click();
 await expect.poll(async()=>(await read(page)).taskAttempts.at(-1).guidanceLevel).toBe(1);
 for(const [id,value] of Object.entries({a:'Case-based',b:'Aggregate',c:'Aggregate',d:'Case-based',e:'Aggregate'}))
  await page.locator('.al-dataset-'+id).getByRole('radio',{name:value,exact:true}).check();
 await submit.click();await expect(page.locator('.al-classification-feedback')).toContainText('All classifications are correct.');
 await page.getByRole('button',{name:'Try another case',exact:true}).click();await expect(page.getByRole('radio')).toHaveCount(6);
 for(const [id,value] of Object.entries({a:'Case-based',b:'Aggregate',c:'Case-based'}))
  await page.locator('.al-dataset-'+id).getByRole('radio',{name:value,exact:true}).check();
 await submit.click();await expect(page.locator('.al-classification-feedback')).toContainText('All classifications are correct.');
 const writing='My portable reflection: one row represents one individual case.';
 await page.locator('textarea').first().fill(writing);await page.getByRole('button',{name:'Record',exact:true}).click();
 await expect(page.locator('.course-reflection-status')).toContainText('Recorded in this browser.');
 const source=await read(page);
 await panel(page).getByRole('button',{name:'Download learner backup',exact:true}).click();
 const d=page.getByRole('dialog');await d.getByLabel('Backup password',{exact:true}).fill(password);await d.getByLabel('Confirm backup password').fill(password);
 const downloading=page.waitForEvent('download');await d.getByRole('button',{name:'Download encrypted backup',exact:true}).click();
 const download=await downloading;const file=info.outputPath('learning-record.albackup');await download.saveAs(file);
 const raw=readFileSync(file,'utf8');expect(raw).not.toContain(writing);expect(raw).not.toContain(source.learner);
 const destination=await browser.newContext({baseURL:'http://127.0.0.1:8765',viewport:{width:1100,height:900}});
 try {
  const target=await destination.newPage();await open(target);
  const before=JSON.stringify(await read(target));await preview(target,file);
  await expect(target.getByRole('dialog')).toContainText('Continue the learner record');
  expect(JSON.stringify(await read(target))).toBe(before); // Preview has no effect.
  await target.getByRole('dialog').getByRole('button',{name:'Cancel',exact:true}).click();
  expect(JSON.stringify(await read(target))).toBe(before);
  await preview(target,file);await target.getByRole('dialog').getByRole('button',{name:'Import record',exact:true}).click();
  await expect(target.getByRole('dialog')).toContainText('Learner record imported');
  await target.getByRole('dialog').getByRole('button',{name:'Close',exact:true}).click();
  const restored=await read(target);expect(restored).toEqual(source);
  await target.reload();await expect(panel(target)).toBeVisible();expect(await read(target)).toEqual(source);
  await open(target,'u03-n06-case-or-aggregate.ipynb');await runAll(target);
  await expect(target.getByRole('radio')).toHaveCount(6);await expect(target.locator('textarea').first()).toHaveValue(writing);
  await expect(target.locator('input[type="radio"]:checked')).toHaveCount(3);
  await target.getByRole('button',{name:'Try another case',exact:true}).click();
  await expect.poll(async()=>(await read(target)).taskAttempts.at(-1).taskId).toBe('new-case-2');
  await preview(target,file);await expect(target.getByRole('dialog')).toContainText('0 new submitted attempts');
  await target.getByRole('dialog').getByRole('button',{name:'Import record',exact:true}).click();
  await expect(target.getByRole('dialog')).toContainText('Learner record imported');
  await target.getByRole('dialog').getByRole('button',{name:'Close',exact:true}).click();
  expect((await read(target)).observations).toHaveLength(source.observations.length);
  expect((await read(target)).taskAttempts.at(-1).taskId).toBe('new-case-2');
  await panel(target).locator('.al-backups').scrollIntoViewIfNeeded();await target.screenshot({path:info.outputPath('restored-learning-record.png')});
 }finally{await destination.close();}
});

test('wrong password and failed storage preserve a browser record; retry can restore it',async({page})=>{
 const catalog=JSON.parse(readFileSync('app-assets/adaptive-learning/catalog.json','utf8')) as Catalog;
 const r:LearnerRecord={schema:'al-learner-record/0.1',learner:'urn:uuid:12345678-1234-4234-8234-123456789012',audience:catalog.audiences[0].iri,
  guidance:{},observations:[{iri:'urn:uuid:12345678-1234-4234-8234-123456789013',activity:catalog.activities[0].iri,object:catalog.activities[0].iri+'/exercise',action:ACTION.outputValidated,outcome:OUTCOME.correct,guidanceLevel:0,at:'2026-10-28T12:00:00Z'}]};
 const file={name:'test.albackup',mimeType:'application/octet-stream',buffer:Buffer.from(await encryptBackup(portableRecord(catalog,r,'2026-10-28T12:00:00Z'),password))};
 await open(page);const before=await read(page);
 await preview(page,file,'This password is incorrect');await expect(page.getByRole('dialog')).toContainText('password is incorrect');
 await page.getByRole('dialog').getByRole('button',{name:'Close',exact:true}).click();expect(await read(page)).toEqual(before);
 await preview(page,file);await expect(page.getByRole('dialog')).toContainText('Continue the learner record');
 await page.evaluate(key=>{
  const original=Storage.prototype.setItem;
  (window as unknown as {restoreStorage:()=>void}).restoreStorage=()=>{Storage.prototype.setItem=original;};
  Storage.prototype.setItem=function(k:string,v:string){if(k===key)throw new DOMException('quota','QuotaExceededError');original.call(this,k,v);};
 },key);
 await page.getByRole('dialog').getByRole('button',{name:'Import record',exact:true}).click();
 await expect(page.getByRole('dialog')).toContainText('could not save the imported record');expect(await read(page)).toEqual(before);
 await page.getByRole('dialog').getByRole('button',{name:'Close',exact:true}).click();
 await page.evaluate(()=>(window as unknown as {restoreStorage:()=>void}).restoreStorage());
 await preview(page,file);await page.getByRole('dialog').getByRole('button',{name:'Import record',exact:true}).click();
 await expect(page.getByRole('dialog')).toContainText('Learner record imported');
 await page.getByRole('dialog').getByRole('button',{name:'Close',exact:true}).click();expect(await read(page)).toEqual(r);
 await page.reload();await expect(panel(page)).toBeVisible();expect(await read(page)).toEqual(r);
});
