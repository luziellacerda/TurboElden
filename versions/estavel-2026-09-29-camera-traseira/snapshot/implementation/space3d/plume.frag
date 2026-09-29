uniform sampler2D hullDepthMap;
varying vec2 uv;
float hash(vec3 p){p=fract(p*.1031);p+=dot(p,p.yzx+33.33);return fract((p.x+p.y)*p.z);}
float noise(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x),mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);}
vec2 intersectBox(vec3 ro,vec3 rd,vec3 low,vec3 high){vec3 a=(low-ro)/rd,b=(high-ro)/rd;vec3 mn=min(a,b),mx=max(a,b);return vec2(max(max(mn.x,mn.y),mn.z),min(min(mx.x,mx.y),mx.z));}
void main(){
 mat3 inv=transpose3(shipRotation());vec3 ro=localFromWorld(camera()),rd=normalize(inv*cameraBasis()*normalize(vec3(uv/2.9,-1.)));
 vec2 hit=intersectBox(ro,rd,vec3(-.20,-.20,-1.58),vec3(.20,.20,-.700));
 float hullDistance=dot(texture2D(hullDepthMap,uv*.5+.5).rgb,vec3(1.,1./255.,1./65025.))*20.;hit.y=min(hit.y,hullDistance-.0007);
 if(hit.y<=max(hit.x,0.))discard;
 float start=max(hit.x,0.),stepSize=(hit.y-start)/48.;vec3 sum=vec3(0.);float trans=1.;
 for(int i=0;i<48;i++){
  vec3 p=ro+rd*(start+(float(i)+.5)*stepSize);float z=-.70681-p.z;
  if(z<0.)continue;
  float turbulence=noise(p*vec3(62.,62.,36.)+vec3(0.,0.,time*8.));
  float cells=.88+.12*cos(z*68.);
  float radius=(.043+z*.044)*(.90+.13*boost())*(.95+.05*cos(z*68.));
  // The wake bends slightly opposite the current turn; the aperture stays fixed.
  vec2 wake=vec2(1.05*turnRate(),0.)*z*z;
  vec2 curl=vec2(sin(z*27.-time*8.),cos(z*23.-time*6.))*z*z*.012+wake;
  float r=length(p.xy+curl),core=exp(-r*r/(radius*radius)*2.6);
  float tail=1.-smoothstep(.24+boost()*.08,.51+boost()*.18,z);
  float jet=core*cells*tail*(.82+.28*turbulence);
  float haze=exp(-r*r/pow(.035+z*.14,2.)*2.6)*smoothstep(.25,.48,z)*(1.-smoothstep(.50,.84,z))*smoothstep(.48,.85,turbulence)*.11;
  float alpha=1.-exp(-(jet*48.+haze*9.)*stepSize);
  vec3 fire=mix(vec3(1.9,.43,.055),vec3(.30,.45,1.2),smoothstep(.02,.18,z))*(.8+.30*boost());
  fire=mix(fire,vec3(2.8,2.6,2.2),smoothstep(.35,.92,jet));
  vec3 color=mix(vec3(.07,.085,.10),fire,jet/max(jet+haze,.001));sum+=trans*alpha*color;trans*=1.-alpha;
 }
 float alpha=1.-trans;if(alpha<.003)discard;gl_FragColor=vec4(tone(sum/max(alpha,.001)),alpha);
}
