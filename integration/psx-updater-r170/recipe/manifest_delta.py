"""Append three private updater components to the exact R169 binary Manifest.

All original string indices, resource map and non-root XML chunks remain exact.
There is no resource recompile, SDK/factory/process rewrite or permission widening.
"""
import struct

NS = 'http://schemas.android.com/apk/res/android'
PACKAGE = 'org.turboramastation.frontend'
NO = 0xffffffff
COMPONENTS = [('activity','Activity'),('service','Service'),('receiver','Receiver')]

def need(ok, reason):
    if not ok: raise ValueError(reason)

def chunks(raw):
    need(struct.unpack_from('<HHI',raw)==(3,8,len(raw)), 'Binary XML header')
    cursor=8; result=[]
    while cursor<len(raw):
        kind,header,size=struct.unpack_from('<HHI',raw,cursor)
        need(8<=header<=size and size%4==0 and cursor+size<=len(raw), 'XML chunk bounds')
        result.append((kind,raw[cursor:cursor+size]));cursor+=size
    need(cursor==len(raw),'XML trailing data')
    return result

def length(raw,offset,utf8):
    if utf8:
        value=raw[offset];offset+=1
        if value&128:value=((value&127)<<8)|raw[offset];offset+=1
    else:
        value=struct.unpack_from('<H',raw,offset)[0];offset+=2
        if value&0x8000:value=((value&0x7fff)<<16)|struct.unpack_from('<H',raw,offset)[0];offset+=2
    return value,offset

def encoded_length(n,utf8):
    if utf8:
        need(n<0x8000,'UTF8 string length')
        return bytes([n]) if n<128 else bytes([128|(n>>8),n&255])
    need(n<0x8000,'UTF16 string length')
    return struct.pack('<H',n)

class Pool:
    def __init__(self,raw):
        self.raw=raw
        kind,header,size,count,styles,flags,start,style_start=struct.unpack_from('<HHIIIIII',raw)
        need(kind==1 and header==28 and size==len(raw) and start>=28+4*(count+styles),'String pool header')
        self.count,self.styles,self.flags,self.start,self.style_start=count,styles,flags,start,style_start
        self.utf8=bool(flags&0x100)
        self.offsets=list(struct.unpack_from('<'+'I'*count,raw,28))
        self.values=[]
        for off in self.offsets:
            offset=start+off;size,offset=length(raw,offset,self.utf8)
            if self.utf8:size,offset=length(raw,offset,True)
            payload=raw[offset:offset+(size if self.utf8 else size*2)]
            self.values.append(payload.decode('utf-8' if self.utf8 else 'utf-16le'))
        self.added=[]
    def index(self,value):
        if value in self.values:return self.values.index(value)
        if value not in self.added:self.added.append(value)
        return self.count+self.added.index(value)
    def text(self,i):
        need(i!=NO and i<len(self.values),'Original string index')
        return self.values[i]
    def build(self):
        end=self.style_start or len(self.raw)
        data=bytearray(self.raw[self.start:end]);offsets=list(self.offsets)
        for value in self.added:
            offsets.append(len(data));u16=len(value.encode('utf-16le'))//2
            if self.utf8:
                payload=value.encode('utf-8');data+=encoded_length(u16,True)+encoded_length(len(payload),True)+payload+b'\0'
            else:data+=encoded_length(u16,False)+value.encode('utf-16le')+b'\0\0'
        data+=b'\0'*((-len(data))%4)
        style_offsets=self.raw[28+4*self.count:28+4*(self.count+self.styles)]
        style_data=self.raw[self.style_start:] if self.style_start else b''
        start=self.start+4*len(self.added);style_start=start+len(data) if self.style_start else 0
        header=struct.pack('<HHIIIIII',1,28,start+len(data)+len(style_data),len(offsets),self.styles,self.flags&~1,start,style_start)
        padding=self.raw[28+4*(self.count+self.styles):self.start]
        result=header+struct.pack('<'+'I'*len(offsets),*offsets)+style_offsets+padding+data+style_data
        need(Pool(result).values==self.values+self.added,'String pool readback')
        return result

def name(chunk,pool):return pool.text(struct.unpack_from('<I',chunk,20)[0])

def attributes(chunk,pool):
    start,stride,count=struct.unpack_from('<HHH',chunk,24)
    need(stride==20 and 16+start+stride*count==len(chunk),'Attribute layout')
    result={}
    for i in range(count):
        off=16+start+stride*i
        namespace,key,raw,size,zero,kind,value=struct.unpack_from('<IIIHBBI',chunk,off)
        need(size==8 and zero==0,'Typed attribute')
        key=(None if namespace==NO else pool.text(namespace),pool.text(key))
        need(key not in result,'Duplicate attribute')
        result[key]=(off,kind,pool.text(value) if kind==3 else value,raw)
    return result

def component(pool,namespace,tag,suffix,resource_ids):
    full='org.emulationstation.frontend.station.StationAppUpdate'+suffix
    fields=[('name',3,full),('exported',18,0)]
    if tag=='service':fields.append(('foregroundServiceType',17,1))
    fields.sort(key=lambda f:resource_ids[pool.index(f[0])])
    values=[]
    for key,kind,value in fields:
        if kind==3:value=pool.index(value)
        values.append(struct.pack('<IIIHBBI',namespace,pool.index(key),value if kind==3 else NO,8,0,kind,value))
    start=struct.pack('<HHIII',0x102,16,36+20*len(values),0,NO)+struct.pack('<IIHHHHHH',NO,pool.index(tag),20,20,len(values),0,0,0)+b''.join(values)
    end=struct.pack('<HHIII',0x103,16,24,0,NO)+struct.pack('<II',NO,pool.index(tag))
    return start+end

def patch(raw,version=12,version_name='1.0.8-R170'):
    original=chunks(raw)
    pools=[v for k,v in original if k==1];maps=[v for k,v in original if k==0x180]
    need(len(pools)==len(maps)==1,'One string pool/resource map required')
    pool=Pool(pools[0]);resource_ids=struct.unpack_from('<'+'I'*((len(maps[0])-8)//4),maps[0],8)
    namespace=pool.index(NS)
    need(namespace<pool.count,'Existing Android namespace required')
    for field,expected in [('name',0x01010003),('exported',0x01010010),('foregroundServiceType',0x01010599)]:
        i=pool.index(field);need(i<len(resource_ids) and resource_ids[i]==expected,'Existing attribute resource ID differs')
    stack=[];roots=[];application_ends=[];permissions={};existing=[];sdk=[]
    for i,(kind,chunk) in enumerate(original):
        if kind==0x102:
            tag=name(chunk,pool);attrs=attributes(chunk,pool)
            if not stack:need(tag=='manifest','Root tag');roots.append(i)
            if tag=='uses-sdk':sdk.append((attrs.get((NS,'minSdkVersion')),attrs.get((NS,'targetSdkVersion'))))
            if tag=='uses-permission':
                permission=attrs.get((NS,'name'));need(permission is not None,'Permission name')
                need(permission[2] not in permissions,'Duplicate original permission')
                permissions[permission[2]]=attrs
            if len(stack)==2 and stack==['manifest','application']:
                entry=attrs.get((NS,'name'))
                if entry:existing.append(entry[2])
            stack.append(tag)
        elif kind==0x103:
            tag=name(chunk,pool);need(stack and stack[-1]==tag,'XML nesting')
            if tag=='application':application_ends.append(i)
            stack.pop()
    need(not stack and len(roots)==len(application_ends)==1 and len(sdk)==1,'Manifest structure')
    need(sdk[0][0][2]==26 and sdk[0][1][2]==34,'Preserve exact R169 SDK26/34')
    for suffix in ['REQUEST_INSTALL_PACKAGES','FOREGROUND_SERVICE','FOREGROUND_SERVICE_DATA_SYNC']:
        attrs=permissions.get('android.permission.'+suffix)
        need(attrs is not None and (NS,'maxSdkVersion') not in attrs,'Existing required permission')
    for _,suffix in COMPONENTS:need('org.emulationstation.frontend.station.StationAppUpdate'+suffix not in existing,'Updater already present')
    root=bytearray(original[roots[0]][1]);attrs=attributes(root,pool)
    need(attrs[(None,'package')][2]==PACKAGE,'Package differs')
    off,kind,old,_=attrs[(NS,'versionCode')];need(kind==16 and old==11 and version==12,'R169 to R170 version scope')
    struct.pack_into('<I',root,off+16,version)
    off,kind,old,_=attrs[(NS,'versionName')];need(kind==3 and old=='1.0.8-turboeden-unico','Original version name')
    i=pool.index(version_name);struct.pack_into('<I',root,off+8,i);struct.pack_into('<I',root,off+16,i)
    additions=b''.join(component(pool,namespace,tag,suffix,resource_ids) for tag,suffix in COMPONENTS)
    output=[]
    for i,(kind,chunk) in enumerate(original):
        if i==application_ends[0]:output.append(additions)
        output.append(pool.build() if kind==1 else bytes(root) if i==roots[0] else chunk)
    body=b''.join(output);result=struct.pack('<HHI',3,8,len(body)+8)+body
    after=chunks(result)
    # Independent chunk comparison: only root attributes, string-pool append and
    # exactly the six new start/end chunks can differ.
    index=application_ends[0]
    retained=after[:index]+after[index+6:]
    need(len(retained)==len(original),'Original XML chunk count')
    for i,(before,after_chunk) in enumerate(zip(original,retained)):
        if i!=roots[0] and before[0]!=1:need(before==after_chunk,'Unrelated XML node changed')
    need(Pool(after[0][1]).values[:pool.count]==pool.values,'Original string values')
    return result
