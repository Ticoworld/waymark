const Module = require('node:module')
const path = require('node:path')
const fs = require('node:fs')
const os = require('node:os')

const appRoot = path.resolve(process.argv[2] || '')
const profileRoot = path.resolve(process.argv[3] || '')
const walletId = process.argv[4]
const genesis = '0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606'
if (!appRoot || !profileRoot || !walletId || !profileRoot.includes(`${path.sep}wo07-r8-neuron-profile`)) {
  throw new Error('usage: node verify-owned-wallet.js <extracted-neuron-app> <existing-wo07-r8-neuron-profile> <wallet-uuid>')
}
process.env.NODE_ENV = 'production'
process.env.WO07_R8_PROFILE_DIR = profileRoot
process.env.NODE_PATH = [path.join(appRoot, 'node_modules'), process.env.NODE_PATH].filter(Boolean).join(path.delimiter)
Module._initPaths()
const electronStub = { app: { isPackaged: true, getPath: name => name === 'userData' ? profileRoot : path.join(os.tmpdir(), name), getName: () => 'Neuron-WO07-R8', getVersion: () => '0.204.1', on: () => {}, once: () => {} }, ipcMain: { on: () => {}, handle: () => {}, removeHandler: () => {} }, shell: { openExternal: async () => {} }, BrowserWindow: class {} }
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
  const dataSource = connection.getConnection('light')
  const Wallets = require(path.join(appRoot, 'dist/services/wallets')).default.getInstance()
  const NetworkService = require(path.join(appRoot, 'dist/services/networks')).default.getInstance()
  const network = NetworkService.getCurrent()
  if (network.id !== 'light_client_testnet' || network.genesisHash !== genesis || network.type !== 2 || NetworkService.isMainnet()) throw new Error('Neuron network selection did not reopen as TESTNET Light Client')
  const wallet = Wallets.get(walletId)
  const Addresses = require(path.join(appRoot, 'dist/services/addresses')).default
  const AddressInfo = require(path.join(appRoot, 'dist/database/chain/entities/hd-public-key-info')).default
  const SyncProgress = require(path.join(appRoot, 'dist/database/chain/entities/sync-progress')).default
  const infos = await dataSource.getRepository(AddressInfo).find({ where: { walletId } })
  const progress = await dataSource.getRepository(SyncProgress).find({ where: { walletId } })
  const metas = await Addresses.getAddressesByWalletId(walletId)
  const first = metas.find(item => item.addressType === 0 && item.addressIndex === 0)
  const script = first.generateDefaultLockScript()
  const publicScript = { codeHash: script.codeHash, hashType: script.hashType, args: script.args }
  const keyStorePath = path.join(profileRoot, 'wallets', `${walletId}.json`)
  const lockHash = require('@ckb-lumos/lumos/utils').computeScriptHash(publicScript)
  const defaultRow = progress.find(row => row.hash === lockHash)
  if (!defaultRow || !fs.existsSync(keyStorePath) || infos.length !== 30 || progress.length !== 90) throw new Error('wallet/profile persistence check failed')
  process.stdout.write(`${JSON.stringify({
    verdict: 'REOPENED', network: { id: network.id, type: network.type, genesisHash: network.genesisHash }, walletId: wallet.id, name: wallet.name,
    account0: { path: first.path, address: first.address, lockScript: publicScript, scriptHash: lockHash },
    addressRows: infos.length, syncProgressRows: progress.length,
    defaultProgress: { walletId: defaultRow.walletId, synced: defaultRow.syncedBlockNumber, start: defaultRow.lightStartBlockNumber },
    keystorePresent: true, keystoreBytes: fs.statSync(keyStorePath).size,
  }, null, 2)}\n`)
  await dataSource.destroy()
}
main().catch(error => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1 })
