#!/usr/bin/env python3
"""Add only update hooks to the actual latest API/HTTP/Android sources.

No historical source is used as a replacement. Refuse duplicate/ambiguous
anchors; record both hashes. This does not build, sign, or install an APK.
"""
import argparse
import hashlib
import json
from pathlib import Path

MARKER = '// STATION_APP_UPDATES_V1'
API = '''
    // STATION_APP_UPDATES_V1
    public JSONObject appUpdates(Session session,boolean authorize,JSONObject request,Cancellation cancel)throws Exception {
        String id=string(request,"requestId");
        if(!id.matches("[0-9a-f]{32}"))throw new IOException("UPDATE_REQUEST_ID");
        byte[] body=request.toString().getBytes(StandardCharsets.UTF_8);
        if(body.length>8192)throw new IOException("UPDATE_BODY");
        long started=clock.millis();
        JSONObject result=signed("POST",authorize?"updates/authorize":"updates/check",body,session,
            authorize?"TurboRamaStationAndroid/app-update-grant/v1":"TurboRamaStationAndroid/app-update/v1",16384,cancel);
        equal(result,"requestId",id);lifetime(result,60);notExpired(started+60000);
        return result;
    }
    public Response openAppUpdate(Session session,String grantId,long expectedSize,Cancellation cancel)throws Exception {
        valid(session);token(grantId);
        if(expectedSize<1024||expectedSize>8L*1024*1024*1024)throw new IOException("UPDATE_SIZE");
        Response response=exchange("GET",ROOT+"updates/artifacts/"+grantId,null,session,cancel);
        boolean accepted=false;
        try{success(response,cancel);
            if(!mime(response.type).equals("application/vnd.android.package-archive")||response.length!=expectedSize)
                throw new IOException("UPDATE_HEADERS");
            accepted=true;return response;
        }finally{if(!accepted)response.close();}
    }
'''

def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('Update hook requires exactly one current-source anchor: '+old[:70])
    return text.replace(old, new)

def patch(name, text):
    if MARKER in text:
        raise ValueError('Update hooks already applied')
    newline = '\r\n' if '\r\n' in text else '\n'
    if name == 'StationApi.java':
        text = replace_once(text, '    private JSONObject signed(', API.replace('\n',newline)+newline+'    private JSONObject signed(')
    elif name == 'StationHttp.java':
        anchor='if (!"GET".equals(method)) return false;'
        text=replace_once(text,anchor,
            MARKER+newline+
            '        if ("GET".equals(method) && path.startsWith("/v1/station/updates/artifacts/") && StationProtocol.activationCode(path.substring("/v1/station/updates/artifacts/".length()))) return true;'+newline+'        '+anchor)
        # Existing POST allowlists return directly. Include the two new POSTs
        # in that expression without changing routing, pins, proof or timeouts.
        text=replace_once(text,'path.equals("/v1/station/downloads/authorize")',
            '(path.equals("/v1/station/downloads/authorize") || path.equals("/v1/station/updates/check") || path.equals("/v1/station/updates/authorize"))')
    elif name == 'StationAndroid.java':
        text=replace_once(text,'        return instance;','        '+MARKER+newline+'        StationAppUpdateUi.install(instance,context);'+newline+'        return instance;')
    else:
        raise ValueError('Unexpected source')
    return text

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    proof={};outputs={}
    for name in ('StationApi.java','StationHttp.java','StationAndroid.java'):
        source=(args.source_dir/name).read_bytes()
        result=patch(name,source.decode()).encode()
        outputs[name]=result
        proof[name]={'before':hashlib.sha256(source).hexdigest(),'after':hashlib.sha256(result).hexdigest()}
    args.out.mkdir(parents=True,exist_ok=False)
    for name,result in outputs.items():(args.out/name).write_bytes(result)
    (args.out/'update-hooks.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({'patched':list(proof),'apkBuiltSignedOrInstalled':False}))

if __name__=='__main__':main()
