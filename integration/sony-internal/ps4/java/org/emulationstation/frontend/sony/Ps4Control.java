package org.emulationstation.frontend.sony;

import android.net.LocalSocket;
import android.view.InputDevice;
import android.view.KeyEvent;
import android.view.MotionEvent;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.Consumer;

/** Exact BACHATA/1 controller snapshots, event driven with coalesced bounded writes. */
final class Ps4Control implements Closeable {
    static final int CROSS=0x4000,CIRCLE=0x2000,SQUARE=0x8000,TRIANGLE=0x1000;
    private final Ps4UnixServer listener;
    private final Consumer<String> events;
    private final ExecutorService workers=Executors.newFixedThreadPool(2,r->{Thread t=new Thread(r,"StationPS4-Control");t.setDaemon(true);return t;});
    private final Object lock=new Object();
    private final Map<Integer,Integer> deviceSlots=new HashMap<>();
    private final State[] states={new State(),new State(),new State(),new State()};
    private final LinkedHashMap<Integer,String> pending=new LinkedHashMap<>();
    private volatile boolean closed;
    private volatile LocalSocket peer;
    private OutputStream output;
    private static final class State {
        long sequence,buttons,keyButtons,hatButtons,touchButtons;
        int lx=128,ly=128,rx=128,ry=128,physicalLx=128,physicalLy=128,physicalRx=128,physicalRy=128,
            touchLx=128,touchLy=128,touchRx=128,touchRy=128,l2,r2,axisL2,axisR2;
        boolean touch,touchActive;
        String snapshot(int slot) {
            return "BACHATA/1 INPUT slot="+slot+" seq="+(++sequence)+" buttons="+buttons+
                " lx="+lx+" ly="+ly+" rx="+rx+" ry="+ry+" l2="+l2+" r2="+r2+
                " touch="+(touch?1:0)+" tx=0 ty=0\n";
        }
        void combine() {
            buttons=keyButtons|hatButtons|touchButtons;
            l2=(buttons&0x100)!=0?255:axisL2;r2=(buttons&0x200)!=0?255:axisR2;
            if(axisL2>0)buttons|=0x100;if(axisR2>0)buttons|=0x200;
            touch=(buttons&0x100000)!=0;
            lx=touchActive?touchLx:physicalLx;ly=touchActive?touchLy:physicalLy;
            rx=touchActive?touchRx:physicalRx;ry=touchActive?touchRy:physicalRy;
        }
        void neutral() {
            buttons=keyButtons=hatButtons=touchButtons=0;
            lx=ly=rx=ry=physicalLx=physicalLy=physicalRx=physicalRy=touchLx=touchLy=touchRx=touchRy=128;
            l2=r2=axisL2=axisR2=0;touch=touchActive=false;
        }
    }
    Ps4Control(File path,Consumer<String> events) throws IOException {
        listener=new Ps4UnixServer(path);this.events=events;
        workers.execute(this::accept);workers.execute(this::write);
    }
    private void accept() {
        try {
            LocalSocket client=listener.accept();peer=client;
            client.setSendBufferSize(8192);
            synchronized(lock) {output=client.getOutputStream();for(int i=0;i<4;i++) pending.put(i,states[i].snapshot(i));lock.notifyAll();}
            InputStream in=client.getInputStream();StringBuilder line=new StringBuilder();int next;
            while(!closed && (next=in.read())!=-1) {
                if(next=='\n') {
                    String frame=line.toString();line.setLength(0);
                    if(frame.equals("BACHATA/1 HELLO version=1") || frame.equals("BACHATA/1 EVENT Starting") ||
                       frame.equals("BACHATA/1 EVENT Running") || frame.equals("BACHATA/1 EVENT Frame") ||
                       frame.startsWith("BACHATA/1 EVENT Stopped exit_code=") || frame.startsWith("BACHATA/1 ERROR code=")) events.accept(frame);
                    else throw new IOException("Protocolo PS4 incompatível");
                } else {if(line.length()>=512) throw new IOException("Mensagem PS4 inválida");line.append((char)next);}
            }
        } catch(IOException failure) {if(!closed) events.accept("transport_closed");}
        finally { synchronized(lock) {output=null;lock.notifyAll();} }
    }
    private void write() {
        while(!closed) {
            String value;OutputStream target;
            synchronized(lock) {
                while(!closed && (output==null || pending.isEmpty())) try {lock.wait();} catch(InterruptedException e){return;}
                if(closed) return;
                int slot=pending.keySet().iterator().next();value=pending.remove(slot);target=output;
            }
            try {target.write(value.getBytes(StandardCharsets.US_ASCII));target.flush();}
            catch(IOException failure) {if(!closed) events.accept("transport_closed");synchronized(lock){output=null;}}
        }
    }
    private void changed(int slot) {pending.put(slot,states[slot].snapshot(slot));lock.notifyAll();}
    private int slot(int device) {
        Integer existing=deviceSlots.get(device);if(existing!=null) return existing;
        boolean[] used=new boolean[4];for(int value:deviceSlots.values()) used[value]=true;
        for(int i=0;i<4;i++) if(!used[i]) {deviceSlots.put(device,i);return i;}return -1;
    }
    boolean key(KeyEvent event) {
        InputDevice device=event.getDevice();
        if(device==null || !gamepad(device.getSources())) return false;
        int mask=mask(event.getKeyCode());if(mask==0) return false;
        if(event.getAction()!=KeyEvent.ACTION_DOWN && event.getAction()!=KeyEvent.ACTION_UP) return false;
        synchronized(lock) {
            int slot=slot(event.getDeviceId());if(slot<0) return true;
            State s=states[slot];long before=s.buttons;
            if(event.getAction()==KeyEvent.ACTION_DOWN) s.keyButtons|=mask;else s.keyButtons&=~mask;
            s.combine();
            if(before!=s.buttons) changed(slot);
        }return true;
    }
    boolean motion(MotionEvent event) {
        if(!gamepad(event.getSource()) || event.getAction()!=MotionEvent.ACTION_MOVE) return false;
        synchronized(lock) {
            int slot=slot(event.getDeviceId());if(slot<0) return true;State s=states[slot];
            int lx=axis(event,MotionEvent.AXIS_X),ly=axis(event,MotionEvent.AXIS_Y),
                rx=axis(event,MotionEvent.AXIS_Z),ry=axis(event,MotionEvent.AXIS_RZ),
                l2=trigger(event,MotionEvent.AXIS_LTRIGGER,MotionEvent.AXIS_BRAKE),
                r2=trigger(event,MotionEvent.AXIS_RTRIGGER,MotionEvent.AXIS_GAS);
            long hat=0;
            float hx=event.getAxisValue(MotionEvent.AXIS_HAT_X),hy=event.getAxisValue(MotionEvent.AXIS_HAT_Y);
            if(hx<-.5f) hat|=0x80;if(hx>.5f)hat|=0x20;if(hy<-.5f)hat|=0x10;if(hy>.5f)hat|=0x40;
            long before=s.buttons;int oldL2=s.l2,oldR2=s.r2;
            boolean axes=s.lx!=lx||s.ly!=ly||s.rx!=rx||s.ry!=ry;
            s.physicalLx=lx;s.physicalLy=ly;s.physicalRx=rx;s.physicalRy=ry;s.axisL2=l2;s.axisR2=r2;s.hatButtons=hat;s.combine();
            if(axes||oldL2!=s.l2||oldR2!=s.r2||before!=s.buttons) {
                changed(slot);
            }
        }return true;
    }
    void touchSnapshot(long buttons,int lx,int ly,int rx,int ry) {
        synchronized(lock) {
            State s=states[0];long before=s.buttons;boolean axes=s.lx!=lx||s.ly!=ly||s.rx!=rx||s.ry!=ry;
            s.touchButtons=buttons;s.touchLx=lx;s.touchLy=ly;s.touchRx=rx;s.touchRy=ry;s.touchActive=true;s.combine();
            if(before!=s.buttons||axes)changed(0);
        }
    }
    void clearTouch() {
        synchronized(lock){State s=states[0];long before=s.buttons;int lx=s.lx,ly=s.ly,rx=s.rx,ry=s.ry;
            s.touchButtons=0;s.touchActive=false;s.combine();
            if(before!=s.buttons||lx!=s.lx||ly!=s.ly||rx!=s.rx||ry!=s.ry)changed(0);
        }
    }
    void neutral() {synchronized(lock) {for(int i=0;i<4;i++){states[i].neutral();changed(i);}}}
    void removed(int device) {synchronized(lock) {Integer slot=deviceSlots.remove(device);if(slot!=null){states[slot].neutral();changed(slot);}}}
    static boolean gamepad(int source) {return (source&InputDevice.SOURCE_GAMEPAD)==InputDevice.SOURCE_GAMEPAD || (source&InputDevice.SOURCE_JOYSTICK)==InputDevice.SOURCE_JOYSTICK;}
    private static int axis(MotionEvent event,int axis) {
        InputDevice device=event.getDevice();InputDevice.MotionRange range=device==null?null:device.getMotionRange(axis,event.getSource());
        float value=event.getAxisValue(axis);if(range!=null && Math.abs(value)<=range.getFlat()) value=0;
        return Math.max(0,Math.min(255,Math.round((value+1)*127.5f)));
    }
    private static int trigger(MotionEvent event,int primary,int secondary) {return Math.max(0,Math.min(255,Math.round(Math.max(event.getAxisValue(primary),event.getAxisValue(secondary))*255)));}
    private static int mask(int key) {
        switch(key) {
            case KeyEvent.KEYCODE_BUTTON_A:return CROSS;case KeyEvent.KEYCODE_BUTTON_B:return CIRCLE;
            case KeyEvent.KEYCODE_BUTTON_X:return SQUARE;case KeyEvent.KEYCODE_BUTTON_Y:return TRIANGLE;
            case KeyEvent.KEYCODE_DPAD_UP:return 0x10;case KeyEvent.KEYCODE_DPAD_RIGHT:return 0x20;
            case KeyEvent.KEYCODE_DPAD_DOWN:return 0x40;case KeyEvent.KEYCODE_DPAD_LEFT:return 0x80;
            case KeyEvent.KEYCODE_BUTTON_L1:return 0x400;case KeyEvent.KEYCODE_BUTTON_R1:return 0x800;
            case KeyEvent.KEYCODE_BUTTON_L2:return 0x100;case KeyEvent.KEYCODE_BUTTON_R2:return 0x200;
            case KeyEvent.KEYCODE_BUTTON_THUMBL:return 2;case KeyEvent.KEYCODE_BUTTON_THUMBR:return 4;
            case KeyEvent.KEYCODE_BUTTON_START:return 8;case KeyEvent.KEYCODE_BUTTON_SELECT:return 0x100000;
            default:return 0;
        }
    }
    @Override public void close() throws IOException {
        closed=true;synchronized(lock){lock.notifyAll();}
        try {LocalSocket client=peer;if(client!=null)client.close();}
        finally {try{listener.close();}finally{workers.shutdownNow();}}
    }
}
