"""One-class Switch configuration path overlay on the exact R131 DEX8.

No game, save, directory or custom path is deleted or moved. Existing launcher,
DOCTYPE check, backup and atomic configuration writer remain byte-identical.
"""
import hashlib

TYPE = "Lorg/emulationstation/frontend/switchengine/SwitchConfigPatcher;"
BASE_DEX_SHA = "1f099e70e5d5220e46fa92d6ac8743f26bd70c63f2ebc99f4316db970cad90a5"
BASE_CLASS_SHA = "ce2c73f546612a7a12012fae19dd7ec2cb8227fbf3668904b307df78ee7c330e"
LEGACY = "SAMBOX-Vfull/sistema/roms/switch"
CANONICAL = "roms/switch"
OLD_BRANCH = '    const-string v9, "' + LEGACY + '"'
NEW_BRANCH = '    const-string v9, "' + CANONICAL + '"'
OLD_CALL = "    :cond_7\n    move v9, v12"
NEW_CALL = """    :cond_7
    invoke-static {p0, v11}, Lorg/emulationstation/frontend/switchengine/SwitchConfigPatcher;->r132MigrateLegacyPath(Ljava/io/File;Lorg/w3c/dom/Element;)Z

    move-result v13

    if-eqz v13, :r132_path_done

    if-nez v9, :r132_path_done

    add-int/lit8 v10, v10, 0x1

    :r132_path_done
    move v9, v12"""

# NOFOLLOW_LINKS retains a link or non-directory at the exact legacy leaf.
# DirectoryStream is lazy: hasNext checks only whether any child exists; it
# never reads or enumerates a game collection. Access/close errors retain it.
METHODS = """
.method private static r132LegacyVacant(Ljava/io/File;)Z
    .locals 7

    const/4 v0, 0x0

    :r132_attributes_start
    invoke-virtual {p0}, Ljava/io/File;->toPath()Ljava/nio/file/Path;
    move-result-object v1
    const/4 v2, 0x1
    new-array v3, v2, [Ljava/nio/file/LinkOption;
    sget-object v4, Ljava/nio/file/LinkOption;->NOFOLLOW_LINKS:Ljava/nio/file/LinkOption;
    aput-object v4, v3, v0
    const-class v4, Ljava/nio/file/attribute/BasicFileAttributes;
    invoke-static {v1, v4, v3}, Ljava/nio/file/Files;->readAttributes(Ljava/nio/file/Path;Ljava/lang/Class;[Ljava/nio/file/LinkOption;)Ljava/nio/file/attribute/BasicFileAttributes;
    move-result-object v4
    invoke-interface {v4}, Ljava/nio/file/attribute/BasicFileAttributes;->isDirectory()Z
    move-result v2
    if-eqz v2, :r132_vacant_return
    invoke-static {v1}, Ljava/nio/file/Files;->newDirectoryStream(Ljava/nio/file/Path;)Ljava/nio/file/DirectoryStream;
    move-result-object v5
    :r132_attributes_end
    .catch Ljava/nio/file/NoSuchFileException; {:r132_attributes_start .. :r132_attributes_end} :r132_vacant_missing
    .catch Ljava/lang/Exception; {:r132_attributes_start .. :r132_attributes_end} :r132_vacant_error

    :r132_stream_start
    invoke-interface {v5}, Ljava/nio/file/DirectoryStream;->iterator()Ljava/util/Iterator;
    move-result-object v6
    invoke-interface {v6}, Ljava/util/Iterator;->hasNext()Z
    move-result v2
    invoke-interface {v5}, Ljava/nio/file/DirectoryStream;->close()V
    :r132_stream_end
    .catchall {:r132_stream_start .. :r132_stream_end} :r132_stream_error
    if-nez v2, :r132_vacant_return
    const/4 v0, 0x1
    return v0

    :r132_stream_error
    move-exception v6
    :r132_close_start
    invoke-interface {v5}, Ljava/nio/file/DirectoryStream;->close()V
    :r132_close_end
    .catch Ljava/lang/Exception; {:r132_close_start .. :r132_close_end} :r132_vacant_error
    return v0

    :r132_vacant_missing
    move-exception v1
    const/4 v0, 0x1
    return v0

    :r132_vacant_error
    move-exception v1
    :r132_vacant_return
    return v0
.end method

.method private static r132MigrateLegacyPath(Ljava/io/File;Lorg/w3c/dom/Element;)Z
    .locals 10

    const/4 v0, 0x0
    invoke-interface {p1}, Lorg/w3c/dom/Element;->getChildNodes()Lorg/w3c/dom/NodeList;
    move-result-object v1
    const/4 v2, 0x0
    const/4 v3, 0x0

    :r132_find_path
    invoke-interface {v1}, Lorg/w3c/dom/NodeList;->getLength()I
    move-result v4
    if-ge v3, v4, :r132_path_found
    invoke-interface {v1, v3}, Lorg/w3c/dom/NodeList;->item(I)Lorg/w3c/dom/Node;
    move-result-object v4
    instance-of v6, v4, Lorg/w3c/dom/Element;
    if-eqz v6, :r132_next_path
    invoke-interface {v4}, Lorg/w3c/dom/Node;->getNodeName()Ljava/lang/String;
    move-result-object v5
    const-string v6, "path"
    invoke-virtual {v6, v5}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    if-eqz v6, :r132_next_path
    if-nez v2, :r132_path_return
    check-cast v4, Lorg/w3c/dom/Element;
    move-object v2, v4
    :r132_next_path
    add-int/lit8 v3, v3, 0x1
    goto :r132_find_path

    :r132_path_found
    if-eqz v2, :r132_path_return
    invoke-interface {v2}, Lorg/w3c/dom/Element;->getAttributes()Lorg/w3c/dom/NamedNodeMap;
    move-result-object v4
    invoke-interface {v4}, Lorg/w3c/dom/NamedNodeMap;->getLength()I
    move-result v4
    if-nez v4, :r132_path_return
    invoke-interface {v2}, Lorg/w3c/dom/Element;->getChildNodes()Lorg/w3c/dom/NodeList;
    move-result-object v4
    invoke-interface {v4}, Lorg/w3c/dom/NodeList;->getLength()I
    move-result v5
    const/4 v6, 0x1
    if-ne v5, v6, :r132_path_return
    invoke-interface {v4, v0}, Lorg/w3c/dom/NodeList;->item(I)Lorg/w3c/dom/Node;
    move-result-object v4
    invoke-interface {v4}, Lorg/w3c/dom/Node;->getNodeType()S
    move-result v4
    const/4 v5, 0x3
    if-eq v4, v5, :r132_plain_path
    const/4 v5, 0x4
    if-ne v4, v5, :r132_path_return

    :r132_plain_path
    new-instance v7, Ljava/io/File;
    const-string v9, "SAMBOX-Vfull/sistema/roms/switch"
    invoke-direct {v7, p0, v9}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V
    invoke-virtual {v7}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;
    move-result-object v9
    invoke-interface {v2}, Lorg/w3c/dom/Element;->getTextContent()Ljava/lang/String;
    move-result-object v4
    invoke-virtual {v9, v4}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v4
    if-eqz v4, :r132_path_return
    invoke-static {v7}, Lorg/emulationstation/frontend/switchengine/SwitchConfigPatcher;->r132LegacyVacant(Ljava/io/File;)Z
    move-result v4
    if-eqz v4, :r132_path_return

    :r132_canonical_start
    new-instance v8, Ljava/io/File;
    const-string v9, "roms/switch"
    invoke-direct {v8, p0, v9}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V
    invoke-virtual {v8}, Ljava/io/File;->toPath()Ljava/nio/file/Path;
    move-result-object v1
    new-array v4, v0, [Ljava/nio/file/attribute/FileAttribute;
    invoke-static {v1, v4}, Ljava/nio/file/Files;->createDirectories(Ljava/nio/file/Path;[Ljava/nio/file/attribute/FileAttribute;)Ljava/nio/file/Path;
    invoke-static {v7}, Lorg/emulationstation/frontend/switchengine/SwitchConfigPatcher;->r132LegacyVacant(Ljava/io/File;)Z
    move-result v4
    if-eqz v4, :r132_path_return
    invoke-virtual {v8}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;
    move-result-object v9
    invoke-interface {v2, v9}, Lorg/w3c/dom/Element;->setTextContent(Ljava/lang/String;)V
    :r132_canonical_end
    .catch Ljava/lang/Exception; {:r132_canonical_start .. :r132_canonical_end} :r132_path_error
    const/4 v0, 0x1
    return v0

    :r132_path_error
    move-exception v1
    :r132_path_return
    return v0
.end method
"""


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def patch(raw):
    if digest(raw) != BASE_CLASS_SHA:
        raise ValueError("Exact unmodified R131 SwitchConfigPatcher smali required")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if text.count(OLD_BRANCH) != 1 or text.count(OLD_CALL) != 1 or "r132" in text:
        raise ValueError("Switch path anchors changed")
    patched = (text.replace(OLD_BRANCH, NEW_BRANCH).replace(OLD_CALL, NEW_CALL) + METHODS).replace("\n", "\r\n").encode("utf-8")
    verify(raw, patched)
    return patched, {"baselineClassSha256": digest(raw), "patchedClassSha256": digest(patched),
        "allowedTypes": [TYPE], "newClassCount": 0, "addedPrivateMethods": 2,
        "newInstallRelativePath": CANONICAL, "exactLegacyRelativePath": LEGACY,
        "migrationTrigger": "existing Switch apply during preparation; never renderer",
        "missingOrEmptyLegacyOnly": True, "anyChildOrLinkOrAccessErrorPreservesLegacy": True,
        "recursiveScan": False, "gameOrDirectoryDeletion": False, "gameOrDirectoryMove": False,
        "legacyMkdirRemoved": True, "atomicConfigWriterPreserved": True,
        "existingSwitchCommandAndEnginePreserved": True, "inverseByteIdentical": True}


def verify(original, patched):
    text = patched.decode("utf-8").replace("\r\n", "\n")
    if not text.endswith(METHODS) or text.count(NEW_BRANCH) != 2 or text.count(NEW_CALL) != 1:
        raise ValueError("Closed Switch path overlay changed")
    inverse = text[:-len(METHODS)].replace(NEW_CALL, OLD_CALL).replace(NEW_BRANCH, OLD_BRANCH).replace("\n", "\r\n").encode("utf-8")
    if inverse != original or digest(original) != BASE_CLASS_SHA:
        raise ValueError("Switch overlay changed any original bytes outside approved anchors")
