// Password-encrypted backup files using browser Web Crypto. No network or storage.
import { MAX_BACKUP_BYTES, PortableRecord } from './record';
const FORMAT='al-encrypted-backup/1';
const ITERATIONS=600000;
const AAD=new TextEncoder().encode(`${FORMAT}|PBKDF2-SHA256|${ITERATIONS}|AES-256-GCM`);
function bytes64(bytes: Uint8Array): string {
  let s='';for (let i=0;i<bytes.length;i+=8192) s+=String.fromCharCode(...bytes.subarray(i,i+8192));
  return btoa(s);
}
function unbase64(value: unknown, length?: number): Uint8Array {
  if (typeof value!=='string' || !/^[A-Za-z0-9+/]*={0,2}$/.test(value) || value.length%4) throw new Error('Invalid backup encoding.');
  const bytes=Uint8Array.from(atob(value),c=>c.charCodeAt(0));
  if (length!==undefined && bytes.length!==length) throw new Error('Invalid backup encryption parameters.');
  return bytes;
}
async function key(password: string, salt: Uint8Array): Promise<CryptoKey> {
  if (!globalThis.crypto?.subtle) throw new Error('Encrypted backups require HTTPS or a local development address and a browser with Web Crypto.');
  if (password.length<12 || password.length>1024) throw new Error('Use a backup password of 12 to 1024 characters.');
  const material=await crypto.subtle.importKey('raw',new TextEncoder().encode(password),'PBKDF2',false,['deriveKey']);
  return crypto.subtle.deriveKey({name:'PBKDF2',hash:'SHA-256',iterations:ITERATIONS,salt},material,{name:'AES-GCM',length:256},false,['encrypt','decrypt']);
}
export async function encryptBackup(payload: PortableRecord, password: string): Promise<string> {
  const clear=new TextEncoder().encode(JSON.stringify(payload));
  if (clear.byteLength>MAX_BACKUP_BYTES/2) throw new Error('This learner record is too large for this backup version.');
  const salt=crypto.getRandomValues(new Uint8Array(16)),iv=crypto.getRandomValues(new Uint8Array(12));
  const encrypted=await crypto.subtle.encrypt({name:'AES-GCM',iv,additionalData:AAD,tagLength:128},await key(password,salt),clear);
  return JSON.stringify({format:FORMAT,kdf:'PBKDF2-SHA256',iterations:ITERATIONS,cipher:'AES-256-GCM',salt:bytes64(salt),iv:bytes64(iv),ciphertext:bytes64(new Uint8Array(encrypted))});
}
export async function decryptBackup(text: string, password: string): Promise<unknown> {
  if (new TextEncoder().encode(text).byteLength>MAX_BACKUP_BYTES) throw new Error('The backup file is too large.');
  let e: Record<string,unknown>;
  try {e=JSON.parse(text);} catch {throw new Error('This is not an encrypted learner backup. Evidence and reflection downloads cannot be imported.');}
  if (!e || Array.isArray(e) || e.format!==FORMAT || e.kdf!=='PBKDF2-SHA256' || e.iterations!==ITERATIONS || e.cipher!=='AES-256-GCM' || Object.keys(e).sort().join(',')!=='cipher,ciphertext,format,iterations,iv,kdf,salt') throw new Error('This backup format or encryption version is not supported.');
  const salt=unbase64(e.salt,16),iv=unbase64(e.iv,12),encrypted=unbase64(e.ciphertext);
  if (encrypted.length<16 || encrypted.length>MAX_BACKUP_BYTES/2+16) throw new Error('Invalid backup size.');
  const derived=await key(password,salt);
  try {
    const clear=await crypto.subtle.decrypt({name:'AES-GCM',iv,additionalData:AAD,tagLength:128},derived,encrypted);
    return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(clear));
  } catch { throw new Error('The password is incorrect or the backup is damaged. Existing work has not changed.'); }
}
