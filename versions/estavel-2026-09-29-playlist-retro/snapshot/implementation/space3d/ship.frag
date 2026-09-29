uniform sampler2D albedoMap;
uniform sampler2D normalMap;
uniform sampler2D ormMap;
uniform sampler2D emissionMap;
varying vec3 worldPosition;
varying vec3 worldNormal;
varying vec4 worldTangent;
varying vec2 uv;
vec3 brdf(vec3 n,vec3 v,vec3 l,vec3 color,float metal,float rough){
 vec3 h=normalize(v+l);float nl=max(dot(n,l),0.),nv=max(dot(n,v),.001),nh=max(dot(n,h),0.),vh=max(dot(v,h),0.);
 float a=rough*rough,a2=a*a;float d=a2/(PI*pow(nh*nh*(a2-1.)+1.,2.));
 float k=(rough+1.)*(rough+1.)/8.;float g=nv/(nv*(1.-k)+k)*nl/(nl*(1.-k)+k);
 vec3 f0=mix(vec3(.04),color,metal);vec3 f=f0+(1.-f0)*pow(1.-vh,5.);
 return ((1.-f)*(1.-metal)*color/PI+d*g*f/max(4.*nv*nl,.001))*nl;
}
vec3 environment(vec3 r,float rough){
 float spread=mix(130.,4.,rough*rough);vec3 e=vec3(.019,.022,.028);
 e+=vec3(.18,.25,.29)*pow(max(dot(r,normalize(vec3(-.8,.3,1.))),0.),2.);
 e+=vec3(4.8,4.7,4.2)*pow(max(dot(r,normalize(vec3(-2.,3.8,-2.))),0.),spread);
 e+=vec3(.30,.65,.43)*pow(max(dot(r,normalize(vec3(3.,1.,2.))),0.),spread*.55);
 return e;
}
float wordmark(vec2 q){
 if(q.x<0.||q.x>1.||q.y<0.||q.y>1.)return 0.;
 return texture2D(emissionMap,(vec2(0.,1824.)+q*vec2(1024.,192.))/2048.).a;
}
void main(){
 vec3 local=localFromWorld(worldPosition);vec3 localN=transpose3(shipRotation())*normalize(worldNormal);
 float kind=abs(worldTangent.w);vec3 tex=texture2D(albedoMap,uv).rgb;vec3 original=pow(tex,vec3(2.2));
 vec3 orm=texture2D(ormMap,uv).rgb;float rough=clamp(orm.g,.2,.85),metal=orm.b,opacity=1.;vec3 base=original;
 if(kind<1.5){
  // The original UV panel/rivet drawing remains. Graphite livery is applied in material space.
  float shade=dot(tex,vec3(.2126,.7152,.0722));
  base=clamp(original,vec3(.008),vec3(.085))*.85;rough=.23+orm.g*.25;metal=.42;
  // Green leading wing accents and tail-tip cap are paint, never emissive outlines.
  float wing=smoothstep(.17,.23,abs(local.x))*(1.-smoothstep(.005,.010,abs(local.z-(.02-abs(local.x)*.31))))*smoothstep(.30,.70,localN.y);
  float tail=smoothstep(.385,.412,local.y)*(1.-smoothstep(.025,.038,abs(local.x)));
  float stripe=max(wing,tail);base=mix(base,vec3(.015,.155,.045),stripe);metal=mix(metal,.1,stripe);
  // Separate shoulder decals: each side has a complete word, with a clear dorsal gap.
  // The source glyph bounds are 1166 x 142. World dimensions restore that 8.21:1 ratio.
  float flank=local.x<0.?-1.:1.;
  vec2 shoulder=vec2(.5-(local.z-.025)*flank/.45,.5+((abs(local.x)-.060)*.8660254-(local.y-.065)*.5)/.05480);
  float side=wordmark(shoulder)*smoothstep(.65,.82,dot(localN,vec3(flank*.5,.8660254,0.)))*smoothstep(.025,.034,abs(local.x))*(1.-smoothstep(.095,.110,abs(local.x)))*smoothstep(.023,.030,local.y);
  float wingText=wordmark(vec2((.665-abs(local.x))/.45,.5-(local.z+.06+.24*abs(local.x))/.054808))*smoothstep(.5,.8,localN.y)*smoothstep(.20,.23,abs(local.x));
  float tailText=wordmark(vec2((-.47-local.z)/.22,1.-((local.y-.25)/.026793+.5)))*smoothstep(.6,.9,abs(localN.x))*smoothstep(.17,.21,local.y);
  float brand=max(side,max(wingText,tailText));base=mix(base,vec3(.57,.62,.58),brand);rough=mix(rough,.48,brand);metal*=1.-brand;
 }else if(kind<2.5){base=vec3(.008,.020,.022);rough=.09;metal=0.;}
 else if(kind<3.5){base=mix(original,vec3(.18,.145,.098),.38);rough=.26+orm.g*.2;metal=.82;}
 else if(kind<4.5){base=original;rough=.67;metal=.12;}
 else {base=original;rough=.35;metal=.2;}
 vec3 n=normalize(worldNormal),t=normalize(worldTangent.xyz);t=normalize(t-n*dot(t,n));
 if(kind<1.5||kind>2.5)n=normalize(mat3(t,normalize(cross(n,t))*sign(worldTangent.w),n)*(texture2D(normalMap,uv).xyz*2.-1.));
 vec3 v=normalize(camera()-worldPosition);
 vec3 light=brdf(n,v,normalize(vec3(-2.,3.8,-2.)),base,metal,rough)*vec3(5.0,4.8,4.5);
 light+=brdf(n,v,normalize(vec3(3.,1.,2.)),base,metal,rough)*vec3(.65,1.25,.91);
 light+=brdf(n,v,normalize(vec3(-3.,.3,1.)),base,metal,rough)*vec3(.32,.50,.65);
 float nv=max(dot(n,v),0.);vec3 f0=mix(vec3(.04),base,metal);vec3 f=f0+(max(vec3(1.-rough),f0)-f0)*pow(1.-nv,5.);
 light+=(base*(1.-metal)*vec3(.09,.10,.11)+environment(reflect(-v,n),rough)*f)*orm.r;
 if(kind>1.5&&kind<2.5){opacity=.32+.62*pow(1.-nv,3.);light+=environment(reflect(-v,n),.065)*.55;}
 if(kind>4.5&&kind<5.5)light+=vec3(1.8,.025,.007);
 if(kind>5.5&&kind<6.5)light+=vec3(.03,1.5,.15);
 if(kind>6.5)light+=vec3(.22,.33,.24)*(.8+.2*sin(time*3.));
 // Warm engine radiation illuminates the metal petals nearest the single aperture.
 float rear=1.-smoothstep(-.73,-.64,local.z);float bore=1.-smoothstep(.038,.068,length(local.xy));
 if(kind>2.5&&kind<3.5)light+=vec3(1.2,.22,.02)*rear*bore*(1.-smoothstep(-.2,.35,dot(normalize(local.xy+vec2(.00001)),localN.xy)))*(.4+boost()*.6);
 gl_FragColor=vec4(tone(light),opacity);
}
