const path = require('node:path')
const Module = require('node:module')
const os = require('node:os')
const appRoot = path.resolve(process.argv[2] || '')
const url = process.argv[3] || 'http://127.0.0.1:19100'
if (!appRoot) throw new Error('usage: node probe-boundaries.js <extracted-neuron-app> [light-rpc-url]')
process.env.NODE_PATH = [path.join(appRoot, 'node_modules'), process.env.NODE_PATH].filter(Boolean).join(path.delimiter)
require('node:module').Module._initPaths()
const originalLoad = Module._load
Module._load = function (request, parent, isMain) {
  if (request === 'electron') return { app: { isPackaged: true, getPath: name => path.join(os.tmpdir(), name), getName: () => 'Neuron-WO07-R11', getVersion: () => '0.204.1' } }
  return originalLoad.call(this, request, parent, isMain)
}
const LightRPC = require(path.join(appRoot, 'dist/utils/ckb-rpc')).LightRPC
const rpc = new LightRPC(url)
const script = { codeHash: '0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8', hashType: 'type', args: '0xa2ade6127fcbb7f1ccfe4a886f6b1e9c5c92d837' }
const H = 22944378
const hex = n => `0x${n.toString(16)}`

async function query(from, to) {
  const result = await rpc.getTransactions({ script, scriptType: 'lock', blockRange: [hex(from), hex(to)] }, 'asc', '0x64', undefined)
  return result.txs.map(item => ({ hash: item.txHash, blockNumber: item.blockNumber, txIndex: item.txIndex }))
}

async function main() {
  const atH = await query(H, H + 1)
  const atHPlusOne = await query(H + 1, H + 2)
  const beforeH = await query(H - 1, H)
  const expected = '0x42dc0f3efabc9134fc2244f5c01c3b52768ba8d23f29c78d839208afa844e435'
  if (atH.length || beforeH.length || atHPlusOne.length !== 1 || atHPlusOne[0].hash !== expected) throw new Error('half-open H/H+1 range assertion failed')
  process.stdout.write(`${JSON.stringify({ handoffHeight: H, ranges: { beforeH: { range: [hex(H - 1), hex(H)], results: beforeH }, atH: { range: [hex(H), hex(H + 1)], results: atH }, atHPlusOne: { range: [hex(H + 1), hex(H + 2)], results: atHPlusOne } }, halfOpenBoundaryCorrect: true }, null, 2)}\n`)
}
main().catch(error => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1 })
