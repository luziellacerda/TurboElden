package org.emulationstation.frontend.relay.log.helpers;

import org.emulationstation.frontend.relay.log.ILoggerFactory;
import org.emulationstation.frontend.relay.log.IMarkerFactory;
import org.emulationstation.frontend.relay.log.spi.MDCAdapter;
import org.emulationstation.frontend.relay.log.spi.SLF4JServiceProvider;

public class SubstituteServiceProvider implements SLF4JServiceProvider {
    private final SubstituteLoggerFactory loggerFactory = new SubstituteLoggerFactory();
    private final IMarkerFactory markerFactory = new BasicMarkerFactory();
    private final MDCAdapter mdcAdapter = new BasicMDCAdapter();

    @Override
    public ILoggerFactory getLoggerFactory() {
        return loggerFactory;
    }

    public SubstituteLoggerFactory getSubstituteLoggerFactory() {
        return loggerFactory;
    }

    @Override
    public IMarkerFactory getMarkerFactory() {
        return markerFactory;
    }

    @Override
    public MDCAdapter getMDCAdapter() {
        return mdcAdapter;
    }

    @Override
    public String getRequestedApiVersion() {
        throw new UnsupportedOperationException();
    }

    @Override
    public void initialize() {

    }
}
