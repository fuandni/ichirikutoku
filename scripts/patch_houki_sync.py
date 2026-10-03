from pathlib import Path
import sys

p = Path(sys.argv[1])
s = p.read_text(encoding='utf-8')
marker = 'HOUKI_CLOUD_SYNC_V1'
if marker in s:
    print('Houki cloud sync already present')
    raise SystemExit(0)
if '</body>' not in s:
    raise SystemExit('missing </body>')

injected = r'''
<style>
#houkiCloudStatus{display:inline-block;margin-left:8px;padding:3px 8px;border-radius:999px;font-size:12px;font-weight:700;background:#eef2f7;color:#334155;vertical-align:middle}
#houkiCloudStatus.ok{background:#dcfce7;color:#166534}#houkiCloudStatus.busy{background:#fef3c7;color:#92400e}#houkiCloudStatus.error{background:#fee2e2;color:#991b1b}#houkiCloudStatus.offline{background:#e5e7eb;color:#4b5563}
</style>
<script>
/* HOUKI_CLOUD_SYNC_V1 */
(()=>{
  const nativeStoreSet=store.set.bind(store);
  const nativeStoreGet=store.get.bind(store);
  let applying=false,timer=null,inFlight=false,queued=false,authKnown=false;
  let recAt={},resetAt=0,reviewUpdatedAt=0,localUpdatedAt=0;

  function intv(v,d=0){const n=Number(v);return Number.isFinite(n)?Math.trunc(n):d}
  function syncMetaFrom(o,legacyMode=false){
    const m=o&&o._sync&&typeof o._sync==='object'?o._sync:{};
    const ra=m.recAt&&typeof m.recAt==='object'?m.recAt:{};
    recAt={};
    Object.keys(rec||{}).forEach(id=>{recAt[id]=Math.max(1,intv(ra[id],legacyMode?1:0)||1)});
    resetAt=Math.max(0,intv(m.resetAt,0));
    reviewUpdatedAt=Math.max(0,intv(m.reviewUpdatedAt,0));
    if(!reviewUpdatedAt&&Array.isArray(review)&&review.length)reviewUpdatedAt=legacyMode?1:0;
    localUpdatedAt=Math.max(0,intv(m.updatedAt,0));
  }
  function enrichState(o,touch=false){
    if(!o||typeof o!=='object')o={};
    if(touch)localUpdatedAt=Date.now();
    o._sync={recAt:{...recAt},resetAt,reviewUpdatedAt,updatedAt:localUpdatedAt};
    return o;
  }
  function badge(){
    let el=document.getElementById('houkiCloudStatus');
    if(el)return el;
    el=document.createElement('span');el.id='houkiCloudStatus';el.textContent='同期準備中';
    const n=document.getElementById('storenote');
    if(n&&n.parentNode)n.parentNode.insertBefore(el,n.nextSibling);else document.body.prepend(el);
    return el;
  }
  function status(text,kind=''){
    const el=badge();el.textContent=text;el.className=kind;
  }
  async function login(){
    const password=window.prompt('この端末を同期へ接続します。\n同期パスワードを入力してください。');
    if(password===null)return false;
    const r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password})});
    if(!r.ok){window.alert('同期パスワードが違います。');return false}
    authKnown=true;return true;
  }
  async function ensureAuth(interactive=false){
    try{
      const r=await fetch('/api/houki/state',{cache:'no-store'});
      if(r.ok){authKnown=true;return true}
      if(r.status===401&&interactive)return await login();
      return false;
    }catch(e){return false}
  }
  async function readLocal(){
    try{
      const r=await nativeStoreGet(STORE_KEY);
      if(r&&r.value){const o=JSON.parse(r.value);return o&&typeof o==='object'?o:{}}
    }catch(e){}
    return {};
  }
  async function writeLocal(o){
    applying=true;
    try{
      syncMetaFrom(o,false);
      await nativeStoreSet(STORE_KEY,JSON.stringify(enrichState(o,false)));
      applyState(o);
    }finally{applying=false}
  }
  async function syncNow(interactive=false){
    if(inFlight){queued=true;return}
    if(!navigator.onLine){status('オフライン','offline');return}
    inFlight=true;status('同期中','busy');
    try{
      if(!authKnown){
        const ok=await ensureAuth(interactive);
        if(!ok){status(interactive?'未接続':'要ログイン','error');return}
      }
      let local=await readLocal();
      if(!local._sync){
        syncMetaFrom(local,true);
        localUpdatedAt=Math.max(localUpdatedAt,1);
        local=enrichState(local,false);
        await nativeStoreSet(STORE_KEY,JSON.stringify(local));
      }else{
        syncMetaFrom(local,false);
      }
      let r=await fetch('/api/houki/sync',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({state:local,updatedAt:localUpdatedAt})});
      if(r.status===401&&interactive){
        authKnown=false;
        if(await login())r=await fetch('/api/houki/sync',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({state:local,updatedAt:localUpdatedAt})});
      }
      if(!r.ok)throw new Error('sync '+r.status);
      const data=await r.json();
      if(data&&data.state)await writeLocal(data.state);
      status('同期済み','ok');
      const note=document.getElementById('storenote');
      if(note)note.textContent='進捗と表示設定はブラウザとサーバーに自動保存されています。';
    }catch(e){
      console.warn('法規の同期に失敗しました',e);authKnown=false;
      status(navigator.onLine?'同期失敗':'オフライン',navigator.onLine?'error':'offline');
    }finally{
      inFlight=false;
      if(queued){queued=false;queue(250)}
    }
  }
  function queue(delay=450){clearTimeout(timer);timer=setTimeout(()=>syncNow(false),delay)}

  const baseStateObject=stateObject;
  stateObject=function(){return enrichState(baseStateObject(),false)};
  const baseApplyState=applyState;
  applyState=function(o){
    const hasSync=!!(o&&o._sync&&typeof o._sync==='object');
    baseApplyState(o);
    if(hasSync)syncMetaFrom(o,false);
    else{
      const now=Date.now();recAt={};Object.keys(rec||{}).forEach(id=>recAt[id]=now);
      resetAt=0;reviewUpdatedAt=now;localUpdatedAt=now;
    }
  };
  const baseMark=mark;
  mark=function(v){
    const now=Date.now();if(cur&&cur.id)recAt[cur.id]=now;reviewUpdatedAt=now;
    return baseMark(v);
  };
  if(typeof doImport==='function'){
    const baseImport=doImport;
    doImport=function(replace){const now=Date.now();reviewUpdatedAt=now;const r=baseImport(replace);Object.keys(rec||{}).forEach(id=>recAt[id]=now);return r};
  }
  const resetBtn=document.getElementById('reset');
  if(resetBtn)resetBtn.addEventListener('click',()=>{const now=Date.now();resetAt=now;recAt={};reviewUpdatedAt=now},{capture:true});
  const clearBtn=document.getElementById('revClear');
  if(clearBtn)clearBtn.addEventListener('click',()=>{reviewUpdatedAt=Date.now()},{capture:true});

  store.set=async function(key,value){
    if(key!==STORE_KEY||applying)return nativeStoreSet(key,value);
    try{
      let o=JSON.parse(value);syncMetaFrom(o,!!(!o._sync));
      localUpdatedAt=Date.now();o=enrichState(o,false);
      const result=await nativeStoreSet(key,JSON.stringify(o));queue();return result;
    }catch(e){const result=await nativeStoreSet(key,value);queue();return result}
  };

  window.addEventListener('online',()=>{status('再接続','busy');queue(100)});
  window.addEventListener('offline',()=>status('オフライン','offline'));
  window.addEventListener('focus',()=>queue(150));
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)queue(150)});
  window.addEventListener('load',()=>{badge();status('接続確認','busy');setTimeout(()=>syncNow(true),50)});
})();
</script>
'''
s = s.replace('</body>', injected + '\n</body>', 1)
p.write_text(s, encoding='utf-8')
print('Injected HOUKI_CLOUD_SYNC_V1')
