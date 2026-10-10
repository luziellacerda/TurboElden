package org.emulationstation.frontend.station;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** Host proof for aggregate legacy-cache diagnosis; uses synthetic identities only. */
public final class ExistingCoverCacheDiagnosticsTest {
    private static final String COVER="cover_test_1234";
    private static final byte[] PNG=new byte[]{(byte)137,80,78,71,13,10,26,10,1,2,3,4};
    private static int checks;
    private static void check(boolean value,String message){checks++;if(!value)throw new AssertionError(message);}
    private static void has(String text,String token){check(text.contains(token),"Missing diagnostic token: "+token);}
    private static void clear(Path root)throws IOException{
        if(!Files.exists(root,LinkOption.NOFOLLOW_LINKS))return;
        Files.walk(root).sorted(Comparator.reverseOrder()).forEach(path->{try{Files.delete(path);}catch(IOException e){throw new UncheckedIOException(e);}});
    }
    private static void table(Path root,String text)throws IOException{
        Files.write(root.resolve("revisions.tsv"),text.getBytes(StandardCharsets.UTF_8));
    }
    public static void main(String[] args)throws Exception{
        Path root=Paths.get(args[0]).toAbsolutePath();clear(root);

        ExistingCoverCache missingDirectory=new ExistingCoverCache(root);
        has(missingDirectory.diagnostics(),"tableStatus=directory-missing");
        check(missingDirectory.exactPath(COVER,7)==null,"Missing directory is cold");
        has(missingDirectory.diagnostics(),"revisionMissing=1");

        Files.createDirectories(root);Files.write(root.resolve(COVER+".png"),PNG);
        ExistingCoverCache missingTable=new ExistingCoverCache(root);
        has(missingTable.diagnostics(),"tableStatus=table-missing");
        has(missingTable.diagnostics(),"indexedImages=1");
        has(missingTable.diagnostics(),"imageWithoutRevision=1");
        check(missingTable.exactPath(COVER,7)==null,"Filename alone never authorizes a legacy image");

        clear(root);Files.createDirectories(root);Files.write(root.resolve(COVER+".png"),PNG);table(root,COVER+"\t6\n");
        ExistingCoverCache mismatch=new ExistingCoverCache(root);
        check(mismatch.exactPath(COVER,7)==null,"Mismatched item revision is rejected");
        has(mismatch.diagnostics(),"revisionMismatch=1");

        clear(root);Files.createDirectories(root);table(root,COVER+"\t7\n");
        ExistingCoverCache absentImage=new ExistingCoverCache(root);
        check(absentImage.exactPath(COVER,7)==null,"Matching table without an image is cold");
        has(absentImage.diagnostics(),"matchingRevisionNoImage=1");
        has(absentImage.diagnostics(),"revisionWithoutImage=1");

        clear(root);Files.createDirectories(root);Files.write(root.resolve(COVER+".PNG"),PNG);table(root,COVER+"\t7\r\n");
        ExistingCoverCache exact=new ExistingCoverCache(root);
        check(exact.exactPath(COVER,7)!=null,"Case-only historical extension variation is accepted after signature proof");
        has(exact.diagnostics(),"accepted=1");
        has(exact.diagnostics(),"tableStatus=parsed");

        clear(root);Files.createDirectories(root);Files.write(root.resolve(COVER+".png"),"not-image".getBytes(StandardCharsets.UTF_8));table(root,COVER+"\t7\n");
        ExistingCoverCache corrupt=new ExistingCoverCache(root);
        check(corrupt.exactPath(COVER,7)==null,"Invalid image signature is rejected");
        has(corrupt.diagnostics(),"fileRejected=1");

        clear(root);Files.createDirectories(root);Files.write(root.resolve(COVER+".png"),PNG);Files.write(root.resolve(COVER+".jpg"),PNG);
        Files.write(root.resolve("cover_other_123.bmp"),PNG);
        table(root,COVER+"\t7\n"+COVER+"\t8\n"+"broken\n");
        ExistingCoverCache conflicts=new ExistingCoverCache(root);
        check(conflicts.exactPath(COVER,7)==null,"Conflicting table/image evidence fails closed");
        String aggregate=conflicts.diagnostics();
        has(aggregate,"tableConflicts=1");has(aggregate,"tableInvalid=1");
        has(aggregate,"imageConflicts=1");has(aggregate,"unsupportedExtensions=1");
        check(!aggregate.contains(COVER)&&!aggregate.contains(root.toString()),"Diagnostics never expose identities or private paths");

        clear(root);System.out.println("PASS "+checks+" aggregate legacy-cover diagnostics checks");
    }
}
