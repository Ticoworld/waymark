const Module = require('node:module')
const path = require('node:path')
const fs = require('node:fs')
const os = require('node:os')
const http = require('node:http')

const appRoot = path.resolve(process.argv[2] || '')
const profileRoot = path.resolve(process.argv[3] || '')
if (!appRoot || !profileRoot || !profileRoot.includes(`${path.sep}wo07-r6-queue-db`)) {
  throw new Error('usage: node queue-smoke.js <extracted-neuron-app> <new-wo07-r6-queue-db-directory>')
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

const zeroHash = `0x${'00'.repeat(32)}`
const fundingBlockHash = `0x${'ab'.repeat(32)}`
const spendingBlockHash = `0x${'cd'.repeat(32)}`
const ownedLock = { code_hash: '0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8', hash_type: 'type', args: '0xbc5882c4309431ee23ad7bbad4b5c3325539eebd' }
const otherLock = { ...ownedLock, args: '0x1111111111111111111111111111111111111111' }
const rawTx = (previousHash, lock, capacity) => ({
  version: '0x0',
  cell_deps: [],
  header_deps: [],
  inputs: [{ previous_output: { tx_hash: previousHash, index: '0x0' }, since: '0x0' }],
  outputs: [{ capacity, lock, type: null }],
  outputs_data: ['0x'],
  witnesses: ['0x'],
})
const TransactionModel = require(path.join(appRoot, 'dist/models/chain/transaction')).default
const asNeuronSdkTx = tx => ({
  version: tx.version,
  cellDeps: tx.cell_deps,
  headerDeps: tx.header_deps,
  inputs: tx.inputs.map(input => ({ previousOutput: { txHash: input.previous_output.tx_hash, index: input.previous_output.index }, since: input.since })),
  outputs: tx.outputs.map(output => ({ capacity: output.capacity, lock: { codeHash: output.lock.code_hash, hashType: output.lock.hash_type, args: output.lock.args }, type: null })),
  outputsData: tx.outputs_data,
  witnesses: tx.witnesses,
})
const fundingRawTx = rawTx(zeroHash, ownedLock, '0x2540be400')
const fundingHash = TransactionModel.fromSDK(asNeuronSdkTx(fundingRawTx)).computeHash()
const spendingRawTx = rawTx(fundingHash, otherLock, '0x218711a00')
const spendingHash = TransactionModel.fromSDK(asNeuronSdkTx(spendingRawTx)).computeHash()
const transactions = {
  [fundingHash]: { transaction: { ...fundingRawTx, hash: fundingHash }, tx_status: { status: 'committed', block_hash: fundingBlockHash, block_number: '0x1', tx_index: '0x0' } },
  [spendingHash]: { transaction: { ...spendingRawTx, hash: spendingHash }, tx_status: { status: 'committed', block_hash: spendingBlockHash, block_number: '0x2', tx_index: '0x0' } },
}
const headers = {
  [fundingBlockHash]: { compact_target: '0x1e083126', dao: `0x${'00'.repeat(32)}`, epoch: '0x0', hash: fundingBlockHash, nonce: '0x0', number: '0x1', parent_hash: zeroHash, proposals_hash: zeroHash, timestamp: '0x1', transactions_root: zeroHash, uncles_hash: zeroHash, version: '0x0' },
  [spendingBlockHash]: { compact_target: '0x1e083126', dao: `0x${'00'.repeat(32)}`, epoch: '0x0', hash: spendingBlockHash, nonce: '0x0', number: '0x2', parent_hash: fundingBlockHash, proposals_hash: zeroHash, timestamp: '0x2', transactions_root: zeroHash, uncles_hash: zeroHash, version: '0x0' },
}
const rpcMethods = []
const rpcCalls = []
const rpcServer = http.createServer((request, response) => {
  let body = ''
  request.on('data', chunk => { body += chunk })
  request.on('end', () => {
    const messages = JSON.parse(body)
    const batch = Array.isArray(messages) ? messages : [messages]
    const results = batch.map(message => {
      rpcMethods.push(message.method)
      rpcCalls.push({ method: message.method, params: message.params })
      let result = null
      if (message.method === 'get_transaction') result = transactions[message.params[0]] || null
      if (message.method === 'get_header') result = headers[message.params[0]] || null
      return { jsonrpc: '2.0', id: message.id, result }
    })
    response.writeHead(200, { 'content-type': 'application/json' })
    response.end(JSON.stringify(Array.isArray(messages) ? results : results[0]))
  })
})

const connectors = []
class ControlledConnector {
  constructor() {
    this.transactionsSubject = new Subject()
    this.blockTipsSubject = new Subject()
    connectors.push(this)
  }
  async connect() {
    setImmediate(() => this.transactionsSubject.next({ txHashes: [fundingHash, spendingHash], params: { blockNumber: 2 } }))
  }
  async notifyCurrentBlockNumberProcessed() {}
  stop() {}
}

const electronStub = {
  app: {
    isPackaged: true,
    getPath: name => name === 'userData' ? profileRoot : path.join(os.tmpdir(), name),
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
  if (request === './light-synchronizer' && parent?.filename.endsWith(`${path.sep}sync${path.sep}queue.js`)) {
    return { __esModule: true, default: ControlledConnector }
  }
  return originalLoad.call(this, request, parent, isMain)
}

async function main() {
  await new Promise((resolve, reject) => rpcServer.listen(0, '127.0.0.1', error => error ? reject(error) : resolve()))
  const database = require(path.join(appRoot, 'dist/database/chain/ormconfig'))
  await database.default('0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606')
  const connection = require(path.join(appRoot, 'dist/database/chain/connection'))
  const dataSource = connection.getConnection('light')
  const Persister = require(path.join(appRoot, 'dist/services/tx/transaction-persistor')).TransactionPersistor
  const saveCalls = []
  const saveFetchTx = Persister.saveFetchTx
  Persister.saveFetchTx = async (tx, ...args) => {
    saveCalls.push({ hash: tx.hash, computedHash: tx.computeHash(), blockNumber: tx.blockNumber, inputHash: tx.inputs[0]?.previousOutput?.txHash, outputArgs: tx.outputs.map(output => output.lock.args) })
    return saveFetchTx(tx, ...args)
  }
  const Queue = require(path.join(appRoot, 'dist/block-sync-renderer/sync/queue')).default
  const queue = new Queue(`http://127.0.0.1:${rpcServer.address().port}`, [], 2, false)
  await queue.start()
  await new Promise((resolve, reject) => {
    const started = Date.now()
    const timer = setInterval(async () => {
      if (connectors.length && rpcMethods.includes('get_transaction') && rpcMethods.filter(v => v === 'get_transaction').length >= 3) {
        clearInterval(timer)
        try { await queue.stopAndWait(); resolve() } catch (error) { reject(error) }
      } else if (Date.now() - started > 15000) {
        clearInterval(timer)
        reject(new Error(`queue timed out; RPC methods=${rpcMethods.join(',')}`))
      }
    }, 50)
  })
  const TransactionEntity = require(path.join(appRoot, 'dist/database/chain/entities/transaction')).default
  const InputEntity = require(path.join(appRoot, 'dist/database/chain/entities/input')).default
  const OutputEntity = require(path.join(appRoot, 'dist/database/chain/entities/output')).default
  const transactionsSaved = await dataSource.getRepository(TransactionEntity).find()
  const inputsSaved = await dataSource.getRepository(InputEntity).find()
  const outputsSaved = await dataSource.getRepository(OutputEntity).find()
  const beforeRestart = {
    transactions: transactionsSaved.map(row => ({ hash: row.hash, blockNumber: row.blockNumber })),
    inputs: inputsSaved.map(row => ({ txHash: row.transactionHash, previousHash: row.outPointTxHash, previousIndex: row.outPointIndex, capacity: row.capacity })),
    outputs: outputsSaved.map(row => ({ txHash: row.outPointTxHash, index: row.outPointIndex, status: row.status, capacity: row.capacity })),
  }
  await dataSource.destroy()
  await database.default('0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606')
  const reopened = connection.getConnection('light')
  const afterRestart = {
    transactions: (await reopened.getRepository(TransactionEntity).find()).map(row => ({ hash: row.hash, blockNumber: row.blockNumber })),
    inputs: (await reopened.getRepository(InputEntity).find()).map(row => ({ txHash: row.transactionHash, previousHash: row.outPointTxHash, previousIndex: row.outPointIndex, capacity: row.capacity })),
    outputs: (await reopened.getRepository(OutputEntity).find()).map(row => ({ txHash: row.outPointTxHash, index: row.outPointIndex, status: row.status, capacity: row.capacity })),
  }
  process.stdout.write(JSON.stringify({
    source: 'Neuron v0.204.1 packaged Queue and TransactionPersistor; synthetic-only fixture',
    profileRoot,
    rpcMethods,
    rpcCalls,
    requestedHashes: [fundingHash, spendingHash],
    saveCalls,
    ipcEvents,
    queueCompletionSignal: 'stopAndWait resolved after processing task',
    beforeRestart,
    afterRestart,
    restartExact: JSON.stringify(beforeRestart) === JSON.stringify(afterRestart),
  }))
  await reopened.destroy()
  await new Promise(resolve => rpcServer.close(resolve))
}

main().catch(error => {
  process.stderr.write(`${error.stack || error}\n`)
  rpcServer.close()
  process.exitCode = 1
})
