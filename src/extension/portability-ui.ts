import { Dialog, showDialog } from '@jupyterlab/apputils';
import { Widget } from '@lumino/widgets';
import { Catalog } from '../engine';
import { decryptBackup, encryptBackup } from '../portability/crypto';
import { MAX_BACKUP_BYTES, portableRecord, previewImport, readPortable } from '../portability/record';
import { LearnerStore } from './store';

function paragraph(parent: HTMLElement, text: string): void {
  const p=document.createElement('p');p.textContent=text;parent.append(p);
}
function input(parent: HTMLElement, text: string, type: string): HTMLInputElement {
  const label=document.createElement('label');label.className='al-backup-field';
  const span=document.createElement('span');span.textContent=text;
  const field=document.createElement('input');field.type=type;
  if (type==='password') {field.autocomplete='off';field.maxLength=1024;field.spellcheck=false;}
  label.append(span,field);parent.append(label);return field;
}
class ExportForm extends Widget {
  private password: HTMLInputElement;
  private confirm: HTMLInputElement;
  constructor() {
    super();this.addClass('al-backup-form');
    paragraph(this.node,'Save submitted attempts, hint history, task progress, and recorded reflections in an encrypted file. Notebook files and unrecorded writing need separate downloads. Sign-in links are excluded.');
    this.password=input(this.node,'Backup password','password');
    this.confirm=input(this.node,'Confirm backup password','password');
    paragraph(this.node,'Use at least 12 characters. Keep the password separately from the file. A forgotten password cannot be recovered by the course.');
  }
  getValue(): {password:string;confirmation:string} {return {password:this.password.value,confirmation:this.confirm.value};}
  dispose(): void {this.password.value='';this.confirm.value='';super.dispose();}
}
class ImportForm extends Widget {
  private file: HTMLInputElement;
  private password: HTMLInputElement;
  constructor() {
    super();this.addClass('al-backup-form');
    paragraph(this.node,'Choose an encrypted learner backup (.albackup). It is read and decrypted in this browser. Preview the record before importing.');
    paragraph(this.node,'Close other course tabs before importing.');
    this.file=input(this.node,'Learner backup file','file');this.file.accept='.albackup';
    this.password=input(this.node,'Backup password','password');
    paragraph(this.node,'Evidence (.nq) and reflection-text downloads are readable copies and cannot restore a learner record.');
  }
  getValue(): {file:File|null;password:string} {return {file:this.file.files?.[0]??null,password:this.password.value};}
  dispose(): void {this.password.value='';this.file.value='';super.dispose();}
}
async function problem(title: string, error: unknown): Promise<void> {
  await showDialog({title,body:error instanceof Error ? error.message : 'The backup operation could not be completed. Your existing work has not changed.',buttons:[Dialog.okButton({label:'Close'})]});
}
export async function downloadBackup(catalog: Catalog, store: LearnerStore): Promise<void> {
  const result=await showDialog({title:'Download learner backup',body:new ExportForm(),buttons:[Dialog.cancelButton(),Dialog.okButton({label:'Download encrypted backup'})]});
  if (!result.button.accept || !result.value) return;
  const {password,confirmation}=result.value;
  try {
    if (password!==confirmation) throw new Error('The backup passwords do not match.');
    const encrypted=await encryptBackup(portableRecord(catalog,store.record,new Date().toISOString()),password);
    const url=URL.createObjectURL(new Blob([encrypted],{type:'application/octet-stream'}));
    const link=document.createElement('a');link.href=url;link.download='learning-record.albackup';
    document.body.append(link);link.click();link.remove();
    // Let the browser finish consuming the object URL before releasing it.
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  } catch(error) {await problem('Backup not downloaded',error);}
}
export async function restoreBackup(catalog: Catalog, store: LearnerStore): Promise<boolean> {
  const result=await showDialog({title:'Import learner backup',body:new ImportForm(),buttons:[Dialog.cancelButton(),Dialog.okButton({label:'Preview backup'})]});
  if (!result.button.accept || !result.value) return false;
  try {
    const {file,password}=result.value;
    if (!file) throw new Error('Choose a learner backup file first.');
    if (file.size>MAX_BACKUP_BYTES) throw new Error('The backup file is too large.');
    const backup=readPortable(await decryptBackup(await file.text(),password),catalog);
    const expected=store.portabilitySnapshot();
    const preview=previewImport(catalog,store.record,backup);
    const body=document.createElement('div');body.className='al-backup-preview';
    paragraph(body,preview.mode==='continue'?'Continue the learner record from this backup in this empty browser.':'Merge this backup into the same learner record. Existing attempts are kept and duplicate attempts are counted once.');
    paragraph(body,`${preview.newObservations} new submitted attempts; ${preview.newAttempts} new task sessions; ${preview.reflections} recorded reflection answers in the resulting record.`);
    paragraph(body,'All saved reflection versions are retained. The most recently dated saved answer becomes current; ties keep the answer already in this browser.');
    if (preview.courseChanged) paragraph(body,'Course content has changed since this backup. Progress will be recalculated using the current course rules. Older task versions may require new practice.');
    paragraph(body,'Notebook files and unsaved answers are not included. Sign-in links do not transfer. Import only your own learner backup.');
    const accepted=await showDialog({title:'Preview learner backup',body:new Widget({node:body}),buttons:[Dialog.cancelButton(),Dialog.okButton({label:'Import record'})]});
    if (!accepted.button.accept) return false;
    store.importPortable(preview.record,expected);
    await showDialog({title:'Learner record imported',body:'Your record was saved in this browser. Re-run the activity setup or reflection cells to restore their controls and saved writing. Notebook files are unchanged.',buttons:[Dialog.okButton({label:'Close'})]});
    return true;
  } catch(error) {await problem('Backup not imported',error);return false;}
}
