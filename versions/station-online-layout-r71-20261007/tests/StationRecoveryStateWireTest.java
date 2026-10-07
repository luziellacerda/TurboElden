package org.emulationstation.frontend.netplay;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.Arrays;
import org.json.JSONObject;

/** Pure v2 launch/barrier framing and bounded byte-ledger regressions, not gameplay. */
public final class StationRecoveryStateWireTest {
    private static int checks;
    private interface Checked { void run() throws Exception; }
    private static void check(boolean value, String label) {
        checks++;
        if (!value) throw new AssertionError(label);
    }
    private static void reject(Checked action, String label) throws Exception {
        try { action.run(); throw new AssertionError("Accepted " + label); }
        catch (IOException expected) { checks++; }
    }
    private static void decode(byte[] frame) throws Exception { StationRecoveryWire.decode(ByteBuffer.wrap(frame)); }
    private static void testLaunch() throws Exception {
        for (String phase : new String[]{"starting", "connecting", "waiting-reconnect", "synchronizing", "playing", "unrecoverable"}) {
            for (boolean started : new boolean[]{false, true}) {
                for (boolean host : new boolean[]{false, true}) {
                    for (boolean listening : new boolean[]{false, true}) {
                        JSONObject room = new JSONObject().put("roomId", "synthetic").put("generation", 7)
                                .put("state", phase).put("transport", "relay-wss-v2")
                                .put("recoveryProtocol", "station-stream.v2").put("recoveryStarted", started)
                                .put("hostListening", listening);
                        boolean allowed = !started && !phase.equals("unrecoverable") && (host || listening);
                        check(StationLaunchPolicy.eligible(room, host) == allowed, "v2 launch respects real first barrier and retained engine");
                        check(StationLaunchPolicy.key(room).equals("synthetic:7"), "attachment state never changes match launch key");
                    }
                }
            }
            JSONObject legacy = new JSONObject().put("state", phase).put("transport", "relay-wss-v1");
            for (boolean host : new boolean[]{false, true})
                check(StationLaunchPolicy.eligible(legacy, host) == StationLaunchPolicy.eligible(phase, host), "v1 launch policy preserved");
        }
    }
    private static void testFrames() throws Exception {
        for (int type = 1; type <= 13; type++) {
            byte[] payload = type == StationRecoveryWire.DATA ? new byte[]{1, 2, 3} : new byte[0];
            StationRecoveryWire frame = new StationRecoveryWire(type, 11, type == StationRecoveryWire.DATA ? 0 : 12, payload);
            byte[] encoded = frame.encode();
            StationRecoveryWire parsed = StationRecoveryWire.decode(ByteBuffer.wrap(encoded));
            check(parsed.type == type && parsed.offset == 11 && Arrays.equals(parsed.data, payload), "opcode round trip " + type);
            check(Arrays.equals(encoded, parsed.encode()), "exact framing bytes " + type);
        }
        byte[] control = new StationRecoveryWire(StationRecoveryWire.PING, 5, 0).encode();
        reject(() -> decode(Arrays.copyOf(control, 23)), "short header");
        reject(() -> decode(Arrays.copyOf(control, 25)), "payload on control");
        byte[] badMagic = control.clone(); badMagic[0] = 0;
        reject(() -> decode(badMagic), "wrong magic");
        for (int reserved = 5; reserved <= 7; reserved++) {
            byte[] badReserved = control.clone(); badReserved[reserved] = 1;
            reject(() -> decode(badReserved), "reserved header bit");
        }
        for (int opcode : new int[]{0, 14, 255}) {
            byte[] badType = control.clone(); badType[4] = (byte) opcode;
            reject(() -> decode(badType), "unknown opcode");
        }
        reject(() -> decode(new StationRecoveryWire(StationRecoveryWire.PING, -1, 0).encode()), "negative offset");
        reject(() -> decode(new StationRecoveryWire(StationRecoveryWire.PING, 0, -1).encode()), "negative value");
        reject(() -> decode(new StationRecoveryWire(StationRecoveryWire.DATA, 0, 0).encode()), "empty DATA");
        reject(() -> decode(new StationRecoveryWire(StationRecoveryWire.DATA, 0, 1, new byte[]{1}).encode()), "DATA control value");
        reject(() -> decode(new StationRecoveryWire(StationRecoveryWire.DATA, 0, 0, new byte[16385]).encode()), "oversized DATA");
        byte[] maximum = new StationRecoveryWire(StationRecoveryWire.DATA, 0, 0, new byte[16384]).encode();
        check(StationRecoveryWire.decode(ByteBuffer.wrap(maximum)).data.length == 16384, "maximum DATA accepted");
        ByteBuffer slice = ByteBuffer.allocate(control.length + 8); slice.position(4); slice.put(control); slice.flip(); slice.position(4);
        check(StationRecoveryWire.decode(slice).type == StationRecoveryWire.PING && slice.position() == 4, "decode respects slice and caller position");
    }
    private static void testLedger() throws Exception {
        for (int capacity : new int[]{32767, 1048577}) {
            try { new StationRecoveryWire.Bytes(capacity); throw new AssertionError("Invalid capacity accepted"); }
            catch (IllegalArgumentException expected) { checks++; }
        }
        StationRecoveryWire.Bytes bytes = new StationRecoveryWire.Bytes(32768);
        check(bytes.capacity() == 32768 && bytes.pending() == 0 && bytes.credit() == 32768, "fixed empty window");
        byte[] first = new byte[16384], second = new byte[16384]; Arrays.fill(first, (byte) 3); Arrays.fill(second, (byte) 7);
        bytes.append(0, first); bytes.append(16384, second);
        check(bytes.next == 32768 && bytes.pending() == 32768 && bytes.credit() == 0, "full window stops growth");
        check(Arrays.equals(bytes.read(0), first) && Arrays.equals(bytes.read(16384), second), "retained bytes exact");
        bytes.append(0, first);
        check(bytes.next == 32768 && bytes.pending() == 32768, "replay never duplicates accepted bytes");
        reject(() -> bytes.append(32768, new byte[]{1}), "no credit until actual delivery ACK");
        reject(() -> bytes.append(32769, new byte[]{1}), "offset gap");
        reject(() -> bytes.append(32767, new byte[]{7, 7}), "partially new overlap");
        byte[] changed = first.clone(); changed[23]++;
        reject(() -> bytes.append(0, changed), "divergent retained replay");
        reject(() -> bytes.confirm(32769), "ACK beyond accepted prefix");
        bytes.confirm(16384);
        check(bytes.pending() == 16384 && bytes.credit() == 16384, "delivery returns bounded credit");
        bytes.append(0, changed);
        check(bytes.next == 32768, "already delivered prefix is never delivered twice");
        reject(() -> bytes.confirm(1), "ACK regression");
        reject(() -> bytes.read(0), "reading reclaimed prefix");
        bytes.append(32768, first);
        check(bytes.pending() == 32768 && Arrays.equals(bytes.read(32768), first), "ring wraps while retaining bytes exactly");
        bytes.confirm(49152);
        check(bytes.pending() == 0 && bytes.credit() == 32768 && bytes.read(49152).length == 0, "all real TCP delivery acknowledged");
        reject(() -> bytes.append(49152, new byte[0]), "empty append");
        reject(() -> bytes.append(49152, new byte[16385]), "oversized append");
    }
    public static void main(String[] args) throws Exception {
        testLaunch(); testFrames(); testLedger();
        System.out.println("StationRecoveryStateWireTest: " + checks + " checks passed");
    }
}
