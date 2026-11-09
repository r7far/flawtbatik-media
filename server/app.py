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
        ''')


# ---------- helpers ----------
def now_iso():
    return datetime.now(RIYADH).strftime('%Y-%m-%d %H:%M')


def hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(16)
    h = hashlib.scrypt(pw.encode(), salt=bytes.fromhex(salt), n=2 ** 14, r=8, p=1, dklen=32).hex()
    return salt + '$' + h


def check_pw(pw, stored):
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


def user_public(u):
    return {k: u[k] for k in ('id', 'username', 'name', 'sheet_name', 'role', 'job', 'active')}


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
        ck = http.cookies.SimpleCookie(self.headers.get('Cookie') or '')
        tok = ck.get('ftb') and ck['ftb'].value
        if not tok:
            return None
        with db() as c:
            r = c.execute('SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=? AND u.active=1', (tok,)).fetchone()
        return r

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
            log(u['id'], 'logged in')
            secure = '; Secure' if self.headers.get('X-Forwarded-Proto') == 'https' else ''
            return self.send(200, {'ok': True, 'user': user_public(u)},
                             headers={'Set-Cookie': 'ftb=%s; Path=/; HttpOnly; SameSite=Lax; Max-Age=2592000%s' % (tok, secure)})
        if p == '/api/logout':
            ck = http.cookies.SimpleCookie(self.headers.get('Cookie') or '')
            if ck.get('ftb'):
                with db() as c:
                    c.execute('DELETE FROM sessions WHERE token=?', (ck['ftb'].value,))
            return self.send(200, {'ok': True}, headers={'Set-Cookie': 'ftb=; Path=/; Max-Age=0'})
        if p == '/api/me':
            u = self.user()
            return self.send(200, {'user': user_public(u) if u else None, 'maintenance': setting('maintenance') == '1',
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

        # ---- tasks
        if p == '/api/tasks':
            u = self.need()
            if not u:
                return
            with db() as c:
                tasks = [dict(r) for r in c.execute('SELECT * FROM tasks ORDER BY week, due, row')]
                pub = {r['n']: r['published'] for r in c.execute('SELECT * FROM weeks')}
                subs = [dict(r) for r in c.execute('SELECT s.*, u.name AS by_name FROM subs s LEFT JOIN users u ON u.id=s.user_id ORDER BY s.id')]
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
            u = self.need('admin')
            if not u:
                return
            if p == '/api/admin/users':
                if method == 'GET':
                    with db() as c:
                        return self.send(200, {'users': [user_public(r) for r in c.execute('SELECT * FROM users ORDER BY id')]})
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
                        if len(b.get('password') or '') < 6:
                            return self.err(400, 'Password must be at least 6 characters')
                        try:
                            c.execute('INSERT INTO users(username,name,sheet_name,role,job,pw,created) VALUES(?,?,?,?,?,?,?)',
                                      (*fields.values(), hash_pw(b['password']), now_iso()))
                        except sqlite3.IntegrityError:
                            return self.err(400, 'This username is taken')
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
                keys = ('bridge_url', 'bridge_token', 'maintenance', 'ntfy')
                if method == 'GET':
                    return self.send(200, {k: (setting(k) if k != 'bridge_token' else ('set' if setting(k) else '')) for k in keys}
                                     | {'last_sync': setting('last_sync')})
                for k in keys:
                    if k in b and not (k == 'bridge_token' and b[k] in ('', 'set')):
                        set_setting(k, str(b[k]).strip())
                log(u['id'], 'settings changed')
                return self.send(200, {'ok': True})
            if p == '/api/admin/log':
                with db() as c:
                    rows = [dict(r) for r in c.execute('SELECT l.at,l.what,u.name FROM log l LEFT JOIN users u ON u.id=l.user_id ORDER BY l.id DESC LIMIT 300')]
                return self.send(200, {'log': rows})
        return self.err(404, 'Not found')


def periodic_sync():
    while True:
        time.sleep(600)
        try:
            if setting('bridge_url'):
                sync_from_sheet()
        except Exception:
            pass


def no_users():
    with db() as c:
        return c.execute('SELECT COUNT(*) n FROM users').fetchone()['n'] == 0


if __name__ == '__main__':
    init_db()
    threading.Thread(target=periodic_sync, daemon=True).start()
    print('FTB media on :%d' % PORT, flush=True)
    ThreadingHTTPServer(('0.0.0.0', PORT), H).serve_forever()
