const Module = require('node:module')
const path = require('node:path')
const fs = require('node:fs')
const os = require('node:os')

const appRoot = path.resolve(process.argv[2] || '')
const profileRoot = path.resolve(process.argv[3] || '')
if (!appRoot || !profileRoot || !profileRoot.includes(`${path.sep}wo07-r6-neuron-db`)) {
  throw new Error('usage: node persistor-smoke.js <extracted-neuron-app> <new-wo07-r6-neuron-db-directory>')
}
if (fs.existsSync(profileRoot)) throw new Error(`refusing to overwrite profile: ${profileRoot}`)
fs.mkdirSync(path.join(profileRoot, 'cells'), { recursive: true })
process.env.NODE_ENV = 'production'
process.env.WO07_R6_PROFILE_DIR = profileRoot
process.env.NODE_PATH = [path.join(appRoot, 'node_modules'), process.env.NODE_PATH].filter(Boolean).join(path.delimiter)
Module._initPaths()

const electronStub = {
  app: {
    isPackaged: true,
    getPath: name => name === 'userData' ? process.env.WO07_R6_PROFILE_DIR : path.join(os.tmpdir(), name),
    getName: () => 'Neuron-WO07-R6',
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
  return originalLoad.call(this, request, parent, isMain)
}

async function main() {
  const database = require(path.join(appRoot, 'dist/database/chain/ormconfig'))
  const genesis = '0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606'
  await database.default(genesis)
  const connection = require(path.join(appRoot, 'dist/database/chain/connection'))
  const dataSource = connection.getConnection('light')
  if (!dataSource.isInitialized) throw new Error('Neuron TESTNET light-mode SQLite DataSource did not initialize')

  const Transaction = require(path.join(appRoot, 'dist/models/chain/transaction')).default
  const Persistor = require(path.join(appRoot, 'dist/services/tx/transaction-persistor')).TransactionPersistor
  const TransactionEntity = require(path.join(appRoot, 'dist/database/chain/entities/transaction')).default
  const InputEntity = require(path.join(appRoot, 'dist/database/chain/entities/input')).default
  const OutputEntity = require(path.join(appRoot, 'dist/database/chain/entities/output')).default
  const lockHash = '0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8'
  const lockArgs = '0xbc5882c4309431ee23ad7bbad4b5c3325539eebd'
  const lock = { codeHash: '0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8', hashType: 'type', args: lockArgs }
  const otherLock = { codeHash: lock.codeHash, hashType: 'type', args: '0x1111111111111111111111111111111111111111' }
  const anchor = '0x' + '00'.repeat(32)
  const blockHash = '0x' + 'ab'.repeat(32)
  const txHash1 = '0x' + '01'.repeat(32)
  const txHash2 = '0x' + '02'.repeat(32)
  const makeTx = (hash, blockNumber, previousHash, inputLock, outputLock, outputCapacity) => Transaction.fromObject({
    hash,
    version: '0x0',
    cellDeps: [],
    headerDeps: [],
    inputs: [{ previousOutput: { txHash: previousHash, index: '0x0' }, since: '0x0', lock: inputLock }],
    outputs: [{ capacity: outputCapacity, lock: outputLock }],
    outputsData: ['0x'],
    witnesses: ['0x'],
    blockHash,
    blockNumber: `0x${blockNumber.toString(16)}`,
    timestamp: '0x1',
    status: 'success',
  })

  const funding = makeTx(txHash1, 1, anchor, otherLock, lock, '10000000000')
  const spending = makeTx(txHash2, 2, txHash1, lock, otherLock, '9000000000')
  await Persistor.saveFetchTx(funding, new Set([lockArgs]))
  await Persistor.saveFetchTx(spending, new Set([lockArgs]))

  const rowsBeforeRestart = (await dataSource.getRepository(TransactionEntity).find()).map(row => ({ hash: row.hash, blockNumber: row.blockNumber })).sort((a, b) => a.blockNumber - b.blockNumber)
  const outputsBeforeRestart = (await dataSource.getRepository(OutputEntity).find()).map(row => ({ txHash: row.outPointTxHash, index: row.outPointIndex, status: row.status, capacity: row.capacity })).sort((a, b) => a.txHash.localeCompare(b.txHash))
  const inputsBeforeRestart = (await dataSource.getRepository(InputEntity).find()).map(row => ({ txHash: row.transactionHash, previousTxHash: row.outPointTxHash, previousIndex: row.outPointIndex }))
  await dataSource.destroy()
  await database.default(genesis)
  const reopened = connection.getConnection('light')
  const rowsAfterRestart = (await reopened.getRepository(TransactionEntity).find()).map(row => ({ hash: row.hash, blockNumber: row.blockNumber })).sort((a, b) => a.blockNumber - b.blockNumber)
  const outputsAfterRestart = (await reopened.getRepository(OutputEntity).find()).map(row => ({ txHash: row.outPointTxHash, index: row.outPointIndex, status: row.status, capacity: row.capacity })).sort((a, b) => a.txHash.localeCompare(b.txHash))

  process.stdout.write(JSON.stringify({
    source: 'Neuron v0.204.1 packaged JavaScript; synthetic-only persistor smoke test',
    profileRoot,
    dbFiles: fs.readdirSync(path.join(profileRoot, 'cells')).filter(name => name.startsWith('light-')),
    rowsBeforeRestart,
    outputsBeforeRestart,
    inputsBeforeRestart,
    restartExact: JSON.stringify(rowsBeforeRestart) === JSON.stringify(rowsAfterRestart) && JSON.stringify(outputsBeforeRestart) === JSON.stringify(outputsAfterRestart),
    rowsAfterRestart,
    outputsAfterRestart,
  }))
  await reopened.destroy()
}

main().catch(error => {
  process.stderr.write(`${error.stack || error}\n`)
  process.exitCode = 1
})
