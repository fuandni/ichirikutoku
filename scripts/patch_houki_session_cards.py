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

/* Exam-session answer area: text choices remain in the original qtext view. */
#houkiSessionAnswer{margin:16px 0 20px;padding:13px;background:#fff;border:1px solid #d7dee9;border-radius:12px;max-width:100%;min-width:0}
#houkiSessionAnswer .houki-answer-title{font-weight:800;font-size:16px;margin:0 0 8px}
#houkiSessionAnswer .houki-answer-hint{margin:0 0 10px;color:#475467;font-size:13px}
#houkiSessionAnswer .houki-number-buttons{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
#houkiSessionAnswer .houki-number-buttons button{min-width:0;min-height:54px;border:2px solid #9daac0;background:#fff;color:#172554;border-radius:10px;font:800 24px/1.2 system-ui,sans-serif;cursor:pointer;touch-action:manipulation}
#houkiSessionAnswer .houki-number-buttons button:focus-visible{outline:3px solid #2563eb;outline-offset:2px}
#houkiSessionAnswer .houki-number-buttons button:disabled{opacity:1;cursor:default}
#houkiSessionAnswer .houki-number-buttons button.houki-picked-correct,
#houkiSessionAnswer .houki-number-buttons button.houki-right{background:#dcfce7;border-color:#15803d;color:#14532d}
#houkiSessionAnswer .houki-number-buttons button.houki-picked-wrong{background:#fee2e2;border-color:#b91c1c;color:#7f1d1d}
#houkiSessionAnswer .houki-answer-feedback{margin:12px 0 0;line-height:1.55;font-weight:750;overflow-wrap:anywhere}
#houkiSessionAnswer .houki-next-question{display:block;width:100%;margin:12px 0 0;min-height:48px;border:1px solid #2457d6;background:#2457d6;color:#fff;border-radius:9px;font:750 17px/1.3 system-ui,sans-serif;cursor:pointer}
#houkiSessionAnswer .houki-next-question[hidden]{display:none}
body.houki-fixed-exam #reveal,body.houki-fixed-exam #mkok,body.houki-fixed-exam #mkng,
body.houki-fixed-exam #next,body.houki-fixed-exam #skip{display:none!important}
body.houki-fixed-exam #qtext{max-width:100%;min-width:0;overflow-wrap:anywhere}
body.houki-fixed-exam #qtext .mobile-options{max-width:100%;min-width:0}
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
  let activePrefix="",exam=null;
  function records(){try{return typeof rec==="object"&&rec?rec:{}}catch(e){return {}}}
  function tally(prefix){
    const r=records();let answered=0,correct=0,wrong=0;
    for(let q=1;q<=12;q++){
      const id=prefix+String(q).padStart(2,"0");
      if(!Object.prototype.hasOwnProperty.call(r,id))continue;
      if(r[id]==="o"){answered++;correct++}
      else if(r[id]==="x"){answered++;wrong++}
    }
    return {answered,correct,wrong};
  }
  function clearSelection(){
    document.querySelectorAll("#houkiSessionCards .houki-exam-card").forEach(b=>{
      b.classList.remove("selected");b.setAttribute("aria-pressed","false");
    });
  }
  function quitFixedMode(){
    if(!exam)return;
    exam=null;activePrefix="";document.body.classList.remove("houki-fixed-exam");clearSelection();
    updateAnswerPanel();
    const notice=document.getElementById("houkiSessionNotice");
    if(notice)notice.textContent="試験回別モードを終了し、通常演習へ戻りました。";
  }
  function showPosition(pos){
    if(!exam)return;
    const item=ITEMS.find(x=>x.id===exam.ids[pos]);
    if(!item){quitFixedMode();return}
    exam.pos=pos;exam.graded=false;
    document.body.classList.add("houki-fixed-exam");
    show(item);
    updateAnswerPanel();
    scrollQuestionTop();
    const notice=document.getElementById("houkiSessionNotice");
    if(notice)notice.textContent=exam.entry.label+"：第"+(pos+1)+"/12問。回答は問題文の下にある1〜4のボタンで選んでください。";
  }
  function updateAnswerPanel(choice=null){
    const box=document.getElementById("houkiSessionAnswer");
    if(!box)return;
    box.hidden=!exam;
    if(!exam)return;
    const feedback=box.querySelector(".houki-answer-feedback");
    const next=box.querySelector(".houki-next-question");
    const graded=!!exam.graded;
    box.querySelectorAll(".houki-number-buttons button").forEach(button=>{
      const n=Number(button.dataset.answer);
      button.disabled=graded;
      button.classList.toggle("houki-picked-correct",graded&&n===choice&&choice===cur.a);
      button.classList.toggle("houki-picked-wrong",graded&&n===choice&&choice!==cur.a);
      button.classList.toggle("houki-right",graded&&n===cur.a&&choice!==cur.a);
    });
    feedback.textContent=graded?(choice===cur.a?"正解です。":"不正解です。")+" 正答は "+cur.a+" 番です。":"";
    next.hidden=!graded;
    next.textContent=exam.pos===11?"12問の結果へ":"次の問題へ";
  }
  function answer(n){
    if(!exam||exam.graded||![1,2,3,4].includes(n))return;
    if(!cur||cur.id!==exam.ids[exam.pos])return;
    const correct=n===cur.a;
    rec[cur.id]=correct?"o":"x";
    const k=review.indexOf(cur.id);
    if(correct){if(k>=0)review.splice(k,1)}
    else if(k<0)review.push(cur.id);
    exam.graded=true;
    // Native grade path: keep browser storage, cloud sync, review list and statistics.
    stats();renderTable();revSummary();persist();
    paint(true);
    const ans=document.getElementById("ans");
    if(ans){ans.textContent=cur.a;ans.classList.remove("hidden")}
    document.getElementById("reveal").disabled=true;
    document.getElementById("mkok").disabled=true;
    document.getElementById("mkng").disabled=true;
    updateAnswerPanel(n);
    refresh();
  }
  function nextInExam(){
    if(!exam)return;
    const next=exam.pos+1;
    if(next>=12){
      const entry=exam.entry,score=tally(entry.prefix);
      exam=null;document.body.classList.remove("houki-fixed-exam");updateAnswerPanel();
      const notice=document.getElementById("houkiSessionNotice");
      if(notice)notice.textContent=entry.label+" の出題終了。記録 "+score.answered+"/12問、正解 "+score.correct+"/12問。未回答があればカードから再開できます。";
      refresh();return;
    }
    showPosition(next);
  }
  function signal(el){el.dispatchEvent(new Event("change",{bubbles:true}))}
  function setChecked(el,val){
    if(!el||el.checked===val)return;
    el.checked=val;signal(el);
  }
  function resetFilters(){
    const topic=document.getElementById("tgroup");
    if(topic&&topic.tagName==="SELECT"&&topic.selectedIndex!==0){
      topic.selectedIndex=0;signal(topic);
    }
    // These are the native law app's actual category and frequency controls.
    document.querySelectorAll(".fc,.ft").forEach(el=>setChecked(el,true));
  }
  function start(entry){
    exam=null;
    const term=document.getElementById("fterm");
    const a=document.getElementById("fslotA");
    const b=document.getElementById("fslotB");
    const notice=document.getElementById("houkiSessionNotice");
    if(!term||!a||!b){
      notice.textContent="試験回フィルターが見つかりません。既存の演習画面から選んでください。";
      return;
    }
    const opt=Array.from(term.options).find(o=>o.textContent.trim()===entry.term);
    if(!opt){notice.textContent=entry.term+" はこの問題集に登録されていません。";return}
    resetFilters();
    term.value=opt.value;signal(term);
    setChecked(a,entry.slot==="A");setChecked(b,entry.slot==="B");
    const unseen=document.querySelector('input[name="mode"][value="unseen"]');
    if(unseen&&!unseen.checked){unseen.checked=true;signal(unseen)}
    activePrefix=entry.prefix;
    clearSelection();
    document.querySelectorAll("#houkiSessionCards .houki-exam-card").forEach(button=>{
      if(button.dataset.prefix===activePrefix){
        button.classList.add("selected");button.setAttribute("aria-pressed","true");
      }
    });
    // Use the existing question data and renderer. Avoid random repeats inside a set.
    const ids=Array.from({length:12},(_,i)=>entry.prefix+String(i+1).padStart(2,"0"));
    if(typeof ITEMS==="undefined"||typeof show!=="function"||
       ids.some(id=>!ITEMS.some(item=>item.id===id))){
      notice.textContent="12問のデータを確認できません。元の法規演習から出題してください。";
      return;
    }
    const r=records();
    const firstMissing=ids.findIndex(id=>r[id]!=="o"&&r[id]!=="x");
    exam={entry,ids,pos:-1};
    showPosition(firstMissing>=0?firstMissing:0);
    refresh();
  }
  function refresh(){
    const wrap=document.getElementById("houkiSessionCards");
    if(!wrap)return;
    wrap.querySelectorAll(".houki-exam-card").forEach(button=>{
      const t=tally(button.dataset.prefix);
      const isDone=t.answered===12;
      button.classList.toggle("done",isDone);
      const pct=Math.round(t.correct/12*100);
      button.querySelector(".houki-exam-progress").textContent=
        (isDone?"完了 ":"進捗 ")+t.answered+"/12 · 正解 "+t.correct+" ("+pct+"%)";
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
    const answerBox=document.createElement("section");
    answerBox.id="houkiSessionAnswer";answerBox.hidden=true;
    answerBox.innerHTML='<p class="houki-answer-title">回答を選択</p>'+
      '<p class="houki-answer-hint">上の選択肢を読んで、正しい番号を選んでください。</p>'+
      '<div class="houki-number-buttons" role="group" aria-label="解答番号"></div>'+
      '<p class="houki-answer-feedback" role="status" aria-live="polite"></p>'+
      '<button type="button" class="houki-next-question" hidden>次の問題へ</button>';
    for(let n=1;n<=4;n++){
      const btn=document.createElement("button");
      btn.type="button";btn.dataset.answer=String(n);btn.textContent=String(n);
      btn.setAttribute("aria-label",n+"番を回答");
      btn.addEventListener("click",()=>answer(n));
      answerBox.querySelector(".houki-number-buttons").append(btn);
    }
    answerBox.querySelector(".houki-next-question").addEventListener("click",nextInExam);
    // Place controls after all source options, never inside long choice text.
    const question=document.getElementById("qtext");
    if(question&&question.parentNode)question.insertAdjacentElement("afterend",answerBox);
    else wrap.append(answerBox);
    root.insertBefore(wrap,root.firstElementChild);
    // Native self-grading calls draw() after marking: advance through this
    // session's twelve questions, preserving original persistent records.
    if(typeof draw==="function"){
      const nativeDraw=draw;
      draw=function(){if(exam){nextInExam();return}return nativeDraw()};
    }
    for(const id of ["next","skip"]){
      const btn=document.getElementById(id);
      if(btn)btn.addEventListener("click",e=>{
        if(!exam)return;
        e.preventDefault();e.stopImmediatePropagation();nextInExam();
      },true);
    }
    const index=document.getElementById("tbody");
    if(index)index.addEventListener("click",()=>quitFixedMode(),true);
    document.querySelectorAll("#fterm,#fslotA,#fslotB,.fc,.ft,#tgroup,input[name=mode]").forEach(el=>
      el.addEventListener("change",quitFixedMode));
    refresh();
    document.addEventListener("keydown",e=>{
      if(!exam||e.altKey||e.ctrlKey||e.metaKey)return;
      const target=e.target;
      if(target&&target.closest&&target.closest('input,select,textarea,[contenteditable="true"]'))return;
      if(/^[1-4]$/.test(e.key)){e.preventDefault();e.stopImmediatePropagation();answer(Number(e.key))}
      else if((e.key==="Enter"||e.key===" ")&&exam.graded){
        e.preventDefault();e.stopImmediatePropagation();nextInExam();
      }else if(e.key===" "||e.key==="Enter"){
        e.preventDefault();e.stopImmediatePropagation();
      }
    },true);
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
