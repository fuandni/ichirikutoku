import os, json, time, hmac, hashlib, base64, sqlite3, secrets
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

APP_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get('DB_PATH', str(APP_DIR / 'progress.db')))
QUIZ_PASSWORD = os.environ.get('QUIZ_PASSWORD', '')
SESSION_SECRET = os.environ.get('SESSION_SECRET', '')
COOKIE_SECURE = os.environ.get('COOKIE_SECURE', 'true').lower() not in ('0', 'false', 'no')
COOKIE_NAME = 'ichirikutoku_session'
COOKIE_DAYS = int(os.environ.get('COOKIE_DAYS', '365'))

if not QUIZ_PASSWORD:
    raise RuntimeError('QUIZ_PASSWORD is required')
if len(SESSION_SECRET) < 32:
    raise RuntimeError('SESSION_SECRET must be at least 32 characters')

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
app = FastAPI(title='Ichirikutoku Progress Sync', docs_url=None, redoc_url=None, openapi_url=None)


def db_conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA journal_mode=WAL')
    con.execute('PRAGMA synchronous=NORMAL')
    return con


def init_db():
    with db_conn() as con:
        con.execute('''
            CREATE TABLE IF NOT EXISTS state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                db_json TEXT NOT NULL DEFAULT '{"mastery":{},"attempts":[]}',
                session_json TEXT,
                session_updated_at INTEGER NOT NULL DEFAULT 0,
                updated_at INTEGER NOT NULL DEFAULT 0
            )
        ''')
        con.execute('INSERT OR IGNORE INTO state(id) VALUES (1)')
        con.execute('''
            CREATE TABLE IF NOT EXISTS houki_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                state_json TEXT NOT NULL DEFAULT '{}',
                updated_at INTEGER NOT NULL DEFAULT 0
            )
        ''')
        con.execute('INSERT OR IGNORE INTO houki_state(id) VALUES (1)')
        con.commit()


init_db()


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip('=')


def sign_session(exp: int) -> str:
    payload = str(exp)
    sig = hmac.new(SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).digest()
    return payload + '.' + b64u(sig)


def verify_session(token: str | None) -> bool:
    if not token or '.' not in token:
        return False
    payload, sig = token.split('.', 1)
    try:
        exp = int(payload)
    except ValueError:
        return False
    if exp < int(time.time()):
        return False
    expected = sign_session(exp).split('.', 1)[1]
    return hmac.compare_digest(sig, expected)


def require_auth(request: Request):
    if not verify_session(request.cookies.get(COOKIE_NAME)):
        raise HTTPException(status_code=401, detail='authentication required')


def safe_json_obj(value: Any, fallback: Dict[str, Any]) -> Dict[str, Any]:
    return value if isinstance(value, dict) else fallback


def normalize_db(value: Any) -> Dict[str, Any]:
    obj = safe_json_obj(value, {})
    mastery = obj.get('mastery') if isinstance(obj.get('mastery'), dict) else {}
    attempts = obj.get('attempts') if isinstance(obj.get('attempts'), list) else []
    return {'mastery': mastery, 'attempts': attempts}


def merge_mastery(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for qid in set(a) | set(b):
        x = a.get(qid)
        y = b.get(qid)
        if not isinstance(x, dict):
            out[qid] = y if isinstance(y, dict) else {}
            continue
        if not isinstance(y, dict):
            out[qid] = x
            continue
        merged = dict(x)
        for k in ('attempts', 'correct', 'wrong'):
            try:
                merged[k] = max(int(x.get(k, 0) or 0), int(y.get(k, 0) or 0))
            except Exception:
                pass
        tx = int(x.get('lastAt', 0) or 0)
        ty = int(y.get('lastAt', 0) or 0)
        if ty >= tx:
            for k, v in y.items():
                if k not in ('attempts', 'correct', 'wrong'):
                    merged[k] = v
        out[qid] = merged
    return out


def merge_attempts(a: list, b: list) -> list:
    by_id: Dict[str, dict] = {}
    anonymous = []
    for item in list(a) + list(b):
        if not isinstance(item, dict):
            continue
        iid = item.get('id')
        if not iid:
            anonymous.append(item)
            continue
        old = by_id.get(str(iid))
        if old is None or int(item.get('finished', 0) or 0) >= int(old.get('finished', 0) or 0):
            by_id[str(iid)] = item
    merged = list(by_id.values()) + anonymous
    merged.sort(key=lambda x: int(x.get('finished', 0) or 0))
    return merged[-100:]


def merge_db(server: Any, client: Any) -> Dict[str, Any]:
    s = normalize_db(server)
    c = normalize_db(client)
    return {
        'mastery': merge_mastery(s['mastery'], c['mastery']),
        'attempts': merge_attempts(s['attempts'], c['attempts'])
    }


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value or 0)
    except Exception:
        return default


def normalize_houki(value: Any) -> Dict[str, Any]:
    obj = safe_json_obj(value, {})
    raw_rec = obj.get('rec') if isinstance(obj.get('rec'), dict) else {}
    rec = {str(k): v for k, v in raw_rec.items() if v in ('o', 'x')}
    review = obj.get('review') if isinstance(obj.get('review'), list) else []
    review = list(dict.fromkeys(str(x) for x in review if isinstance(x, (str, int))))
    ui = obj.get('ui') if isinstance(obj.get('ui'), dict) else {}
    sync = obj.get('_sync') if isinstance(obj.get('_sync'), dict) else {}
    raw_rec_at = sync.get('recAt') if isinstance(sync.get('recAt'), dict) else {}
    rec_at = {}
    for qid in rec:
        t = _int(raw_rec_at.get(qid), 0)
        rec_at[qid] = t if t > 0 else 1
    return {
        'version': _int(obj.get('version'), 1) or 1,
        'rec': rec,
        'review': review,
        'ui': ui,
        'fs': obj.get('fs'),
        'exportedAt': obj.get('exportedAt'),
        '_sync': {
            'recAt': rec_at,
            'resetAt': _int(sync.get('resetAt'), 0),
            'reviewUpdatedAt': _int(sync.get('reviewUpdatedAt'), 0) or (1 if review else 0),
            'updatedAt': _int(sync.get('updatedAt'), 0),
        }
    }


def merge_houki(server: Any, client: Any, server_updated: int, client_updated: int) -> Dict[str, Any]:
    s = normalize_houki(server)
    c = normalize_houki(client)
    ss = s['_sync']
    cs = c['_sync']
    s_rec = s['rec']
    c_rec = c['rec']
    s_at = ss['recAt']
    c_at = cs['recAt']
    s_reset = _int(ss.get('resetAt'), 0)
    c_reset = _int(cs.get('resetAt'), 0)

    merged_rec: Dict[str, str] = {}
    merged_at: Dict[str, int] = {}
    for qid in set(s_rec) | set(c_rec):
        if qid in s_rec:
            se = (_int(s_at.get(qid), 1) or 1, s_rec[qid], 's')
        else:
            se = (s_reset, None, 's')
        if qid in c_rec:
            ce = (_int(c_at.get(qid), 1) or 1, c_rec[qid], 'c')
        else:
            ce = (c_reset, None, 'c')

        if ce[0] > se[0]:
            chosen = ce
        elif se[0] > ce[0]:
            chosen = se
        else:
            chosen = ce if client_updated > server_updated else se
        if chosen[1] in ('o', 'x'):
            merged_rec[qid] = chosen[1]
            merged_at[qid] = chosen[0]

    s_review_at = _int(ss.get('reviewUpdatedAt'), 0)
    c_review_at = _int(cs.get('reviewUpdatedAt'), 0)
    if c_review_at > s_review_at:
        review = c['review']
        review_at = c_review_at
    elif s_review_at > c_review_at:
        review = s['review']
        review_at = s_review_at
    else:
        review = c['review'] if client_updated > server_updated else s['review']
        review_at = max(s_review_at, c_review_at)

    newer = c if client_updated > server_updated else s
    return {
        'version': max(_int(s.get('version'), 1), _int(c.get('version'), 1), 1),
        'rec': merged_rec,
        'review': review,
        'ui': newer.get('ui') if isinstance(newer.get('ui'), dict) else {},
        'fs': newer.get('fs'),
        'exportedAt': newer.get('exportedAt'),
        '_sync': {
            'recAt': merged_at,
            'resetAt': max(s_reset, c_reset),
            'reviewUpdatedAt': review_at,
            'updatedAt': max(server_updated, client_updated),
        }
    }


class LoginBody(BaseModel):
    password: str


class SyncBody(BaseModel):
    db: Dict[str, Any]
    session: Any = None
    sessionUpdatedAt: int = 0


class HoukiSyncBody(BaseModel):
    state: Dict[str, Any]
    updatedAt: int = 0


@app.get('/health')
def health():
    return {'ok': True, 'time': int(time.time() * 1000)}


@app.post('/api/login')
def login(body: LoginBody, response: Response):
    if not secrets.compare_digest(body.password, QUIZ_PASSWORD):
        raise HTTPException(status_code=401, detail='invalid password')
    exp = int(time.time()) + COOKIE_DAYS * 86400
    response.set_cookie(
        COOKIE_NAME,
        sign_session(exp),
        max_age=COOKIE_DAYS * 86400,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite='lax',
        path='/'
    )
    return {'ok': True}


@app.post('/api/logout')
def logout(request: Request, response: Response):
    require_auth(request)
    response.delete_cookie(COOKIE_NAME, path='/')
    return {'ok': True}


@app.get('/api/state')
def state(request: Request):
    require_auth(request)
    with db_conn() as con:
        row = con.execute('SELECT * FROM state WHERE id=1').fetchone()
    db_obj = json.loads(row['db_json']) if row['db_json'] else {'mastery': {}, 'attempts': []}
    session_obj = json.loads(row['session_json']) if row['session_json'] else None
    return {
        'db': db_obj,
        'session': session_obj,
        'sessionUpdatedAt': int(row['session_updated_at'] or 0),
        'updatedAt': int(row['updated_at'] or 0)
    }


@app.post('/api/sync')
def sync(body: SyncBody, request: Request):
    require_auth(request)
    now = int(time.time() * 1000)
    with db_conn() as con:
        con.execute('BEGIN IMMEDIATE')
        row = con.execute('SELECT * FROM state WHERE id=1').fetchone()
        server_db = json.loads(row['db_json']) if row['db_json'] else {'mastery': {}, 'attempts': []}
        merged = merge_db(server_db, body.db)

        server_session_updated = int(row['session_updated_at'] or 0)
        server_session_json = row['session_json']
        if int(body.sessionUpdatedAt or 0) >= server_session_updated:
            session_json = json.dumps(body.session, ensure_ascii=False, separators=(',', ':')) if body.session is not None else None
            session_updated = int(body.sessionUpdatedAt or 0)
        else:
            session_json = server_session_json
            session_updated = server_session_updated

        db_json = json.dumps(merged, ensure_ascii=False, separators=(',', ':'))
        con.execute(
            'UPDATE state SET db_json=?, session_json=?, session_updated_at=?, updated_at=? WHERE id=1',
            (db_json, session_json, session_updated, now)
        )
        con.commit()

    session_obj = json.loads(session_json) if session_json else None
    return {
        'db': merged,
        'session': session_obj,
        'sessionUpdatedAt': session_updated,
        'updatedAt': now
    }


@app.get('/api/houki/state')
def houki_state(request: Request):
    require_auth(request)
    with db_conn() as con:
        row = con.execute('SELECT * FROM houki_state WHERE id=1').fetchone()
    state_obj = normalize_houki(json.loads(row['state_json']) if row['state_json'] else {})
    updated = int(row['updated_at'] or 0)
    state_obj['_sync']['updatedAt'] = updated
    return {'state': state_obj, 'updatedAt': updated}


@app.post('/api/houki/sync')
def houki_sync(body: HoukiSyncBody, request: Request):
    require_auth(request)
    embedded = (body.state.get('_sync') or {}).get('updatedAt') if isinstance(body.state.get('_sync'), dict) else 0
    client_updated = max(_int(body.updatedAt, 0), _int(embedded, 0))
    with db_conn() as con:
        con.execute('BEGIN IMMEDIATE')
        row = con.execute('SELECT * FROM houki_state WHERE id=1').fetchone()
        server_updated = int(row['updated_at'] or 0)
        server_state = json.loads(row['state_json']) if row['state_json'] else {}
        merged = merge_houki(server_state, body.state, server_updated, client_updated)
        merged_updated = max(server_updated, client_updated)
        merged['_sync']['updatedAt'] = merged_updated
        state_json = json.dumps(merged, ensure_ascii=False, separators=(',', ':'))
        con.execute('UPDATE houki_state SET state_json=?, updated_at=? WHERE id=1', (state_json, merged_updated))
        con.commit()
    return {'state': merged, 'updatedAt': merged_updated}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})
