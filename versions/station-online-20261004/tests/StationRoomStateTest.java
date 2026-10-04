package org.emulationstation.frontend.netplay;
import org.json.*;import java.io.*;
public class StationRoomStateTest {
 static JSONObject v(long r,String i)throws Exception{return new JSONObject().put("instance",i).put("revision",r);}
 public static void main(String[] a)throws Exception{StationRoomState s=new StationRoomState();String id="a".repeat(32);
 if(!s.accept(v(10,id))||s.accept(v(9,id))||s.get().getLong("revision")!=10)throw new AssertionError();
 if(!s.accept(v(11,id)))throw new AssertionError();
 try{s.accept(v(1,"b".repeat(32)));throw new AssertionError();}catch(IOException expected){}
 s.reset();if(!s.accept(v(0,"b".repeat(32))))throw new AssertionError();
 try{s.accept(v(-1,"b".repeat(32)));throw new AssertionError();}catch(IOException expected){}
 System.out.println("PASS 6 executable revision and restart checks");}}
