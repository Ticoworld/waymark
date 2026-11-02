const crypto = require('node:crypto')
const fs = require('node:fs')
const path = require('node:path')

const [sourceArg, configTemplateArg, destinationArg] = process.argv.slice(2)
const source = path.resolve(sourceArg || '')
const template = path.resolve(configTemplateArg || '')
const destination = path.resolve(destinationArg || '')
if (!sourceArg || !configTemplateArg || !destinationArg || !source.includes(`${path.sep}wo07-r7-imported-store`) || !template.includes(`${path.sep}wo07-r10-native-copy2`) || !destination.includes(`${path.sep}wo07-r11-preimport-node`)) {
  throw new Error('usage: node prepare-preimport-client.js <stopped-r7-store-root> <offline-r10-config-root> <new-r11-preimport-root>')
}
const sourceStore = path.join(source, 'data', 'store')
if (!fs.existsSync(path.join(sourceStore, 'CURRENT')) || !fs.existsSync(path.join(template, 'config.toml'))) throw new Error('R7 store/config template missing')
if (fs.existsSync(destination)) throw new Error(`refusing to overwrite destination: ${destination}`)
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')
fs.mkdirSync(path.join(destination, 'data', 'network'), { recursive: true })
fs.cpSync(sourceStore, path.join(destination, 'data', 'store'), { recursive: true, errorOnExist: true })
const slash = value => value.replaceAll('\\', '/')
let config = fs.readFileSync(path.join(template, 'config.toml'), 'utf8')
config = config
  .replaceAll(slash(path.join(template, 'data', 'store')), slash(path.join(destination, 'data', 'store')))
  .replaceAll(slash(path.join(template, 'data', 'network')), slash(path.join(destination, 'data', 'network')))
  .replace('127.0.0.1:19097', '127.0.0.1:19100')
  .replace(/\/tcp\/19160/g, '/tcp/19170')
if (config.includes(slash(path.join(template, 'data', 'store'))) || !config.includes('bootnodes = []') || !config.includes('max_outbound_peers = 1')) throw new Error('offline preimport config isolation failed')
fs.writeFileSync(path.join(destination, 'config.toml'), config, { flag: 'wx' })
const copied = []
const walk = dir => {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const file = path.join(dir, entry.name)
    if (entry.isDirectory()) walk(file)
    else copied.push({ relative: path.relative(sourceStore, file), bytes: fs.statSync(file).size, sourceHash: hash(file), copyHash: hash(path.join(destination, 'data', 'store', path.relative(sourceStore, file))) })
  }
}
walk(sourceStore)
if (copied.some(file => file.sourceHash !== file.copyHash)) throw new Error('preimport store copy hash mismatch')
process.stdout.write(`${JSON.stringify({ sourceStore, destinationStore: path.join(destination, 'data', 'store'), fileCount: copied.length, bytes: copied.reduce((n, file) => n + file.bytes, 0), allHashesMatch: true, freshNetworkDirectory: true, bootnodes: 0, maxOutboundPeers: 1, rpc: '127.0.0.1:19100' }, null, 2)}\n`)
