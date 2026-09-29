// Original procedural atmosphere. No video, image overlay or external texture.
uniform float aspect;
uniform vec2 vanishingPoint;
uniform float travelDistance;
varying vec2 uv;
float cloudHash(vec3 p){p=fract(p*.1031);p+=dot(p,p.yzx+33.33);return fract((p.x+p.y)*p.z);}
float cloudNoise(vec3 p){
 vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
 return mix(mix(mix(cloudHash(i),cloudHash(i+vec3(1,0,0)),f.x),mix(cloudHash(i+vec3(0,1,0)),cloudHash(i+vec3(1,1,0)),f.x),f.y),mix(mix(cloudHash(i+vec3(0,0,1)),cloudHash(i+vec3(1,0,1)),f.x),mix(cloudHash(i+vec3(0,1,1)),cloudHash(i+vec3(1,1,1)),f.x),f.y),f.z);
}
float cloudDensity(vec3 p,float lod){
 float broad=cloudNoise(p*vec3(.32,.24,.32)+vec3(17.1,4.7,8.2));
 float medium=mix(cloudNoise(p*1.17+vec3(8.3,21.7,3.1)),.5,lod*.65);
 float fine=mix(cloudNoise(p*2.17),.5,lod);
 float top=-.94+(broad-.48)*2.2;
 float vertical=smoothstep(-3.6,-2.5,p.y)*(1.-smoothstep(top-.65,top+.24,p.y));
 return max(broad*.64+medium*.25+fine*.11-.50,0.)*8.5*vertical;
}
void main(){
 // Camera and distant banks share the exact native star-field origin and travel clock.
 // Converting the top-left native coordinates once removes the former sideways drift.
 vec2 radial=uv-vec2(vanishingPoint.x*2.-1.,1.-vanishingPoint.y*2.);
 vec3 ro=vec3(0.,1.8,travelDistance);
 vec3 rd=normalize(vec3(radial.x*aspect,radial.y,2.9));
 float near=0.,far=0.;
 if(rd.y<-.025){near=max(0.,(-.20-ro.y)/rd.y);far=min(24.,(-3.6-ro.y)/rd.y);}
 float dt=max(0.,far-near)/64.,trans=1.;vec3 light=vec3(0.);
 float jitter=(cloudHash(vec3(floor(gl_FragCoord.xy),19.3))-.5)*.24;
 if(far>near)for(int i=0;i<64;i++){
  float distance=near+(float(i)+.5+jitter)*dt;vec3 p=ro+rd*distance;
  float lod=smoothstep(6.,20.,distance);
  float density=cloudDensity(p,lod)*(1.-smoothstep(18.,24.,distance));
  float sun=exp(-cloudDensity(p+vec3(-.35,.72,-.22),lod)*2.8);
  float alpha=1.-exp(-density*dt*1.18);
  vec3 shade=mix(vec3(.095,.13,.14),vec3(.63,.69,.67),sun);
  shade=mix(shade,vec3(.18,.24,.25),smoothstep(8.,30.,distance)*.62);
  light+=trans*alpha*shade;trans*=1.-alpha;
 }
 // Distant sheets expand radially toward the edges, with depth-dependent parallax.
 // Their transitions fade at the ends of the travel cycle; there is no diagonal scroll.
 float phaseA=fract(travelDistance*.006+.21),phaseB=fract(travelDistance*.006+.71);
 vec2 field=radial*vec2(aspect,1.);
 float mistA=cloudNoise(vec3(field*mix(7.,1.5,phaseA),31.7));
 float mistB=cloudNoise(vec3(field*mix(7.,1.5,phaseB),52.4));
 float fadeA=smoothstep(0.,.15,phaseA)*(1.-smoothstep(.83,1.,phaseA));
 float fadeB=smoothstep(0.,.15,phaseB)*(1.-smoothstep(.83,1.,phaseB));
 float veil=(smoothstep(.50,.80,mistA)*fadeA+smoothstep(.50,.80,mistB)*fadeB)*.10;
 light+=trans*veil*vec3(.32,.39,.38);trans*=1.-veil;
 // Keep the central synopsis readable without an opaque rectangle or a hard edge.
 vec2 screen=uv*.5+.5;
 float reading=smoothstep(.30,.43,screen.x)*(1.-smoothstep(.73,.83,screen.y))*smoothstep(.16,.32,screen.y);
 float strength=mix(.78,.44,reading);
 gl_FragColor=vec4(light*strength,(1.-trans)*strength); // Premultiplied for native composition.
}
