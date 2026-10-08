"""Replace the narrow diagonal feather with a broad continuous alpha ramp."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK=Path(r'E:\ESTUDO APK\work\station-title-count-r85-20261008')
p=WORK/'carousel-inputs/d0/native_space.h';s=p.read_text('utf8')
old='float line=y<=startY?right:right*(h-y)/(h-startY);\n     float diagonal=1.f-gameBackdropEase((x-line+h*.10f)/(h*.10f));'
new='''// Alpha decreases across the whole diagonal area, not a narrow band.
     float down=y<=startY?0:(y-startY)/(h-startY);
     float diagonal=1.f-gameBackdropEase(x/right+down);'''
assert s.count(old)==1;s=s.replace(old,new);p.write_text(s,'utf8')
old='f0987cc3ba846ed2b4f632d64d41ed799d4ffad29190e18915498992b2f69354';current='f4bcd0a6879e53c2dc434dba29bda26c8a49001a4ddca6b36d10a647f359e1d4'
for name in ['package_candidate.py','refresh_candidate.py']:
 p=ROOT/'recipes'/name;s=p.read_text();assert old in s;p.write_text(s.replace(old,current),'utf8')
for name in ['native','package']:
 p=WORK/name;dest=WORK/(name+'-before-soft-diagonal');assert p.resolve().parent==WORK.resolve() and not dest.exists();p.rename(dest)
for name in ['installation-motorola-r85','physical-check']:
 p=ROOT/'evidence'/(name+'.json');dest=p.with_name(name+'-before-soft-diagonal.json');assert not dest.exists();p.rename(dest)
print('Broad soft diagonal alpha applied; synopsis remains outside the fade.')
