#!/usr/bin/env python3
"""Add an exam-session card launcher to the existing law practice page.

Idempotent, additive: the original questions, self-marking workflow and
local/server sync code are left untouched. Run on the deployed HTML file.
"""
from pathlib import Path
import sys

MARKER = "HOUKI_SESSION_CARDS_V1"
if len(sys.argv) != 2:
    raise SystemExit("Usage: python3 patch_houki_session_cards.py /path/to/houki-practice/index.html")

path = Path(sys.argv[1])
html = path.read_text(encoding="utf-8")
if MARKER in html:
    print("Session cards already installed; no changes.")
    raise SystemExit(0)
if "</body>" not in html:
    raise SystemExit("Cannot patch page without </body>.")
if not all(s in html for s in ('id="fterm"', 'id="fslotA"', 'id="fslotB"')):
    raise SystemExit("Expected law-practice session filters not found; refusing to patch.")

addition = r"""
<style>
/* HOUKI_SESSION_CARDS_V1 */
#houkiSessionCards{max-width:1160px;margin:12px auto 20px;padding:12px;background:#f6f8fd;
 border:1px solid #dae0e9;border-radius:14px;color:#111827;box-sizing:border-box;
 font:inherit}
#houkiSessionCards *{box-sizing:border-box}
#houkiSessionCards h2{margin:0 0 6px;font-size:21px;font-weight:800}
#houkiSessionCards .houki-exam-help{font-size:13px;color:#475467;margin:0 0 14px}
#houkiSessionCards .houki-exam-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
#houkiSessionCards button.houki-exam-card{font:inherit;border:2px solid #dae0e9;border-radius:12px;
 background:#fff;padding:16px 12px;min-height:126px;text-align:left;cursor:pointer;
 display:flex;flex-direction:column;justify-content:space-between;gap:10px;color:#111827}
#houkiSessionCards button.houki-exam-card:hover,
#houkiSessionCards button.houki-exam-card:focus-visible{border-color:#2870e8;outline:0}
#houkiSessionCards button.houki-exam-card.done{border:3px solid #2870e8}
#houkiSessionCards button.houki-exam-card.selected{box-shadow:0 0 0 3px #b8d2ff}
#houkiSessionCards .houki-exam-name{font-size:18px;font-weight:800;line-height:1.3}
#houkiSessionCards .houki-exam-count{color:#667085;font-size:14px}
#houkiSessionCards .houki-exam-progress{background:#edf2ff;border-radius:9px;
 color:#5e6a82;padding:6px 9px;font-size:14px;font-weight:700;line-height:1.3}
#houkiSessionCards #houkiSessionNotice{margin:12px 0 0;color:#334155;font-size:13px}
@media(min-width:800px){#houkiSessionCards .houki-exam-grid{grid-template-columns:repeat(4,minmax(0,1fr))}}
@media(max-width:400px){#houkiSessionCards{margin:8px 5px 14px;padding:9px}
 #houkiSessionCards .houki-exam-grid{gap:9px}
 #houkiSessionCards button.houki-exam-card{padding:12px 9px;min-height:114px}
 #houkiSessionCards .houki-exam-name{font-size:16px}
 #houkiSessionCards .houki-exam-progress{font-size:12px}}
</style>
<script>
/* HOUKI_SESSION_CARDS_V1 */
(()=>{
  "use strict";
  // Prefixes are the IDs used by the 216-question law-practice database.
  const sessions=[
    {p:"50",label:"令和5年10月"},
    {p:"62",label:"令和6年2月"},
    {p:"66",label:"令和6年6月"},
    {p:"60",label:"令和6年10月"},
    {p:"72",label:"令和7年2月"},
    {p:"76",label:"令和7年6月"},
    {p:"70",label:"令和7年10月"},
    {p:"82",label:"令和8年2月"},
    {p:"86",label:"令和8年6月"}
  ];
  const entryList=sessions.flatMap(s=>["A","B"].map(slot=>({
    label:s.label+" "+slot,term:s.label+"期",slot:slot,prefix:"JY"+s.p+slot+"-"
  })));
  let activePrefix="";
  function records(){try{return typeof rec==="object"&&rec?rec:{}}catch(e){return {}}}
  function count(prefix){
    const r=records();let n=0;
    for(let q=1;q<=12;q++){
      const id=prefix+String(q).padStart(2,"0");
      if(Object.prototype.hasOwnProperty.call(r,id)&&r[id]!=null)n++;
    }
    return n;
  }
  function signal(el){el.dispatchEvent(new Event("change",{bubbles:true}))}
  function setChecked(el,val){
    if(!el||el.checked===val)return;
    el.checked=val;signal(el);
  }
  function resetFilters(){
    // A fixed twelve-question exam must not inherit topic/difficulty filters.
    const topic=document.getElementById("tgroup");
    if(topic&&topic.tagName==="SELECT"&&topic.selectedIndex!==0){
      topic.selectedIndex=0;signal(topic);
    }
    for(const id of ["fcat","ftier"]){
      const root=document.getElementById(id);
      if(!root)continue;
      root.querySelectorAll('input[type="checkbox"]').forEach(el=>setChecked(el,true));
    }
  }
  function start(entry){
    const term=document.getElementById("fterm");
    const a=document.getElementById("fslotA");
    const b=document.getElementById("fslotB");
    const notice=document.getElementById("houkiSessionNotice");
    if(!term||!a||!b){
      notice.textContent="試験回フィルターが見つかりません。既存の演習画面から選んでください。";
      return;
    }
    const opt=Array.from(term.options).find(o=>o.textContent.trim()===entry.term);
    if(!opt){
      notice.textContent=entry.term+" はこの問題集に登録されていません。";
      return;
    }
    resetFilters();
    term.value=opt.value;signal(term);
    setChecked(a,entry.slot==="A");
    setChecked(b,entry.slot==="B");
    const unseen=document.getElementById("unseen");
    if(unseen&&unseen.type==="radio"&&!unseen.checked){unseen.checked=true;signal(unseen)}
    activePrefix=entry.prefix;
    document.querySelectorAll("#houkiSessionCards button.houki-exam-card").forEach(button=>{
      button.classList.toggle("selected",button.dataset.prefix===activePrefix);
      button.setAttribute("aria-pressed",button.dataset.prefix===activePrefix?"true":"false");
    });
    notice.textContent=entry.label+" を選択しました。既存の進捗・同期を引き継いで12問を演習します。";
    // Keep the native question renderer and self-grading behavior intact.
    const pick=Array.from(document.querySelectorAll("button")).find(button=>
      button.closest("#houkiSessionCards")===null && /出題する/.test(button.textContent||""));
    if(pick){
      pick.click();
      const box=document.getElementById("sheetlabel")||pick;
      box.scrollIntoView({block:"start",behavior:"smooth"});
    }else{
      const box=document.getElementById("sheetlabel")||term;
      box.scrollIntoView({block:"start",behavior:"smooth"});
      notice.textContent+=" 「出題する」ボタンを押して始めてください。";
    }
  }
  function refresh(){
    const wrap=document.getElementById("houkiSessionCards");
    if(!wrap)return;
    wrap.querySelectorAll(".houki-exam-card").forEach(button=>{
      const n=count(button.dataset.prefix);
      const isDone=n===12;
      button.classList.toggle("done",isDone);
      button.querySelector(".houki-exam-progress").textContent=(isDone?"完了 ":"記録 ")+n+"/12 ("+Math.round(n/12*100)+"%)";
    });
  }
  function mount(){
    if(document.getElementById("houkiSessionCards"))return;
    const filters=document.getElementById("fterm");
    if(!filters)return;
    const wrap=document.createElement("section");
    wrap.id="houkiSessionCards";
    const header=document.createElement("h2");
    header.textContent="法規｜試験回から解く";
    const help=document.createElement("p");
    help.className="houki-exam-help";
    help.textContent="試験回ごとに12問。出題・正答表示・自己採点は従来の法規演習を使用します。";
    const grid=document.createElement("div");
    grid.className="houki-exam-grid";
    for(const entry of entryList){
      const button=document.createElement("button");
      button.type="button";button.className="houki-exam-card";
      button.dataset.prefix=entry.prefix;
      button.setAttribute("aria-label",entry.label+" の法規12問を解く");
      button.setAttribute("aria-pressed","false");
      const name=document.createElement("span");
      name.className="houki-exam-name";name.textContent=entry.label;
      const total=document.createElement("span");
      total.className="houki-exam-count";total.textContent="12問";
      const progress=document.createElement("span");
      progress.className="houki-exam-progress";
      button.append(name,total,progress);
      button.addEventListener("click",()=>start(entry));
      grid.append(button);
    }
    const notice=document.createElement("p");
    notice.id="houkiSessionNotice";notice.setAttribute("aria-live","polite");
    wrap.append(header,help,grid,notice);
    const root=document.querySelector("main")||document.body;
    root.insertBefore(wrap,root.firstElementChild);
    refresh();
    // Also captures updates arriving asynchronously from Oracle cloud sync.
    setInterval(refresh,2000);
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",mount,{once:true});
  else mount();
})();
</script>
"""
path.write_text(html.replace("</body>", addition + "\n</body>", 1), encoding="utf-8")
print("Installed HOUKI_SESSION_CARDS_V1")
