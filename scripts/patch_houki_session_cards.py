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


#houkiSessionAnswer .houki-progress-label{font-size:14px;color:#334155;font-weight:700}
#houkiSessionAnswer .houki-jumps{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:5px;margin:14px 0}
#houkiSessionAnswer .houki-jumps[hidden]{display:none}
#houkiSessionAnswer .houki-jumps button{min-width:0;min-height:38px;border:1px solid #b8c3d6;border-radius:7px;background:#fff;color:#111827;font:700 15px system-ui,sans-serif}
#houkiSessionAnswer .houki-jumps button.current{outline:2px solid #2457d6}
#houkiSessionAnswer .houki-jumps button.correct{background:#dbf6e5}
#houkiSessionAnswer .houki-jumps button.wrong{background:#ffe3e0}
#houkiSessionAnswer .houki-bottom-nav{display:grid;grid-template-columns:1fr 1fr;gap:8px}
#houkiSessionAnswer .houki-prev-question{width:100%;min-height:48px;border:1px solid #94a3b8;background:#fff;color:#1e293b;border-radius:9px;font:700 16px system-ui,sans-serif}
#houkiSessionAnswer .houki-finish-question{display:block;width:100%;margin:10px 0 0;min-height:42px;border:1px solid #94a3b8;background:#fff;color:#334155;border-radius:8px;font:700 15px system-ui,sans-serif}
#houkiSessionAnswer .houki-finish-question[hidden],#houkiSessionAnswer .houki-prev-question[hidden]{display:none}
#houkiSessionAnswer .houki-next-question{margin:0}
#houkiSessionAnswer .houki-result-rows[hidden],#houkiSessionAnswer .houki-export[hidden]{display:none}
#houkiSessionAnswer .houki-result-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:9px 0}
#houkiSessionAnswer .houki-result-grid button{min-height:44px;border-radius:8px;border:1px solid #9ca3af;background:#fff;font:700 14px system-ui,sans-serif}
#houkiSessionAnswer .houki-result-grid button.correct{background:#dcfce7}
#houkiSessionAnswer .houki-result-grid button.wrong{background:#fee2e2}
#houkiSessionAnswer .houki-export{width:100%;max-width:100%;min-width:0;font-size:13px;line-height:1.55;margin-top:8px}
#houkiExamRecent{display:grid;gap:7px}
#houkiSessionCards .houki-recent-row{width:100%;text-align:left;border:1px solid #cbd5e1;border-radius:8px;padding:11px;background:#fff;color:#1e293b;font:600 13px system-ui,sans-serif}

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
  const EXAM_KEY="rikutoku1-hoki-session-v1";
  function safeObject(x){return x&&typeof x==="object"&&!Array.isArray(x)?x:{}}
  function loadDb(){try{return safeObject(JSON.parse(localStorage.getItem(EXAM_KEY)||"{}"))}catch(e){return {}}}
  function normalizeDb(raw){
    raw=safeObject(raw);
    const entries=Object.entries(safeObject(raw.attempts)).filter(([id,a])=>id.length<100&&a&&
       typeof a==="object"&&typeof a.prefix==="string"&&Array.isArray(a.ids)&&a.ids.length===12);
    const attempts=Object.fromEntries(entries.slice(-100));
    return {version:1,attempts,lastId:typeof raw.lastId==="string"?raw.lastId:"",updatedAt:Number(raw.updatedAt)||0};
  }
  let examDb=normalizeDb(loadDb()),activePrefix="",exam=null,finishedEntry=null,examReviewMode=false;
  function saveDbToLocal(){try{localStorage.setItem(EXAM_KEY,JSON.stringify(examDb))}catch(e){}}
  function mergeExamDb(first,second){
    const a=normalizeDb(first),b=normalizeDb(second),all={...a.attempts};
    for(const [id,item] of Object.entries(b.attempts)){
      if(!all[id]||(Number(item.savedAt)||0)>(Number(all[id].savedAt)||0))all[id]=item;
    }
    const selected=b.updatedAt>a.updatedAt?b.lastId:a.lastId;
    const ordered=Object.values(all).sort((x,y)=>(Number(y.savedAt)||0)-(Number(x.savedAt)||0)).slice(0,100);
    const attempts=Object.fromEntries(ordered.map(x=>[x.id,x]));
    return {version:1,attempts,lastId:attempts[selected]?selected:ordered[0]?.id||"",
      updatedAt:Math.max(a.updatedAt,b.updatedAt)};
  }
  function records(){try{return typeof rec==="object"&&rec?rec:{}}catch(e){return {}}}
  function tally(prefix){
    const r=records();let answered=0,correct=0,wrong=0;
    for(let q=1;q<=12;q++){
      const val=r[prefix+String(q).padStart(2,"0")];
      if(val==="o"){answered++;correct++}else if(val==="x"){answered++;wrong++}
    }
    return {answered,correct,wrong};
  }
  function scoreAttempt(a){
    const vals=Object.values(safeObject(a.answers)).filter(x=>x&&x.choice!=null);
    const answered=vals.length,correct=vals.filter(x=>x.correct).length;
    return {answered,correct,wrong:answered-correct,rate:answered?Math.round(correct/answered*100):0};
  }
  function activeAttempt(){return exam?.attempt||null}
  function persistExam(){
    const a=activeAttempt();
    if(!a)return;
    const now=Date.now();a.savedAt=now;a.position=exam.pos;
    examDb.attempts[a.id]=JSON.parse(JSON.stringify(a));
    examDb.lastId=a.id;examDb.updatedAt=now;
    const ordered=Object.values(examDb.attempts).sort((x,y)=>y.savedAt-x.savedAt).slice(0,100);
    examDb.attempts=Object.fromEntries(ordered.map(x=>[x.id,x]));
    saveDbToLocal();
    try{persist()}catch(e){console.warn("Exam sync unavailable",e)}
    refresh();renderRecent();
  }
  function findEntry(prefix){return entryList.find(e=>e.prefix===prefix)||null}
  function clearSelection(){
    document.querySelectorAll("#houkiSessionCards .houki-exam-card").forEach(b=>{
      b.classList.remove("selected");b.setAttribute("aria-pressed","false");
    });
  }
  function markSelection(prefix){
    clearSelection();
    document.querySelectorAll("#houkiSessionCards .houki-exam-card").forEach(b=>{
      const on=b.dataset.prefix===prefix;
      b.classList.toggle("selected",on);b.setAttribute("aria-pressed",String(on));
    });
  }
  function quitFixedMode(){
    if(!exam&&!finishedEntry)return;
    exam=null;finishedEntry=null;activePrefix="";examReviewMode=false;
    document.body.classList.remove("houki-fixed-exam");clearSelection();
    const panel=document.getElementById("houkiSessionAnswer");
    if(panel)panel.hidden=true;
    const notice=document.getElementById("houkiSessionNotice");
    if(notice)notice.textContent="試験回別モードを終了しました。";
    renderRecent();
  }
  function updateAnswerPanel(){
    const box=document.getElementById("houkiSessionAnswer");
    if(!box)return;
    box.hidden=!exam;
    if(!exam)return;
    box.querySelector(".houki-number-buttons").style.display="grid";
    box.querySelector(".houki-result-rows").hidden=true;
    box.querySelector(".houki-copy").hidden=true;
    box.querySelector(".houki-export").hidden=true;
    box.querySelector(".houki-answer-title").textContent="回答を選択";
    box.querySelector(".houki-answer-hint").textContent="問題文と選択肢を読み、正しい番号を選んでください。";
    const r=safeObject(exam.attempt.answers[cur.id]);
    const graded=Number.isInteger(r.choice);
    const feedback=box.querySelector(".houki-answer-feedback");
    box.querySelectorAll(".houki-number-buttons button").forEach(button=>{
      const n=Number(button.dataset.answer);
      button.disabled=examReviewMode;
      button.classList.toggle("houki-picked-correct",graded&&n===r.choice&&r.correct);
      button.classList.toggle("houki-picked-wrong",graded&&n===r.choice&&!r.correct);
      button.classList.toggle("houki-right",graded&&n===cur.a&&n!==r.choice);
    });
    feedback.textContent=graded?(r.correct?"正解です。":"不正解です。")+" 正答は "+cur.a+" 番です。":"未回答";
    const next=box.querySelector(".houki-next-question");
    next.hidden=false;next.textContent=examReviewMode?"結果に戻る":exam.pos===11?"結果を表示":"次の問題";
    const prev=box.querySelector(".houki-prev-question");
    prev.disabled=exam.pos===0;prev.hidden=examReviewMode;
    const fin=box.querySelector(".houki-finish-question");
    fin.hidden=examReviewMode;
    const jump=box.querySelector(".houki-jumps");
    jump.hidden=examReviewMode;
    if(!examReviewMode){
      jump.querySelectorAll("button").forEach((b,i)=>{
        const saved=exam.attempt.answers[exam.ids[i]];
        b.className=(i===exam.pos?"current ":"")+(saved?.choice!=null?(saved.correct?"correct":"wrong"):"");
        b.setAttribute("aria-current",i===exam.pos?"step":"false");
      });
    }
    const subtitle=box.querySelector(".houki-progress-label");
    subtitle.textContent=exam.entry.label+"　"+(exam.pos+1)+"/12　回答済 "+scoreAttempt(exam.attempt).answered+"/12";
  }
  function showPosition(pos){
    if(!exam||pos<0||pos>=12)return;
    const item=ITEMS.find(x=>x.id===exam.ids[pos]);
    if(!item){quitFixedMode();return}
    exam.pos=pos;
    document.body.classList.add("houki-fixed-exam");
    show(item);
    const r=safeObject(exam.attempt.answers[item.id]);
    if(r.choice!=null){
      paint(true);
      const ans=document.getElementById("ans");
      if(ans){ans.textContent=cur.a;ans.classList.remove("hidden")}
    }
    updateAnswerPanel();
    if(!examReviewMode)persistExam();
    scrollQuestionTop();
  }
  function answer(n){
    if(!exam||examReviewMode||![1,2,3,4].includes(n))return;
    if(!cur||cur.id!==exam.ids[exam.pos])return;
    const correct=n===cur.a,now=Date.now(),id=cur.id;
    exam.attempt.answers[id]={choice:n,correct,time:now};
    // Delegate marking to the existing law-sync wrapper: it timestamps
    // per-question updates in recAt and writes through the Oracle sync path.
    mark(correct?"o":"x");
    paint(true);
    const ans=document.getElementById("ans");
    if(ans){ans.textContent=cur.a;ans.classList.remove("hidden")}
    updateAnswerPanel();persistExam();
  }
  function nextInExam(){
    if(!exam)return;
    if(examReviewMode){showResult(exam.attempt);return}
    if(exam.pos>=11){finishExam(false);return}
    showPosition(exam.pos+1);
  }
  function start(entry, saved=null){
    const term=document.getElementById("fterm");
    const a=document.getElementById("fslotA"),b=document.getElementById("fslotB");
    const notice=document.getElementById("houkiSessionNotice");
    if(!term||!a||!b)return;
    const option=Array.from(term.options).find(o=>o.textContent.trim()===entry.term);
    if(!option){notice.textContent=entry.term+" が見つかりません。";return}
    const ids=Array.from({length:12},(_,i)=>entry.prefix+String(i+1).padStart(2,"0"));
    if(ids.some(id=>!ITEMS.some(item=>item.id===id))){notice.textContent="問題が12問揃っていません。";return}
    exam=null;finishedEntry=null;examReviewMode=false;
    document.querySelectorAll(".fc,.ft").forEach(el=>{el.checked=true});
    const group=document.getElementById("tgroup");if(group){group.selectedIndex=0}
    term.value=option.value;a.checked=entry.slot==="A";b.checked=entry.slot==="B";
    const unseen=document.querySelector('input[name="mode"][value="unseen"]');
    if(unseen)unseen.checked=true;
    term.dispatchEvent(new Event("change",{bubbles:true}));
    a.dispatchEvent(new Event("change",{bubbles:true}));
    b.dispatchEvent(new Event("change",{bubbles:true}));
    const attempt=saved||{
      id:"L"+Date.now()+"-"+Math.floor(Math.random()*100000),
      prefix:entry.prefix,label:entry.label,ids,
      started:Date.now(),savedAt:Date.now(),position:0,answers:{},status:"active"
    };
    attempt.answers=safeObject(attempt.answers);
    activePrefix=entry.prefix;
    exam={entry,ids,pos:0,attempt};
    markSelection(entry.prefix);
    notice.textContent=entry.label+" の12問を演習中。前後移動・途中終了・再開ができます。";
    showPosition(Math.max(0,Math.min(11,Number(attempt.position)||0)));
  }
  function showResult(a){
    if(!a)return;
    const entry=findEntry(a.prefix)||{label:a.label,prefix:a.prefix};
    const score=scoreAttempt(a);
    if(exam){exam=null;examReviewMode=false}
    finishedEntry=entry;
    document.body.classList.remove("houki-fixed-exam");
    const panel=document.getElementById("houkiSessionAnswer");
    if(!panel)return;
    panel.hidden=false;
    panel.querySelector(".houki-answer-title").textContent=a.label+" の演習結果";
    panel.querySelector(".houki-answer-hint").textContent="回答 "+score.answered+"/12問 · 正解 "+score.correct+"/"+score.answered+" ("+score.rate+"%)";
    panel.querySelector(".houki-number-buttons").style.display="none";
    panel.querySelector(".houki-answer-feedback").textContent="各問題の○×を確認できます。";
    panel.querySelector(".houki-progress-label").textContent="12問の結果";
    panel.querySelector(".houki-prev-question").hidden=true;
    panel.querySelector(".houki-finish-question").hidden=true;
    panel.querySelector(".houki-jumps").hidden=true;
    const btn=panel.querySelector(".houki-next-question");
    btn.hidden=false;btn.textContent="試験回一覧へ戻る";
    const resultRows=panel.querySelector(".houki-result-rows");
    resultRows.hidden=false;resultRows.replaceChildren();
    const summary=document.createElement("p");
    summary.textContent="正解 "+score.correct+"　不正解 "+score.wrong+"　未回答 "+(12-score.answered);
    resultRows.append(summary);
    const grid=document.createElement("div");grid.className="houki-result-grid";
    a.ids.forEach((id,i)=>{
      const r=a.answers[id]||{},button=document.createElement("button");
      button.type="button";button.textContent=(i+1)+"問 "+(r.choice==null?"－":r.correct?"○":"×");
      button.className=r.choice==null?"unanswered":r.correct?"correct":"wrong";
      button.onclick=()=>{
        const it=ITEMS.find(x=>x.id===id);
        if(!it)return;
        show(it);paint(true);
        const ans=document.getElementById("ans");
        if(ans){ans.textContent=cur.a;ans.classList.remove("hidden")}
        panel.scrollIntoView({block:"start",behavior:"smooth"});
      };
      grid.append(button);
    });
    resultRows.append(grid);
    const exportBox=panel.querySelector(".houki-export");
    const lines=["一陸特 法規 演習結果","範囲: "+a.label,
      "回答: "+score.answered+"/12","結果: "+score.correct+"/"+score.answered+" ("+score.rate+"%)",""];
    a.ids.forEach((id,i)=>{
      const r=a.answers[id]||{},q=ITEMS.find(x=>x.id===id);
      lines.push("["+id+"] "+(r.choice==null?"未":r.correct?"○":"×")+
        " | 回答:"+(r.choice??"-")+" | 正答:"+(q?.a??"-")+
        " | "+(q?.term||"")+" / 問"+(i+1));
    });
    exportBox.value=lines.join("\n");exportBox.hidden=false;
    panel.querySelector(".houki-copy").hidden=false;
    panel.scrollIntoView({block:"start",behavior:"smooth"});
  }
  function finishExam(skipConfirmation=false){
    if(!exam||examReviewMode)return;
    const a=exam.attempt,score=scoreAttempt(a);
    if(!skipConfirmation&&score.answered<12&&
       !window.confirm((12-score.answered)+"問が未回答です。結果を表示しますか？"))return;
    a.status="completed";a.finished=Date.now();a.result=score;
    persistExam();showResult(a);refresh();renderRecent();
  }
  function refresh(){
    const wrap=document.getElementById("houkiSessionCards");if(!wrap)return;
    wrap.querySelectorAll(".houki-exam-card").forEach(button=>{
      const t=tally(button.dataset.prefix),isDone=t.answered===12;
      button.classList.toggle("done",isDone);
      const pct=Math.round(t.correct/12*100);
      button.querySelector(".houki-exam-progress").textContent=
        (isDone?"完了 ":"進捗 ")+t.answered+"/12 · 正解 "+t.correct+" ("+pct+"%)";
    });
  }
  function renderRecent(){
    const root=document.getElementById("houkiExamRecent");if(!root)return;
    root.replaceChildren();
    const all=Object.values(examDb.attempts).sort((a,b)=>b.savedAt-a.savedAt).slice(0,8);
    if(!all.length){root.textContent="まだ試験回別の演習履歴はありません。";return}
    all.forEach(a=>{
      const sc=scoreAttempt(a),b=document.createElement("button");
      b.type="button";b.className="houki-recent-row";
      b.textContent=a.label+" · "+(a.status==="completed"?"完了":"途中")+
        "　"+sc.correct+"/"+sc.answered+"　"+new Date(a.savedAt).toLocaleString();
      b.onclick=()=>{
        const entry=findEntry(a.prefix);
        if(!entry)return;
        if(a.status==="completed"){showResult(a);return}
        start(entry,JSON.parse(JSON.stringify(a)));
      };
      root.append(b);
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
    help.textContent="各回12問を自動採点。途中終了、問題移動、結果の保存・再開ができます。";
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
    const recentTitle=document.createElement("h3");recentTitle.textContent="直近の演習";
    const recent=document.createElement("div");recent.id="houkiExamRecent";
    wrap.append(recentTitle,recent);
    const root=document.querySelector("main")||document.body;
    const answerBox=document.createElement("section");
    answerBox.id="houkiSessionAnswer";answerBox.hidden=true;
    answerBox.innerHTML='<p class="houki-answer-title">回答を選択</p>'+
      '<p class="houki-progress-label"></p>'+
      '<p class="houki-answer-hint">問題文と選択肢を読んで回答してください。</p>'+
      '<div class="houki-number-buttons" role="group" aria-label="解答番号"></div>'+
      '<p class="houki-answer-feedback" role="status" aria-live="polite"></p>'+
      '<div class="houki-jumps" role="group" aria-label="問題一覧"></div>'+
      '<div class="houki-bottom-nav"><button type="button" class="houki-prev-question">前の問題</button>'+
      '<button type="button" class="houki-next-question">次の問題</button></div>'+
      '<button type="button" class="houki-finish-question">途中終了・結果を見る</button>'+
      '<div class="houki-result-rows" hidden></div>'+
      '<textarea class="houki-export" rows="7" readonly hidden></textarea>'+
      '<button type="button" class="houki-copy" hidden>結果をコピー</button>';
    for(let n=1;n<=4;n++){
      const b=document.createElement("button");
      b.type="button";b.dataset.answer=String(n);b.textContent=String(n);
      b.setAttribute("aria-label",n+"番を回答");
      b.onclick=()=>answer(n);answerBox.querySelector(".houki-number-buttons").append(b);
    }
    for(let i=0;i<12;i++){
      const b=document.createElement("button");
      b.type="button";b.textContent=String(i+1);b.setAttribute("aria-label","問"+(i+1));
      b.onclick=()=>{if(exam&&!examReviewMode)showPosition(i)};
      answerBox.querySelector(".houki-jumps").append(b);
    }
    answerBox.querySelector(".houki-next-question").onclick=()=>{
      if(exam)nextInExam();
      else{quitFixedMode();wrap.scrollIntoView({block:"start",behavior:"smooth"})}
    };
    answerBox.querySelector(".houki-prev-question").onclick=()=>{if(exam)showPosition(exam.pos-1)};
    answerBox.querySelector(".houki-finish-question").onclick=()=>finishExam(false);
    answerBox.querySelector(".houki-copy").onclick=()=>{
      const value=answerBox.querySelector(".houki-export").value;
      if(navigator.clipboard?.writeText)navigator.clipboard.writeText(value).catch(()=>{});
    };
    // Place controls after all source options, never inside long choice text.
    const question=document.getElementById("qtext");
    if(question&&question.parentNode)question.insertAdjacentElement("afterend",answerBox);
    else wrap.append(answerBox);
    root.insertBefore(wrap,root.firstElementChild);
    // Native mark() normally draws a new random item. Suppress only that
    // automatic advance while the fixed exam engine controls navigation.
    if(typeof draw==="function"){
      const nativeDraw=draw;
      draw=function(){if(exam)return;return nativeDraw()};
    }
    // Native draw() remains available in the ordinary law study mode.
    const index=document.getElementById("tbody");
    if(index)index.addEventListener("click",()=>quitFixedMode(),true);
    document.querySelectorAll("#fterm,#fslotA,#fslotB,.fc,.ft,#tgroup,input[name=mode]").forEach(el=>
      el.addEventListener("change",()=>{if(exam)quitFixedMode()}));
    refresh();
    document.addEventListener("keydown",e=>{
      if(!exam||e.altKey||e.ctrlKey||e.metaKey||e.isComposing)return;
      const t=e.target;
      if(t?.closest?.('input,textarea,select,[contenteditable="true"]'))return;
      if(/^[1-4]$/.test(e.key)){e.preventDefault();e.stopImmediatePropagation();answer(Number(e.key))}
      else if(e.key==="ArrowRight"){e.preventDefault();e.stopImmediatePropagation();nextInExam()}
      else if(e.key==="ArrowLeft"){e.preventDefault();e.stopImmediatePropagation();showPosition(exam.pos-1)}
    },true);
    // Extend the existing law state object rather than creating a parallel login.
    // The matching Oracle merge must preserve the examV1 field.
    if(typeof stateObject==="function"){
      const oldStateObject=stateObject;
      stateObject=function(){const o=oldStateObject();o.examV1=examDb;return o};
    }
    if(typeof applyState==="function"){
      const oldApplyState=applyState;
      applyState=function(o){
        const result=oldApplyState(o);
        if(o?.examV1){examDb=mergeExamDb(examDb,o.examV1);saveDbToLocal()}
        refresh();renderRecent();
        return result;
      };
    }
    renderRecent();
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
