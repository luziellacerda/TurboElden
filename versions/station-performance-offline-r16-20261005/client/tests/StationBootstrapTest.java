package org.emulationstation.frontend.station;

import java.io.IOException;
import java.io.InputStream;
import java.io.ByteArrayInputStream;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;

public final class StationBootstrapTest {
    private static int checks;
    private interface Action { void run() throws Exception; }
    private static void check(boolean value,String message) { checks++;if(!value)throw new AssertionError(message); }
    private static void refused(Action action,String reason)throws Exception {
        try { action.run();throw new AssertionError("Expected refusal"); }
        catch(StationStorage.Failure failure){check(failure.reason.equals(reason),"Precise storage failure");}
    }
    public static void main(String[] args)throws Exception {
        Path fixture=Paths.get(args[0]).toAbsolutePath();Files.createDirectories(fixture);
        Path fresh=fixture.resolve("first-install/EmulationStation/roms");
        check(!Files.exists(fresh),"Fresh install begins without folders");
        Path root=StationStorage.prepareRoot(fresh);
        check(root.equals(fresh.toRealPath()),"Missing nested root created and resolved");
        check(Files.isDirectory(root),"Root is directory");
        check(StationStorage.usableBytes(root)>0,"Existing root has measurable usable space");
        try{StationStorage.usableBytes(root.resolve("absent"));throw new AssertionError("Space queried for absent directory");}
        catch(NotDirectoryException expected){check(true,"Space query requires existing directory");}
        try(java.util.stream.Stream<Path> children=Files.list(root)) { check(children.count()==0,"Write probe leaves no file"); }
        byte[] save={1,2,3,4};Path existing=root.resolve("existing-save.srm");Files.write(existing,save);
        check(StationStorage.prepareRoot(fresh).equals(root),"Second start uses same root");
        check(Arrays.equals(save,Files.readAllBytes(existing)),"Existing save preserved");
        Path privateReceipts=fixture.resolve("fresh-private/station-v2/installs");
        StationInstaller installer=new StationInstaller(root,privateReceipts,(file,sink,cancel)->{throw new IOException("Unused fixture reader");});
        check(Files.isDirectory(privateReceipts),"Fresh private receipts created");
        StationInstaller.directory(root.resolve(".station-v2/staging"));
        check(Files.isDirectory(root.resolve(".station-v2/staging")),"Fresh download staging created");
        Path conflict=fixture.resolve("file-instead-of-folder");Files.write(conflict,"preserve".getBytes(StandardCharsets.UTF_8));
        refused(()->StationStorage.prepareRoot(conflict),"STORAGE_PATH_CONFLICT");
        check(new String(Files.readAllBytes(conflict),StandardCharsets.UTF_8).equals("preserve"),"Conflicting file preserved");
        refused(()->StationStorage.prepareRoot(Paths.get("relative/roms")),"STORAGE_PREPARATION_FAILED");
        refused(()->StationStorage.prepareRoot(null),"STORAGE_PREPARATION_FAILED");
        refused(()->StationStorage.prepareRoot(fixture.getRoot()),"STORAGE_PREPARATION_FAILED");
        Path recovered=fixture.resolve("recovered/roms");
        check(Files.isDirectory(StationStorage.prepareRoot(recovered)),"Preparation succeeds after prior failures");
        StationBundledFiles.Source bundle=new StationBundledFiles.Source(){
            public String[] list(String name){return name.equals("resources")?new String[]{"font.bin","image.bin"}:new String[0];}
            public InputStream open(String name)throws IOException{
                if(!name.equals("resources/font.bin")&&!name.equals("resources/image.bin"))throw new IOException("Missing asset");
                return new ByteArrayInputStream(new byte[]{10,20,30});
            }
        };
        Path resources=fixture.resolve("fresh-resources");
        check(StationBundledFiles.install(bundle,"resources",resources,false)==2,"Packaged files install on a fresh root");
        check(StationBundledFiles.install(bundle,"resources",resources,false)==0,"Existing packaged files are reused");
        Files.write(resources.resolve("font.bin"),new byte[]{42});
        check(StationBundledFiles.install(bundle,"resources",resources,false)==0&&Files.readAllBytes(resources.resolve("font.bin"))[0]==42,"Non-replacing mode preserves custom files");
        Files.delete(resources.resolve("image.bin"));
        check(StationBundledFiles.install(bundle,"resources",resources,false)==1&&Files.size(resources.resolve("image.bin"))==3,"Missing resource restored despite prior installation");
        Files.write(resources.resolve("image.bin"),new byte[0]);
        check(StationBundledFiles.install(bundle,"resources",resources,false)==1,"Empty resource restored");
        Files.write(resources.resolve("user-save.srm"),save);
        check(StationBundledFiles.install(bundle,"resources",resources,true)==2,"New package updates its own resources");
        check(Arrays.equals(save,Files.readAllBytes(resources.resolve("user-save.srm"))),"Package update preserves user additions");
        StationBundledFiles.Source broken=new StationBundledFiles.Source(){
            public String[] list(String name){return new String[0];}
            public InputStream open(String name){return new InputStream(){public int read()throws IOException{throw new IOException("Interrupted asset copy");}};}
        };
        try{StationBundledFiles.install(broken,"resources/font.bin",resources.resolve("font.bin"),true);throw new AssertionError("Copy error accepted");}
        catch(IOException expected){check(Files.size(resources.resolve("font.bin"))==3,"Failed copy preserves previous resource");}
        try(java.util.stream.Stream<Path> children=Files.list(resources)){check(children.noneMatch(p->p.getFileName().toString().startsWith(".station-resource-")),"Resource copy removes its temporary file");}
        System.out.println("PASS "+checks+" fresh-install storage bootstrap checks");
    }
}
