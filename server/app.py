#!/usr/bin/env python3
"""Fla w Tbatik – Media team app (v2).

Python standard library only (runs on the Raspberry Pi).
Data: SQLite in DATA_DIR. Uploaded files: DATA_DIR/files.
Tasks come from the shared Google Sheet (tab "Marketing and Media")
through an Apps Script bridge; the site writes status back to it.
"""
import base64, hashlib, hmac, http.cookies, json, mimetypes, os, re, secrets, sqlite3, threading, time, urllib.parse, urllib.request
from datetime import datetime, date, timezone, timedelta
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

ROOT = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(ROOT, 'public')
TOOLS_DIR = os.path.join(os.path.dirname(ROOT), '_tools')  # the tools pages (index.html, data.js, assets/)
DATA_DIR = os.environ.get('FTB_DATA', os.path.join(ROOT, 'data'))
FILES = os.path.join(DATA_DIR, 'files')
PORT = int(os.environ.get('FTB_PORT', '8090'))
RIYADH = timezone(timedelta(hours=3))
MAX_UPLOAD = 25 * 1024 * 1024
os.makedirs(FILES, exist_ok=True)

STATUSES = ['Not Started', 'In Progress', 'Submitted', 'Changes requested', 'Done']
PROGRESS = {'Not Started': 0, 'In Progress': 30, 'Submitted': 70, 'Changes requested': 50, 'Done': 100}
ROLES = ['admin', 'head', 'member', 'viewer']

_lock = threading.Lock()


def db():
    c = sqlite3.connect(os.path.join(DATA_DIR, 'media.db'), timeout=10)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, name TEXT, sheet_name TEXT,
          role TEXT, job TEXT DEFAULT '', pw TEXT, active INTEGER DEFAULT 1, created TEXT);
        CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, user_id INTEGER, created REAL);
        CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY, v TEXT);
        CREATE TABLE IF NOT EXISTS tasks(key TEXT PRIMARY KEY, row INTEGER, week INTEGER, week_label TEXT, category TEXT,
          task TEXT, detail TEXT, owner TEXT, support TEXT, timing TEXT, due TEXT, priority TEXT, deliverable TEXT,
          status TEXT, progress INTEGER, notes TEXT, synced REAL);
        CREATE TABLE IF NOT EXISTS weeks(n INTEGER PRIMARY KEY, published INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS subs(id INTEGER PRIMARY KEY, task_key TEXT, user_id INTEGER, link TEXT, file TEXT,
          file_name TEXT, note TEXT, caption TEXT, created TEXT, review TEXT, review_by INTEGER, review_note TEXT, reviewed TEXT);
        CREATE TABLE IF NOT EXISTS log(id INTEGER PRIMARY KEY, at TEXT, user_id INTEGER, what TEXT);
        CREATE TABLE IF NOT EXISTS ideas(id INTEGER PRIMARY KEY, at TEXT, user_id INTEGER, kind TEXT, text TEXT, link TEXT, status TEXT DEFAULT '', reply TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS idea_votes(idea_id INTEGER, user_id INTEGER, PRIMARY KEY(idea_id, user_id));
        CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, at TEXT, about INTEGER, author INTEGER, cat TEXT, text TEXT);
        ''')
        cols = [r['name'] for r in c.execute('PRAGMA table_info(users)')]
        if 'invite' not in cols:
            c.execute('ALTER TABLE users ADD COLUMN invite TEXT')
        for col in ('last_seen REAL', 'last_login TEXT', 'last_tasks REAL'):
            if col.split()[0] not in cols:
                c.execute('ALTER TABLE users ADD COLUMN ' + col)


# ---------- helpers ----------
def now_iso():
    return datetime.now(RIYADH).strftime('%Y-%m-%d %H:%M')


def hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(16)
    h = hashlib.scrypt(pw.encode(), salt=bytes.fromhex(salt), n=2 ** 14, r=8, p=1, dklen=32).hex()
    return salt + '$' + h


def check_pw(pw, stored):
    if not stored:
        return False
    try:
        salt, _ = stored.split('$', 1)
        return hmac.compare_digest(hash_pw(pw, salt), stored)
    except Exception:
        return False


def setting(k, default=''):
    with db() as c:
        r = c.execute('SELECT v FROM settings WHERE k=?', (k,)).fetchone()
        return r['v'] if r else default


def set_setting(k, v):
    with db() as c:
        c.execute('INSERT INTO settings(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v', (k, v))


def log(uid, what):
    with db() as c:
        c.execute('INSERT INTO log(at,user_id,what) VALUES(?,?,?)', (now_iso(), uid, what[:500]))


def user_public(u, admin=False):
    d = {k: u[k] for k in ('id', 'username', 'name', 'sheet_name', 'role', 'job', 'active')}
    if admin:
        d['invite'] = ('/invite/' + u['invite']) if u['invite'] else ''
        d['has_password'] = bool(u['pw'])
    return d


def add_user(username, name, sheet_name, role, job=''):
    """Create a user without a password and return the invite token (they set their own password)."""
    tok = secrets.token_urlsafe(18)
    with db() as c:
        c.execute('INSERT INTO users(username,name,sheet_name,role,job,pw,created,invite) VALUES(?,?,?,?,?,?,?,?)',
                  (username.lower(), name, sheet_name, role, job, '', now_iso(), tok))
    return tok


# ---------- sheet bridge ----------
MONTHS = {m: i for i, m in enumerate(['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'], 1)}


def parse_due(s):
    """'Wed 11 Nov', '11 Nov', '2026-11-11', '11/11/2026' -> 'YYYY-MM-DD' or ''."""
    s = (s or '').strip()
    m = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', s)
    if m:
        return '%04d-%02d-%02d' % tuple(map(int, m.groups()))
    m = re.search(r'(\d{1,2})\s+([A-Za-z]{3})', s)
    if m and m.group(2).lower() in MONTHS:
        d, mo = int(m.group(1)), MONTHS[m.group(2).lower()]
        y = 2026 if mo >= 9 else 2027
        return '%04d-%02d-%02d' % (y, mo, d)
    m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m:
        a, b, y = map(int, m.groups())
        return '%04d-%02d-%02d' % (y, b, a) if a > 12 else '%04d-%02d-%02d' % (y, a, b)
    return ''


def bridge(action, payload=None):
    url, token = setting('bridge_url'), setting('bridge_token')
    if not url or not token:
        raise RuntimeError('Sheet bridge is not set up yet (Admin › Settings).')
    body = json.dumps({'token': token, 'action': action, 'payload': payload or {}}).encode()
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=40) as r:
        out = json.loads(r.read().decode())
    if not out.get('ok'):
        raise RuntimeError(out.get('error') or 'Bridge error')
    return out


COLS = ['Department', 'Phase', 'Category', 'Task', 'Subtask / Detail', 'Owner', 'Support', 'Timing', 'Priority',
        'Dependency', 'Deliverable / Evidence', 'Quality Check / Acceptance', 'Status', 'Progress %', 'Notes']


def rows_to_tasks(rows):
    """rows: list of {row: n, values: [15 cells]} from the bridge."""
    week, label, out = 0, '', []
    for r in rows:
        v = [str(x or '').strip() for x in r['values']] + [''] * 15
        joined = ' '.join(v).strip()
        m = re.match(r'^week\s*(\d+)', joined, re.I)
        if m and not v[3]:
            week, label = int(m.group(1)), joined
            continue
        if not v[3] or v[3] == 'Task':
            continue
        key = 'r%d-%s' % (r['row'], hashlib.sha1(v[3].encode()).hexdigest()[:6])
        out.append(dict(key=key, row=r['row'], week=week, week_label=label, category=v[2], task=v[3], detail=v[4],
                        owner=v[5], support=v[6], timing=v[7], due=parse_due(v[7]), priority=v[8], deliverable=v[10],
                        status=v[12] if v[12] in STATUSES else ('Not Started' if not v[12] else v[12]),
                        progress=int(float(v[13] or 0)) if re.match(r'^\d+(\.\d+)?$', v[13] or '') else 0, notes=v[14]))
    return out


def sync_from_sheet():
    out = bridge('read')
    tasks = rows_to_tasks(out['rows'])
    with _lock, db() as c:
        c.execute('DELETE FROM tasks')
        for t in tasks:
            t['synced'] = time.time()
            c.execute('INSERT INTO tasks(%s) VALUES(%s)' % (','.join(t), ','.join('?' * len(t))), tuple(t.values()))
            c.execute('INSERT OR IGNORE INTO weeks(n,published) VALUES(?,0)', (t['week'],))
    set_setting('last_sync', now_iso())
    return len(tasks)


def push_status(task, status, note=None):
    payload = {'row': task['row'], 'task': task['task'], 'status': status, 'progress': PROGRESS.get(status, 0)}
    if note is not None:
        payload['notes'] = note
    try:
        bridge('update', payload)
        return True
    except Exception as e:
        log(None, 'sheet write failed: %s' % e)
        return False


def owners_of(task):
    return task['owner'] or ''


def is_mine(task, user):
    o = owners_of(task).lower()
    if not o:
        return False
    if any(w in o for w in ('everyone', 'all media', 'all (', 'الكل')) or o.strip() == 'all':
        return True
    names = [n.strip().lower() for n in (user['sheet_name'] or user['name']).split(',') if n.strip()]
    first = [n.split()[0] for n in names if n.split()]
    return any(n in o for n in names) or any(re.search(r'\b%s\b' % re.escape(f), o) for f in first)


# ---------- HTTP ----------
class H(BaseHTTPRequestHandler):
    server_version = 'FTBMedia/2'

    def log_message(self, *a):
        pass

    # --- utils
    def send(self, code, obj=None, ctype='application/json', body=None, headers=None):
        if body is None:
            body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', ctype + ('; charset=utf-8' if ctype.startswith(('application/json', 'text/')) else ''))
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'same-origin')
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)

    def err(self, code, msg):
        self.send(code, {'error': msg})

    def body(self):
        n = int(self.headers.get('Content-Length') or 0)
        if n > MAX_UPLOAD * 1.4:
            raise ValueError('too big')
        raw = self.rfile.read(n) if n else b'{}'
        return json.loads(raw.decode() or '{}')

    def local(self):
        if self.headers.get('Cf-Connecting-Ip') or self.headers.get('X-Forwarded-For'):
            return False
        ip = self.client_address[0]
        return ip.startswith(('127.', '192.168.', '10.', '::1'))

    def user(self):
        self.preview_by = None
        ck = http.cookies.SimpleCookie(self.headers.get('Cookie') or '')
        tok = ck.get('ftb') and ck['ftb'].value
        if not tok:
            return None
        with db() as c:
            r = c.execute('SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=? AND u.active=1', (tok,)).fetchone()
            if r and time.time() - (r['last_seen'] or 0) > 20:
                c.execute('UPDATE users SET last_seen=? WHERE id=?', (time.time(), r['id']))
            # Admin "view as": see the site exactly as another user, read only.
            asid = ck.get('ftbas') and ck['ftbas'].value
            if r and r['role'] == 'admin' and asid and asid.isdigit():
                t = c.execute('SELECT * FROM users WHERE id=?', (int(asid),)).fetchone()
                if t:
                    self.preview_by = r['name']
                    return t
        return r

    def real_admin(self):
        ck = http.cookies.SimpleCookie(self.headers.get('Cookie') or '')
        tok = ck.get('ftb') and ck['ftb'].value
        if not tok:
            return None
        with db() as c:
            return c.execute("SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=? AND u.active=1 AND u.role='admin'", (tok,)).fetchone()

    def need(self, *roles):
        u = self.user()
        if not u:
            self.err(401, 'Please log in')
            return None
        if roles and u['role'] not in roles:
            self.err(403, 'Not allowed')
            return None
        if setting('maintenance') == '1' and u['role'] != 'admin':
            self.err(503, 'The site is under maintenance')
            return None
        return u

    # --- routing
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        p = urllib.parse.urlparse(self.path).path
        try:
            if p.startswith('/api/'):
                return self.api('GET', p)
            if p.startswith('/files/'):
                return self.file(p)
            if p == '/tools' or p.startswith('/tools/'):
                return self.tools(p)
            return self.static(p)
        except Exception as e:
            self.err(500, str(e))

    def do_POST(self):
        p = urllib.parse.urlparse(self.path).path
        try:
            return self.api('POST', p)
        except ValueError as e:
            self.err(400, str(e))
        except Exception as e:
            self.err(500, str(e))

    def tools(self, p):
        # The tools site, served here too so it knows who is logged in. Team only.
        if not self.user():
            return self.send(302, {}, headers={'Location': '/'})
        if p in ('/tools', '/tools/'):
            if p == '/tools':
                return self.send(302, {}, headers={'Location': '/tools/'})
            p = '/tools/index.html'
        rel = p[len('/tools/'):]
        if rel == 'local.js':
            # Private team info (names, Drive links). Kept on the Pi, never in git.
            f = os.path.join(DATA_DIR, 'tools-local.js')
            body = open(f, 'rb').read() if os.path.isfile(f) else b''
            return self.send(200, ctype='text/javascript', body=body)
        if not (rel in ('index.html', 'data.js') or rel.startswith('assets/')):
            return self.err(404, 'Not found')
        f = os.path.normpath(os.path.join(TOOLS_DIR, rel))
        if not f.startswith(TOOLS_DIR + os.sep) or not os.path.isfile(f):
            return self.err(404, 'Not found')
        ctype = mimetypes.guess_type(f)[0] or 'application/octet-stream'
        with open(f, 'rb') as fh:
            self.send(200, ctype=ctype, body=fh.read())

    def static(self, p):
        if p in ('/', '') or not os.path.splitext(p)[1]:
            p = '/index.html'
        f = os.path.normpath(os.path.join(PUBLIC, p.lstrip('/')))
        if not f.startswith(PUBLIC) or not os.path.isfile(f):
            return self.err(404, 'Not found')
        ctype = mimetypes.guess_type(f)[0] or 'application/octet-stream'
        with open(f, 'rb') as fh:
            self.send(200, ctype=ctype, body=fh.read())

    def file(self, p):
        u = self.need()
        if not u:
            return
        name = os.path.basename(p)
        f = os.path.join(FILES, name)
        if not re.match(r'^[a-f0-9]{24}\.[a-z0-9]{1,5}$', name) or not os.path.isfile(f):
            return self.err(404, 'Not found')
        with db() as c:
            s = c.execute('SELECT * FROM subs WHERE file=?', (name,)).fetchone()
        if not s or (u['role'] == 'member' and s['user_id'] != u['id']):
            return self.err(403, 'Not allowed')
        with open(f, 'rb') as fh:
            self.send(200, ctype=mimetypes.guess_type(f)[0] or 'application/octet-stream', body=fh.read())

    def api(self, method, p):
        R = lambda pat: re.fullmatch(pat, p)
        b = self.body() if method == 'POST' else {}

        # ---- view as (admin preview)
        if p == '/api/viewas' and method == 'POST':
            self.user()
            real = self.real_admin()
            if not real:
                return self.err(403, 'Not allowed')
            uid = b.get('id')
            if uid:
                log(real['id'], 'viewing the site as user %s' % uid)
                return self.send(200, {'ok': True}, headers={'Set-Cookie': 'ftbas=%d; Path=/; HttpOnly; SameSite=Lax; Max-Age=7200' % int(uid)})
            return self.send(200, {'ok': True}, headers={'Set-Cookie': 'ftbas=; Path=/; Max-Age=0'})
        if method == 'POST' and p not in ('/api/logout', '/api/login'):
            self.user()
            if self.preview_by:
                return self.err(403, 'Preview only. Nothing was changed.')

        # ---- auth
        if p == '/api/login' and method == 'POST':
            with db() as c:
                u = c.execute('SELECT * FROM users WHERE username=? AND active=1', ((b.get('username') or '').strip().lower(),)).fetchone()
            if not u or not check_pw(b.get('password') or '', u['pw']):
                time.sleep(0.7)
                return self.err(401, 'Wrong username or password')
            tok = secrets.token_urlsafe(32)
            with db() as c:
                c.execute('INSERT INTO sessions VALUES(?,?,?)', (tok, u['id'], time.time()))
            with db() as c:
                c.execute('UPDATE users SET last_login=?, last_seen=? WHERE id=?', (now_iso(), time.time(), u['id']))
            log(u['id'], 'logged in')
            secure = '; Secure' if self.headers.get('X-Forwarded-Proto') == 'https' else ''
            return self.send(200, {'ok': True, 'user': user_public(u)},
                             headers={'Set-Cookie': 'ftb=%s; Path=/; HttpOnly; SameSite=Lax; Max-Age=2592000%s' % (tok, secure)})
        if p == '/api/logout':
            ck = http.cookies.SimpleCookie(self.headers.get('Cookie') or '')
            if ck.get('ftb'):
                with db() as c:
                    c.execute('DELETE FROM sessions WHERE token=?', (ck['ftb'].value,))
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Set-Cookie', 'ftb=; Path=/; Max-Age=0')
            self.send_header('Set-Cookie', 'ftbas=; Path=/; Max-Age=0')
            out = b'{"ok": true}'
            self.send_header('Content-Length', str(len(out)))
            self.end_headers()
            self.wfile.write(out)
            return
        if p == '/api/me':
            u = self.user()
            return self.send(200, {'user': user_public(u) if u else None, 'preview_by': getattr(self, 'preview_by', None),
                                   'maintenance': setting('maintenance') == '1',
                                   'setup': no_users() and self.local()})
        if p == '/api/setup' and method == 'POST':
            # First admin can only be created from the home network, before any user exists.
            if not (no_users() and self.local()):
                return self.err(403, 'Setup is closed')
            un, pw, name = (b.get('username') or '').strip().lower(), b.get('password') or '', (b.get('name') or '').strip() or 'Rashad'
            if not re.match(r'^[a-z0-9_.-]{3,30}$', un) or len(pw) < 8:
                return self.err(400, 'Username 3–30 letters/numbers, password at least 8 characters')
            with db() as c:
                c.execute('INSERT INTO users(username,name,sheet_name,role,job,pw,created) VALUES(?,?,?,?,?,?,?)',
                          (un, name, name, 'admin', 'Media & Marketing lead', hash_pw(pw), now_iso()))
            log(None, 'admin created: %s' % un)
            return self.send(200, {'ok': True})
        if p == '/api/password' and method == 'POST':
            u = self.need()
            if not u:
                return
            if not check_pw(b.get('old') or '', u['pw']) or len(b.get('new') or '') < 6:
                return self.err(400, 'Old password is wrong, or the new one is shorter than 6')
            with db() as c:
                c.execute('UPDATE users SET pw=? WHERE id=?', (hash_pw(b['new']), u['id']))
            return self.send(200, {'ok': True})

        m = R(r'/api/invite/([\w-]{10,40})')
        if m:
            with db() as c:
                iu = c.execute('SELECT * FROM users WHERE invite=? AND active=1', (m.group(1),)).fetchone()
            if not iu:
                return self.err(404, 'This invite link is not valid any more. Ask Rashad for a new one.')
            if method == 'GET':
                return self.send(200, {'name': iu['name'], 'username': iu['username']})
            if len(b.get('password') or '') < 6:
                return self.err(400, 'Password must be at least 6 characters')
            with db() as c:
                c.execute('UPDATE users SET pw=?, invite=NULL WHERE id=?', (hash_pw(b['password']), iu['id']))
            log(iu['id'], 'set own password from invite')
            return self.send(200, {'ok': True, 'username': iu['username']})

        # ---- ideas box (everyone on the team)
        if p == '/api/ideas' or p.startswith('/api/ideas/'):
            u = self.need()
            if not u:
                return
            lead = u['role'] in ('admin', 'head')
            if p == '/api/ideas' and method == 'GET':
                with db() as c:
                    rows = [dict(r) for r in c.execute('''SELECT i.*, us.name AS author,
                        (SELECT COUNT(*) FROM idea_votes v WHERE v.idea_id=i.id) AS votes,
                        (SELECT COUNT(*) FROM idea_votes v WHERE v.idea_id=i.id AND v.user_id=?) AS mine
                        FROM ideas i LEFT JOIN users us ON us.id=i.user_id ORDER BY i.id DESC''', (u['id'],))]
                for r in rows:
                    r['own'] = r['user_id'] == u['id']
                return self.send(200, {'ideas': rows, 'lead': lead})
            if p == '/api/ideas' and method == 'POST':
                text = (b.get('text') or '').strip()[:3000]
                link = (b.get('link') or '').strip()[:500]
                kind = b.get('kind') if b.get('kind') in ('Post', 'Grid', 'Carousel', 'Reel', 'Story', 'Event idea', 'Other') else 'Other'
                if not text:
                    return self.err(400, 'Write your idea first')
                if link and not re.match(r'^https?://', link):
                    return self.err(400, 'The link must start with https://')
                with db() as c:
                    c.execute('INSERT INTO ideas(at,user_id,kind,text,link) VALUES(?,?,?,?,?)', (now_iso(), u['id'], kind, text, link))
                log(u['id'], 'added an idea')
                return self.send(200, {'ok': True})
            m = re.match(r'^/api/ideas/(\d+)/(vote|status|delete)$', p)
            if not m or method != 'POST':
                return self.err(404, 'Not found')
            iid, act = int(m.group(1)), m.group(2)
            with db() as c:
                idea = c.execute('SELECT * FROM ideas WHERE id=?', (iid,)).fetchone()
                if not idea:
                    return self.err(404, 'Not found')
                if act == 'vote':
                    if c.execute('SELECT 1 FROM idea_votes WHERE idea_id=? AND user_id=?', (iid, u['id'])).fetchone():
                        c.execute('DELETE FROM idea_votes WHERE idea_id=? AND user_id=?', (iid, u['id']))
                    else:
                        c.execute('INSERT INTO idea_votes VALUES(?,?)', (iid, u['id']))
                    return self.send(200, {'ok': True})
                if act == 'status':
                    if not lead:
                        return self.err(403, 'Not allowed')
                    st = b.get('status') if b.get('status') in ('', 'Chosen', 'Later', 'Not now') else ''
                    c.execute('UPDATE ideas SET status=?, reply=? WHERE id=?', (st, (b.get('reply') or '').strip()[:1000], iid))
            if act == 'status':
                log(u['id'], 'marked an idea: ' + (st or 'open'))
                return self.send(200, {'ok': True})
                if act == 'delete':
                    if not (lead or idea['user_id'] == u['id']):
                        return self.err(403, 'Not allowed')
                    c.execute('DELETE FROM ideas WHERE id=?', (iid,))
                    c.execute('DELETE FROM idea_votes WHERE idea_id=?', (iid,))
                    return self.send(200, {'ok': True})

        # ---- tasks
        if p == '/api/tasks':
            u = self.need()
            if not u:
                return
            with db() as c:
                tasks = [dict(r) for r in c.execute('SELECT * FROM tasks ORDER BY week, due, row')]
                pub = {r['n']: r['published'] for r in c.execute('SELECT * FROM weeks')}
                subs = [dict(r) for r in c.execute('SELECT s.*, u.name AS by_name FROM subs s LEFT JOIN users u ON u.id=s.user_id ORDER BY s.id')]
            if not self.preview_by:
                with db() as c:
                    c.execute('UPDATE users SET last_tasks=? WHERE id=?', (time.time(), u['id']))
            if u['role'] != 'admin':
                tasks = [t for t in tasks if pub.get(t['week'])]
            if u['role'] == 'member':
                tasks = [t for t in tasks if is_mine(t, u)]
            keys = {t['key'] for t in tasks}
            subs = [s for s in subs if s['task_key'] in keys and (u['role'] != 'member' or s['user_id'] == u['id'])]
            for t in tasks:
                t['published'] = bool(pub.get(t['week']))
                t['subs'] = [s for s in subs if s['task_key'] == t['key']]
            return self.send(200, {'tasks': tasks, 'last_sync': setting('last_sync')})

        m = R(r'/api/tasks/([\w-]+)/(status|submit|review)')
        if m and method == 'POST':
            u = self.need('admin', 'head', 'member')
            if not u:
                return
            key, act = m.groups()
            with db() as c:
                t = c.execute('SELECT * FROM tasks WHERE key=?', (key,)).fetchone()
            if not t:
                return self.err(404, 'Task not found')
            t = dict(t)
            if u['role'] == 'member' and not is_mine(t, u):
                return self.err(403, 'Not your task')
            if act == 'status':
                st = b.get('status')
                allowed = STATUSES if u['role'] in ('admin', 'head') else ['Not Started', 'In Progress']
                if st not in allowed:
                    return self.err(400, 'Status not allowed')
                new_status = st
            elif act == 'submit':
                link, note, cap = (b.get('link') or '').strip(), (b.get('note') or '').strip(), (b.get('caption') or '').strip()
                fname = fstore = None
                if b.get('file'):
                    data = base64.b64decode(b['file'].split(',', 1)[-1])
                    if len(data) > MAX_UPLOAD:
                        return self.err(400, 'File is bigger than 25 MB. Use a Drive link instead.')
                    ext = (os.path.splitext(b.get('file_name') or '')[1].lower().lstrip('.') or 'bin')[:5]
                    if not re.match(r'^[a-z0-9]+$', ext):
                        ext = 'bin'
                    fstore = secrets.token_hex(12) + '.' + ext
                    with open(os.path.join(FILES, fstore), 'wb') as fh:
                        fh.write(data)
                    fname = (b.get('file_name') or fstore)[:120]
                if link and not re.match(r'^https?://', link):
                    return self.err(400, 'The link must start with https://')
                if not (link or fstore or note):
                    return self.err(400, 'Add a file, a link or a note')
                with db() as c:
                    c.execute('INSERT INTO subs(task_key,user_id,link,file,file_name,note,caption,created) VALUES(?,?,?,?,?,?,?,?)',
                              (key, u['id'], link, fstore, fname, note, cap, now_iso()))
                new_status = 'Submitted'
            else:  # review
                if u['role'] not in ('admin', 'head'):
                    return self.err(403, 'Only Suhad or Rashad can review')
                verdict = b.get('verdict')
                if verdict not in ('approve', 'changes'):
                    return self.err(400, 'Bad verdict')
                with db() as c:
                    last = c.execute('SELECT id FROM subs WHERE task_key=? ORDER BY id DESC LIMIT 1', (key,)).fetchone()
                    if last:
                        c.execute('UPDATE subs SET review=?, review_by=?, review_note=?, reviewed=? WHERE id=?',
                                  (verdict, u['id'], (b.get('note') or '').strip(), now_iso(), last['id']))
                new_status = 'Done' if verdict == 'approve' else 'Changes requested'
            with db() as c:
                c.execute('UPDATE tasks SET status=?, progress=? WHERE key=?', (new_status, PROGRESS[new_status], key))
            log(u['id'], '%s → %s: %s' % (t['task'], new_status, act))
            ok = push_status(t, new_status)
            return self.send(200, {'ok': True, 'status': new_status, 'sheet': ok})

        # ---- admin
        if p.startswith('/api/admin/'):
            # Head of media may only see Team status; everything else is admin only.
            u = self.need('admin', 'head') if p == '/api/admin/team' else self.need('admin')
            if not u:
                return
            if p == '/api/admin/users':
                if method == 'GET':
                    with db() as c:
                        return self.send(200, {'users': [user_public(r, True) for r in c.execute('SELECT * FROM users ORDER BY id')],
                                               'public': public_url()})
                uid = b.get('id')
                fields = {k: (b.get(k) or '').strip() for k in ('username', 'name', 'sheet_name', 'role', 'job')}
                fields['username'] = fields['username'].lower()
                if fields['role'] not in ROLES or not re.match(r'^[a-z0-9_.-]{3,30}$', fields['username']) or not fields['name']:
                    return self.err(400, 'Username (3–30 letters/numbers), name and role are needed')
                with db() as c:
                    if uid:
                        if int(uid) == u['id'] and fields['role'] != 'admin':
                            return self.err(400, "You can't remove your own admin role")
                        c.execute('UPDATE users SET username=?,name=?,sheet_name=?,role=?,job=?,active=? WHERE id=?',
                                  (*fields.values(), 1 if b.get('active', True) else 0, uid))
                        if b.get('password'):
                            c.execute('UPDATE users SET pw=? WHERE id=?', (hash_pw(b['password']), uid))
                            c.execute('DELETE FROM sessions WHERE user_id=?', (uid,))
                        if not b.get('active', True):
                            c.execute('DELETE FROM sessions WHERE user_id=?', (uid,))
                    else:
                        if c.execute('SELECT 1 FROM users WHERE username=?', (fields['username'],)).fetchone():
                            return self.err(400, 'This username is taken')
                if not uid:
                    add_user(fields['username'], fields['name'], fields['sheet_name'], fields['role'], fields['job'])
                    if b.get('password'):
                        with db() as c:
                            c.execute('UPDATE users SET pw=?, invite=NULL WHERE username=?', (hash_pw(b['password']), fields['username']))
                log(u['id'], 'user saved: %s' % fields['username'])
                return self.send(200, {'ok': True})
            if p == '/api/admin/sync' and method == 'POST':
                try:
                    n = sync_from_sheet()
                except Exception as e:
                    return self.err(502, str(e))
                log(u['id'], 'synced %d tasks' % n)
                return self.send(200, {'ok': True, 'count': n, 'last_sync': setting('last_sync')})
            if p == '/api/admin/weeks' and method == 'POST':
                with db() as c:
                    c.execute('INSERT INTO weeks(n,published) VALUES(?,?) ON CONFLICT(n) DO UPDATE SET published=excluded.published',
                              (int(b['n']), 1 if b.get('published') else 0))
                log(u['id'], 'week %s %s' % (b['n'], 'published' if b.get('published') else 'hidden'))
                return self.send(200, {'ok': True})
            if p == '/api/admin/settings':
                keys = ('bridge_url', 'bridge_token', 'maintenance', 'ntfy', 'board_url')
                if method == 'GET':
                    return self.send(200, {k: (setting(k) if k != 'bridge_token' else ('set' if setting(k) else '')) for k in keys}
                                     | {'last_sync': setting('last_sync')})
                for k in keys:
                    if k in b and not (k == 'bridge_token' and b[k] in ('', 'set')):
                        set_setting(k, str(b[k]).strip())
                log(u['id'], 'settings changed')
                return self.send(200, {'ok': True})
            if p == '/api/admin/invite' and method == 'POST':
                tok = secrets.token_urlsafe(18)
                with db() as c:
                    c.execute('UPDATE users SET invite=?, pw=? WHERE id=?', (tok, '', int(b['id'])))
                    c.execute('DELETE FROM sessions WHERE user_id=?', (int(b['id']),))
                log(u['id'], 'new invite link for user %s' % b['id'])
                return self.send(200, {'ok': True, 'invite': '/invite/' + tok})
            if p == '/api/admin/token' and method == 'POST':
                # New bridge token, shown once so Rashad can paste it into the Apps Script properties.
                tok = secrets.token_urlsafe(24)
                set_setting('bridge_token', tok)
                log(u['id'], 'new bridge token')
                return self.send(200, {'ok': True, 'token': tok})
            if p == '/api/admin/team':
                now = time.time()
                with db() as c:
                    users = [dict(r) for r in c.execute("SELECT * FROM users WHERE active=1 AND role!='admin' ORDER BY id")]
                    tasks = [dict(r) for r in c.execute('SELECT * FROM tasks ORDER BY week, due, row')]
                    pub = {r['n']: r['published'] for r in c.execute('SELECT * FROM weeks')}
                    subs = [dict(r) for r in c.execute('SELECT task_key, user_id, created, review FROM subs ORDER BY id')]
                    last = {r['user_id']: (r['at'], r['what']) for r in c.execute(
                        'SELECT user_id, at, what FROM log WHERE id IN (SELECT MAX(id) FROM log GROUP BY user_id)')}
                tasks = [t for t in tasks if pub.get(t['week'])]
                out = []
                for x in users:
                    mine = [t for t in tasks if is_mine(t, x)]
                    tl = []
                    for t in mine:
                        ss = [q for q in subs if q['task_key'] == t['key'] and q['user_id'] == x['id']]
                        tl.append({'task': t['task'], 'week': t['week'], 'due': t['due'] or t['timing'],
                                   'status': t['status'] or 'Not Started',
                                   'submitted': ss[-1]['created'] if ss else ''})
                    seen = x['last_seen'] or 0
                    out.append({'id': x['id'], 'name': x['name'], 'role': x['role'],
                                'joined': not x['invite'] and bool(x['pw']),
                                'online': now - seen < 150, 'seen_ago': int(now - seen) if seen else None,
                                'last_login': x['last_login'] or '',
                                'tasks_ago': int(now - x['last_tasks']) if x['last_tasks'] else None,
                                'last_action': last.get(x['id'], ('', ''))[1], 'last_action_at': last.get(x['id'], ('', ''))[0],
                                'tasks': tl})
                return self.send(200, {'team': out})
            if p == '/api/admin/notes':
                # Private notes about team members (work, skills, communication, behaviour). Admins only.
                if method == 'POST':
                    if b.get('delete'):
                        with db() as c:
                            c.execute('DELETE FROM notes WHERE id=?', (int(b['delete']),))
                        return self.send(200, {'ok': True})
                    text = (b.get('text') or '').strip()[:2000]
                    cat = b.get('cat') if b.get('cat') in ('Work', 'Skills', 'Communication', 'Behaviour', 'Other') else 'Other'
                    if not text or not str(b.get('about') or '').isdigit():
                        return self.err(400, 'Write the note and choose a person')
                    with db() as c:
                        c.execute('INSERT INTO notes(at,about,author,cat,text) VALUES(?,?,?,?,?)', (now_iso(), int(b['about']), u['id'], cat, text))
                    return self.send(200, {'ok': True})
                with db() as c:
                    rows = [dict(r) for r in c.execute('SELECT n.id,n.at,n.about,n.cat,n.text,a.name AS author FROM notes n LEFT JOIN users a ON a.id=n.author ORDER BY n.id DESC')]
                    people = [dict(r) for r in c.execute("SELECT id,name,role FROM users WHERE role!='admin' ORDER BY id")]
                return self.send(200, {'notes': rows, 'people': people})
            if p == '/api/admin/log':
                with db() as c:
                    rows = [dict(r) for r in c.execute('SELECT l.at,l.what,u.name FROM log l LEFT JOIN users u ON u.id=l.user_id ORDER BY l.id DESC LIMIT 300')]
                return self.send(200, {'log': rows})
        return self.err(404, 'Not found')


def public_url():
    """Outside link: a fixed one from settings, else the current Cloudflare quick-tunnel name."""
    fixed = setting('public_url')
    if fixed:
        return fixed.rstrip('/')
    try:
        with urllib.request.urlopen('http://127.0.0.1:20241/quicktunnel', timeout=2) as r:
            host = json.load(r).get('hostname')
        return 'https://' + host if host else ''
    except Exception:
        return ''


def periodic_sync():
    while True:
        time.sleep(600)
        try:
            if setting('bridge_url'):
                sync_from_sheet()
        except Exception:
            pass


def no_users():
    """True while there is no admin who has set a password (first setup still open)."""
    with db() as c:
        return c.execute("SELECT COUNT(*) n FROM users WHERE role='admin' AND pw<>''").fetchone()['n'] == 0


if __name__ == '__main__':
    import sys
    init_db()
    if len(sys.argv) > 1 and sys.argv[1] == 'adduser':
        # python3 app.py adduser USERNAME "Full Name" ROLE ["Name in sheet"] ["Job"]
        a = sys.argv[2:] + ['', '']
        try:
            add_user(a[0], a[1], a[3] or a[1], a[2], a[4])
            print('added', a[0], '(invite link is in Admin › Users)')
        except sqlite3.IntegrityError:
            print('exists', a[0])
        sys.exit(0)
    threading.Thread(target=periodic_sync, daemon=True).start()
    print('FTB media on :%d' % PORT, flush=True)
    ThreadingHTTPServer(('0.0.0.0', PORT), H).serve_forever()
