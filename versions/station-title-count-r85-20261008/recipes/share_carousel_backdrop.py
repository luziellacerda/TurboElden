"""Apply the user-approved background to platforms and collections as requested."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK=Path(r'E:\ESTUDO APK\work\station-title-count-r85-20261008')
p=WORK/'carousel-inputs/d0/native_space.h';s=p.read_text('utf8')
s=s.replace('// Game-only backdrop: solid black up to the diagonal through the B in','// Shared carousel backdrop: solid black up to the diagonal through the B in')
s=s.replace('drawGameCornerBackdrop','drawCarouselDiagonalBackdrop')
a=s.index(' if(!systemsMode){drawCarouselDiagonalBackdrop(w,h);return;}')
s=s[:a]+' drawCarouselDiagonalBackdrop(w,h);\n}\n'
p.write_text(s,'utf8')
old='f4bcd0a6879e53c2dc434dba29bda26c8a49001a4ddca6b36d10a647f359e1d4';current='43e439567bff11e652eb4a94b3f14bc1e79be61fb131a6a061bda62319dc7dc0'
for name in ['package_candidate.py','refresh_candidate.py']:
 p=ROOT/'recipes'/name;s=p.read_text();assert old in s;p.write_text(s.replace(old,current),'utf8')
for name in ['native','package']:
 p=WORK/name;dest=WORK/(name+'-before-shared-backdrop');assert p.resolve().parent==WORK.resolve() and not dest.exists();p.rename(dest)
for name in ['installation-motorola-r85','physical-check']:
 p=ROOT/'evidence'/(name+'.json');dest=p.with_name(name+'-before-shared-backdrop.json');assert not dest.exists();p.rename(dest)
print('Same approved backdrop shared by all open carousels; other UI untouched.')
