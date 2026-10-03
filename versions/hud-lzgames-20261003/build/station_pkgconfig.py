"""Small build-only reader for bundled .pc dependencies; no system packages."""
import os, re, sys, shlex
from pathlib import Path

root = Path(os.environ['PKG_CONFIG_PATH'])
mode = next(a for a in sys.argv[1:] if a in ('--cflags', '--libs'))
seen = set()
out = []

def package(name):
    if name in seen: return
    seen.add(name)
    path = root/(name+'.pc')
    if not path.is_file(): raise RuntimeError('Missing dependency '+str(path))
    variables = {'pcfiledir':root.as_posix()}
    fields = {}
    def expand(s):
        for _ in range(30):
            new = re.sub(r'\$\{([^}]+)\}', lambda m:variables[m[1]], s)
            if new == s: return s
            s = new
        raise RuntimeError('Recursive pc variables')
    for line in path.read_text().splitlines():
        if not line or line.startswith('#'): continue
        if re.match(r'\w+\s*=', line):
            k,v = line.split('=',1); variables[k.strip()] = expand(v.strip())
        elif ':' in line:
            k,v = line.split(':',1); fields[k.strip()] = v.strip()
    val = expand(fields.get('Cflags' if mode=='--cflags' else 'Libs',''))
    # Prefix paths may have spaces; quote each -I/-L path through its next flag.
    val = re.sub(r'(-[IL])(.+?)(?=\s+-|$)', lambda m:m[1]+'"'+m[2].strip().strip('"')+'"', val)
    out.extend(shlex.split(val))
    req = fields.get('Requires','') + ' ' + fields.get('Requires.private','')
    for dep in re.findall(r'(?:^|[,\s])([A-Za-z][\w.+-]*)', req):
        package(dep)
    if mode == '--libs':
        out.extend(shlex.split(expand(fields.get('Libs.private',''))))

for arg in sys.argv[1:]:
    if arg.startswith('-'): continue
    for p in arg.split(): package(p)
print(' '.join(shlex.quote(p) for p in dict.fromkeys(out)))
