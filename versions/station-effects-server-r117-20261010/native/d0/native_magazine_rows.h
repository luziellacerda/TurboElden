// Four one-row parcels, each from a different quarter. Seeds are the actual
// shared chassis' side lamps, header, lower lamps and footer in 1536px UV space.
// Every framebuffer row is visited exactly once; work remains <= four rows/frame.
struct MagazineRowPlan {
 int height=0,seed[4]={},ordinal=0,done=0;
 void reset(int h){
  height=h;ordinal=done=0;const int artY[4]={1454,1010,565,80};
  for(int q=0;q<4;q++){int lo=q*h/4,hi=(q+1)*h/4;
   int first=(int)((1536-artY[q])*(long long)h/1536);
   seed[q]=hi>lo?(first<lo?lo:first>=hi?hi-1:first):lo;}
 }
 int next(){
  if(done>=height)return -1;const int order[4]={2,3,1,0};
  for(;;){int q=order[ordinal%4],step=ordinal/4;ordinal++;
   int lo=q*height/4,span=(q+1)*height/4-lo;if(step>=span)continue;
   done++;return lo+(seed[q]-lo+step)%span;}
 }
};
