"""Exact R128 DEX28 smali delta: local display rows and non-network demo guards."""
from __future__ import annotations
import hashlib
import re

FRONTEND='Lorg/emulationstation/frontend/station/StationFrontend;'
HELPER='Lorg/emulationstation/frontend/station/StationLocalSonyDemos;'
CHANGED_METHODS=('publishCurrent','start','remove','cover')

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def one(text:str,old:str,new:str)->str:
    if text.count(old)!=1:raise ValueError('Exact frontend anchor missing or ambiguous')
    return text.replace(old,new,1)
def method(text:str,signature:str)->str:
    found=re.findall(r'^\.method '+re.escape(signature)+r'\n.*?^\.end method$',text,re.M|re.S)
    if len(found)!=1:raise ValueError('Method signature not unique: '+signature)
    return found[0]
def patch(original:bytes)->bytes:
    text=original.decode('utf-8')
    # BaksmaliWriter follows the Windows line separator. Match canonical LF
    # internally and restore the donor style without changing other methods.
    crlf='\r\n' in text
    if crlf and '\n' in text.replace('\r\n',''):raise ValueError('Mixed donor line endings')
    text=text.replace('\r\n','\n')
    # No aliases/register growth. Here v0=context, v3=rows, v5 overwritten next.
    sig='private static publishCurrent(Lorg/emulationstation/frontend/station/StationAndroid;)V'
    old=method(text,sig)
    anchor='    iget-object v0, v4, Lorg/emulationstation/frontend/station/StationAndroid;->context:Landroid/content/Context;\n\n    iget-object v5, v14, Lorg/emulationstation/frontend/station/StationCoordinator$Library;->catalog:Lorg/emulationstation/frontend/station/StationCatalog;'
    addition='    iget-object v0, v4, Lorg/emulationstation/frontend/station/StationAndroid;->context:Landroid/content/Context;\n\n    sget-object v5, '+FRONTEND+'->requestedStorageRoot:Ljava/lang/String;\n\n    invoke-static {v0, v3, v5}, '+HELPER+'->append(Landroid/content/Context;Ljava/util/ArrayList;Ljava/lang/String;)V\n\n    iget-object v5, v14, Lorg/emulationstation/frontend/station/StationCoordinator$Library;->catalog:Lorg/emulationstation/frontend/station/StationCatalog;'
    text=one(text,old,one(old,anchor,addition))
    for name in ('start','remove'):
        sig='public static '+name+'(Ljava/lang/String;)Z';old=method(text,sig)
        guard='    invoke-static {p0}, '+HELPER+'->rejectAction(Ljava/lang/String;)Z\n\n    move-result v0\n\n    if-eqz v0, :station_demo_continue\n\n    const/4 v0, 0x0\n\n    return v0\n\n    :station_demo_continue\n'
        new=one(old,'    .locals 1\n','    .locals 1\n\n'+guard)
        text=one(text,old,new)
    sig='public static cover(Ljava/lang/String;)V';old=method(text,sig)
    guard='    invoke-static {p0}, '+HELPER+'->isPublishedDemo(Ljava/lang/String;)Z\n\n    move-result v0\n\n    if-eqz v0, :station_demo_continue\n\n    const/4 v0, 0x0\n\n    new-array v0, v0, [B\n\n    const/4 v1, 0x1\n\n    const-wide/16 v2, 0x0\n\n    invoke-static {p0, v0, v1, v2, v3}, '+FRONTEND+'->publishCoverResult(Ljava/lang/String;[BIJ)V\n\n    return-void\n\n    :station_demo_continue\n'
    text=one(text,old,one(old,'    .locals 1\n','    .locals 4\n\n'+guard))
    return (text.replace('\n','\r\n') if crlf else text).encode('utf-8')

def verify(original:bytes,patched:bytes)->dict:
    expected=patch(original)
    if expected!=patched:raise ValueError('Frontend contains an unapproved change')
    # Every unchanged method is byte-for-byte identical at the smali level.
    a=re.findall(r'^\.method .*?^\.end method$',original.decode().replace('\r\n','\n'),re.M|re.S)
    b=re.findall(r'^\.method .*?^\.end method$',patched.decode().replace('\r\n','\n'),re.M|re.S)
    if len(a)!=len(b):raise ValueError('Frontend method set changed')
    changed=[]
    for left,right in zip(a,b):
        if left!=right:changed.append(left.splitlines()[0])
    if len(changed)!=4:raise ValueError('Expected exactly four frontend methods')
    return {'originalSha256':sha(original),'patchedSha256':sha(patched),'changedMethods':changed,
            'allOtherFrontendMethodsSmaliIdentical':True,'signedCatalogParserChanged':False,
            'catalogueWarmupAndCacheLogicChanged':False,'downloadImplementationChanged':False}

def canonical(text:str)->str:
    # Labels are scoped PER METHOD, and baksmali reuses cond_0 etc. in each one.
    # The only debug ordering normalization is an adjacent label/.line pair:
    # both have zero encoded width and therefore describe the same address.
    # Preserve the line number and its position relative to every instruction.
    def canonical_method(match):
        body=match.group()
        labels=re.findall(r'^\s*(:[A-Za-z0-9_]+)\s*$',body,re.M)
        if len(labels)!=len(set(labels)):raise ValueError('Duplicate label within one method')
        mapping={label:':canonical_'+str(i) for i,label in enumerate(labels)}
        body=re.sub(r':[A-Za-z0-9_]+',lambda m:mapping.get(m.group(),m.group()),body)
        lines=[line.strip() for line in body.splitlines() if line.strip()]
        for index in range(1,len(lines)):
            if not re.fullmatch(r'\.line [0-9]+',lines[index]):continue
            current=index
            while current>0 and re.fullmatch(r':canonical_[0-9]+',lines[current-1]):
                lines[current-1],lines[current]=lines[current],lines[current-1];current-=1
        return '\n'.join(lines)
    text=text.replace('\r\n','\n')
    text=re.sub(r'^\.method .*?^\.end method$',canonical_method,text,flags=re.M|re.S)
    return '\n'.join(line.strip() for line in text.splitlines() if line.strip())

def verify_actual(original:bytes,assembled:bytes)->dict:
    expected=patch(original).decode('utf-8')
    if canonical(expected)!=canonical(assembled.decode('utf-8')):
        raise ValueError('Actual DEX frontend differs from the exact approved patch')
    result=verify(original,patch(original));result['actualAssembledFrontendVerified']=True
    result['actualSmaliSha256']=sha(assembled)
    return result
