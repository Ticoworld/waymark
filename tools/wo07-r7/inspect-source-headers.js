const { DatabaseSync } = require('node:sqlite')

const dbPath = process.argv[2]
if (!dbPath) throw new Error('usage: node --experimental-sqlite inspect-source-headers.js <source.sqlite>')

const db = new DatabaseSync(dbPath, { readOnly: true })
const rows = db.prepare("select hex(key) as k, hex(value) as v from kv where substr(key,1,1)=x'60'").all()
const scriptArgs = 'BC5882C4309431EE23AD7BBAD4B5C3325539EEBD'
const selected = rows.filter(row => row.k.includes(scriptArgs))
const scriptEnd = selected[0]?.k.indexOf(scriptArgs) + scriptArgs.length
if (!selected.length || scriptEnd < scriptArgs.length) throw new Error('fixture Script index rows not found')

const byHeight = new Map()
for (const row of selected) {
  const height = Number.parseInt(row.k.slice(scriptEnd, scriptEnd + 16), 16)
  const txHash = `0x${row.v.toLowerCase()}`
  if (!byHeight.has(height)) byHeight.set(height, new Set())
  byHeight.get(height).add(txHash)
}

for (const [height, txHashes] of [...byHeight].sort(([a], [b]) => a - b)) {
  const heightKey = Buffer.from(`C0${height.toString(16).padStart(16, '0')}`, 'hex')
  const mapping = db.prepare('select value from kv where key=?').get(heightKey)
  const blockHash = mapping?.value
  const header = blockHash && db.prepare('select value from kv where key=?').get(Buffer.concat([Buffer.from([0xa0]), blockHash]))
  console.log(JSON.stringify({
    height,
    blockHash: blockHash ? `0x${Buffer.from(blockHash).toString('hex')}` : null,
    headerPresent: Boolean(header),
    headerBytes: header?.value.length ?? null,
    txHashes: [...txHashes].sort(),
  }))
}
db.close()
