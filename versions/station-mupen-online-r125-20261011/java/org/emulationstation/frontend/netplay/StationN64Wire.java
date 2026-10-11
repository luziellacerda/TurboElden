package org.emulationstation.frontend.netplay;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;

/** Mupen TCP and datagrams inside the authenticated, replayable Station DATA stream.
 * No tickets, roles or epochs are accepted from this inner protocol. */
final class StationN64Wire {
    static final int TCP=1, UDP=2, MAX_TCP=16384, MAX_UDP=512;
    static final int MAGIC=0x534e3634; // SN64, version 1 follows.
    static void header(OutputStream out)throws IOException {
        DataOutputStream d=new DataOutputStream(out);d.writeInt(MAGIC);d.writeByte(1);d.flush();
    }
    static void checkHeader(InputStream in)throws IOException {
        DataInputStream d=new DataInputStream(in);
        if(d.readInt()!=MAGIC||d.readUnsignedByte()!=1)throw new IOException("N64_WIRE_VERSION");
    }
    static void frame(OutputStream out,int kind,byte[] bytes,int offset,int count)throws IOException {
        if((kind!=TCP&&kind!=UDP)||count<1||count>(kind==TCP?MAX_TCP:MAX_UDP))throw new IOException("N64_FRAME_SIZE");
        synchronized(out){DataOutputStream d=new DataOutputStream(out);d.writeByte(kind);d.writeShort(count);d.write(bytes,offset,count);d.flush();}
    }
    interface Receiver {void tcp(byte[] bytes)throws IOException;void udp(byte[] bytes)throws IOException;}
    static void read(InputStream in,Receiver receiver)throws IOException {
        DataInputStream d=new DataInputStream(in);checkHeader(d);
        for(;;){int kind=d.read();if(kind<0)throw new EOFException("N64_STREAM_END");int n=d.readUnsignedShort();
            if((kind!=TCP&&kind!=UDP)||n<1||n>(kind==TCP?MAX_TCP:MAX_UDP))throw new IOException("N64_FRAME_SIZE");
            byte[] bytes=new byte[n];d.readFully(bytes);if(kind==TCP)receiver.tcp(bytes);else receiver.udp(bytes);
        }
    }
    static byte[] exact(InputStream in,int size)throws IOException {
        byte[] result=new byte[size];new DataInputStream(in).readFully(result);return result;
    }
    static String filename(InputStream in)throws IOException {
        ByteArrayOutputStream bytes=new ByteArrayOutputStream();
        for(int i=0;i<128;i++){int b=in.read();if(b<0)throw new EOFException();if(b==0){String s;
            try{s=StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(bytes.toByteArray())).toString();}
            catch(CharacterCodingException e){throw new IOException("N64_SAVE_NAME",e);}
            if(s.isEmpty()||s.equals(".")||s.equals(".."))throw new IOException("N64_SAVE_NAME");
            for(int n=0;n<s.length();n++){char c=s.charAt(n);if(c=='/'||c=='\\'||Character.isISOControl(c))throw new IOException("N64_SAVE_NAME");}
            return s;}bytes.write(b);}
        throw new IOException("N64_SAVE_NAME");
    }
    static int int32(byte[] b,int n){return ((b[n]&255)<<24)|((b[n+1]&255)<<16)|((b[n+2]&255)<<8)|(b[n+3]&255);}
    /** Bounded stream queue. Backpressure reaches the existing Station receive window. */
    static final class Queue extends InputStream {
        private final byte[] bytes=new byte[262144];private int at,size;private boolean closed;
        synchronized void put(byte[] source)throws IOException {
            int offset=0;while(offset<source.length){while(size==bytes.length&&!closed)await();if(closed)throw new EOFException();
                int count=Math.min(source.length-offset,Math.min(bytes.length-size,bytes.length-((at+size)%bytes.length)));
                System.arraycopy(source,offset,bytes,(at+size)%bytes.length,count);size+=count;offset+=count;notifyAll();}
        }
        private void await()throws IOException{try{wait();}catch(InterruptedException e){Thread.currentThread().interrupt();throw new InterruptedIOException();}}
        @Override public synchronized int read()throws IOException {while(size==0&&!closed)await();if(size==0)return -1;int b=bytes[at]&255;at=(at+1)%bytes.length;size--;notifyAll();return b;}
        @Override public synchronized int read(byte[] dst,int offset,int length)throws IOException {
            if(offset<0||length<0||offset>dst.length-length)throw new IndexOutOfBoundsException();if(length==0)return 0;
            while(size==0&&!closed)await();if(size==0)return -1;int count=Math.min(length,Math.min(size,bytes.length-at));
            System.arraycopy(bytes,at,dst,offset,count);at=(at+count)%bytes.length;size-=count;notifyAll();return count;
        }
        @Override public synchronized void close(){closed=true;notifyAll();}
    }
}
