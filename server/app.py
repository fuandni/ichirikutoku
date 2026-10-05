import os, json, time, hmac, hashlib, base64, secrets
from pathlib import Path
import oracledb
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

APP_DIR = Path(__file__).resolve().parent
QUIZ_PASSWORD = os.environ.get('QUIZ_PASSWORD', '')
SESSION_SECRET = os.environ.get('SESSION_SECRET', '')
COOKIE_SECURE = os.environ.get('COOKIE_SECURE', 'true').lower() not in ('0', 'false', 'no')
COOKIE_NAME = 'ichirikutoku_session'
COOKIE_DAYS = int(os.environ.get('COOKIE_DAYS', '365'))

ORACLE_USER = os.environ.get('ORACLE_USER', '')
ORACLE_PASSWORD = os.environ.get('ORACLE_PASSWORD', '')
ORACLE_DSN = os.environ.get('ORACLE_DSN', '')

if not QUIZ_PASSWORD:
    raise RuntimeError('QUIZ_PASSWORD is required')
if len(SESSION_SECRET) < 32:
    raise RuntimeError('SESSION_SECRET must be at least 32 characters')
if not ORACLE_USER:
    raise RuntimeError('ORACLE_USER is required')
if not ORACLE_PASSWORD:
    raise RuntimeError('ORACLE_PASSWORD is required')
if not ORACLE_DSN:
    raise RuntimeError('ORACLE_DSN is required')

app = FastAPI(title='Ichirikutoku Progress Sync', docs_url=None, redoc_url=None, openapi_url=None)


def db_conn():
    return oracledb.connect(
        user=ORACLE_USER,
        password=ORACLE_PASSWORD,
        dsn=ORACLE_DSN
    )


def lob_text(value):
    if value is None:
        return None
    if hasattr(value, 'read'):
        return value.read()
    return value

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

    con = db_conn()
    try:
        cur = con.cursor()
        cur.execute(
            'SELECT db_json, session_json, session_updated_at, updated_at '
            'FROM state WHERE id=1'
        )
        row = cur.fetchone()
        if row is None:
            raise RuntimeError('state id=1 not found')

        db_json = lob_text(row[0])
        session_json = lob_text(row[1])
        session_updated_at = int(row[2] or 0)
        updated_at = int(row[3] or 0)
    finally:
        con.close()

    db_obj = json.loads(db_json) if db_json else {'mastery': {}, 'attempts': []}
    session_obj = json.loads(session_json) if session_json else None

    return {
        'db': db_obj,
        'session': session_obj,
        'sessionUpdatedAt': session_updated_at,
        'updatedAt': updated_at
    }


@app.post('/api/sync')
def sync(body: SyncBody, request: Request):
    require_auth(request)
    now = int(time.time() * 1000)

    con = db_conn()
    try:
        cur = con.cursor()
        cur.execute(
            'SELECT db_json, session_json, session_updated_at, updated_at '
            'FROM state WHERE id=1 FOR UPDATE'
        )
        row = cur.fetchone()
        if row is None:
            raise RuntimeError('state id=1 not found')

        server_db_json = lob_text(row[0])
        server_db = json.loads(server_db_json) if server_db_json else {
            'mastery': {},
            'attempts': []
        }
        merged = merge_db(server_db, body.db)

        server_session_updated = int(row[2] or 0)
        server_session_json = lob_text(row[1])

        if int(body.sessionUpdatedAt or 0) >= server_session_updated:
            session_json = (
                json.dumps(body.session, ensure_ascii=False, separators=(',', ':'))
                if body.session is not None else None
            )
            session_updated = int(body.sessionUpdatedAt or 0)
        else:
            session_json = server_session_json
            session_updated = server_session_updated

        db_json = json.dumps(merged, ensure_ascii=False, separators=(',', ':'))

        cur.setinputsizes(
            db_json=oracledb.DB_TYPE_CLOB,
            session_json=oracledb.DB_TYPE_CLOB
        )
        cur.execute(
            '''
            UPDATE state
               SET db_json = :db_json,
                   session_json = :session_json,
                   session_updated_at = :session_updated_at,
                   updated_at = :updated_at
             WHERE id = 1
            ''',
            db_json=db_json,
            session_json=session_json,
            session_updated_at=session_updated,
            updated_at=now
        )
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

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

    con = db_conn()
    try:
        cur = con.cursor()
        cur.execute(
            'SELECT state_json, updated_at '
            'FROM houki_state WHERE id=1'
        )
        row = cur.fetchone()
        if row is None:
            raise RuntimeError('houki_state id=1 not found')

        state_json = lob_text(row[0])
        updated = int(row[1] or 0)
    finally:
        con.close()

    state_obj = normalize_houki(json.loads(state_json) if state_json else {})
    state_obj['_sync']['updatedAt'] = updated
    return {'state': state_obj, 'updatedAt': updated}


@app.post('/api/houki/sync')
def houki_sync(body: HoukiSyncBody, request: Request):
    require_auth(request)
    embedded = (
        (body.state.get('_sync') or {}).get('updatedAt')
        if isinstance(body.state.get('_sync'), dict)
        else 0
    )
    client_updated = max(_int(body.updatedAt, 0), _int(embedded, 0))

    con = db_conn()
    try:
        cur = con.cursor()
        cur.execute(
            'SELECT state_json, updated_at '
            'FROM houki_state WHERE id=1 FOR UPDATE'
        )
        row = cur.fetchone()
        if row is None:
            raise RuntimeError('houki_state id=1 not found')

        server_updated = int(row[1] or 0)
        server_json = lob_text(row[0])
        server_state = json.loads(server_json) if server_json else {}

        merged = merge_houki(
            server_state,
            body.state,
            server_updated,
            client_updated
        )
        merged_updated = max(server_updated, client_updated)
        merged['_sync']['updatedAt'] = merged_updated
        state_json = json.dumps(
            merged,
            ensure_ascii=False,
            separators=(',', ':')
        )

        cur.setinputsizes(state_json=oracledb.DB_TYPE_CLOB)
        cur.execute(
            '''
            UPDATE houki_state
               SET state_json = :state_json,
                   updated_at = :updated_at
             WHERE id = 1
            ''',
            state_json=state_json,
            updated_at=merged_updated
        )
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

    return {'state': merged, 'updatedAt': merged_updated}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})
