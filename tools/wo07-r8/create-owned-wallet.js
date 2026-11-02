const Module = require('node:module')
const path = require('node:path')
const fs = require('node:fs')
const os = require('node:os')

const appRoot = path.resolve(process.argv[2] || '')
const profileRoot = path.resolve(process.argv[3] || '')
const genesis = '0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606'
if (!appRoot || !profileRoot || !profileRoot.includes(`${path.sep}wo07-r8-neuron-profile`)) {
  throw new Error('usage: node create-owned-wallet.js <extracted-neuron-app> <new-wo07-r8-neuron-profile-directory>')
}
if (fs.existsSync(profileRoot)) throw new Error(`refusing to overwrite profile: ${profileRoot}`)
fs.mkdirSync(profileRoot, { recursive: true })
fs.mkdirSync(path.join(profileRoot, 'networks'), { recursive: true })
process.env.NODE_ENV = 'production'
process.env.WO07_R8_PROFILE_DIR = profileRoot
process.env.NODE_PATH = [path.join(appRoot, 'node_modules'), process.env.NODE_PATH].filter(Boolean).join(path.delimiter)
Module._initPaths()

const testnet = {
  id: 'light_client_testnet', name: 'Light Client TESTNET', remote: 'http://127.0.0.1:19076',
  genesisHash: genesis, type: 2, chain: 'light_client_testnet', readonly: true,
}
fs.writeFileSync(path.join(profileRoot, 'networks', 'index.json'), JSON.stringify({
  selected: testnet.id,
  networks: [testnet],
  AddedLightNetwork: true,
}))
const electronStub = {
  app: {
    isPackaged: true,
    getPath: name => name === 'userData' ? profileRoot : path.join(os.tmpdir(), name),
    getName: () => 'Neuron-WO07-R8', getVersion: () => '0.204.1',
    on: () => {}, once: () => {},
  },
  ipcMain: { on: () => {}, handle: () => {}, removeHandler: () => {} },
  shell: { openExternal: async () => {} },
  BrowserWindow: class {},
}
const originalLoad = Module._load
Module._load = function (request, parent, isMain) {
  if (request === 'electron') return electronStub
  let resolved
  try { resolved = parent && Module._resolveFilename(request, parent, isMain) } catch {}
  if (resolved === path.join(appRoot, 'dist/block-sync-renderer/index.js')) {
    return { resetSyncTaskQueue: { asyncPush: async () => undefined } }
  }
  return originalLoad.call(this, request, parent, isMain)
}

async function main() {
  const database = require(path.join(appRoot, 'dist/database/chain/ormconfig'))
  await database.default(genesis)
  const connection = require(path.join(appRoot, 'dist/database/chain/connection'))
  const dataSource = connection.getConnection('light')
  if (!dataSource.isInitialized) throw new Error('Neuron TESTNET Light SQLite DataSource did not initialize')
  const NetworkService = require(path.join(appRoot, 'dist/services/networks')).default.getInstance()
  await NetworkService.activate('light_client_testnet')
  if (NetworkService.getCurrent().id !== 'light_client_testnet' || NetworkService.getCurrent().genesisHash !== genesis || NetworkService.isMainnet()) {
    throw new Error('Neuron network service did not select TESTNET Light Client')
  }

  const { hd } = require('@ckb-lumos/lumos')
  const mnemonic = hd.mnemonic.generateMnemonic()
  const password = `r8-disposable-${require('node:crypto').randomBytes(24).toString('hex')}`
  const WalletsController = require(path.join(appRoot, 'dist/controllers/wallets')).default
  const imported = await new WalletsController().importMnemonic({ name: 'WO07-R8 disposable TESTNET', password, mnemonic })
  const walletId = imported.result.id

  const WalletsService = require(path.join(appRoot, 'dist/services/wallets')).default
  const wallet = WalletsService.getInstance().get(walletId)
  const Addresses = require(path.join(appRoot, 'dist/services/addresses')).default
  const AddressInfo = require(path.join(appRoot, 'dist/database/chain/entities/hd-public-key-info')).default
  const generationQueue = Addresses.generateAndSaveForExtendedKeyQueue
  const deadline = Date.now() + 30000
  while (Date.now() < deadline) {
    const count = await dataSource.getRepository(AddressInfo).count({ where: { walletId } })
    if (count >= 30 && generationQueue.length() === 0 && generationQueue.running() === 0) break
    await new Promise(resolve => setTimeout(resolve, 100))
  }
  const addressMetas = await Addresses.getAddressesByWalletId(walletId)
  if (!addressMetas.length || generationQueue.length() || generationQueue.running()) throw new Error('Neuron address generation did not settle')
  const defaultMeta = addressMetas.find(item => item.addressType === 0 && item.addressIndex === 0)
  if (!defaultMeta) throw new Error('Neuron account-0 default address metadata missing')
  const lock = defaultMeta.generateDefaultLockScript()
  const lockScript = { codeHash: lock.codeHash, hashType: lock.hashType, args: lock.args }
  if (!defaultMeta.address.startsWith('ckt')) throw new Error('Neuron generated a non-TESTNET address')

  const LightSynchronizer = require(path.join(appRoot, 'dist/block-sync-renderer/sync/light-synchronizer')).default
  const rpcCalls = []
  const lightRpc = {
    getScripts: async () => [],
    setScripts: async (scripts, mode) => { rpcCalls.push({ mode, scripts: scripts.length }) },
  }
  await LightSynchronizer.prototype.initSyncProgress.call({ addressMetas, lightRpc })
  const SyncProgress = require(path.join(appRoot, 'dist/database/chain/entities/sync-progress')).default
  const progressRows = await dataSource.getRepository(SyncProgress).find({ where: { walletId } })
  const defaultProgress = progressRows.find(row => row.hash === require('@ckb-lumos/lumos/utils').computeScriptHash(lockScript))
  if (!defaultProgress) throw new Error('Neuron did not initialize progress for its account-0 default lock Script')

  const output = {
    verdict: 'WALLET_CREATED',
    network: { id: NetworkService.getCurrent().id, type: 'Light', genesisHash: genesis },
    wallet: { id: walletId, name: wallet.name, scriptCount: addressMetas.length },
    account0: {
      path: defaultMeta.path, address: defaultMeta.address,
      lockScript, scriptHash: defaultProgress.hash,
    },
    progress: {
      rows: progressRows.length,
      defaultScript: {
        walletId: defaultProgress.walletId, scriptType: defaultProgress.scriptType,
        start: defaultProgress.lightStartBlockNumber, localSaved: defaultProgress.localSavedBlockNumber,
        synced: defaultProgress.syncedBlockNumber,
      },
      lightRpcRegistrationCalls: rpcCalls,
    },
    persistedFiles: fs.readdirSync(profileRoot, { recursive: true }).filter(entry => typeof entry === 'string').sort(),
  }
  process.stdout.write(`${JSON.stringify(output, null, 2)}\n`)
  await dataSource.destroy()
}

main().catch(error => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1 })
