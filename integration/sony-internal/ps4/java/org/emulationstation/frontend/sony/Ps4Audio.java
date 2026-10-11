package org.emulationstation.frontend.sony;

import android.media.AudioAttributes;
import android.media.AudioFormat;
import android.media.AudioTrack;
import android.net.LocalSocket;
import java.io.*;
import java.util.Set;
import java.util.concurrent.*;
import java.util.function.Consumer;

/** BACHATA_ALSA_SOCKET: five-byte requests, prepared PCM streams, no UI polling. */
final class Ps4Audio implements Closeable {
    private static final int MAX_PCM=262144;
    private final Ps4UnixServer server;
    private final Consumer<String> error;
    private final Set<LocalSocket> peers=ConcurrentHashMap.newKeySet();
    private final Set<AudioTrack> tracks=ConcurrentHashMap.newKeySet();
    private final ExecutorService acceptor=Executors.newSingleThreadExecutor(r->daemon(r,"StationPS4-AudioAccept"));
    private final ThreadPoolExecutor streams=new ThreadPoolExecutor(0,8,30,TimeUnit.SECONDS,
        new SynchronousQueue<>(),r->daemon(r,"StationPS4-Audio"));
    private volatile boolean closed;
    Ps4Audio(File path,Consumer<String> error) throws IOException {
        this.server=new Ps4UnixServer(path);this.error=error;acceptor.execute(this::accept);
    }
    private static Thread daemon(Runnable run,String name) {Thread t=new Thread(run,name);t.setDaemon(true);return t;}
    private void accept() {
        try {
            while(!closed) {
                LocalSocket peer=server.accept();peers.add(peer);
                try {streams.execute(()->play(peer));}
                catch(RejectedExecutionException full) {peers.remove(peer);peer.close();if(!closed)error.accept("Limite de áudio PS4 excedido");}
            }
        } catch(IOException failure) {if(!closed) error.accept("O áudio PS4 não pôde iniciar");}
    }
    private void play(LocalSocket peer) {
        AudioTrack track=null;
        try {
            InputStream input=new BufferedInputStream(peer.getInputStream());
            byte[] header=new byte[5],pcm=new byte[MAX_PCM];short[] stereo=new short[MAX_PCM*2];
            int channels=0,type=0;
            while(!closed && readHeader(input,header)) {
                int code=header[0]&255;long length=u32(header,1);
                if(code==0) {if(length!=0)throw new IOException("Invalid close");break;}
                if(code==4) {
                    if(length!=10)throw new IOException("Invalid prepare");
                    readFully(input,pcm,10);channels=pcm[0]&255;type=pcm[1]&255;
                    long rate=u32(pcm,2),requested=u32(pcm,6);
                    if((channels!=1&&channels!=2&&channels!=8)||type>4||rate<8000||rate>192000||requested>16*1024*1024)
                        throw new IOException("Unsupported PCM format");
                    if(track!=null)release(track);
                    int minimum=AudioTrack.getMinBufferSize((int)rate,AudioFormat.CHANNEL_OUT_STEREO,AudioFormat.ENCODING_PCM_16BIT);
                    if(minimum<=0)throw new IOException("Unsupported audio rate");
                    int buffer=Math.max(minimum,Math.min(MAX_PCM,Math.max(4096,(int)requested)));
                    track=new AudioTrack.Builder().setAudioAttributes(new AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_GAME).setContentType(AudioAttributes.CONTENT_TYPE_MUSIC).build())
                        .setAudioFormat(new AudioFormat.Builder().setSampleRate((int)rate)
                            .setChannelMask(AudioFormat.CHANNEL_OUT_STEREO).setEncoding(AudioFormat.ENCODING_PCM_16BIT).build())
                        .setTransferMode(AudioTrack.MODE_STREAM).setBufferSizeInBytes(buffer).build();
                    if(track.getState()!=AudioTrack.STATE_INITIALIZED){track.release();track=null;throw new IOException("AudioTrack unavailable");}
                    synchronized(tracks){if(closed){track.release();track=null;break;}tracks.add(track);}
                    track.play();
                } else if(code==5) {
                    if(track==null||length<1||length>MAX_PCM)throw new IOException("Invalid PCM write");
                    int bytes=(int)length;readFully(input,pcm,bytes);
                    int width=type==0?1:(type<=2?2:4),frameBytes=channels*width;
                    if(bytes%frameBytes!=0)throw new IOException("Incomplete PCM frame");
                    int count=convert(pcm,bytes,channels,type,stereo),offset=0;
                    while(!closed&&offset<count) {
                        int n=track.write(stereo,offset,count-offset,AudioTrack.WRITE_BLOCKING);
                        if(n<=0)throw new IOException("Audio write failed");offset+=n;
                    }
                } else throw new IOException("Unknown ALSA request");
            }
        } catch(IOException|IllegalArgumentException|IllegalStateException failure) {
            if(!closed) error.accept("Formato ou saída de áudio PS4 indisponível");
        } finally {
            if(track!=null)release(track);peers.remove(peer);try{peer.close();}catch(IOException ignored){}
        }
    }
    static int convert(byte[] input,int bytes,int channels,int type,short[] output) {
        int width=type==0?1:(type<=2?2:4),frames=bytes/(channels*width);
        for(int f=0;f<frames;f++) {
            int position=f*channels*width;
            short left=sample(input,position,type),right=channels==1?left:sample(input,position+width,type);
            output[f*2]=left;output[f*2+1]=right;
        }return frames*2;
    }
    private static short sample(byte[] input,int offset,int type) {
        if(type==0)return (short)(((input[offset]&255)-128)<<8);
        if(type==1)return (short)((input[offset]&255)|(input[offset+1]<<8));
        if(type==2)return (short)((input[offset]<<8)|(input[offset+1]&255));
        int bits=type==3?(int)u32(input,offset):((input[offset]&255)<<24)|((input[offset+1]&255)<<16)|
            ((input[offset+2]&255)<<8)|(input[offset+3]&255);
        float value=Float.intBitsToFloat(bits);if(!Float.isFinite(value))value=0;
        if(value<=-1)return -32768;return (short)Math.round(Math.min(1,value)*32767);
    }
    private static long u32(byte[] data,int p) {return (data[p]&255L)|((data[p+1]&255L)<<8)|((data[p+2]&255L)<<16)|((data[p+3]&255L)<<24);}
    private static boolean readHeader(InputStream input,byte[] header) throws IOException {
        int first=input.read();if(first<0)return false;header[0]=(byte)first;readFully(input,header,1,4);return true;
    }
    private static void readFully(InputStream input,byte[] data,int size) throws IOException {readFully(input,data,0,size);}
    private static void readFully(InputStream input,byte[] data,int offset,int size) throws IOException {
        int end=offset+size;while(offset<end){int n=input.read(data,offset,end-offset);if(n<0)throw new EOFException();offset+=n;}
    }
    private void release(AudioTrack track) {
        if(!tracks.remove(track))return;
        try{track.pause();track.flush();}catch(IllegalStateException ignored){}track.release();
    }
    @Override public void close() throws IOException {
        closed=true;
        try {server.close();}
        finally {
            for(LocalSocket peer:peers)try{peer.close();}catch(IOException ignored){}
            synchronized(tracks){for(AudioTrack track:tracks)release(track);}
            acceptor.shutdownNow();streams.shutdownNow();
        }
    }
}
