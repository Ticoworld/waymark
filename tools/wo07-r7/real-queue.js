const Module = require('node:module')
const path = require('node:path')
const fs = require('node:fs')
const os = require('node:os')

const appRoot = path.resolve(process.argv[2] || '')
const profileRoot = path.resolve(process.argv[3] || '')
const rpcUrl = process.argv[4]
if (!appRoot || !profileRoot || !profileRoot.includes(`${path.sep}wo07-r6-queue-db`) || !rpcUrl) {
  throw new Error('usage: node real-queue.js <extracted-neuron-app> <new-wo07-r6-queue-db-directory> <light-rpc-url>')
}
if (fs.existsSync(profileRoot)) throw new Error(`refusing to overwrite profile: ${profileRoot}`)
fs.mkdirSync(path.join(profileRoot, 'cells'), { recursive: true })
process.env.NODE_ENV = 'production'
process.env.WO07_R6_PROFILE_DIR = profileRoot
process.env.NODE_PATH = [path.join(appRoot, 'node_modules'), process.env.NODE_PATH].filter(Boolean).join(path.delimiter)
Module._initPaths()
const { Subject } = require('rxjs')
const ipcEvents = []
process.send = message => ipcEvents.push(message)

const hashes = [
  '0x2017462e567ea3ad2e24407859fe1164c126af4a0f385d45316e45e7de004d66',
  '0xb7503283af42a8fd1595306e2d5dd4a789e103980207fdafb5229b2e20b7113c',
  '0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894',
  '0x69c04b470dbc5470ff554b2901fcc047edda082b46d8af523ae84a99e03d62b7',
  '0xb23fbbb1db9ca0da48f76993e9258fdadb0f3bc81d9999924561e72583aa5d5a',
  '0xce0b13ba3f23babc6e4cc011a992b1f7bf610dd92b4f6719afde1c91a5e2ab39',
  '0x2067edf16ab143e7bff9ef91803e36ce6a32347c632c75a37d382443ae379738',
  '0xe4cbdffa9002b0283c2c71cc19ec646b85cb58274b8f45d72496e78ae96b4cbd',
]
const connectors = []
class ControlledConnector {
  constructor() {
    this.transactionsSubject = new Subject()
    this.blockTipsSubject = new Subject()
    connectors.push(this)
  }
  async connect() {
    setImmediate(() => this.transactionsSubject.next({ txHashes: hashes, params: { blockNumber: 22655842 } }))
  }
  async notifyCurrentBlockNumberProcessed() {}
  stop() {}
}

const electronStub = {
  app: {
    isPackaged: true,
    getPath: name => name === 'userData' ? profileRoot : path.join(os.tmpdir(), name),
    getName: () => 'Neuron-WO07-R7',
    getVersion: () => '0.204.1',
    on: () => {},
    once: () => {},
  },
  ipcMain: { on: () => {}, handle: () => {}, removeHandler: () => {} },
  shell: { openExternal: async () => {} },
  BrowserWindow: class {},
}
const originalLoad = Module._load
Module._load = function (request, parent, isMain) {
  if (request === 'electron') return electronStub
  if (request === '../../services/networks' && parent?.filename.endsWith(`${path.sep}database${path.sep}chain${path.sep}connection.js`)) {
    return { __esModule: true, default: { getInstance: () => ({ getCurrent: () => ({ type: 2 }) }) } }
  }
  if (request === './light-synchronizer' && parent?.filename.endsWith(`${path.sep}sync${path.sep}queue.js`)) {
    return { __esModule: true, default: ControlledConnector }
  }
  return originalLoad.call(this, request, parent, isMain)
}

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms))
const snapshot = async (dataSource, TransactionEntity, InputEntity, OutputEntity) => ({
  transactions: (await dataSource.getRepository(TransactionEntity).find()).map(row => ({ hash: row.hash, blockNumber: row.blockNumber })).sort((a, b) => a.blockNumber - b.blockNumber || a.hash.localeCompare(b.hash)),
  inputs: (await dataSource.getRepository(InputEntity).find()).map(row => ({ txHash: row.transactionHash, previousHash: row.outPointTxHash, previousIndex: row.outPointIndex, capacity: row.capacity })).sort((a, b) => a.txHash.localeCompare(b.txHash) || a.previousIndex - b.previousIndex),
  outputs: (await dataSource.getRepository(OutputEntity).find()).map(row => ({ txHash: row.outPointTxHash, index: row.outPointIndex, status: row.status, capacity: row.capacity })).sort((a, b) => a.txHash.localeCompare(b.txHash) || a.index - b.index),
})

async function main() {
  const database = require(path.join(appRoot, 'dist/database/chain/ormconfig'))
  await database.default('0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606')
  const connection = require(path.join(appRoot, 'dist/database/chain/connection'))
  const dataSource = connection.getConnection('light')
  const TransactionEntity = require(path.join(appRoot, 'dist/database/chain/entities/transaction')).default
  const InputEntity = require(path.join(appRoot, 'dist/database/chain/entities/input')).default
  const OutputEntity = require(path.join(appRoot, 'dist/database/chain/entities/output')).default
  const Persister = require(path.join(appRoot, 'dist/services/tx/transaction-persistor')).TransactionPersistor
  const saveCalls = []
  const saveFetchTx = Persister.saveFetchTx
  Persister.saveFetchTx = async (tx, ...args) => {
    saveCalls.push({ hash: tx.hash, computedHash: tx.computeHash(), blockNumber: tx.blockNumber, previousHashes: tx.inputs.map(input => input.previousOutput?.txHash) })
    return saveFetchTx(tx, ...args)
  }
  const Queue = require(path.join(appRoot, 'dist/block-sync-renderer/sync/queue')).default
  const queue = new Queue(rpcUrl, [], 2, false)
  await queue.start()

  const deadline = Date.now() + 60000
  let beforeRestart
  while (Date.now() < deadline) {
    beforeRestart = await snapshot(dataSource, TransactionEntity, InputEntity, OutputEntity)
    if (beforeRestart.transactions.length === hashes.length) break
    await sleep(500)
  }
  if (beforeRestart.transactions.length !== hashes.length) {
    throw new Error(`Queue did not persist all target transactions; count=${beforeRestart.transactions.length}; hashes=${saveCalls.map(x => x.hash).join(',')}`)
  }
  await queue.stopAndWait()
  beforeRestart = await snapshot(dataSource, TransactionEntity, InputEntity, OutputEntity)
  await dataSource.destroy()
  await database.default('0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606')
  const reopened = connection.getConnection('light')
  const afterRestart = await snapshot(reopened, TransactionEntity, InputEntity, OutputEntity)
  process.stdout.write(JSON.stringify({
    source: 'Neuron v0.204.1 packaged Queue and TransactionPersistor; real R3 D2 TESTNET transactions; pipeline-only, no wallet ownership/cache rows',
    profileRoot,
    rpcUrl,
    expectedHashes: hashes,
    saveCalls,
    ipcEvents,
    queueCompletion: 'stopAndWait resolved after all eight transactions were persisted',
    beforeRestart,
    afterRestart,
    restartExact: JSON.stringify(beforeRestart) === JSON.stringify(afterRestart),
  }))
  await reopened.destroy()
}

main().catch(error => {
  process.stderr.write(`${error.stack || error}\n`)
  process.exitCode = 1
})
