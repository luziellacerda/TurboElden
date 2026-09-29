attribute vec3 position;
varying vec3 worldPosition;
void main(){worldPosition=worldFromLocal(position);gl_Position=project(worldPosition);}
