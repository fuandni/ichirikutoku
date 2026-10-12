import ast
from pathlib import Path
from typing import Any, Dict

path = Path(__file__).resolve().parents[1] / "server" / "app.py"
source = ast.parse(path.read_text(encoding="utf-8"))
names = {"safe_json_obj", "_int", "normalize_exam_v1", "merge_exam_v1",
         "normalize_houki", "merge_houki"}
nodes = [node for node in source.body
         if isinstance(node, ast.FunctionDef) and node.name in names]
namespace = {"Any": Any, "Dict": Dict}
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)

class API:
    pass

app = API()
for name in names:
    setattr(app, name, namespace[name])

def attempt(aid, when, answer=1):
    prefix = "JY50A-"
    ids = [prefix+f"{i:02d}" for i in range(1,13)]
    return {"id":aid,"prefix":prefix,"ids":ids,"label":"令和5年10月 A",
            "status":"active","savedAt":when,"started":100,"position":2,
            "answers":{ids[0]:{"choice":answer,"correct":answer==1,"time":when}}}

def test_merges_same_session_by_timestamp():
    a={"attempts":{"L1":attempt("L1",100)},"lastId":"L1","updatedAt":100}
    b={"attempts":{"L1":attempt("L1",200,2)},"lastId":"L1","updatedAt":200}
    out=app.merge_exam_v1(a,b)
    assert out["attempts"]["L1"]["answers"]["JY50A-01"]["choice"]==2

def test_merge_keeps_history_from_both_devices():
    a={"attempts":{"L1":attempt("L1",100)},"lastId":"L1","updatedAt":100}
    b={"attempts":{"L2":attempt("L2",200)},"lastId":"L2","updatedAt":200}
    out=app.merge_exam_v1(a,b)
    assert set(out["attempts"])=={"L1","L2"}
    assert out["lastId"]=="L2"

def test_old_law_progress_not_lost():
    old={"rec":{"JY50A-01":"o"},"_sync":{"recAt":{"JY50A-01":50}}}
    upgraded={"examV1":{"attempts":{"L1":attempt("L1",100)},"lastId":"L1","updatedAt":100},
              "rec":{"JY50A-02":"x"},"_sync":{"recAt":{"JY50A-02":90}}}
    out=app.merge_houki(old,upgraded,50,90)
    assert out["rec"]=={"JY50A-01":"o","JY50A-02":"x"}
    assert "L1" in out["examV1"]["attempts"]

if __name__=="__main__":
    test_merges_same_session_by_timestamp()
    test_merge_keeps_history_from_both_devices()
    test_old_law_progress_not_lost()
    print("Law exam sync merge: PASS")
