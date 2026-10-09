package org.emulationstation.frontend.netplay;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.Arrays;

/** Matches the 24-byte network-order TSR2 contract. No ROM hashes or per-frame signatures. */
final class StationRecoveryWire {
    static final int HEADER=24,MAX_DATA=16384;
    static final int HELLO=1,WELCOME=2,DATA=3,ACK=4,ACCEPTED=5,STATE=6,
        PAUSED=7,READY=8,PING=9,PONG=10,SUSPEND=11,FOREGROUND=12,NEED_SYNC=13;
    final int type;final long offset,value;final byte[] data;
    StationRecoveryWire(int type,long offset,long value,byte[] data){this.type=type;this.offset=offset;this.value=value;this.data=data;}
    StationRecoveryWire(int type,long offset,long value){this(type,offset,value,new byte[0]);}
    byte[] encode(){ByteBuffer b=ByteBuffer.allocate(HEADER+data.length);b.putInt(0x54535232).put((byte)type).put(new byte[3]).putLong(offset).putLong(value).put(data);return b.array();}
    static StationRecoveryWire decode(ByteBuffer incoming)throws IOException {
        ByteBuffer b=incoming.slice();int size=b.remaining();
        if(size<HEADER||size>HEADER+MAX_DATA||b.getInt()!=0x54535232)throw new IOException("FRAME");
        int type=b.get()&255;
        if(type<1||type>13||b.get()!=0||b.get()!=0||b.get()!=0)throw new IOException("FRAME");
        long offset=b.getLong(),value=b.getLong();
        if(offset<0||offset>Long.MAX_VALUE-MAX_DATA||value<0||(type==DATA?(size==HEADER||value!=0):size!=HEADER))throw new IOException("FRAME");
        byte[] data=new byte[b.remaining()];b.get(data);return new StationRecoveryWire(type,offset,value,data);
    }
    static final class Bytes {
        private final byte[] bytes;long next,delivered;
        Bytes(int capacity){if(capacity<32768||capacity>1048576)throw new IllegalArgumentException("WINDOW");bytes=new byte[capacity];}
        int capacity(){return bytes.length;}
        long pending(){return next-delivered;}
        int credit(){return (int)(bytes.length-pending());}
        void append(long offset,byte[] data)throws IOException{
            if(data.length==0||data.length>MAX_DATA||offset<0||offset>Long.MAX_VALUE-data.length||offset>next)throw new IOException("OFFSET");
            long end=offset+data.length;
            if(offset<next){
                if(end>next)throw new IOException("OFFSET");
                for(long at=Math.max(offset,delivered);at<end;at++)if(bytes[(int)(at%bytes.length)]!=data[(int)(at-offset)])throw new IOException("BYTES");
                return;
            }
            if(data.length>credit())throw new IOException("WINDOW");
            for(int i=0;i<data.length;i++)bytes[(int)((offset+i)%bytes.length)]=data[i];next=end;
        }
        void confirm(long offset)throws IOException {if(offset<delivered||offset>next)throw new IOException("OFFSET");delivered=offset;}
        byte[] read(long offset)throws IOException{
            if(offset<delivered||offset>next)throw new IOException("OFFSET");int size=(int)Math.min(MAX_DATA,next-offset);byte[] result=new byte[size];
            for(int i=0;i<size;i++)result[i]=bytes[(int)((offset+i)%bytes.length)];return result;
        }
    }
}
