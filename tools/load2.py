"""Replace the planned (p-) tasks with a new set. Old p- tasks nobody touched (Not Started, no submissions) are removed.
Weeks stay hidden unless already published."""
import json, sqlite3, sys, os
db = sqlite3.connect(sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser('~/ftb-media-data/media.db'))
tasks = json.load(open(sys.argv[1], encoding='utf-8'))
new = {t['key'] for t in tasks}
with db:
    old = [r[0] for r in db.execute("SELECT key FROM tasks WHERE key LIKE 'p-%' AND status='Not Started' AND key NOT IN (SELECT DISTINCT task_key FROM subs WHERE task_key IS NOT NULL)")]
    gone = [k for k in old if k not in new]
    db.executemany('DELETE FROM tasks WHERE key=?', [(k,) for k in gone])
    cols = list(tasks[0]); upd = [c for c in cols if c not in ('key', 'status', 'progress', 'notes')]
    for t in tasks:
        db.execute('INSERT INTO tasks(%s) VALUES(%s) ON CONFLICT(key) DO UPDATE SET %s' % (','.join(cols), ','.join('?' * len(cols)), ','.join('%s=excluded.%s' % (c, c) for c in upd)), tuple(t[c] for c in cols))
        db.execute('INSERT OR IGNORE INTO weeks(n,published) VALUES(?,0)', (t['week'],))
print('removed', len(gone), 'loaded', len(tasks))
print('weeks', db.execute('SELECT * FROM weeks ORDER BY n').fetchall())
print('per week', db.execute("SELECT week,count(*) FROM tasks GROUP BY week").fetchall())
