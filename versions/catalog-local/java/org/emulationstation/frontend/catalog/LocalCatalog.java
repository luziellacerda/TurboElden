package org.emulationstation.frontend.catalog;

import android.content.Context;
import java.io.IOException;
import java.io.InputStream;

/** Asset access happens on the existing HttpBridge worker, never on the UI thread. */
public final class LocalCatalog {
    private LocalCatalog() {}

    public static byte[] read(Context context) throws IOException {
        if (context == null) throw new IOException("Contexto do catalogo local indisponivel.");
        try (InputStream input = context.getAssets().open(CatalogData.ASSET)) {
            return CatalogData.readVerified(input);
        }
    }
}
