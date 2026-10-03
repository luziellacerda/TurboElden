import org.emulationstation.frontend.netplay.NetplayPaths;
import java.io.*;
import java.nio.file.*;
import java.util.*;

public final class NetplayPathsTest {
    static int checks;
    interface Checked {void run()throws Exception;}
    static void check(boolean yes,String name){if(!yes)throw new AssertionError(name);checks++;}
    static void rejects(Checked action,String name)throws Exception{try{action.run();throw new AssertionError(name);}catch(IOException expected){checks++;}}
    public static void main(String[]args)throws Exception{
        Path root=Files.createTempDirectory(Paths.get(args[0]),"paths-fixture-");
        File privateFiles=Files.createDirectories(root.resolve("private")).toFile();
        Path folder=Files.createDirectories(root.resolve("game files"));Path rom=folder.resolve("Example (BR).iso");Files.write(rom,new byte[]{1,2,3});
        String[] paths={rom.toString(),rom.toString(),folder.resolve("removed.iso").toString()};
        File snapshot=NetplayPaths.writeSnapshot(privateFiles,paths);
        check(Arrays.equals(paths,NetplayPaths.readSnapshot(privateFiles,snapshot.getName())),"snapshot roundtrip");
        check(snapshot.isFile(),"read preserves snapshot for lifecycle recreation");
        check(Arrays.equals(paths,NetplayPaths.readSnapshot(privateFiles,snapshot.getName())),"read after recreation");
        check(Arrays.equals(new String[]{folder.toString()},NetplayPaths.installedFolders(paths)),"deduplicate verified folders");
        check(Arrays.equals(new String[]{"content://existing","/user/library",folder.toString()},NetplayPaths.mergeFolders(new String[]{"content://existing","/user/library"},new String[]{folder.toString(),"/user/library"})),"preserve prior paths");
        check(NetplayPaths.installedFolders(new String[0]).length==0,"empty library");
        rejects(()->NetplayPaths.readSnapshot(privateFiles,"../outside.paths"),"traversal rejected");
        rejects(()->NetplayPaths.writeSnapshot(privateFiles,new String[]{"relative.iso"}),"relative write rejected");
        rejects(()->NetplayPaths.installedFolders(new String[]{"relative.iso"}),"relative game rejected");
        rejects(()->NetplayPaths.writeSnapshot(privateFiles,new String[40001]),"count bound");
        File truncated=NetplayPaths.writeSnapshot(privateFiles,paths);try(RandomAccessFile f=new RandomAccessFile(truncated,"rw")){f.setLength(10);}
        rejects(()->NetplayPaths.readSnapshot(privateFiles,truncated.getName()),"truncation rejected");
        File trailing=NetplayPaths.writeSnapshot(privateFiles,paths);try(FileOutputStream f=new FileOutputStream(trailing,true)){f.write(5);}
        rejects(()->NetplayPaths.readSnapshot(privateFiles,trailing.getName()),"trailing bytes rejected");
        NetplayPaths.deleteSnapshot(privateFiles,snapshot.getName());check(!snapshot.exists(),"own snapshot cleanup");check(Files.size(rom)==3,"game untouched");
        System.out.println("PASS NetplayPaths checks="+checks+" fixture="+root);
    }
}
