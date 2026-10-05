package org.emulationstation.frontend.station;

import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;

/** Prepares an application-selected root, including on the first installation. */
public final class StationStorage {
    private StationStorage() {}

    /** Android denies Files.getFileStore(); File queries available space through statvfs. */
    public static long usableBytes(Path directory) throws IOException {
        StationInstaller.checkParents(directory);
        if (!Files.isDirectory(directory, LinkOption.NOFOLLOW_LINKS))
            throw new NotDirectoryException("Storage space requires an existing directory");
        return directory.toFile().getUsableSpace();
    }

    public static final class Failure extends IOException {
        public final String reason;
        public final String userMessage;
        private Failure(String reason, String message, Exception cause) {
            super(reason, cause); this.reason=reason; this.userMessage=message;
        }
    }

    public static Path prepareRoot(Path supplied) throws Failure {
        try {
            if (supplied==null || !supplied.isAbsolute() || supplied.getParent()==null)
                throw new IOException("Invalid application storage root");
            Path target=supplied.normalize();
            if (target.getParent()==null) throw new IOException("Invalid application storage root");
            // Only the root supplied by the application may contain an OS alias (/sdcard,
            // /storage/emulated/0, etc.). Never use this method for catalog/archive paths.
            // toRealPath() alone fails when a fresh installation has no games directory.
            Path ancestor=target;
            while (true) {
                try { Files.readAttributes(ancestor, BasicFileAttributes.class, LinkOption.NOFOLLOW_LINKS); break; }
                catch (NoSuchFileException absent) {
                    ancestor=ancestor.getParent();
                    if (ancestor==null) throw absent;
                }
            }
            Path canonical=ancestor.toRealPath();
            if (!Files.isDirectory(canonical, LinkOption.NOFOLLOW_LINKS))
                throw new NotDirectoryException("Application storage ancestor is not a directory");
            Path root=StationInstaller.directory(canonical.resolve(ancestor.relativize(target)));
            if (!Files.isDirectory(root, LinkOption.NOFOLLOW_LINKS))
                throw new NotDirectoryException("Application storage root is not a directory");
            // Test actual access instead of trusting a permission flag or mkdirs return.
            Path probe=Files.createTempFile(root, ".station-write-", ".tmp");
            Files.delete(probe);
            return root;
        } catch (AccessDeniedException | SecurityException denied) {
            throw new Failure("STORAGE_ACCESS_DENIED",
                "Permita o acesso aos arquivos nas configurações do Android e volte ao aplicativo para preparar a pasta de jogos.", denied);
        } catch (NotDirectoryException | FileAlreadyExistsException conflict) {
            throw new Failure("STORAGE_PATH_CONFLICT",
                "Há um arquivo ocupando o caminho da pasta de jogos. Seus arquivos foram preservados; libere esse caminho e tente novamente.", conflict);
        } catch (IOException | InvalidPathException failed) {
            throw new Failure("STORAGE_PREPARATION_FAILED",
                "Não foi possível preparar a pasta de jogos. Confira o armazenamento disponível e a permissão de acesso aos arquivos e tente novamente.", failed);
        }
    }
}
