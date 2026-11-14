"""Load the planned media tasks (keys p-NN) into the site DB. Weeks stay hidden until Rashad publishes them.
Re-running updates text but keeps status/progress."""
import json, sqlite3, sys, os
db = sqlite3.connect(sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser('~/ftb-media-data/media.db'))
tasks = json.load(open(sys.argv[1], encoding='utf-8'))
cols = list(tasks[0])
upd = [c for c in cols if c not in ('key', 'status', 'progress', 'notes')]
with db:
    for t in tasks:
        db.execute('INSERT INTO tasks(%s) VALUES(%s) ON CONFLICT(key) DO UPDATE SET %s' % (
            ','.join(cols), ','.join('?' * len(cols)), ','.join('%s=excluded.%s' % (c, c) for c in upd)), tuple(t[c] for c in cols))
        db.execute('INSERT OR IGNORE INTO weeks(n,published) VALUES(?,0)', (t['week'],))
print('loaded', len(tasks), 'planned tasks')
print('weeks', db.execute('SELECT * FROM weeks ORDER BY n').fetchall())
print('per week', db.execute("SELECT week,count(*) FROM tasks GROUP BY week").fetchall())
