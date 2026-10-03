"""Technical texture optimization only: preserve generated art and alpha."""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parent
GENERATED=Path(r'C:\Users\Admin\.codex\generated_images\01a0e819-6ced-7b82-a2bb-94e74409891a')
INPUTS={'snes':'exec-ca81b7c9-14d3-468e-b1c7-31651497d7da.png','megadrive':'exec-376a276c-4acc-4333-bd3e-1a5190509f47.png'}
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    out=ROOT/'assets/turbo-console';out.mkdir(parents=True,exist_ok=True)
    provenance=[];header=['// Generated illustration texture data. No runtime network or image decode.',
        'struct StationConsoleAsset {const char*key;unsigned width,height;const unsigned char*rgba;};']
    configs=[]
    for key,name in INPUTS.items():
        path=GENERATED/name;image=Image.open(path).convert('RGBA');originalSize=image.size
        image.thumbnail((512,512),Image.Resampling.LANCZOS)
        assert image.getextrema()[3][0]<255,'Transparent background required'
        image.save(out/(key+'.png'),optimize=True)
        raw=image.tobytes();header.append('static const unsigned char stationConsole_'+key+'[]={')
        header.extend(','.join(str(v) for v in raw[i:i+128])+',' for i in range(0,len(raw),128));header.append('};')
        configs.append('{"'+key+'",'+str(image.width)+','+str(image.height)+',stationConsole_'+key+'}')
        provenance.append({'key':key,'source':str(path),'sourceSha256':sha(path.read_bytes()),'sourceSize':originalSize,
            'origin':'Generated with built-in image generation for this requested console illustration; not an archival photograph',
            'asset':'turbo-console/'+key+'.png','assetSha256':sha((out/(key+'.png')).read_bytes()),'textureSize':image.size,
            'rgbaBytes':len(raw),'rgbaSha256':sha(raw),'transform':'RGBA conversion and maximum512px thumbnail; original aspect and alpha retained'})
    header.append('static const StationConsoleAsset stationConsoleAssets[]={'+','.join(configs)+'};')
    (ROOT/'native/console_assets.h').write_text('\n'.join(header)+'\n',encoding='utf-8')
    (ROOT/'evidence/console-assets-provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{'key':r['key'],'size':r['textureSize'],'bytes':r['rgbaBytes']} for r in provenance]))
if __name__=='__main__':main()
