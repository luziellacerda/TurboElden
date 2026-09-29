varying vec3 worldPosition;
void main(){
 // Store ray distance in RGB8, so this also works with GLES2 without depth-texture extensions.
 float distanceToHull=clamp(length(worldPosition-camera())/20.,0.,.9999);
 vec3 encodedDepth=fract(distanceToHull*vec3(1.,255.,65025.));encodedDepth.xy-=encodedDepth.yz/255.;
 gl_FragColor=vec4(encodedDepth,1.);
}
