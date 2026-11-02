const Module = require('node:module')
const path = require('node:path')
const os = require('node:os')

const appRoot = path.resolve(process.argv[2] || '')
const profileRoot = path.resolve(process.argv[3] || '')
const rpcUrl = process.argv[4] || 'http://127.0.0.1:19110'
const walletId = '1c2d9dbd-4894-4ac6-93bf-b5352acb3eb0'
const txHash = '0x42dc0f3efabc9134fc2244f5c01c3b52768ba8d23f29c78d839208afa844e435'
const scriptHash = '0x28535e1e70eb2ae8c56a829e1f9d3777fdf6b310c9c1dff17e4ae01917e45e62'
const genesis = '0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606'
const handoff = 22944378
if (!appRoot || !profileRoot.includes(`${path.sep}wo07-r12-pending-replay`)) throw new Error('usage: node restart-pending-queue.js <extracted-neuron-app> <r12-pending-profile> [light-rpc-url]')
process.env.NODE_ENV = 'production'
process.env.WO07_R6_PROFILE_DIR = profileRoot
process.env.NODE_PATH = [path.join(appRoot, 'node_modules'), process.env.NODE_PATH].filter(Boolean).join(path.delimiter)
Module._initPaths()
let walletService
const addressTasks = []
process.send = message => {
  if (message.channel === 'check-and-save-wallet-address') addressTasks.push(walletService.checkAndGenerateAddress(message.message))
}
const electronStub = {
  app: { isPackaged: true, getPath: name => name === 'userData' ? profileRoot : path.join(os.tmpdir(), name), getName: () => 'Neuron-WO07-R12', getVersion: () => '0.204.1', on: () => {}, once: () => {} },
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
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms))

async function main() {
  const database = require(path.join(appRoot, 'dist/database/chain/ormconfig'))
  await database.default(genesis)
  const connection = require(path.join(appRoot, 'dist/database/chain/connection'))
  const ds = connection.getConnection('light')
  const entity = name => require(path.join(appRoot, `dist/database/chain/entities/${name}`)).default
  const Cache = entity('indexer-tx-hash-cache')
  const Transaction = entity('transaction')
  const Output = entity('output')
  const Progress = entity('sync-progress')
  const pendingBefore = await ds.getRepository(Cache).find({ where: { walletId, txHash } })
  const transactionsBefore = await ds.getRepository(Transaction).count({ where: { hash: txHash } })
  if (pendingBefore.length !== 1 || pendingBefore[0].isProcessed || transactionsBefore) throw new Error('profile is not at the expected pending-cache restart boundary')

  const NetworkService = require(path.join(appRoot, 'dist/services/networks')).default.getInstance()
  await NetworkService.update('light_client_testnet', { remote: rpcUrl })
  const Wallets = require(path.join(appRoot, 'dist/services/wallets')).default.getInstance()
  walletService = Wallets
  if (!Wallets.get(walletId) || Wallets.getCurrent()?.id !== walletId) throw new Error('real disposable wallet identity missing')
  const Addresses = require(path.join(appRoot, 'dist/services/addresses')).default
  const metas = await Addresses.getAddressesByWalletId(walletId)
  const Queue = require(path.join(appRoot, 'dist/block-sync-renderer/sync/queue')).default
  const queue = new Queue(rpcUrl, metas, 2, false)
  await queue.start()
  const deadline = Date.now() + 90000
  let cache
  let transactions
  let progress
  while (Date.now() < deadline) {
    cache = await ds.getRepository(Cache).findOneBy({ walletId, txHash })
    transactions = await ds.getRepository(Transaction).find({ where: { hash: txHash } })
    progress = await ds.getRepository(Progress).findOneBy({ walletId, hash: scriptHash })
    if (cache?.isProcessed && transactions.length === 1 && progress?.localSavedBlockNumber > handoff) break
    await sleep(300)
  }
  await queue.stopAndWait()
  await Promise.all(addressTasks)
  if (!cache?.isProcessed || transactions?.length !== 1 || progress?.localSavedBlockNumber <= handoff) throw new Error('Neuron Queue did not resume pending cached work')
  const outputs = await ds.getRepository(Output).find({ where: { outPointTxHash: txHash } })
  const live = outputs.filter(row => row.outPointIndex === '0' && row.status === 'live' && row.capacity === '1000000000000')
  if (outputs.length !== 1 || live.length !== 1) throw new Error(`replayed owned output mismatch: ${JSON.stringify(outputs)}`)
  const beforeRestart = { cache: { txHash: cache.txHash, isProcessed: cache.isProcessed }, transaction: transactions.map(row => ({ hash: row.hash, blockNumber: row.blockNumber, blockHash: row.blockHash, status: row.status })), outputs: outputs.map(row => ({ index: row.outPointIndex, capacity: row.capacity, status: row.status })), progress: { synced: progress.syncedBlockNumber, localSaved: progress.localSavedBlockNumber } }
  await ds.destroy()
  await database.default(genesis)
  const reopened = connection.getConnection('light')
  const afterCache = await reopened.getRepository(Cache).findOneBy({ walletId, txHash })
  const afterTx = await reopened.getRepository(Transaction).find({ where: { hash: txHash } })
  const afterOutputs = await reopened.getRepository(Output).find({ where: { outPointTxHash: txHash } })
  const afterProgress = await reopened.getRepository(Progress).findOneBy({ walletId, hash: scriptHash })
  const afterRestart = { cache: { txHash: afterCache.txHash, isProcessed: afterCache.isProcessed }, transaction: afterTx.map(row => ({ hash: row.hash, blockNumber: row.blockNumber, blockHash: row.blockHash, status: row.status })), outputs: afterOutputs.map(row => ({ index: row.outPointIndex, capacity: row.capacity, status: row.status })), progress: { synced: afterProgress.syncedBlockNumber, localSaved: afterProgress.localSavedBlockNumber } }
  if (JSON.stringify(beforeRestart) !== JSON.stringify(afterRestart)) throw new Error('replayed result changed after SQLite reopen')
  process.stdout.write(`${JSON.stringify({ verdict: 'PENDING_CACHE_RESUMED_IN_SIMULATED_RESTART', walletId, txHash, pendingCacheBeforeQueue: pendingBefore.length, missingTransactionRowsBeforeQueue: transactionsBefore, completedCacheAfterQueue: afterCache.isProcessed, transactionRowsAfterQueue: afterTx.length, outputRowsAfterQueue: afterOutputs.length, progress: afterRestart.progress, restartExact: true, addressGenerationCallbacks: addressTasks.length, limitation: 'The pending state was reconstructed in a disposable DB clone from an actual R11 cache row; this was not an OS process kill at the original write boundary.' }, null, 2)}\n`)
  await reopened.destroy()
}
main().catch(error => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1 })
