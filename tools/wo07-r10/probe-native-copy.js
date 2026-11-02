const url = process.argv[2] || 'http://127.0.0.1:19097'
const script = {
  code_hash: '0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8',
  hash_type: 'type',
  args: '0xa2ade6127fcbb7f1ccfe4a886f6b1e9c5c92d837',
}
const scriptHash = '0x28535e1e70eb2ae8c56a829e1f9d3777fdf6b310c9c1dff17e4ae01917e45e62'
const txHash = '0x42dc0f3efabc9134fc2244f5c01c3b52768ba8d23f29c78d839208afa844e435'
const start = '0x15e1a7a'
const end = '0x15e1b35'
let id = 0

async function rpc(method, params = []) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ jsonrpc: '2.0', id: ++id, method, params }),
  })
  const value = await response.json()
  if (value.error) throw new Error(`${method}: ${JSON.stringify(value.error)}`)
  return value.result
}

async function main() {
  const tip = await rpc('get_tip_header')
  const scripts = await rpc('get_scripts')
  const registered = scripts.find(item => item.script.args === script.args && item.script.code_hash === script.code_hash && item.script.hash_type === script.hash_type && item.script_type === 'lock')
  if (!registered) throw new Error('owned R8 Script registration missing from copied native store')
  const query = {
    script,
    script_type: 'lock',
    block_range: [start, end],
    group_by_transaction: true,
  }
  const result = await rpc('get_transactions', [query, 'asc', '0x64', null])
  const matches = result.objects.map(item => ({ hash: item.transaction.hash, blockNumber: item.block_number, txIndex: item.tx_index }))
  const transaction = await rpc('get_transaction', [txHash])
  const success = matches.length === 1 && matches[0].hash === txHash && transaction?.transaction?.hash === txHash && transaction.tx_status?.status === 'committed' && transaction.tx_status.block_hash === '0x4e5c9e8562027923c11a8608b10c399dccb59f145e047eb0f58a8a8b5b56f52c'
  const output = transaction?.transaction?.outputs?.[0]
  if (!success || output?.lock?.args !== script.args || output?.capacity !== '0xe8d4a51000') throw new Error('copied-state RPC result did not match the expected owned transaction/output')
  process.stdout.write(`${JSON.stringify({ rpc: url, tip: { height: tip.number, hash: tip.hash }, registeredScript: { scriptHash, role: registered.script_type, cursor: registered.block_number ?? registered.blockNumber }, range: [start, end], transactions: matches, transactionStatus: transaction.tx_status.status, transactionBlockHash: transaction.tx_status.block_hash, ownedOutput: { capacity: output.capacity, args: output.lock.args }, exactExpectedState: true }, null, 2)}\n`)
}
main().catch(error => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1 })
