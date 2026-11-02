const crypto = require('node:crypto')
const fs = require('node:fs')
const path = require('node:path')

const [sourceArg, destinationArg] = process.argv.slice(2)
const source = path.resolve(sourceArg || '')
const destination = path.resolve(destinationArg || '')
if (!sourceArg || !destinationArg || !source.includes(`${path.sep}wo07-r9-owned-source`) || !destination.includes(`${path.sep}wo07-r10-native-copy`)) {
  throw new Error('usage: node clone-quiescent-store.js <stopped-r9-source-root> <new-r10-copy-root>')
}
const sourceStore = path.join(source, 'data', 'store')
const sourceConfig = path.join(source, 'config.toml')
if (!fs.existsSync(path.join(sourceStore, 'CURRENT')) || !fs.existsSync(sourceConfig)) throw new Error('R9 source store/config missing')
if (fs.existsSync(destination)) throw new Error(`refusing to overwrite destination: ${destination}`)

const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')
fs.mkdirSync(path.join(destination, 'data', 'network'), { recursive: true })
fs.cpSync(sourceStore, path.join(destination, 'data', 'store'), { recursive: true, errorOnExist: true })
const slash = value => value.replaceAll('\\', '/')
let config = fs.readFileSync(sourceConfig, 'utf8')
config = config
  .replaceAll(slash(sourceStore), slash(path.join(destination, 'data', 'store')))
  .replaceAll(slash(path.join(source, 'data', 'network')), slash(path.join(destination, 'data', 'network')))
  .replace(/bootnodes\s*=\s*\[[\s\S]*?\]/m, 'bootnodes = []')
  .replace(/max_outbound_peers\s*=\s*\d+/, 'max_outbound_peers = 1')
  .replace(/\/tcp\/19150/g, '/tcp/19160')
  .replace('127.0.0.1:19087', '127.0.0.1:19097')
if (config.includes(slash(sourceStore)) || config.includes('127.0.0.1:19087') || !config.includes('bootnodes = []') || !config.includes('max_outbound_peers = 1')) {
  throw new Error('destination config isolation failed')
}
fs.writeFileSync(path.join(destination, 'config.toml'), config, { flag: 'wx' })

const copied = []
const walk = directory => {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const file = path.join(directory, entry.name)
    if (entry.isDirectory()) walk(file)
    else copied.push({ relativePath: path.relative(sourceStore, file), bytes: fs.statSync(file).size, sourceSha256: hash(file), copySha256: hash(path.join(destination, 'data', 'store', path.relative(sourceStore, file))) })
  }
}
walk(sourceStore)
if (copied.some(file => file.sourceSha256 !== file.copySha256)) throw new Error('copied store hash mismatch')
process.stdout.write(`${JSON.stringify({ sourceStore, destinationStore: path.join(destination, 'data', 'store'), files: copied.length, bytes: copied.reduce((sum, file) => sum + file.bytes, 0), allHashesMatch: true, networkDirectoryFresh: true, bootnodes: 0, maxOutboundPeers: 1, rpc: '127.0.0.1:19097', p2p: '127.0.0.1:19160' }, null, 2)}\n`)
