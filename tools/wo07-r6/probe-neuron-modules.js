const Module = require('node:module')
const path = require('node:path')

const appRoot = path.resolve(process.argv[2] || '')
if (!appRoot) throw new Error('usage: node probe-neuron-modules.js <extracted-neuron-app>')
process.env.NODE_ENV = 'test'

const electronStub = {
  app: {
    isPackaged: true,
    getPath: () => path.join(require('node:os').tmpdir(), 'wo07-r6-electron-stub'),
    getName: () => 'Neuron',
    getVersion: () => '0.204.1',
    on: () => {},
    once: () => {},
    whenReady: () => Promise.resolve(),
  },
  ipcMain: { on: () => {}, handle: () => {}, removeHandler: () => {} },
  shell: { openExternal: async () => {} },
  BrowserWindow: class {},
}
const originalLoad = Module._load
Module._load = function (request, parent, isMain) {
  if (request === 'electron') return electronStub
  return originalLoad.call(this, request, parent, isMain)
}

const originalNodePath = process.env.NODE_PATH
process.env.NODE_PATH = [path.join(appRoot, 'node_modules'), originalNodePath].filter(Boolean).join(path.delimiter)
Module._initPaths()

const checks = [
  ['typeorm', () => require(path.join(appRoot, 'node_modules/typeorm'))],
  ['sqlite3', () => require(path.join(appRoot, 'node_modules/sqlite3'))],
  ['neuron transaction persistor', () => require(path.join(appRoot, 'dist/services/tx/transaction-persistor'))],
  ['neuron light synchronizer', () => require(path.join(appRoot, 'dist/block-sync-renderer/sync/light-synchronizer'))],
  ['neuron transaction queue', () => require(path.join(appRoot, 'dist/block-sync-renderer/sync/queue'))],
  ['neuron sync progress service', () => require(path.join(appRoot, 'dist/services/sync-progress'))],
]

for (const [name, load] of checks) {
  try {
    const value = load()
    process.stdout.write(`${name}: loaded (${Object.keys(value || {}).join(',')})\n`)
  } catch (error) {
    process.stdout.write(`${name}: FAILED ${error.stack || error}\n`)
    break
  }
}
