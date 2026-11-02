const Module = require('node:module')
const path = require('node:path')
const os = require('node:os')

const appRoot = path.resolve(process.argv[2] || '')
const profileRoot = path.resolve(process.argv[3] || '')
const walletId = process.argv[4]
const rpcUrl = process.argv[5]
const handoff = 22944378
const expectedHash = '0x42dc0f3efabc9134fc2244f5c01c3b52768ba8d23f29c78d839208afa844e435'
const genesis = '0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606'
if (!appRoot || !profileRoot || !walletId || !rpcUrl || !profileRoot.includes(`${path.sep}wo07-r8-neuron-profile-real-testnet`)) {
  throw new Error('usage: node owned-sync-baseline.js <extracted-neuron-app> <r8-testnet-profile> <wallet-uuid> <local-light-rpc-url>')
}
process.env.NODE_ENV = 'production'
process.env.WO07_R6_PROFILE_DIR = profileRoot
process.env.NODE_PATH = [path.join(appRoot, 'node_modules'), process.env.NODE_PATH].filter(Boolean).join(path.delimiter)
Module._initPaths()
const electronStub = {
  app: { isPackaged: true, getPath: name => name === 'userData' ? profileRoot : path.join(os.tmpdir(), name), getName: () => 'Neuron-WO07-R9', getVersion: () => '0.204.1', on: () => {}, once: () => {} },
  ipcMain: { on: () => {}, handle: () => {}, removeHandler: () => {} },
  shell: { openExternal: async () => {} }, BrowserWindow: class {},
}
const ipcEvents = []
process.send = message => ipcEvents.push(message)

let syncConnector
const originalLoad = Module._load
Module._load = function (request, parent, isMain) {
  if (request === 'electron') return electronStub
  let resolved
  try { resolved = parent && Module._resolveFilename(request, parent, isMain) } catch {}
  if (resolved === path.join(appRoot, 'dist/block-sync-renderer/index.js')) return { resetSyncTaskQueue: { asyncPush: async () => undefined } }
  if (request === './light-synchronizer' && parent?.filename.endsWith(`${path.sep}sync${path.sep}queue.js`)) {
    return { __esModule: true, default: syncConnector }
  }
  return originalLoad.call(this, request, parent, isMain)
}

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms))
const sortBy = key => (a, b) => String(a[key]).localeCompare(String(b[key]))

async function main() {
  const database = require(path.join(appRoot, 'dist/database/chain/ormconfig'))
  await database.default(genesis)
  const connection = require(path.join(appRoot, 'dist/database/chain/connection'))
  const dataSource = connection.getConnection('light')
  const NetworkService = require(path.join(appRoot, 'dist/services/networks')).default.getInstance()
  if (NetworkService.getCurrent().id !== 'light_client_testnet' || NetworkService.getCurrent().genesisHash !== genesis) throw new Error('R8 profile is not TESTNET')
  await NetworkService.update('light_client_testnet', { remote: rpcUrl })

  const Wallets = require(path.join(appRoot, 'dist/services/wallets')).default.getInstance()
  const wallet = Wallets.get(walletId)
  if (!wallet || Wallets.getCurrent()?.id !== walletId) throw new Error('Neuron wallet ID/current-wallet association mismatch')
  const Addresses = require(path.join(appRoot, 'dist/services/addresses')).default
  const metas = await Addresses.getAddressesByWalletId(walletId)
  const first = metas.find(item => item.addressType === 0 && item.addressIndex === 0)
  if (!first || !first.address.startsWith('ckt')) throw new Error('TESTNET account-0 address missing')
  const scriptObj = first.generateDefaultLockScript()
  const script = { codeHash: scriptObj.codeHash, hashType: scriptObj.hashType, args: scriptObj.args }
  const scriptHash = require('@ckb-lumos/lumos/utils').computeScriptHash(script)
  const WalletUpdate = require(path.join(appRoot, 'dist/services/wallets')).default.getInstance()
  WalletUpdate.update(walletId, { name: wallet.name, startBlockNumber: handoff })
  const SyncProgressService = require(path.join(appRoot, 'dist/services/sync-progress')).default
  await SyncProgressService.deleteWalletSyncProgress(walletId)

  const LightSynchronizer = require(path.join(appRoot, 'dist/block-sync-renderer/sync/light-synchronizer')).default
  const LightRPC = require(path.join(appRoot, 'dist/utils/ckb-rpc')).LightRPC
  const lightRpc = new LightRPC(rpcUrl)
  let rpcQueryCount = 0
  const ranges = []
  const txHashesFromRpc = []
  const originalGetTransactions = lightRpc.getTransactions.bind(lightRpc)
  lightRpc.getTransactions = async (...args) => {
    rpcQueryCount++
    ranges.push(args[0].blockRange)
    const result = await originalGetTransactions(...args)
    txHashesFromRpc.push(...result.txs.map(tx => tx.txHash))
    return result
  }
  const sync = Object.create(LightSynchronizer.prototype)
  sync.lightRpc = lightRpc
  sync.addressMetas = metas
  const scriptsBefore = await lightRpc.getScripts()
  await sync.initSyncProgress()
  const scriptsAfter = await lightRpc.getScripts()
  const nativeOwned = scriptsAfter.find(item => require('@ckb-lumos/lumos/utils').computeScriptHash(item.script) === scriptHash)
  if (!nativeOwned) throw new Error('Neuron did not register its derived Script with the local v0.5.4 client')

  const deadline = Date.now() + 90000
  let cursor = parseInt(nativeOwned.blockNumber)
  while (cursor <= handoff && Date.now() < deadline) {
    await sleep(1000)
    const scripts = await lightRpc.getScripts()
    const current = scripts.find(item => require('@ckb-lumos/lumos/utils').computeScriptHash(item.script) === scriptHash)
    cursor = current ? parseInt(current.blockNumber) : 0
  }
  if (cursor <= handoff) throw new Error(`native Script cursor did not pass H; cursor=${cursor}`)

  const SyncProgress = require(path.join(appRoot, 'dist/database/chain/entities/sync-progress')).default
  const IndexerCache = require(path.join(appRoot, 'dist/database/chain/entities/indexer-tx-hash-cache')).default
  const TransactionEntity = require(path.join(appRoot, 'dist/database/chain/entities/transaction')).default
  const InputEntity = require(path.join(appRoot, 'dist/database/chain/entities/input')).default
  const OutputEntity = require(path.join(appRoot, 'dist/database/chain/entities/output')).default
  const progressAtFloor = await dataSource.getRepository(SyncProgress).findOneBy({ hash: scriptHash })
  if (!progressAtFloor || progressAtFloor.walletId !== walletId || progressAtFloor.syncedBlockNumber !== handoff) throw new Error('Neuron start-height progress row mismatch')

  const scriptStates = await sync.upsertTxHashes()
  const cacheBeforeProgress = await dataSource.getRepository(IndexerCache).find({ where: { walletId } })
  if (!cacheBeforeProgress.some(row => row.txHash === expectedHash)) throw new Error(`expected faucet tx absent from Neuron cache: ${JSON.stringify(txHashesFromRpc)}`)
  await sync.updateSyncedBlockOfScripts(scriptStates)
  const progressAfterDiscovery = await dataSource.getRepository(SyncProgress).findOneBy({ hash: scriptHash })

  const { Subject } = require('rxjs')
  const queueModule = path.join(appRoot, 'dist/block-sync-renderer/sync/queue')
  class CacheConnector {
    constructor(addresses, url) {
      sync.transactionsSubject = new Subject()
      sync.blockTipsSubject = new Subject()
      sync.addressesByWalletId = new Map([[walletId, metas]])
      sync.pollingIndexer = true
      sync.syncMultisig = false
      sync._needGenerateAddress = false
      sync.processNextBlockNumber = async () => undefined
      this.transactionsSubject = sync.transactionsSubject
      this.blockTipsSubject = sync.blockTipsSubject
    }
    async connect() { setTimeout(() => sync.processTxsInNextBlockNumber().catch(error => process.stderr.write(`${error.stack || error}\n`)), 150) }
    async notifyCurrentBlockNumberProcessed(blockNumber) { await sync.notifyCurrentBlockNumberProcessed(blockNumber) }
    stop() { sync.pollingIndexer = false }
  }
  syncConnector = CacheConnector
  const Queue = require(queueModule).default
  const queue = new Queue(rpcUrl, metas, 2, false)
  await queue.start()
  const txDeadline = Date.now() + 90000
  let transactionRows = []
  while (Date.now() < txDeadline) {
    transactionRows = await dataSource.getRepository(TransactionEntity).find({ where: { hash: expectedHash } })
    if (transactionRows.length) break
    await sleep(500)
  }
  if (!transactionRows.length) {
    queue.stop()
    throw new Error('Neuron queue did not persist the confirmed owned TESTNET transaction within 90 seconds')
  }
  await queue.stopAndWait()

  const snapshot = async ds => ({
    transactions: (await ds.getRepository(TransactionEntity).find({ where: { hash: expectedHash } })).map(row => ({ hash: row.hash, blockNumber: row.blockNumber, blockHash: row.blockHash })),
    inputs: (await ds.getRepository(InputEntity).find({ where: { transactionHash: expectedHash } })).map(row => ({ txHash: row.transactionHash, previousHash: row.outPointTxHash, previousIndex: row.outPointIndex, capacity: row.capacity, lockArgs: row.lockArgs })).sort(sortBy('previousHash')),
    outputs: (await ds.getRepository(OutputEntity).find({ where: { outPointTxHash: expectedHash } })).map(row => ({ txHash: row.outPointTxHash, index: row.outPointIndex, status: row.status, capacity: row.capacity, lockArgs: row.lockArgs })).sort((a, b) => a.index - b.index),
    cache: (await ds.getRepository(IndexerCache).find({ where: { walletId, txHash: expectedHash } })).map(row => ({ walletId: row.walletId, txHash: row.txHash, blockNumber: row.blockNumber, isProcessed: row.isProcessed })),
    progress: await (async () => {
      const row = await ds.getRepository(SyncProgress).findOneBy({ hash: scriptHash })
      return row && { walletId: row.walletId, hash: row.hash, start: row.lightStartBlockNumber, synced: row.syncedBlockNumber, localSaved: row.localSavedBlockNumber, scriptType: row.scriptType }
    })(),
  })
  const rowsBeforeRestart = await snapshot(dataSource)
  await dataSource.destroy()
  await database.default(genesis)
  const reopened = connection.getConnection('light')
  const rowsAfterRestart = await snapshot(reopened)
  process.stdout.write(`${JSON.stringify({
    verdict: 'OWNED_NORMAL_SYNC', network: { id: NetworkService.getCurrent().id, genesis },
    walletId, script, scriptHash, address: first.address, handoffHeight: handoff,
    nativeScriptsBefore: scriptsBefore.length, nativeScriptsAfter: scriptsAfter.length,
    nativeCursorAfterFilter: cursor, rpcQueryCount, queriedRanges: [...new Set(ranges.map(range => `${range[0]}..${range[1]}`))],
    txHashesReturned: [...new Set(txHashesFromRpc)], cacheCountBeforeProgress: cacheBeforeProgress.length,
    syncedProgressAfterCacheWrite: progressAfterDiscovery?.syncedBlockNumber,
    beforeRestart: rowsBeforeRestart, afterRestart: rowsAfterRestart,
    restartExact: JSON.stringify(rowsBeforeRestart) === JSON.stringify(rowsAfterRestart), ipcEvents,
    notes: 'Ordinary Neuron sync baseline only. No D2 artifact was imported; no acceleration claim.',
  }, null, 2)}\n`)
  await reopened.destroy()
}

main().catch(error => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1 })
