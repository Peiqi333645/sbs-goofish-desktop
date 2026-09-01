const { app, BrowserWindow, dialog, shell } = require("electron");
const { spawn } = require("child_process");
const fs = require("fs");
const http = require("http");
const net = require("net");
const path = require("path");

let port = 0;
let mainWindow;
let backendProcess;
let quitting = false;

function backendExecutable() {
  return path.join(
    process.resourcesPath,
    "backend",
    process.platform === "win32" ? "sbs-goofish-backend.exe" : "sbs-goofish-backend"
  );
}

function getFreePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.unref();
    server.once("error", reject);
    server.listen({ host: "127.0.0.1", port: 0 }, () => {
      const address = server.address();
      const selectedPort = typeof address === "object" && address ? address.port : 0;
      server.close(error => error ? reject(error) : resolve(selectedPort));
    });
  });
}

function waitForBackend(timeoutMs = 60000) {
  const startedAt = Date.now();
  return new Promise((resolve, reject) => {
    const retry = () => {
      if (Date.now() - startedAt >= timeoutMs) {
        reject(new Error("后台服务启动超时"));
        return;
      }
      setTimeout(check, 500);
    };
    const check = () => {
      const request = http.get(
        { hostname: "127.0.0.1", port, path: "/health", timeout: 1500 },
        response => {
          response.resume();
          response.statusCode === 200 ? resolve() : retry();
        }
      );
      request.on("timeout", () => request.destroy());
      request.on("error", retry);
    };
    check();
  });
}

function startBackend() {
  const executable = backendExecutable();
  if (!fs.existsSync(executable)) {
    throw new Error(`找不到后台程序：${executable}`);
  }
  backendProcess = spawn(executable, [], {
    cwd: app.getPath("userData"),
    env: {
      ...process.env,
      SBS_USER_DATA_DIR: app.getPath("userData"),
      SBS_DESKTOP_EXECUTABLE: executable,
      SERVER_PORT: String(port),
      PLAYWRIGHT_BROWSERS_PATH: path.join(process.resourcesPath, "playwright-browsers"),
      RUN_HEADLESS: "true",
      LOGIN_IS_EDGE: "false",
      PYTHONUTF8: "1",
    },
    windowsHide: true,
    stdio: "ignore",
  });
  backendProcess.on("exit", code => {
    backendProcess = null;
    if (!quitting && code !== 0) {
      dialog.showErrorBox("SBS闲鱼助手", "后台服务意外停止，请重新打开软件。");
    }
  });
}

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1380,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    show: false,
    title: "SBS闲鱼助手 0.1.2",
    backgroundColor: "#191919",
    icon: path.join(__dirname, "build", "icon.png"),
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith(`http://127.0.0.1:${port}`)) return { action: "allow" };
    shell.openExternal(url);
    return { action: "deny" };
  });
  await waitForBackend();
  await mainWindow.webContents.session.clearCache();
  await mainWindow.loadURL(`http://127.0.0.1:${port}/?desktopVersion=0.1.2`);
  mainWindow.show();
}

function stopBackend() {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
}

const lock = app.requestSingleInstanceLock();
if (!lock) {
  app.quit();
} else {
  app.on("second-instance", () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
  app.whenReady().then(async () => {
    try {
      port = await getFreePort();
      startBackend();
      await createWindow();
    } catch (error) {
      stopBackend();
      dialog.showErrorBox(
        "SBS闲鱼助手启动失败",
        `${error.message}\n\n数据目录：${app.getPath("userData")}`
      );
      app.quit();
    }
  });
}

app.on("before-quit", () => {
  quitting = true;
  stopBackend();
});
app.on("window-all-closed", () => app.quit());
