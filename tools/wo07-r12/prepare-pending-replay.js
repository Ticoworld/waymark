const Module = require('node:module')
const path = require('node:path')
const fs = require('node:fs')
const os = require('node:os')

const appRoot = path.resolve(process.argv[2] || '')
const source = path.resolve(process.argv[3] || '')
const destination = path.resolve(process.argv[4] || '')
const walletId = '1c2d9dbd-4894-4ac6-93bf-b5352acb3eb0'
const txHash = '0x42dc0f3efabc9134fc2244f5c01c3b52768ba8d23f29c78d839208afa844e435'
const scriptHash = '0x28535e1e70eb2ae8c56a829e1f9d3777fdf6b310c9c1dff17e4ae01917e45e62'
const genesis = '0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606'
const handoff = 22944378
if (!appRoot || !source.includes(`${path.sep}wo07-r8-neuron-profile-real-testnet-r11`) || !destination.includes(`${path.sep}wo07-r12-pending-replay`)) {
  throw new Error('usage: node prepare-pending-replay.js <extracted-neuron-app> <completed-r11-profile-copy> <new-r12-pending-profile>')
}
if (fs.existsSync(destination)) throw new Error(`refusing to overwrite disposable destination: ${destination}`)
fs.cpSync(source, destination, { recursive: true, errorOnExist: true })
process.env.NODE_ENV = 'production'
process.env.WO07_R6_PROFILE_DIR = destination
process.env.NODE_PATH = [path.join(appRoot, 'node_modules'), process.env.NODE_PATH].filter(Boolean).join(path.delimiter)
Module._initPaths()
const electronStub = {
  app: { isPackaged: true, getPath: name => name === 'userData' ? destination : path.join(os.tmpdir(), name), getName: () => 'Neuron-WO07-R12', getVersion: () => '0.204.1', on: () => {}, once: () => {} },
  ipcMain: { on: () => {}, handle: () => {}, removeHandler: () => {} }, shell: { openExternal: async () => {} }, BrowserWindow: class {},
}
const originalLoad = Module._load
Module._load = function (request, parent, isMain) {
  if (request === 'electron') return electronStub
  let resolved
  try { resolved = parent && Module._resolveFilename(request, parent, isMain) } catch {}
  if (resolved === path.join(appRoot, 'dist/block-sync-renderer/index.js')) return { resetSyncTaskQueue: { asyncPush: async () => undefined } }
  return originalLoad.call(this, request, parent, isMain)
}

async function main() {
  const database = require(path.join(appRoot, 'dist/database/chain/ormconfig'))
  await database.default(genesis)
  const connection = require(path.join(appRoot, 'dist/database/chain/connection'))
  const ds = connection.getConnection('light')
  const entity = name => require(path.join(appRoot, `dist/database/chain/entities/${name}`)).default
  const Transaction = entity('transaction')
  const Input = entity('input')
  const Output = entity('output')
  const Cache = entity('indexer-tx-hash-cache')
  const TxLock = entity('tx-lock')
  const Description = entity('tx-description')
  const Progress = entity('sync-progress')
  const cached = await ds.getRepository(Cache).find({ where: { walletId, txHash } })
  const txRows = await ds.getRepository(Transaction).find({ where: { hash: txHash } })
  const outputs = await ds.getRepository(Output).find({ where: { outPointTxHash: txHash } })
  if (cached.length !== 1 || !cached[0].isProcessed || txRows.length !== 1 || outputs.length !== 1) {
    throw new Error('source clone is not the completed one-transaction R11 state')
  }
  await ds.getRepository(Transaction).delete({ hash: txHash })
  await ds.getRepository(Input).delete({ transactionHash: txHash })
  await ds.getRepository(Output).delete({ outPointTxHash: txHash })
  await ds.getRepository(TxLock).delete({ transactionHash: txHash })
  await ds.getRepository(Description).delete({ txHash })
  await ds.getRepository(Cache).update({ id: cached[0].id }, { isProcessed: false })
  await ds.getRepository(Progress).update({ walletId, hash: scriptHash }, { localSavedBlockNumber: handoff })
  const pending = await ds.getRepository(Cache).find({ where: { walletId, txHash } })
  const progress = await ds.getRepository(Progress).findOneBy({ walletId, hash: scriptHash })
  const remainingTxs = await ds.getRepository(Transaction).count({ where: { hash: txHash } })
  const remainingOutputs = await ds.getRepository(Output).count({ where: { outPointTxHash: txHash } })
  if (pending.length !== 1 || pending[0].isProcessed || remainingTxs || remainingOutputs || progress.localSavedBlockNumber !== handoff) {
    throw new Error('could not construct the captured cache-durable / app-persistence-pending state')
  }
  process.stdout.write(`${JSON.stringify({ simulatedInterruption: 'cache durable; transaction persistence not complete', profile: destination, walletId, txHash, pendingCacheRows: pending.length, isProcessed: pending[0].isProcessed, transactionRows: remainingTxs, outputRows: remainingOutputs, syncedBlockNumber: progress.syncedBlockNumber, localSavedBlockNumber: progress.localSavedBlockNumber, note: 'Disposable clone only. Reuses an actual R11 cache row and removes completed app rows to recreate the pre-persistence checkpoint; no transaction or cache record is invented.' }, null, 2)}\n`)
  await ds.destroy()
}
main().catch(error => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1 })
