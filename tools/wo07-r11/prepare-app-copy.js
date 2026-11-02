const Module = require('node:module')
const path = require('node:path')
const fs = require('node:fs')
const os = require('node:os')

const appRoot = path.resolve(process.argv[2] || '')
const source = path.resolve(process.argv[3] || '')
const destination = path.resolve(process.argv[4] || '')
const walletId = '1c2d9dbd-4894-4ac6-93bf-b5352acb3eb0'
const txHash = '0x42dc0f3efabc9134fc2244f5c01c3b52768ba8d23f29c78d839208afa844e435'
const genesis = '0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606'
if (!appRoot || !source.includes(`${path.sep}wo07-r8-neuron-profile-real-testnet`) || !destination.includes(`${path.sep}wo07-r8-neuron-profile-real-testnet-r11`)) {
  throw new Error('usage: node prepare-app-copy.js <extracted-neuron-app> <r8-disposable-profile> <new-r11-profile>')
}
if (!fs.existsSync(path.join(source, 'wallets', `${walletId}.json`))) throw new Error('R8 disposable wallet keystore file missing')
if (fs.existsSync(destination)) throw new Error(`refusing to overwrite existing copied profile: ${destination}`)

fs.cpSync(source, destination, { recursive: true, errorOnExist: true })
process.env.NODE_ENV = 'production'
process.env.WO07_R6_PROFILE_DIR = destination
process.env.NODE_PATH = [path.join(appRoot, 'node_modules'), process.env.NODE_PATH].filter(Boolean).join(path.delimiter)
Module._initPaths()
const electronStub = {
  app: { isPackaged: true, getPath: name => name === 'userData' ? destination : path.join(os.tmpdir(), name), getName: () => 'Neuron-WO07-R11', getVersion: () => '0.204.1', on: () => {}, once: () => {} },
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
  const Wallets = require(path.join(appRoot, 'dist/services/wallets')).default.getInstance()
  const Addresses = require(path.join(appRoot, 'dist/services/addresses')).default
  const Transaction = entity('transaction')
  const Input = entity('input')
  const Output = entity('output')
  const Cache = entity('indexer-tx-hash-cache')
  const Progress = entity('sync-progress')
  const TxLock = entity('tx-lock')
  const Description = entity('tx-description')
  if (Wallets.get(walletId)?.id !== walletId) throw new Error('cloned wallet metadata did not reopen under original UUID')
  const addresses = await Addresses.getAddressesByWalletId(walletId)
  if (addresses.length !== 30) throw new Error(`expected 30 original address rows, got ${addresses.length}`)
  const txRows = await ds.getRepository(Transaction).find()
  const cacheRows = await ds.getRepository(Cache).find({ where: { walletId } })
  const outputRows = await ds.getRepository(Output).find({ where: { outPointTxHash: txHash } })
  const inputRows = await ds.getRepository(Input).find({ where: { transactionHash: txHash } })
  if (txRows.length !== 1 || txRows[0].hash !== txHash || cacheRows.length !== 1 || cacheRows[0].txHash !== txHash || outputRows.length !== 1) {
    throw new Error(`copied app DB did not match the expected single R9 record set: tx=${txRows.length}, cache=${cacheRows.length}, outputs=${outputRows.length}`)
  }
  const progressBefore = await ds.getRepository(Progress).find({ where: { walletId } })
  const before = { walletAddressRows: addresses.length, progressRows: progressBefore.length, transactionRows: txRows.length, transactionInputRows: inputRows.length, transactionOutputRows: outputRows.length, walletCacheRows: cacheRows.length }

  await ds.getRepository(Cache).delete({ walletId, txHash })
  await ds.getRepository(Input).delete({ transactionHash: txHash })
  await ds.getRepository(Output).delete({ outPointTxHash: txHash })
  await ds.getRepository(TxLock).delete({ transactionHash: txHash })
  await ds.getRepository(Description).delete({ txHash })
  await ds.getRepository(Transaction).delete({ hash: txHash })
  await require(path.join(appRoot, 'dist/services/sync-progress')).default.deleteWalletSyncProgress(walletId)
  const after = {
    wallet: (await ds.getRepository(Transaction).count()),
    cache: await ds.getRepository(Cache).count({ where: { walletId } }),
    progress: await ds.getRepository(Progress).count({ where: { walletId } }),
    addressRows: await ds.getRepository(entity('hd-public-key-info')).count({ where: { walletId } }),
  }
  if (after.wallet !== 0 || after.cache !== 0 || after.progress !== 0 || after.addressRows !== 30) throw new Error(`copied app-state reset failed: ${JSON.stringify(after)}`)
  const first = addresses.find(item => item.addressType === 0 && item.addressIndex === 0)
  const script = first.generateDefaultLockScript()
  const scriptIdentity = { codeHash: script.codeHash, hashType: script.hashType, args: script.args, scriptHash: require('@ckb-lumos/lumos/utils').computeScriptHash({ codeHash: script.codeHash, hashType: script.hashType, args: script.args }) }
  process.stdout.write(`${JSON.stringify({ profile: destination, simulatedCleanApplicationState: true, copiedRowsBeforeReset: before, afterReset: after, walletId, address0: first.address, scriptIdentity, deletedOnlyKnownWalletTransactionAndProgressInCopiedProfile: true }, null, 2)}\n`)
  await ds.destroy()
}
main().catch(error => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1 })
