package org.emulationstation.frontend.relay.log.spi;

import org.emulationstation.frontend.relay.log.ILoggerFactory;
import org.emulationstation.frontend.relay.log.IMarkerFactory;
import org.emulationstation.frontend.relay.log.LoggerFactory;
import org.emulationstation.frontend.relay.log.MDC;

/**
 * This interface based on {@link java.util.ServiceLoader} paradigm. 
 * 
 * <p>It replaces the old static-binding mechanism used in SLF4J versions 1.0.x to 1.7.x.
 *
 * @author Ceki G&uml;lc&uml;
 * @since 1.8
 */
public interface SLF4JServiceProvider {

    /**
     * Return the instance of {@link ILoggerFactory} that 
     * {@link org.emulationstation.frontend.relay.log.LoggerFactory} class should bind to.
     * 
     * @return instance of {@link ILoggerFactory} 
     */
    public ILoggerFactory getLoggerFactory();

    /**
     * Return the instance of {@link IMarkerFactory} that 
     * {@link org.emulationstation.frontend.relay.log.MarkerFactory} class should bind to.
     * 
     * @return instance of {@link IMarkerFactory} 
     */
    public IMarkerFactory getMarkerFactory();

    /**
     * Return the instance of {@link MDCAdapter} that
     * {@link MDC} should bind to.
     * 
     * @return instance of {@link MDCAdapter} 
     */
    public MDCAdapter getMDCAdapter();

    /**
     * Return the maximum API version for SLF4J that the logging
     * implementation supports.
     *
     * <p>For example: {@code "2.0.1"}.
     *
     * @return the string API version.
     */
    public String getRequestedApiVersion();

    /**
     * Initialize the logging back-end.
     * 
     * <p><b>WARNING:</b> This method is intended to be called once by 
     * {@link LoggerFactory} class and from nowhere else. 
     * 
     */
    public void initialize();
}
