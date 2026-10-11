package org.emulationstation.frontend.netplay;

import java.util.Arrays;

/** Executed planner: uneven dimensions, four-row quota and full deterministic coverage. */
public final class StationMagazineRowsTest {
    private static int checks;
    private static void check(boolean value){checks++;if(!value)throw new AssertionError("check "+checks);}
    public static void main(String[] args){
        for(int height=1;height<=1536;height++){
            for(int inset: new int[]{0,height/8,height/3}){
                StationMagazineRows plan=new StationMagazineRows();plan.reset(height,inset,height-2*inset);
                boolean[] seen=new boolean[height];int count=0,frames=0;
                while(count<height){
                    int frameRows=0;for(int slice=0;slice<4;slice++){
                        int row=plan.next();if(row<0)break;
                        check(row>=0&&row<height&&!seen[row]);seen[row]=true;count++;frameRows++;
                    }
                    check(frameRows>0&&frameRows<=4);frames++;
                }
                check(frames==(height+3)/4);check(plan.next()==-1&&plan.done()==height);
                for(boolean value:seen)check(value);
            }
        }
        StationMagazineRows plan=new StationMagazineRows();plan.reset(960,0,960);
        int[] actual=new int[4];for(int i=0;i<4;i++)actual[i]=plan.next();
        check(Arrays.equals(actual,new int[]{606,910,328,51}));
        System.out.println("PASS "+checks+" executed Java progressive-field row checks");
    }
}
