#!/usr/bin/env python3
"""Fresh exam-first face for law practice; legacy data, controls and sync remain functional."""
from pathlib import Path
import sys

MARK = "HOUKI_MODERN_UI_V1"
if len(sys.argv) != 2:
    raise SystemExit("Usage: patch_houki_redesign.py /path/to/houki-practice/index.html")
p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
if MARK in s:
    print("Modern UI already present")
    raise SystemExit(0)
if "</body>" not in s or "HOUKI_SESSION_CARDS_V1" not in s:
    raise SystemExit("Expected existing law exam engine not found")
ui = r"""
<style>
/* HOUKI_MODERN_UI_V1 */
body.houki-redesigned{margin:0;background:#f4f7f7;color:#193442;font-family:system-ui,-apple-system,"Yu Gothic UI",Meiryo,sans-serif}
body.houki-redesigned>.wrap{display:none!important}
body.houki-redesigned>#houkiCloudStatus{display:none!important}
#houkiModernUI{min-height:100vh;font:inherit;letter-spacing:.005em}
#houkiModernUI *{box-sizing:border-box}
#houkiModernUI a{color:inherit;text-decoration:none}
#houkiModernUI button{cursor:pointer;touch-action:manipulation}
#houkiModernTop{background:linear-gradient(120deg,#173c47 0%,#1a5960 75%,#267672 100%);color:#f8ffff;padding:16px max(16px,calc((100vw - 1140px)/2)) 36px}
#houkiModernTop .hu-nav{display:flex;align-items:center;gap:12px;justify-content:space-between;flex-wrap:wrap}
#houkiModernTop .hu-home{font-size:13px;font-weight:700;color:#ddf5f2;border:1px solid #b0d8d58c;border-radius:999px;padding:9px 15px}
#houkiModernTop .hu-brand{font-size:13px;font-weight:800;letter-spacing:.12em;color:#d3ebe9}
#houkiModernTop #houkiModernSync{font-size:12px;color:#f2fbf9}
#houkiModernSync #houkiCloudStatus{display:inline-block!important;margin:0;background:#ffffff24!important;color:#fff!important;border:1px solid #ffffff44;border-radius:999px}
#houkiModernTop .hu-eyebrow{margin:38px 0 9px;font-size:13px;letter-spacing:.12em;font-weight:750;color:#bce3df}
#houkiModernTop h1{margin:0;font-size:clamp(29px,4vw,46px);letter-spacing:-.035em;font-weight:850;line-height:1.28}
#houkiModernTop .hu-subtitle{margin:12px 0 0;max-width:690px;color:#d0e7e5;line-height:1.75;font-size:14px}
#houkiModernPage{max-width:1140px;margin:-17px auto 0;padding:0 16px 64px;position:relative}
#houkiModernUI [hidden]{display:none!important}
#houkiModernHome .hu-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-bottom:25px}
#houkiModernHome .hu-stat{border:1px solid #dfe9e8;border-radius:14px;background:#fff;padding:16px 18px;box-shadow:0 9px 22px #1934420b}
#houkiModernHome .hu-stat span{display:block;font-size:12px;color:#527077;font-weight:700}
#houkiModernHome .hu-stat strong{display:block;font-size:25px;color:#183d47;margin-top:5px}
#houkiModernHome .hu-stats small{color:#7b8c92;font-size:11px;margin-left:5px}
#houkiModernHome .hu-intro{margin:0 0 18px}
#houkiModernHome .hu-intro h2{margin:0 0 5px;font-size:23px;letter-spacing:-.02em}
#houkiModernHome .hu-intro p{margin:0;font-size:13px;line-height:1.7;color:#587078}
#houkiModernHome #houkiSessionCards{background:transparent;border:0;padding:0;margin:0;max-width:none}
#houkiModernHome #houkiSessionCards>h2,#houkiModernHome #houkiSessionCards>.houki-exam-help{display:none}
#houkiModernHome #houkiSessionCards .houki-exam-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:13px}
#houkiModernHome #houkiSessionCards button.houki-exam-card{background:#fff;min-height:146px;border:1px solid #dce8e6;padding:19px;border-radius:15px;box-shadow:0 2px 9px #122c3409;color:#133842;gap:10px}
#houkiModernHome #houkiSessionCards button.houki-exam-card:hover{border-color:#248d85;background:#f9fdfc;transform:translateY(-1px)}
#houkiModernHome #houkiSessionCards button.houki-exam-card:focus-visible{outline:3px solid #24a493;outline-offset:2px}
#houkiModernHome #houkiSessionCards .houki-exam-name{font-weight:850;font-size:19px}
#houkiModernHome #houkiSessionCards .houki-exam-count{font-size:12px;color:#6a8386}
#houkiModernHome #houkiSessionCards .houki-exam-progress{background:#e9f4f1;color:#255e59;padding:8px 10px;border-radius:7px;font-size:13px}
#houkiModernHome #houkiSessionCards .houki-exam-card.done{border-color:#229082}
#houkiModernHome #houkiSessionCards #houkiSessionNotice{color:#48666b}
#houkiModernHome #houkiSessionCards>h3{margin:32px 0 12px;font-size:19px;color:#163943}
#houkiModernHome #houkiExamRecent{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
#houkiModernHome #houkiSessionCards .houki-recent-row{background:#fff;border:1px solid #dce8e6;min-height:59px;border-radius:10px;font-size:13px;padding:13px}
#houkiModernExam{background:#fff;border:1px solid #dce8e6;box-shadow:0 14px 30px #10272c0c;border-radius:18px;overflow:hidden}
#houkiModernExam .hu-exam-toolbar{padding:16px 22px;background:#f9fbfb;border-bottom:1px solid #e1e9e8;display:flex;align-items:center;justify-content:space-between;gap:12px}
#houkiModernExam .hu-back{border:1px solid #bdcfcc;color:#23545b;background:#fff;padding:10px 15px;font-size:13px;border-radius:9px;font-weight:750}
#houkiModernExam .hu-active{font-size:14px;color:#416367;font-weight:800;text-align:right}
#houkiModernExam .hu-question-intro{padding:22px 26px 0}
#houkiModernExam .hu-question-intro .hu-question-label{margin:0;color:#338880;letter-spacing:.09em;font-size:12px;font-weight:850}
#houkiModernExam .hu-question-intro h2{margin:5px 0 0;font-size:22px;letter-spacing:-.02em}
#houkiModernExam .hu-question-intro p{margin:6px 0 0;color:#668186;font-size:13px}
#houkiModernExam #sheet{padding:4px 24px 28px!important;border:0!important;border-radius:0!important;box-shadow:none!important;margin:0!important;background:#fff!important;max-width:100%!important;overflow:visible}
#houkiModernExam #sheet .sheet-bar{display:none!important}
#houkiModernExam #sheet .sheet-body{padding:0!important;margin:0!important;max-width:100%!important;overflow:visible!important}
#houkiModernExam #qtext{display:block;width:100%;max-width:100%;min-width:0;font-size:16px;line-height:1.9;overflow-wrap:anywhere}
#houkiModernExam #qtext .qhead{display:block;padding:14px 0 19px;line-height:1.9;white-space:normal;overflow-wrap:anywhere}
#houkiModernExam #qtext .mobile-options{width:100%;max-width:100%;min-width:0;overflow-x:auto}
#houkiModernExam #qtext .mobile-options>*{max-width:100%}
#houkiModernExam #houkiSessionAnswer{padding:18px;margin:23px 0 0;border-radius:14px;background:#f2f8f6;border-color:#d4e6e1;max-width:100%}
#houkiModernExam #houkiSessionAnswer .houki-number-buttons button{border-radius:10px;background:#fff}
#houkiModernExam #houkiSessionAnswer .houki-number-buttons button:not(:disabled):hover{border-color:#2d9a8e}
#houkiModernExam #houkiSessionAnswer .houki-next-question{background:#206963;border-color:#206963}
#houkiModernExam #houkiSessionAnswer .houki-progress-label{font-weight:800;color:#346a68}
#houkiModernFoot{text-align:center;font-size:12px;color:#648084;padding:0 16px 26px}
@media(max-width:800px){#houkiModernHome #houkiSessionCards .houki-exam-grid{grid-template-columns:repeat(2,minmax(0,1fr))}#houkiModernHome #houkiExamRecent{grid-template-columns:1fr}}
@media(max-width:560px){#houkiModernTop{padding:14px 16px 28px}#houkiModernTop .hu-eyebrow{margin-top:28px}#houkiModernPage{padding:0 10px 35px}#houkiModernHome .hu-stats{gap:6px;margin-bottom:20px}#houkiModernHome .hu-stat{padding:12px 9px;border-radius:10px}#houkiModernHome .hu-stat strong{font-size:21px}#houkiModernHome .hu-stat span{font-size:10px}#houkiModernHome .hu-intro h2{font-size:20px}#houkiModernHome #houkiSessionCards .houki-exam-grid{gap:9px}#houkiModernHome #houkiSessionCards button.houki-exam-card{padding:13px;min-height:137px}#houkiModernHome #houkiSessionCards .houki-exam-name{font-size:16px}#houkiModernHome #houkiSessionCards .houki-exam-progress{font-size:11px;line-height:1.5}#houkiModernExam .hu-exam-toolbar{padding:12px 13px}#houkiModernExam .hu-question-intro{padding:18px 14px 0}#houkiModernExam #sheet{padding:4px 12px 20px!important}#houkiModernExam #qtext{font-size:15px;line-height:1.85}#houkiModernExam #houkiSessionAnswer{padding:12px}#houkiModernExam .hu-active{font-size:12px}}
</style>
<script>
/* HOUKI_MODERN_UI_V1 */
(()=>{
"use strict";
function mount(){
  if(document.getElementById("houkiModernUI"))return;
  const cards=document.getElementById("houkiSessionCards");
  const sheet=document.getElementById("sheet");
  const answer=document.getElementById("houkiSessionAnswer");
  if(!cards||!sheet||!answer){console.error("Exam UI dependencies missing; keeping old UI");return}
  const root=document.createElement("div");
  root.id="houkiModernUI";
  root.innerHTML=[
    '<header id="houkiModernTop">',
    '<div class="hu-nav"><a class="hu-home" href="/home/">← 学習ホーム</a><span class="hu-brand">一陸特　/　法規</span><span id="houkiModernSync">学習記録を保存</span></div>',
    '<p class="hu-eyebrow">EXAM PRACTICE · REGULATIONS</p>',
    '<h1>法規 過去問演習</h1>',
    '<p class="hu-subtitle">試験回を選んで12問に挑戦。長文や組合せ問題も読みやすく、回答から結果確認まで、この画面で完結します。</p>',
    '</header><main id="houkiModernPage"><section id="houkiModernHome">',
    '<div class="hu-stats"><div class="hu-stat"><span>収録問題</span><strong>216<small>問</small></strong></div>',
    '<div class="hu-stat"><span>試験回</span><strong>18<small>回</small></strong></div>',
    '<div class="hu-stat"><span>回答記録</span><strong><span id="houkiModernAnswered">0</span><small>/ 216問</small></strong></div></div>',
    '<div class="hu-intro"><h2>試験回から解く</h2><p>年度とA・Bを選択。12問の途中終了・再開、問題移動、結果と履歴の保存に対応しています。</p></div>',
    '<div id="houkiModernCardsSlot"></div></section>',
    '<section id="houkiModernExam" hidden><div class="hu-exam-toolbar">',
    '<button type="button" class="hu-back" id="houkiModernBack">← 試験回一覧</button>',
    '<span class="hu-active" id="houkiModernExamName">法規・12問演習</span></div>',
    '<div class="hu-question-intro"><p class="hu-question-label">QUESTION / REGULATIONS</p>',
    '<h2>問題を解く</h2><p>正しい番号を選択すると自動採点します。</p></div>',
    '<div id="houkiModernSheetSlot"></div></section></main>',
    '<footer id="houkiModernFoot">一陸特 法規 · 回答履歴は既存の保存・同期機能を利用</footer>'
  ].join("");
  document.body.prepend(root);
  document.getElementById("houkiModernCardsSlot").append(cards);
  document.getElementById("houkiModernSheetSlot").append(sheet);
  document.body.classList.add("houki-redesigned");
  const home=document.getElementById("houkiModernHome");
  const exam=document.getElementById("houkiModernExam");
  const examName=document.getElementById("houkiModernExamName");
  const view=(name)=>{
    home.hidden=name!=="home";exam.hidden=name!=="exam";
    if(name==="exam"){
      const selected=cards.querySelector(".houki-exam-card.selected .houki-exam-name");
      examName.textContent=selected?.textContent||"法規・12問演習";
    }
    window.scrollTo({top:0,behavior:"instant"});
  };
  const exit=()=>{
    // The old engine keeps storing partial attempts, and its quit handler
    // listens to the change event from this existing filter.
    const term=document.getElementById("fterm");
    if(term)term.dispatchEvent(new Event("change",{bubbles:true}));
    view("home");
  };
  document.getElementById("houkiModernBack").addEventListener("click",exit);
  cards.addEventListener("click",e=>{
    const card=e.target.closest(".houki-exam-card");
    const recent=e.target.closest(".houki-recent-row");
    if(!card&&!recent)return;
    if(!answer.hidden)view("exam");
  });
  answer.addEventListener("click",e=>{
    const btn=e.target.closest(".houki-next-question");
    if(!btn)return;
    if(answer.hidden&&!document.body.classList.contains("houki-fixed-exam"))view("home");
  });
  // Native question changes must scroll the new question stage, not the hidden legacy page.
  if(typeof scrollQuestionTop==="function"){
    scrollQuestionTop=function(){
      requestAnimationFrame(()=>{
        if(!exam.hidden){
          const rect=exam.getBoundingClientRect();
          window.scrollTo({top:Math.max(0,window.scrollY+rect.top-8),behavior:"instant"});
        }
      });
    };
  }
  function update(){
    try{
      const data=typeof rec==="object"&&rec?rec:{};
      document.getElementById("houkiModernAnswered").textContent=
        Object.keys(data).filter(k=>/^JY\d{2}[AB]-\d{2}$/.test(k)&&["o","x"].includes(data[k])).length;
    }catch(err){}
    const status=document.getElementById("houkiCloudStatus");
    const slot=document.getElementById("houkiModernSync");
    if(status&&slot&&!slot.contains(status))slot.replaceChildren(status);
  }
  update();setInterval(update,2200);
  if(location.hash==="#houkiSessionCards")
    requestAnimationFrame(()=>cards.scrollIntoView({block:"start",behavior:"instant"}));
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",mount,{once:true});
else mount();
})();
</script>
"""
p.write_text(s.replace("</body>",ui+"\n</body>",1),encoding="utf-8")
print("Installed HOUKI_MODERN_UI_V1")
