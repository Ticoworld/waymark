const Module = require('node:module')
const path = require('node:path')
const os = require('node:os')

const appRoot = path.resolve(process.argv[2] || '')
const profileRoot = path.resolve(process.argv[3] || '')
const walletId = process.argv[4]
const txHash = '0x42dc0f3efabc9134fc2244f5c01c3b52768ba8d23f29c78d839208afa844e435'
const genesis = '0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606'
if (!appRoot || !profileRoot || !walletId || !profileRoot.includes(`${path.sep}wo07-r8-neuron-profile-real-testnet`)) {
  throw new Error('usage: node inspect-owned-db.js <extracted-neuron-app> <r8-testnet-profile> <wallet-uuid>')
}
process.env.NODE_ENV = 'production'
process.env.WO07_R6_PROFILE_DIR = profileRoot
process.env.NODE_PATH = [path.join(appRoot, 'node_modules'), process.env.NODE_PATH].filter(Boolean).join(path.delimiter)
Module._initPaths()
const electronStub = {
  app: { isPackaged: true, getPath: name => name === 'userData' ? profileRoot : path.join(os.tmpdir(), name), getName: () => 'Neuron-WO07-R9', getVersion: () => '0.204.1', on: () => {}, once: () => {} },
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
  const entity = file => require(path.join(appRoot, `dist/database/chain/entities/${file}`)).default
  const SyncProgress = entity('sync-progress')
  const Input = entity('input')
  const Output = entity('output')
  const Cache = entity('indexer-tx-hash-cache')
  const Transaction = entity('transaction')
  const transaction = await ds.getRepository(Transaction).findOneBy({ hash: txHash })
  const inputs = await ds.getRepository(Input).find({ where: { transactionHash: txHash } })
  const outputs = await ds.getRepository(Output).find({ where: { outPointTxHash: txHash } })
  const caches = await ds.getRepository(Cache).find({ where: { walletId, txHash } })
  const progress = await ds.getRepository(SyncProgress).find({ where: { walletId } })
  process.stdout.write(`${JSON.stringify({
    transaction: transaction && { hash: transaction.hash, blockNumber: transaction.blockNumber, blockHash: transaction.blockHash, status: transaction.status },
    inputs: inputs.map(row => ({ txHash: row.transactionHash, previousHash: row.outPointTxHash, previousIndex: row.outPointIndex, capacity: row.capacity, lockArgs: row.lockArgs, inputIndex: row.inputIndex })),
    outputs: outputs.map(row => ({ txHash: row.outPointTxHash, index: row.outPointIndex, status: row.status, capacity: row.capacity, lockArgs: row.lockArgs })),
    cache: caches.map(row => ({ walletId: row.walletId, txHash: row.txHash, blockNumber: row.blockNumber, isProcessed: row.isProcessed })),
    progressRows: progress.length,
    ownedProgress: progress.filter(row => row.args === '0xa2ade6127fcbb7f1ccfe4a886f6b1e9c5c92d837').map(row => ({ walletId: row.walletId, hash: row.hash, start: row.lightStartBlockNumber, synced: row.syncedBlockNumber, localSaved: row.localSavedBlockNumber, scriptType: row.scriptType })),
  }, null, 2)}\n`)
  await ds.destroy()
}
main().catch(error => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1 })
