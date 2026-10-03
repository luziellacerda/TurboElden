"""Overrides actually consumed by Android NativeActivity.loadNativeCode."""
def overrides(bridge):
    text=''
    for method,helper in [('getFilesDir','filesDir'),('getCacheDir','cacheDir')]:
        text+=f'''
.method public {method}()Ljava/io/File;
    .locals 2
    invoke-static {{p0}}, Lorg/emulationstation/frontend/{bridge};->{helper}(Landroid/content/Context;)Ljava/lang/String;
    move-result-object v0
    new-instance v1, Ljava/io/File;
    invoke-direct {{v1, v0}}, Ljava/io/File;-><init>(Ljava/lang/String;)V
    return-object v1
.end method
'''
    return text+f'''
.method public getExternalFilesDir(Ljava/lang/String;)Ljava/io/File;
    .locals 1
    invoke-static {{p0, p1}}, Lorg/emulationstation/frontend/{bridge};->externalDirectory(Landroid/content/Context;Ljava/lang/String;)Ljava/io/File;
    move-result-object v0
    return-object v0
.end method
'''
