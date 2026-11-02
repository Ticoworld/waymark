const Module = require('node:module')
const path = require('node:path')
const os = require('node:os')

const appRoot = path.resolve(process.argv[2] || '')
const profileRoot = path.resolve(process.argv[3] || '')
const walletId = '1c2d9dbd-4894-4ac6-93bf-b5352acb3eb0'
const rpcUrl = process.argv[4] || 'http://127.0.0.1:19100'
const handoff = 22944378
const expectedHash = '0x42dc0f3efabc9134fc2244f5c01c3b52768ba8d23f29c78d839208afa844e435'
const genesis = '0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606'
if (!appRoot || !profileRoot.includes(`${path.sep}wo07-r8-neuron-profile-real-testnet-r11`)) throw new Error('usage: node recover-app-copy.js <extracted-neuron-app> <prepared-r11-profile> [light-rpc-url]')
process.env.NODE_ENV = 'production'
process.env.WO07_R6_PROFILE_DIR = profileRoot
process.env.NODE_PATH = [path.join(appRoot, 'node_modules'), process.env.NODE_PATH].filter(Boolean).join(path.delimiter)
Module._initPaths()

const pendingAddressTasks = []
const processMessages = []
let walletService
process.send = message => {
  processMessages.push(message)
  if (message.channel === 'check-and-save-wallet-address') pendingAddressTasks.push(walletService.checkAndGenerateAddress(message.message))
}
const electronStub = {
  app: { isPackaged: true, getPath: name => name === 'userData' ? profileRoot : path.join(os.tmpdir(), name), getName: () => 'Neuron-WO07-R11', getVersion: () => '0.204.1', on: () => {}, once: () => {} },
  ipcMain: { on: () => {}, handle: () => {}, removeHandler: () => {} }, shell: { openExternal: async () => {} }, BrowserWindow: class {},
}
let syncConnector
const originalLoad = Module._load
Module._load = function (request, parent, isMain) {
  if (request === 'electron') return electronStub
  let resolved
  try { resolved = parent && Module._resolveFilename(request, parent, isMain) } catch {}
  if (resolved === path.join(appRoot, 'dist/block-sync-renderer/index.js')) return { resetSyncTaskQueue: { asyncPush: async () => undefined } }
  if (request === './light-synchronizer' && parent?.filename.endsWith(`${path.sep}sync${path.sep}queue.js`)) return { __esModule: true, default: syncConnector }
  return originalLoad.call(this, request, parent, isMain)
}

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms))
const scriptHash = '0x28535e1e70eb2ae8c56a829e1f9d3777fdf6b310c9c1dff17e4ae01917e45e62'

async function main() {
  const database = require(path.join(appRoot, 'dist/database/chain/ormconfig'))
  await database.default(genesis)
  const connection = require(path.join(appRoot, 'dist/database/chain/connection'))
  const ds = connection.getConnection('light')
  const NetworkService = require(path.join(appRoot, 'dist/services/networks')).default.getInstance()
  if (NetworkService.getCurrent().id !== 'light_client_testnet' || NetworkService.getCurrent().genesisHash !== genesis) throw new Error('R11 copied profile is not TESTNET Light Client')
  await NetworkService.update('light_client_testnet', { remote: rpcUrl })
  const Wallets = require(path.join(appRoot, 'dist/services/wallets')).default.getInstance()
  walletService = Wallets
  const wallet = Wallets.get(walletId)
  if (!wallet || Wallets.getCurrent()?.id !== walletId) throw new Error('R8 wallet identity/current-wallet mismatch in app copy')
  const Addresses = require(path.join(appRoot, 'dist/services/addresses')).default
  const metas = await Addresses.getAddressesByWalletId(walletId)
  const first = metas.find(item => item.addressType === 0 && item.addressIndex === 0)
  if (!first) throw new Error('account-0 address metadata missing')
  const ownedScript = first.generateDefaultLockScript()
  const script = { codeHash: ownedScript.codeHash, hashType: ownedScript.hashType, args: ownedScript.args }
  const computedScriptHash = require('@ckb-lumos/lumos/utils').computeScriptHash(script)
  if (computedScriptHash !== scriptHash) throw new Error('derived Script identity changed in application copy')
  const walletStart = parseInt(wallet.startBlockNumber)
  if (walletStart !== handoff) throw new Error(`copied wallet start-height mismatch: ${wallet.startBlockNumber}`)

  const SyncProgress = require(path.join(appRoot, 'dist/database/chain/entities/sync-progress')).default
  const IndexerCache = require(path.join(appRoot, 'dist/database/chain/entities/indexer-tx-hash-cache')).default
  const TransactionEntity = require(path.join(appRoot, 'dist/database/chain/entities/transaction')).default
  const InputEntity = require(path.join(appRoot, 'dist/database/chain/entities/input')).default
  const OutputEntity = require(path.join(appRoot, 'dist/database/chain/entities/output')).default
  const LightSynchronizer = require(path.join(appRoot, 'dist/block-sync-renderer/sync/light-synchronizer')).default
  const LightRPC = require(path.join(appRoot, 'dist/utils/ckb-rpc')).LightRPC
  const lightRpc = new LightRPC(rpcUrl)
  const beforeScripts = await lightRpc.getScripts()
  const nativeBefore = beforeScripts.find(item => require('@ckb-lumos/lumos/utils').computeScriptHash(item.script) === scriptHash)
  if (!nativeBefore) throw new Error('R10 native copy does not contain the genuine R8 Script')
  const setScriptCalls = []
  const originalSetScripts = lightRpc.setScripts.bind(lightRpc)
  lightRpc.setScripts = async (scripts, mode) => {
    setScriptCalls.push({ mode, count: scripts.length, matchingScript: scripts.filter(item => require('@ckb-lumos/lumos/utils').computeScriptHash(item.script) === scriptHash).map(item => ({ blockNumber: item.blockNumber, scriptType: item.scriptType, walletId: item.walletId })) })
    return originalSetScripts(scripts, mode)
  }
  const ranges = []
  const rpcHashes = []
  const originalGetTransactions = lightRpc.getTransactions.bind(lightRpc)
  lightRpc.getTransactions = async (...args) => {
    ranges.push({ scriptHash: require('@ckb-lumos/lumos/utils').computeScriptHash(args[0].script), blockRange: args[0].blockRange })
    const result = await originalGetTransactions(...args)
    rpcHashes.push(...result.txs.map(item => item.txHash))
    return result
  }
  const sync = Object.create(LightSynchronizer.prototype)
  sync.lightRpc = lightRpc
  sync.addressMetas = metas
  const startedAt = Date.now()
  await sync.initSyncProgress()
  const afterScripts = await lightRpc.getScripts()
  const nativeAfterInit = afterScripts.find(item => require('@ckb-lumos/lumos/utils').computeScriptHash(item.script) === scriptHash)
  const progressAfterInit = await ds.getRepository(SyncProgress).find({ where: { walletId } })
  const ownedProgressAfterInit = progressAfterInit.find(item => item.hash === scriptHash)
  if (!ownedProgressAfterInit || ownedProgressAfterInit.syncedBlockNumber !== handoff || ownedProgressAfterInit.localSavedBlockNumber !== handoff) throw new Error('Neuron init did not create app progress at the supported wallet floor')

  const deadline = Date.now() + 120000
  let cursor = parseInt(nativeAfterInit.blockNumber)
  while (cursor <= handoff && Date.now() < deadline) {
    await sleep(1000)
    const currentScripts = await lightRpc.getScripts()
    const current = currentScripts.find(item => require('@ckb-lumos/lumos/utils').computeScriptHash(item.script) === scriptHash)
    cursor = current ? parseInt(current.blockNumber) : 0
  }
  if (cursor <= handoff) throw new Error(`native filter cursor did not pass faucet block; cursor=${cursor}`)

  const scriptStates = await sync.upsertTxHashes()
  const duplicateScriptStates = await sync.upsertTxHashes()
  const cacheBeforeProgress = await ds.getRepository(IndexerCache).find({ where: { walletId, txHash: expectedHash } })
  if (cacheBeforeProgress.length !== 1 || !rpcHashes.includes(expectedHash)) throw new Error(`cache replay did not deduplicate expected result: ${JSON.stringify(cacheBeforeProgress)}`)
  await sync.updateSyncedBlockOfScripts(scriptStates)
  const progressAfterDiscovery = await ds.getRepository(SyncProgress).findOneBy({ hash: scriptHash })

  const { Subject } = require('rxjs')
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
    async notifyCurrentBlockNumberProcessed(blockNumber) {
      if (pendingAddressTasks.length) await Promise.all(pendingAddressTasks.splice(0))
      await sync.notifyCurrentBlockNumberProcessed(blockNumber)
    }
    stop() { sync.pollingIndexer = false }
  }
  syncConnector = CacheConnector
  const Queue = require(path.join(appRoot, 'dist/block-sync-renderer/sync/queue')).default
  const queue = new Queue(rpcUrl, metas, 2, false)
  await queue.start()
  const txDeadline = Date.now() + 90000
  let transactionRows = []
  while (Date.now() < txDeadline) {
    transactionRows = await ds.getRepository(TransactionEntity).find({ where: { hash: expectedHash } })
    if (transactionRows.length) break
    await sleep(500)
  }
  if (!transactionRows.length) { queue.stop(); throw new Error('Neuron Queue did not persist the faucet tx within 90 seconds') }
  const completionDeadline = Date.now() + 30000
  let applicationProgress
  let processedCache
  while (Date.now() < completionDeadline) {
    applicationProgress = await ds.getRepository(SyncProgress).findOneBy({ hash: scriptHash })
    processedCache = await ds.getRepository(IndexerCache).findOneBy({ walletId, txHash: expectedHash })
    if (processedCache?.isProcessed && applicationProgress?.localSavedBlockNumber > handoff) break
    await sleep(200)
  }
  await queue.stopAndWait()

  const snapshot = async dataSource => {
    const progress = await dataSource.getRepository(SyncProgress).findOneBy({ hash: scriptHash })
    return {
      transactions: (await dataSource.getRepository(TransactionEntity).find({ where: { hash: expectedHash } })).map(row => ({ hash: row.hash, blockNumber: row.blockNumber, blockHash: row.blockHash, status: row.status })),
      inputs: (await dataSource.getRepository(InputEntity).find({ where: { transactionHash: expectedHash } })).map(row => ({ previousHash: row.outPointTxHash, previousIndex: row.outPointIndex, capacity: row.capacity, lockArgs: row.lockArgs })),
      outputs: (await dataSource.getRepository(OutputEntity).find({ where: { outPointTxHash: expectedHash } })).map(row => ({ index: row.outPointIndex, status: row.status, capacity: row.capacity, lockArgs: row.lockArgs })),
      cache: (await dataSource.getRepository(IndexerCache).find({ where: { walletId, txHash: expectedHash } })).map(row => ({ walletId: row.walletId, txHash: row.txHash, blockNumber: row.blockNumber, isProcessed: row.isProcessed })),
      progress: progress && { walletId: progress.walletId, start: progress.lightStartBlockNumber, synced: progress.syncedBlockNumber, localSaved: progress.localSavedBlockNumber },
    }
  }
  const beforeRestart = await snapshot(ds)
  await ds.destroy()
  await database.default(genesis)
  const reopened = connection.getConnection('light')
  const afterRestart = await snapshot(reopened)
  const output = beforeRestart.outputs.find(item => item.index === '0')
  if (beforeRestart.transactions.length !== 1 || beforeRestart.cache.length !== 1 || !beforeRestart.cache[0].isProcessed || output?.status !== 'live' || output?.capacity !== '1000000000000' || beforeRestart.progress?.localSaved <= handoff) throw new Error(`application recovery acceptance failed: ${JSON.stringify(beforeRestart)}`)
  process.stdout.write(`${JSON.stringify({
    verdict: 'SIMULATED_APP_RECOVERY_FROM_FULL_NATIVE_COPY',
    walletId, scriptHash, rpcUrl, handoffHeight: handoff, walletStartHeight: walletStart,
    nativeBefore: { cursor: nativeBefore.blockNumber, registered: true },
    nativeAfterInit: { cursor: nativeAfterInit.blockNumber, requestedCursor: setScriptCalls.flatMap(call => call.matchingScript).map(item => item.blockNumber)[0] ?? null },
    setScriptCalls, progressAfterInit: ownedProgressAfterInit && { start: ownedProgressAfterInit.lightStartBlockNumber, synced: ownedProgressAfterInit.syncedBlockNumber, localSaved: ownedProgressAfterInit.localSavedBlockNumber },
    cursorAfterFilter: cursor, historicalQueryRangesForOwnedScript: ranges.filter(item => item.scriptHash === scriptHash).map(item => item.blockRange),
    expectedHashFromRpc: rpcHashes.includes(expectedHash), duplicateUpsertCacheCountBeforeProgress: cacheBeforeProgress.length,
    duplicateUpsertReturnedScriptCount: duplicateScriptStates.length,
    progressAfterDiscovery: progressAfterDiscovery && { synced: progressAfterDiscovery.syncedBlockNumber, localSaved: progressAfterDiscovery.localSavedBlockNumber },
    beforeRestart, afterRestart, restartExact: JSON.stringify(beforeRestart) === JSON.stringify(afterRestart),
    handledAddressGenerationMessages: processMessages.filter(item => item.channel === 'check-and-save-wallet-address').length,
    elapsedMs: Date.now() - startedAt,
    notes: 'Simulated clean application state created by removing the one R9 transaction/cache row and wallet progress rows from a disposable profile copy. Full native store, not selective D2 artifact. No independent app restore or completeness claim.',
  }, null, 2)}\n`)
  await reopened.destroy()
}
main().catch(error => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1 })
