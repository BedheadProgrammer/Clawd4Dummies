const { contextBridge, ipcRenderer } = require('electron');

// Expose type-safe API to renderer
contextBridge.exposeInMainWorld('scanner', {
  startScan: (modules) => ipcRenderer.invoke('scanner:start', modules),
  cancelScan: () => ipcRenderer.invoke('scanner:cancel'),
  onProgress: (callback) => {
    const handler = (_, data) => callback(data);
    ipcRenderer.on('scanner:progress', handler);
    return () => ipcRenderer.removeListener('scanner:progress', handler);
  },
  onResult: (callback) => {
    const handler = (_, data) => callback(data);
    ipcRenderer.on('scanner:result', handler);
    return () => ipcRenderer.removeListener('scanner:result', handler);
  },
});

contextBridge.exposeInMainWorld('exporter', {
  generate: (format, options) => ipcRenderer.invoke('export:generate', format, options),
});
