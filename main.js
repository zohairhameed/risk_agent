const { app, BrowserWindow } = require('electron');

function createWindow() {
  const win = new BrowserWindow({ width: 600, height: 400 });
  win.loadFile('index.html');
}

app.whenReady().then(createWindow);