// ♡ uwu-term ✧ the small, safe bridge between the window and the main process.
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('uwu', {
  config: () => ipcRenderer.invoke('config:get'),
  spawn: (id, cols, rows, cwd) => ipcRenderer.invoke('pty:spawn', id, cols, rows, cwd),
  write: (id, data) => ipcRenderer.send('pty:write', id, data),
  resize: (id, cols, rows) => ipcRenderer.send('pty:resize', id, cols, rows),
  kill: (id) => ipcRenderer.send('pty:kill', id),
  onData: (fn) => ipcRenderer.on('pty:data', (_e, id, data) => fn(id, data)),
  onExit: (fn) => ipcRenderer.on('pty:exit', (_e, id, code) => fn(id, code)),
  onTheme: (fn) => ipcRenderer.on('theme', (_e, t) => fn(t)),
  onWindowState: (fn) => ipcRenderer.on('win:state', (_e, s) => fn(s)),
  copy: (text) => ipcRenderer.send('clip:write', text),
  paste: () => ipcRenderer.invoke('clip:read'),
  openUrl: (url) => ipcRenderer.send('open:url', url),
  minimize: () => ipcRenderer.send('win:minimize'),
  maximize: () => ipcRenderer.send('win:maximize'),
  close: () => ipcRenderer.send('win:close'),
  newWindow: () => ipcRenderer.send('win:new'),
});
