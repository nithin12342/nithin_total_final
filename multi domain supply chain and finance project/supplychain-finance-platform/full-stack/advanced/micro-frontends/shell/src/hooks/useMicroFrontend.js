import { useState, useEffect, useCallback } from 'react';

/**
 * Custom Hook for Micro-Frontend Management
 * 
 * This hook demonstrates advanced React patterns and micro-frontend orchestration:
 * 
 * - Dynamic module loading
 * - Error handling and resilience
 * - State management across micro-frontends
 * - Performance optimization
 * - Security considerations
 * - Real-time communication
 */
export const useMicroFrontend = () => {
  const [microFrontends, setMicroFrontends] = useState(new Map());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState({});

  /**
   * Load a micro-frontend dynamically
   * @param {string} name - Name of the micro-frontend
   * @param {string} url - URL of the micro-frontend
   * @param {Object} options - Loading options
   */
  const loadMicroFrontend = useCallback(async (name, url, options = {}) => {
    try {
      setLoading(true);
      setError(null);

      // Check if micro-frontend is already loaded
      if (microFrontends.has(name)) {
        console.log(`Micro-frontend ${name} already loaded`);
        return microFrontends.get(name);
      }

      // Validate URL
      if (!url || !isValidUrl(url)) {
        throw new Error(`Invalid URL for micro-frontend ${name}: ${url}`);
      }

      // Load the micro-frontend script
      const script = await loadScript(url, options);
      
      // Get the module from window object (Module Federation)
      const module = window[name];
      
      if (!module) {
        throw new Error(`Micro-frontend ${name} not found in window object`);
      }

      // Initialize the micro-frontend
      const microFrontend = {
        name,
        url,
        module,
        script,
        loadedAt: new Date().toISOString(),
        status: 'loaded'
      };

      // Store in state
      setMicroFrontends(prev => new Map(prev).set(name, microFrontend));
      setStatus(prev => ({ ...prev, [name]: 'loaded' }));

      console.log(`Successfully loaded micro-frontend: ${name}`);
      return microFrontend;

    } catch (err) {
      console.error(`Failed to load micro-frontend ${name}:`, err);
      setError(err);
      setStatus(prev => ({ ...prev, [name]: 'error' }));
      throw err;
    } finally {
      setLoading(false);
    }
  }, [microFrontends]);

  /**
   * Unload a micro-frontend
   * @param {string} name - Name of the micro-frontend to unload
   */
  const unloadMicroFrontend = useCallback((name) => {
    try {
      const microFrontend = microFrontends.get(name);
      
      if (!microFrontend) {
        console.warn(`Micro-frontend ${name} not found`);
        return;
      }

      // Remove script from DOM
      if (microFrontend.script && microFrontend.script.parentNode) {
        microFrontend.script.parentNode.removeChild(microFrontend.script);
      }

      // Remove from window object
      if (window[name]) {
        delete window[name];
      }

      // Remove from state
      setMicroFrontends(prev => {
        const newMap = new Map(prev);
        newMap.delete(name);
        return newMap;
      });

      setStatus(prev => {
        const newStatus = { ...prev };
        delete newStatus[name];
        return newStatus;
      });

      console.log(`Successfully unloaded micro-frontend: ${name}`);

    } catch (err) {
      console.error(`Failed to unload micro-frontend ${name}:`, err);
      setError(err);
    }
  }, [microFrontends]);

  /**
   * Reload a micro-frontend
   * @param {string} name - Name of the micro-frontend to reload
   */
  const reloadMicroFrontend = useCallback(async (name) => {
    try {
      const microFrontend = microFrontends.get(name);
      
      if (!microFrontend) {
        throw new Error(`Micro-frontend ${name} not found`);
      }

      // Unload first
      unloadMicroFrontend(name);

      // Wait a bit for cleanup
      await new Promise(resolve => setTimeout(resolve, 100));

      // Reload with cache busting
      const urlWithCacheBust = `${microFrontend.url}?t=${Date.now()}`;
      return await loadMicroFrontend(name, urlWithCacheBust);

    } catch (err) {
      console.error(`Failed to reload micro-frontend ${name}:`, err);
      setError(err);
      throw err;
    }
  }, [microFrontends, unloadMicroFrontend, loadMicroFrontend]);

  /**
   * Get micro-frontend by name
   * @param {string} name - Name of the micro-frontend
   */
  const getMicroFrontend = useCallback((name) => {
    return microFrontends.get(name);
  }, [microFrontends]);

  /**
   * Check if micro-frontend is loaded
   * @param {string} name - Name of the micro-frontend
   */
  const isMicroFrontendLoaded = useCallback((name) => {
    return microFrontends.has(name) && status[name] === 'loaded';
  }, [microFrontends, status]);

  /**
   * Get all loaded micro-frontends
   */
  const getAllMicroFrontends = useCallback(() => {
    return Array.from(microFrontends.values());
  }, [microFrontends]);

  /**
   * Clear all micro-frontends
   */
  const clearAllMicroFrontends = useCallback(() => {
    const names = Array.from(microFrontends.keys());
    names.forEach(name => unloadMicroFrontend(name));
  }, [microFrontends, unloadMicroFrontend]);

  /**
   * Health check for all micro-frontends
   */
  const healthCheck = useCallback(async () => {
    const healthStatus = {};
    
    for (const [name, mf] of microFrontends) {
      try {
        // Check if module is still available
        const isHealthy = window[name] && typeof window[name] === 'object';
        healthStatus[name] = {
          healthy: isHealthy,
          lastCheck: new Date().toISOString(),
          loadedAt: mf.loadedAt
        };
      } catch (err) {
        healthStatus[name] = {
          healthy: false,
          error: err.message,
          lastCheck: new Date().toISOString(),
          loadedAt: mf.loadedAt
        };
      }
    }

    return healthStatus;
  }, [microFrontends]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearAllMicroFrontends();
    };
  }, [clearAllMicroFrontends]);

  return {
    // State
    microFrontends: getAllMicroFrontends(),
    loading,
    error,
    status,
    
    // Actions
    loadMicroFrontend,
    unloadMicroFrontend,
    reloadMicroFrontend,
    getMicroFrontend,
    isMicroFrontendLoaded,
    clearAllMicroFrontends,
    healthCheck,
    
    // Computed
    isMicroFrontendLoading: loading,
    microFrontendError: error,
    loadedCount: microFrontends.size,
  };
};

/**
 * Load a script dynamically
 * @param {string} url - Script URL
 * @param {Object} options - Loading options
 */
const loadScript = (url, options = {}) => {
  return new Promise((resolve, reject) => {
    // Check if script is already loaded
    const existingScript = document.querySelector(`script[src="${url}"]`);
    if (existingScript) {
      resolve(existingScript);
      return;
    }

    const script = document.createElement('script');
    script.src = url;
    script.type = 'text/javascript';
    script.async = options.async !== false;
    script.defer = options.defer || false;
    script.crossOrigin = options.crossOrigin || 'anonymous';
    
    // Add integrity check if provided
    if (options.integrity) {
      script.integrity = options.integrity;
    }

    script.onload = () => {
      console.log(`Script loaded: ${url}`);
      resolve(script);
    };

    script.onerror = (error) => {
      console.error(`Failed to load script: ${url}`, error);
      reject(new Error(`Failed to load script: ${url}`));
    };

    // Add timeout
    const timeout = options.timeout || 30000; // 30 seconds default
    setTimeout(() => {
      if (!script.onload) {
        reject(new Error(`Script load timeout: ${url}`));
      }
    }, timeout);

    document.head.appendChild(script);
  });
};

/**
 * Validate URL
 * @param {string} url - URL to validate
 */
const isValidUrl = (url) => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

/**
 * Hook for micro-frontend communication
 */
export const useMicroFrontendCommunication = () => {
  const [messages, setMessages] = useState([]);
  const [subscribers, setSubscribers] = useState(new Map());

  /**
   * Subscribe to messages from a specific micro-frontend
   * @param {string} source - Source micro-frontend name
   * @param {Function} callback - Callback function
   */
  const subscribe = useCallback((source, callback) => {
    if (!subscribers.has(source)) {
      subscribers.set(source, new Set());
    }
    subscribers.get(source).add(callback);

    return () => {
      const callbacks = subscribers.get(source);
      if (callbacks) {
        callbacks.delete(callback);
        if (callbacks.size === 0) {
          subscribers.delete(source);
        }
      }
    };
  }, [subscribers]);

  /**
   * Publish a message to all subscribers
   * @param {string} source - Source micro-frontend name
   * @param {string} type - Message type
   * @param {any} payload - Message payload
   */
  const publish = useCallback((source, type, payload) => {
    const message = {
      id: `${source}-${Date.now()}-${Math.random()}`,
      source,
      type,
      payload,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev.slice(-99), message]); // Keep last 100 messages

    // Notify subscribers
    const callbacks = subscribers.get(source);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(message);
        } catch (error) {
          console.error(`Error in message callback for ${source}:`, error);
        }
      });
    }
  }, [subscribers]);

  /**
   * Send a message to a specific micro-frontend
   * @param {string} target - Target micro-frontend name
   * @param {string} type - Message type
   * @param {any} payload - Message payload
   */
  const sendMessage = useCallback((target, type, payload) => {
    const message = {
      id: `shell-${Date.now()}-${Math.random()}`,
      source: 'shell',
      target,
      type,
      payload,
      timestamp: new Date().toISOString()
    };

    // Send via postMessage if micro-frontend is in iframe
    const iframe = document.querySelector(`iframe[data-micro-frontend="${target}"]`);
    if (iframe && iframe.contentWindow) {
      iframe.contentWindow.postMessage(message, '*');
    }

    // Also store in local messages
    setMessages(prev => [...prev.slice(-99), message]);
  }, []);

  /**
   * Listen for messages from micro-frontends
   */
  useEffect(() => {
    const handleMessage = (event) => {
      // Validate message origin in production
      if (process.env.NODE_ENV === 'production') {
        // Add origin validation logic here
      }

      if (event.data && event.data.source && event.data.source !== 'shell') {
        const message = {
          ...event.data,
          timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev.slice(-99), message]);

        // Notify subscribers
        const callbacks = subscribers.get(event.data.source);
        if (callbacks) {
          callbacks.forEach(callback => {
            try {
              callback(message);
            } catch (error) {
              console.error(`Error in message callback for ${event.data.source}:`, error);
            }
          });
        }
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [subscribers]);

  return {
    messages,
    subscribe,
    publish,
    sendMessage,
  };
};

export default useMicroFrontend;
