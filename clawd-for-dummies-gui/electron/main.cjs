const { app, BrowserWindow, ipcMain, Menu, dialog } = require('electron');
const path = require('path');
const { spawn, spawnSync } = require('child_process');
const fs = require('fs');

// Log startup
console.log('=== ClawdForDummies GUI Starting ===');
console.log('NODE_ENV:', process.env.NODE_ENV);
console.log('Electron version:', process.versions.electron);
console.log('Node version:', process.versions.node);
console.log('__dirname:', __dirname);

// Track if error dialog has been shown to prevent duplicates
let errorDialogShown = false;
let appIsReady = false;

// Catch unhandled errors - only show dialog if app is ready
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
  if (appIsReady && !errorDialogShown) {
    errorDialogShown = true;
    try {
      dialog.showErrorBox('Application Error', 
        'An unexpected error occurred.\n\n' +
        'Error: ' + error.message
      );
    } catch (e) {
      // Dialog failed, just log it
      console.error('Failed to show error dialog:', e);
    }
    app.quit();
  } else {
    // App not ready yet, exit immediately to prevent zombie process
    process.exit(1);
  }
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled rejection:', reason);
});

let mainWindow;
let pythonProcess = null;

/**
 * Finds an available Python executable on the system.
 * Tries 'py' (Windows launcher), 'python', and 'python3' in order.
 * @returns {string|null} - The Python command to use, or null if not found
 */
function findPythonExecutable() {
  // Try common Python executable names in order of preference
  // This order matches Dev_View.bat for consistency
  // 'py' is the Windows Python Launcher (recommended on Windows)
  // 'python' is common on all platforms
  // 'python3' is common on macOS/Linux
  const candidates = ['py', 'python', 'python3'];
  
  for (const cmd of candidates) {
    try {
      const result = spawnSync(cmd, ['--version'], { 
        encoding: 'utf-8',
        timeout: 5000,
        windowsHide: true
      });
      if (result.status === 0) {
        console.log(`Found Python executable: ${cmd}`);
        return cmd;
      }
    } catch (e) {
      // Command not found or other error, try next
      console.log(`Python candidate '${cmd}' not available: ${e.message}`);
    }
  }
  
  return null;
}

// Sentinel value to indicate Python search has not been performed yet
const PYTHON_NOT_CHECKED = Symbol('PYTHON_NOT_CHECKED');
// Cache the Python executable once found (or null if not found)
let pythonCommand = PYTHON_NOT_CHECKED;

/**
 * Gets the Python executable, caching the result.
 * @returns {string} - The Python command to use
 * @throws {Error} - If Python is not found
 */
function getPythonCommand() {
  if (pythonCommand === PYTHON_NOT_CHECKED) {
    pythonCommand = findPythonExecutable();
  }
  if (pythonCommand === null) {
    throw new Error(
      'Python is not installed or not in PATH. ' +
      'Please install Python 3.8 or higher from https://python.org'
    );
  }
  return pythonCommand;
}

// SECURITY: Whitelist of allowed module names to prevent command injection
const ALLOWED_MODULES = new Set([
  'port',
  'credential', 
  'config',
  'process',
  'permission',
  'network',
  'clawdbot'
]);

/**
 * Validates and sanitizes module names from IPC input.
 * @param {unknown} modules - Input from renderer process
 * @returns {string[]} - Validated module names
 * @throws {Error} - If input is invalid
 */
function validateModules(modules) {
  if (!Array.isArray(modules)) {
    throw new Error('Invalid input: modules must be an array');
  }
  
  const validated = [];
  for (const module of modules) {
    if (typeof module !== 'string') {
      throw new Error('Invalid input: module names must be strings');
    }
    // Sanitize: only allow alphanumeric and underscore
    const sanitized = module.toLowerCase().replace(/[^a-z0-9_]/g, '');
    if (!ALLOWED_MODULES.has(sanitized)) {
      throw new Error(`Invalid module: ${sanitized}`);
    }
    validated.push(sanitized);
  }
  
  if (validated.length === 0) {
    throw new Error('At least one valid module is required');
  }
  
  return validated;
}

/**
 * Validates export format from IPC input.
 * @param {unknown} format - Input from renderer process
 * @returns {string} - Validated format
 * @throws {Error} - If input is invalid
 */
function validateExportFormat(format) {
  const ALLOWED_FORMATS = new Set(['html', 'json', 'markdown', 'console']);
  
  if (typeof format !== 'string') {
    throw new Error('Invalid input: format must be a string');
  }
  
  const sanitized = format.toLowerCase().replace(/[^a-z]/g, '');
  if (!ALLOWED_FORMATS.has(sanitized)) {
    throw new Error(`Invalid format: ${sanitized}`);
  }
  
  return sanitized;
}

/**
 * Validates export options from IPC input.
 * @param {unknown} options - Input from renderer process
 * @returns {object} - Validated options
 */
function validateExportOptions(options) {
  if (typeof options !== 'object' || options === null) {
    return { filename: 'report.html' };
  }
  
  // Sanitize filename: only allow safe characters
  let filename = 'report.html';
  if (typeof options.filename === 'string') {
    // Remove path traversal attempts, dangerous characters, and absolute path indicators
    filename = options.filename
      .replace(/\.\./g, '')
      .replace(/[<>:"|?*\\/]/g, '')
      .replace(/^[A-Za-z]:/g, '') // Remove Windows drive letters
      .replace(/^\//, '') // Remove Unix absolute path indicator
      .slice(0, 255); // Limit length
    
    // Default to safe name if sanitization resulted in empty string
    if (!filename || filename.trim() === '') {
      filename = 'report.html';
    }
  }
  
  return { filename };
}

function createWindow() {
  // Disable default menu for faster startup (must be after app ready)
  Menu.setApplicationMenu(null);
  
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    backgroundColor: '#0D1117',
    show: true, // Show immediately to debug issues
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false, // Disabled for compatibility - enable once working
      preload: path.join(__dirname, 'preload.cjs'),
      webSecurity: true,
    },
  });
  
  // Log when window is ready to show
  mainWindow.once('ready-to-show', () => {
    console.log('Window is ready to show');
  });
  
  // Log renderer process crashes
  mainWindow.webContents.on('render-process-gone', (event, details) => {
    console.error('Renderer process gone:', details.reason, details.exitCode);
    if (!errorDialogShown) {
      errorDialogShown = true;
      dialog.showErrorBox('Application Crashed', 
        'The application renderer crashed.\n\n' +
        'Reason: ' + details.reason
      );
    }
  });
  
  // Log when DOM is ready
  mainWindow.webContents.on('dom-ready', () => {
    console.log('DOM is ready');
  });
  
  // Log when page finishes loading
  mainWindow.webContents.on('did-finish-load', () => {
    console.log('Page finished loading');
  });

  // Set CSP headers - more permissive for Google Fonts
  mainWindow.webContents.session.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [
          "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; connect-src 'self' http://localhost:*; img-src 'self' data:"
        ],
      },
    });
  });

  // Load the app
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173').catch((err) => {
      console.error('Failed to load development URL:', err);
      if (!errorDialogShown) {
        errorDialogShown = true;
        dialog.showErrorBox('Load Error', 
          'Failed to connect to development server at http://localhost:5173\n\n' +
          'Make sure the Vite dev server is running (npm run dev).'
        );
      }
      app.quit();
    });
    mainWindow.webContents.openDevTools();
  } else {
    const indexPath = path.join(__dirname, '../dist/index.html');
    
    // Check if index.html exists before attempting to load
    if (!fs.existsSync(indexPath)) {
      console.error('Production build not found at:', indexPath);
      if (!errorDialogShown) {
        errorDialogShown = true;
        dialog.showErrorBox('Build Not Found', 
          'The production build was not found.\n\n' +
          'The GUI needs to be built before it can run.\n\n' +
          'Please run "npm run build" in the clawd-for-dummies-gui folder.'
        );
      }
      app.quit();
      return;
    }
    
    mainWindow.loadFile(indexPath).catch((err) => {
      console.error('Failed to load production build:', err);
      if (!errorDialogShown) {
        errorDialogShown = true;
        dialog.showErrorBox('Load Error', 
          'Failed to load the application.\n\n' +
          'Please try rebuilding: npm run build'
        );
      }
      app.quit();
    });
  }

  // Handle page load failures (only show if no error dialog already shown)
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.error('Page failed to load:', errorCode, errorDescription);
    if (!errorDialogShown) {
      errorDialogShown = true;
      dialog.showErrorBox('Load Error', 
        'Failed to load the application.\n\n' +
        'Error code: ' + errorCode
      );
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
    if (pythonProcess) {
      pythonProcess.kill();
      pythonProcess = null;
    }
  });
}

// IPC Handlers
ipcMain.handle('scanner:start', async (event, modules) => {
  // SECURITY: Validate input from renderer process
  let validatedModules;
  try {
    validatedModules = validateModules(modules);
  } catch (error) {
    throw new Error(`Validation failed: ${error.message}`);
  }

  return new Promise((resolve, reject) => {
    // Get Python executable
    let pythonCmd;
    try {
      pythonCmd = getPythonCommand();
    } catch (error) {
      reject(error);
      return;
    }
    
    // SECURITY: Whitelist only essential environment variables for Python subprocess
    const safeEnv = {
      PATH: process.env.PATH,
      PYTHONPATH: process.env.PYTHONPATH,
      PYTHONIOENCODING: 'utf-8',
      PYTHONHOME: process.env.PYTHONHOME,
      HOME: process.env.HOME,
      USERPROFILE: process.env.USERPROFILE, // Windows home directory
      SystemRoot: process.env.SystemRoot, // Windows system root
      TEMP: process.env.TEMP,
      TMP: process.env.TMP,
    };
    
    // Spawn Python scanner process with validated modules
    pythonProcess = spawn(pythonCmd, [
      '-m', 'clawd_for_dummies',
      '--modules', ...validatedModules,
      '--output', 'json'
    ], {
      cwd: path.join(__dirname, '../..'),
      env: safeEnv
    });

    let outputData = '';
    let errorData = '';

    pythonProcess.stdout.on('data', (data) => {
      const chunk = data.toString();
      outputData += chunk;
      
      // Send progress updates (with null check for mainWindow)
      if (mainWindow && !mainWindow.isDestroyed() && chunk.includes('Running')) {
        const match = chunk.match(/Running (.+)\.\.\./);
        if (match) {
          mainWindow.webContents.send('scanner:progress', {
            module: match[1],
            status: 'in_progress'
          });
        }
      }
    });

    pythonProcess.stderr.on('data', (data) => {
      errorData += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code === 0 || code === 1 || code === 2) {
        try {
          // Extract JSON from output
          const jsonMatch = outputData.match(/\{[\s\S]*\}/);
          if (jsonMatch) {
            const result = JSON.parse(jsonMatch[0]);
            // SECURITY: Null check before sending to renderer
            if (mainWindow && !mainWindow.isDestroyed()) {
              mainWindow.webContents.send('scanner:result', result);
            }
            resolve(result);
          } else {
            reject(new Error('No JSON output from scanner'));
          }
        } catch (e) {
          reject(new Error(`Failed to parse scanner output: ${e.message}`));
        }
      } else {
        reject(new Error(errorData || 'Scanner failed'));
      }
      pythonProcess = null;
    });

    pythonProcess.on('error', (error) => {
      pythonProcess = null;
      reject(new Error(`Failed to start scanner: ${error.message}`));
    });
  });
});

ipcMain.handle('scanner:cancel', async () => {
  if (pythonProcess) {
    pythonProcess.kill('SIGTERM');
    pythonProcess = null;
    return true;
  }
  return false;
});

ipcMain.handle('export:generate', async (event, format, options) => {
  // SECURITY: Validate input from renderer process
  let validatedFormat;
  let validatedOptions;
  try {
    validatedFormat = validateExportFormat(format);
    validatedOptions = validateExportOptions(options);
  } catch (error) {
    throw new Error(`Validation failed: ${error.message}`);
  }

  return new Promise((resolve, reject) => {
    // Get Python executable
    let pythonCmd;
    try {
      pythonCmd = getPythonCommand();
    } catch (error) {
      reject(error);
      return;
    }
    
    const args = [
      '-m', 'clawd_for_dummies',
      '--output', validatedFormat,
      '--output-file', validatedOptions.filename
    ];

    // SECURITY: Whitelist only essential environment variables for Python subprocess
    const safeEnv = {
      PATH: process.env.PATH,
      PYTHONPATH: process.env.PYTHONPATH,
      PYTHONIOENCODING: 'utf-8',
      PYTHONHOME: process.env.PYTHONHOME,
      HOME: process.env.HOME,
      USERPROFILE: process.env.USERPROFILE, // Windows home directory
      SystemRoot: process.env.SystemRoot, // Windows system root
      TEMP: process.env.TEMP,
      TMP: process.env.TMP,
    };

    const exportProcess = spawn(pythonCmd, args, {
      cwd: path.join(__dirname, '../..'),
      env: safeEnv
    });

    let errorData = '';

    exportProcess.stderr.on('data', (data) => {
      errorData += data.toString();
    });

    exportProcess.on('close', (code) => {
      if (code === 0) {
        resolve(validatedOptions.filename);
      } else {
        reject(new Error(errorData || 'Export failed'));
      }
    });

    exportProcess.on('error', (error) => {
      reject(new Error(`Failed to start export: ${error.message}`));
    });
  });
});

app.whenReady().then(() => {
  appIsReady = true;
  createWindow();
}).catch((err) => {
  console.error('Failed to create window:', err);
  appIsReady = true; // Set so dialog can show
  if (!errorDialogShown) {
    errorDialogShown = true;
    try {
      dialog.showErrorBox('Startup Error', 
        'Failed to start the application.\n\n' +
        'Please check that all dependencies are installed.'
      );
    } catch (e) {
      console.error('Failed to show error dialog:', e);
    }
  }
  app.quit();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
