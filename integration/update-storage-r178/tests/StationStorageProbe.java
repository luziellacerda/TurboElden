import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/** USB diagnostic only. Reads free space; no app-data access or mutation. */
public final class StationStorageProbe {
    public static void main(String[] args) throws Exception {
        Path root = Paths.get("/data/local/tmp");
        boolean blocked = false;
        try {
            Files.getFileStore(root).getUsableSpace();
        } catch (SecurityException expected) {
            blocked = "getFileStore".equals(expected.getMessage());
        }
        long usable = root.toFile().getUsableSpace();
        if (!blocked || usable <= 0) throw new IllegalStateException("Unexpected platform storage behavior");
        System.out.println("GET_FILE_STORE_SECURITY_EXCEPTION_CONFIRMED");
        System.out.println("FILE_GET_USABLE_SPACE_SUCCEEDED");
    }
}
