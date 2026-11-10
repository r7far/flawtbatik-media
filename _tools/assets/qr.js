// Minimal QR code generator (byte mode, error-correction level L, versions 1-5). No dependencies.
const SPEC = { 1: [19, 7], 2: [34, 10], 3: [55, 15], 4: [80, 20], 5: [108, 26] }; // version: [data codewords, EC codewords]
const EXP = [], LOG = [];
for (let i = 0, x = 1; i < 255; i++) { EXP[i] = x; LOG[x] = i; x <<= 1; if (x & 256) x ^= 0x11d; }
const mul = (a, b) => a && b ? EXP[(LOG[a] + LOG[b]) % 255] : 0;
function ecc(data, n) {
  let g = [1];
  for (let i = 0; i < n; i++) { const r = new Array(g.length + 1).fill(0); g.forEach((c, j) => { r[j] ^= c; r[j + 1] ^= mul(c, EXP[i]); }); g = r; }
  const rem = new Array(n).fill(0);
  for (const d of data) { const f = d ^ rem.shift(); rem.push(0); for (let j = 0; j < n; j++) rem[j] ^= mul(g[j + 1], f); }
  return rem;
}
const MASKS = [(r, c) => (r + c) % 2, r => r % 2, (r, c) => c % 3, (r, c) => (r + c) % 3, (r, c) => ((r >> 1) + Math.floor(c / 3)) % 2,
  (r, c) => r * c % 2 + r * c % 3, (r, c) => (r * c % 2 + r * c % 3) % 2, (r, c) => ((r + c) % 2 + r * c % 3) % 2];
function matrix(text) {
  const bytes = [...new TextEncoder().encode(String(text))];
  const v = [1, 2, 3, 4, 5].find(v => bytes.length <= SPEC[v][0] - 2);
  if (!v) throw new Error('too long');
  const [nd, ne] = SPEC[v], n = 17 + 4 * v, bits = [];
  const put = (val, len) => { for (let i = len - 1; i >= 0; i--) bits.push(val >> i & 1); };
  put(4, 4); put(bytes.length, 8); bytes.forEach(b => put(b, 8)); put(0, Math.min(4, nd * 8 - bits.length));
  while (bits.length % 8) bits.push(0);
  const cw = []; for (let i = 0; i < bits.length; i += 8) cw.push(parseInt(bits.slice(i, i + 8).join(''), 2));
  for (let i = 0; cw.length < nd; i++) cw.push(i % 2 ? 17 : 236);
  const all = cw.concat(ecc(cw, ne)), stream = []; all.forEach(b => { for (let i = 7; i >= 0; i--) stream.push(b >> i & 1); });
  const M = Array.from({ length: n }, () => new Array(n).fill(0)), F = Array.from({ length: n }, () => new Array(n).fill(false));
  const set = (r, c, val) => { if (r >= 0 && c >= 0 && r < n && c < n) { M[r][c] = val ? 1 : 0; F[r][c] = true; } };
  for (const [R, C] of [[0, 0], [0, n - 7], [n - 7, 0]]) for (let r = -1; r <= 7; r++) for (let c = -1; c <= 7; c++)
    set(R + r, C + c, r >= 0 && r <= 6 && c >= 0 && c <= 6 && (r === 0 || r === 6 || c === 0 || c === 6 || (r >= 2 && r <= 4 && c >= 2 && c <= 4)));
  if (v > 1) { const a = n - 7; for (let r = -2; r <= 2; r++) for (let c = -2; c <= 2; c++) set(a + r, a + c, Math.max(Math.abs(r), Math.abs(c)) !== 1); }
  for (let i = 8; i < n - 8; i++) { set(6, i, i % 2 === 0); set(i, 6, i % 2 === 0); }
  set(n - 8, 8, 1);
  for (let i = 0; i < 9; i++) { if (!F[8][i]) set(8, i, 0); if (!F[i][8]) set(i, 8, 0); }
  for (let i = 0; i < 8; i++) { set(8, n - 1 - i, 0); if (i < 7) set(n - 1 - i, 8, 0); }
  let k = 0, up = true;
  for (let c = n - 1; c > 0; c -= 2) {
    if (c === 6) c--;
    for (let i = 0; i < n; i++) { const r = up ? n - 1 - i : i; for (const cc of [c, c - 1]) if (!F[r][cc]) M[r][cc] = stream[k++] || 0; }
    up = !up;
  }
  let best = null;
  for (let m = 0; m < 8; m++) {
    const G = M.map((row, r) => row.map((x, c) => F[r][c] ? x : x ^ (MASKS[m](r, c) === 0 ? 1 : 0)));
    let f = (1 << 3 | m) << 10, rem = f; // level L = 01
    for (let i = 14; i >= 10; i--) if (rem >> i & 1) rem ^= 0x537 << (i - 10);
    f = (f | rem) ^ 0x5412;
    for (let i = 0; i < 15; i++) {
      const b = f >> i & 1;
      if (i < 6) G[i][8] = b; else if (i < 8) G[i + 1][8] = b; else G[8][14 - i + (i === 8 ? 1 : 0)] = b;
      if (i < 8) G[8][n - 1 - i] = b; else G[n - 15 + i][8] = b;
    }
    let pen = 0, dark = 0;
    for (let r = 0; r < n; r++) for (const line of [G[r], G.map(row => row[r])]) { let run = 1; for (let c = 1; c <= n; c++) { if (c < n && line[c] === line[c - 1]) run++; else { if (run >= 5) pen += run - 2; run = 1; } } }
    for (let r = 0; r < n - 1; r++) for (let c = 0; c < n - 1; c++) if (G[r][c] === G[r][c + 1] && G[r][c] === G[r + 1][c] && G[r][c] === G[r + 1][c + 1]) pen += 3;
    G.forEach(row => row.forEach(x => dark += x)); pen += Math.floor(Math.abs(dark * 100 / (n * n) - 50) / 5) * 10;
    if (!best || pen < best.pen) best = { pen, G };
  }
  return best.G;
}
function svg(text) {
  const G = matrix(text), n = G.length, q = 4; let d = '';
  G.forEach((row, r) => row.forEach((x, c) => { if (x) d += 'M' + (c + q) + ' ' + (r + q) + 'h1v1h-1z'; }));
  return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + (n + 2 * q) + ' ' + (n + 2 * q) + '" shape-rendering="crispEdges"><rect width="100%" height="100%" fill="#fff"/><path d="' + d + '" fill="#000"/></svg>';
}
window.QR = { matrix, svg };
