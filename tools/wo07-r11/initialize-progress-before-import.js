const Module = require('node:module')
const path = require('node:path')
const os = require('node:os')

const appRoot = path.resolve(process.argv[2] || '')
const profileRoot = path.resolve(process.argv[3] || '')
const rpcUrl = process.argv[4] || 'http://127.0.0.1:19100'
const walletId = '1c2d9dbd-4894-4ac6-93bf-b5352acb3eb0'
const handoff = 22944378
const scriptHash = '0x28535e1e70eb2ae8c56a829e1f9d3777fdf6b310c9c1dff17e4ae01917e45e62'
const genesis = '0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606'
if (!appRoot || !profileRoot.includes(`${path.sep}wo07-r8-neuron-profile-real-testnet-r11`)) throw new Error('usage: node initialize-progress-before-import.js <extracted-neuron-app> <r11-app-copy> [rpc-url]')
process.env.NODE_ENV = 'production'
process.env.WO07_R6_PROFILE_DIR = profileRoot
process.env.NODE_PATH = [path.join(appRoot, 'node_modules'), process.env.NODE_PATH].filter(Boolean).join(path.delimiter)
Module._initPaths()
const electronStub = { app: { isPackaged: true, getPath: name => name === 'userData' ? profileRoot : path.join(os.tmpdir(), name), getName: () => 'Neuron-WO07-R11', getVersion: () => '0.204.1' }, ipcMain: { on: () => {}, handle: () => {} }, shell: { openExternal: async () => {} }, BrowserWindow: class {} }
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
  const Networks = require(path.join(appRoot, 'dist/services/networks')).default.getInstance()
  if (Networks.getCurrent().id !== 'light_client_testnet') throw new Error('app-copy network is not Light TESTNET')
  await Networks.update('light_client_testnet', { remote: rpcUrl })
  const Wallets = require(path.join(appRoot, 'dist/services/wallets')).default.getInstance()
  const wallet = Wallets.get(walletId)
  if (!wallet || parseInt(wallet.startBlockNumber) !== handoff) throw new Error('Neuron wallet identity/start height is invalid')
  const Addresses = require(path.join(appRoot, 'dist/services/addresses')).default
  const metas = await Addresses.getAddressesByWalletId(walletId)
  const SyncProgress = require(path.join(appRoot, 'dist/database/chain/entities/sync-progress')).default
  const IndexerCache = require(path.join(appRoot, 'dist/database/chain/entities/indexer-tx-hash-cache')).default
  const Transaction = require(path.join(appRoot, 'dist/database/chain/entities/transaction')).default
  if (await ds.getRepository(Transaction).count() || await ds.getRepository(IndexerCache).count({ where: { walletId } }) || await ds.getRepository(SyncProgress).count({ where: { walletId } })) throw new Error('preimport app copy is not clean')
  const LightSynchronizer = require(path.join(appRoot, 'dist/block-sync-renderer/sync/light-synchronizer')).default
  const LightRPC = require(path.join(appRoot, 'dist/utils/ckb-rpc')).LightRPC
  const rpc = new LightRPC(rpcUrl)
  const script = metas.find(item => item.addressType === 0 && item.addressIndex === 0).generateDefaultLockScript()
  const before = await rpc.getScripts()
  if (before.some(item => require('@ckb-lumos/lumos/utils').computeScriptHash(item.script) === scriptHash)) throw new Error('preimport native client already has the R8 Script')
  const setScriptCalls = []
  const originalSetScripts = rpc.setScripts.bind(rpc)
  rpc.setScripts = async (scripts, mode) => {
    setScriptCalls.push({ mode, count: scripts.length, target: scripts.filter(item => require('@ckb-lumos/lumos/utils').computeScriptHash(item.script) === scriptHash).map(item => ({ blockNumber: item.blockNumber, walletId: item.walletId, scriptType: item.scriptType })) })
    return originalSetScripts(scripts, mode)
  }
  const sync = Object.create(LightSynchronizer.prototype)
  sync.lightRpc = rpc
  sync.addressMetas = metas
  await sync.initSyncProgress()
  const after = await rpc.getScripts()
  const registered = after.find(item => require('@ckb-lumos/lumos/utils').computeScriptHash(item.script) === scriptHash)
  const progress = await ds.getRepository(SyncProgress).findOneBy({ hash: scriptHash })
  if (!registered || !progress || progress.walletId !== walletId || progress.syncedBlockNumber !== handoff || progress.localSavedBlockNumber !== handoff) throw new Error('legitimate Neuron progress preinitialization failed')
  process.stdout.write(`${JSON.stringify({ phase: 'before-native-store-transfer', walletId, scriptHash, nativeScriptAbsentBefore: true, nativeCursorAfterNeuronInitialization: registered.blockNumber, setScriptCalls, appProgress: { start: progress.lightStartBlockNumber, synced: progress.syncedBlockNumber, localSaved: progress.localSavedBlockNumber }, transactionRows: await ds.getRepository(Transaction).count(), cacheRows: await ds.getRepository(IndexerCache).count({ where: { walletId } }), progressRows: await ds.getRepository(SyncProgress).count({ where: { walletId } }), note: 'Actual Neuron LightSynchronizer.initSyncProgress and SyncProgressService. No transaction/cache rows were introduced.' }, null, 2)}\n`)
  await ds.destroy()
}
main().catch(error => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1 })
