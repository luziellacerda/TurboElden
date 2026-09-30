uniform sampler2D hullDepthMap;
varying vec2 uv;
float hash(vec3 p){p=fract(p*.1031);p+=dot(p,p.yzx+33.33);return fract((p.x+p.y)*p.z);}
float noise(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x),mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);}
vec2 intersectBox(vec3 ro,vec3 rd,vec3 low,vec3 high){vec3 a=(low-ro)/rd,b=(high-ro)/rd;vec3 mn=min(a,b),mx=max(a,b);return vec2(max(max(mn.x,mn.y),mn.z),min(min(mx.x,mx.y),mx.z));}
void main(){
 mat3 inv=transpose3(shipRotation());vec3 ro=localFromWorld(camera()),rd=normalize(inv*cameraBasis()*normalize(vec3(uv/2.9,-1.)));
 vec2 hit=intersectBox(ro,rd,vec3(-.32,-.30,-1.92),vec3(.32,.30,-.700));
 float hullDistance=dot(texture2D(hullDepthMap,uv*.5+.5).rgb,vec3(1.,1./255.,1./65025.))*20.;hit.y=min(hit.y,hullDistance-.0007);
 if(hit.y<=max(hit.x,0.))discard;
 float start=max(hit.x,0.),stepSize=(hit.y-start)/48.;vec3 sum=vec3(0.);float trans=1.;
 float power=clamp(boost(),.25,1.);
 float reach=.30+.56*power;
 // The exit stays attached to the nozzle. Turbulence and older wake bend only
 // downstream; power is the same delayed engine load used by the flight path.
 for(int i=0;i<48;i++){
  vec3 p=ro+rd*(start+(float(i)+.5)*stepSize);float z=-.70681-p.z;
  if(z<0.)continue;
  float broad=noise(p*vec3(23.,23.,15.)+vec3(.4*time,-.2*time,time*5.4));
  float fine=noise(p*vec3(61.,61.,38.)+vec3(-time*.6,time*.3,time*9.));
  float age=z/(1.45+power);
  vec2 delayed=vec2(-turnRate(),aircraftWake.x)*age*z*.62;
  vec2 eddy=vec2(sin(z*17.-time*4.7+broad*3.),cos(z*13.-time*3.8+fine*2.))*z*z*.035;
  vec2 offset=delayed+eddy;
  float radius=(.033+z*.082)*(.83+.28*power)*(1.+(.42*broad-.21)*smoothstep(.03,.25,z));
  float radial=length(p.xy-offset)/max(radius,.001);
  float core=exp(-radial*radial*2.0);
  float diamonds=.88+.12*cos(z*(58.-9.*power)+broad*.55);
  float tail=1.-smoothstep(reach*.46,reach,z);
  float breakup=mix(1.,smoothstep(.13,.78,broad*.68+fine*.32),smoothstep(.10,.58,z));
  float jet=core*diamonds*tail*(.36+.64*breakup);
  float sheath=exp(-radial*radial*.82)*tail*(.35+.65*fine)*.19;
  float smokeRadius=.044+z*.18;
  float r=length(p.xy-offset*1.45);
  float smoke=exp(-r*r/(smokeRadius*smokeRadius)*2.0)*smoothstep(.28,.60,z)*(1.-smoothstep(.72,1.12,z))*smoothstep(.27,.77,broad)*.12;
  float density=jet*24.+sheath*12.+smoke*5.;
  float alpha=1.-exp(-density*stepSize);
  vec3 blue=vec3(.20,.37,1.18),amber=vec3(1.50,.37,.045);
  vec3 fire=mix(amber,blue,smoothstep(.015,.18,z))*(.57+.45*power);
  fire=mix(fire,vec3(1.70,1.50,1.12),.34*smoothstep(.38,.94,jet));
  vec3 haze=vec3(.075,.09,.12);
  float luminous=jet+sheath;
  vec3 color=mix(haze,fire,luminous/max(luminous+smoke,.001));
  sum+=trans*alpha*color;trans*=1.-alpha;
 }
 float alpha=1.-trans;if(alpha<.003)discard;
 gl_FragColor=vec4(tone(sum/max(alpha,.001)),alpha);
}
