"""Change only the application's factory value in a verified binary XML manifest.

All existing strings and other chunks are retained. No resource table rebuild.
"""
import struct

OLD='androidx.core.app.CoreComponentFactory'
NEW='org.emulationstation.frontend.station.StationComponentFactory'
ATTRIBUTE=0x0101057a

def u32(data,offset):return struct.unpack_from('<I',data,offset)[0]
def put32(data,offset,value):struct.pack_into('<I',data,offset,value)

def length(data,offset,utf8):
    if utf8:
        first=data[offset]
        return (((first&127)<<8)|data[offset+1],offset+2) if first&128 else (first,offset+1)
    first=struct.unpack_from('<H',data,offset)[0]
    return (((first&32767)<<16)|struct.unpack_from('<H',data,offset+2)[0],offset+4) if first&32768 else (first,offset+2)

def encode_length(value,utf8):
    if utf8:return bytes([value]) if value<128 else bytes([128|(value>>8),value&255])
    return struct.pack('<H',value) if value<32768 else struct.pack('<HH',32768|(value>>16),value&65535)

def chunks(data):
    assert struct.unpack_from('<HH',data)==(3,8) and u32(data,4)==len(data),'Invalid XML header'
    offset=8
    while offset<len(data):
        kind,header,size=struct.unpack_from('<HHI',data,offset)
        assert size>=header>=8 and offset+size<=len(data),'Invalid XML chunk'
        yield offset,kind,header,size
        offset+=size
    assert offset==len(data)

def string_pool(data,offset):
    count,styles,flags,start,style_start=struct.unpack_from('<IIIII',data,offset+8)
    header=struct.unpack_from('<H',data,offset+2)[0]
    result=[]
    for i in range(count):
        pos=offset+start+u32(data,offset+header+i*4)
        n,pos=length(data,pos,bool(flags&256))
        if flags&256:n,pos=length(data,pos,True)
        result.append(data[pos:pos+n*(1 if flags&256 else 2)].decode('utf-8' if flags&256 else 'utf-16-le'))
    return result

def patch_manifest(data):
    original_chunks=list(chunks(data))
    pool=[c for c in original_chunks if c[1]==1]
    resources=[c for c in original_chunks if c[1]==0x180]
    assert len(pool)==len(resources)==1,'Expected one string pool and resource map'
    po,_,ph,ps=pool[0];strings=string_pool(data,po)
    ro,_,rh,rs=resources[0];resource_ids=list(struct.unpack_from('<'+'I'*((rs-rh)//4),data,ro+rh))
    targets=[]
    for offset,kind,header,size in original_chunks:
        if kind!=0x102:continue
        assert header==16
        element=u32(data,offset+20)
        if strings[element]!='application':continue
        attr_start,attr_size,attr_count=struct.unpack_from('<HHH',data,offset+24)
        assert attr_size==20
        for i in range(attr_count):
            attr=offset+16+attr_start+i*attr_size
            name=u32(data,attr+4)
            if name<len(resource_ids) and resource_ids[name]==ATTRIBUTE:
                assert data[attr+15]==3 and strings[u32(data,attr+16)]==OLD,'Unexpected factory'
                raw=u32(data,attr+8)
                assert raw==0xffffffff or strings[raw]==OLD,'Unexpected raw factory'
                targets.append(attr)
    assert len(targets)==1,'Expected exact application factory attribute'
    count,style_count,flags,start,style_start=struct.unpack_from('<IIIII',data,po+8)
    # Existing offsets retain their logical string-data position. The new offset
    # is appended to the table; styles, if any, retain their original bytes.
    old_pool=data[po:po+ps]
    string_end=style_start if style_start else ps
    string_data=old_pool[start:string_end]
    encoded=NEW.encode('utf-8' if flags&256 else 'utf-16-le')
    encoded=encode_length(len(NEW),bool(flags&256))+(encode_length(len(encoded),True) if flags&256 else b'')+encoded+(b'\0' if flags&256 else b'\0\0')
    new_string_data=string_data+encoded
    new_string_data+=b'\0'*((-len(new_string_data))%4)
    old_offsets=old_pool[ph:ph+count*4]
    style_offsets=old_pool[ph+count*4:start]
    new_pool=bytearray(old_pool[:ph]+old_offsets+struct.pack('<I',len(string_data))+style_offsets+new_string_data+(old_pool[style_start:] if style_start else b''))
    put32(new_pool,4,len(new_pool));put32(new_pool,8,count+1);put32(new_pool,20,start+4)
    if style_start:put32(new_pool,24,start+4+len(new_string_data))
    delta=len(new_pool)-ps
    output=bytearray(data[:po]+new_pool+data[po+ps:]);put32(output,4,len(output))
    attr=targets[0]+delta
    if u32(output,attr+8)!=0xffffffff:put32(output,attr+8,count)
    put32(output,attr+16,count)
    # Proof: reversing this one attribute and swapping the original pool restores
    # the exact input bytes. No other attribute, component or permission changed.
    check=bytearray(output);put32(check,attr+8,u32(data,targets[0]+8));put32(check,attr+16,u32(data,targets[0]+16))
    check=check[:po]+data[po:po+ps]+check[po+len(new_pool):];put32(check,4,len(check))
    assert bytes(check)==data,'Unexpected manifest change'
    assert string_pool(output,po)[:count]==strings and string_pool(output,po)[count]==NEW
    list(chunks(output))
    return bytes(output)
