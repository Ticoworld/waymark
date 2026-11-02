const crypto = require('node:crypto')
const fs = require('node:fs')
const path = require('node:path')

const [sourceArg, templateArg, destinationArg] = process.argv.slice(2)
const source = path.resolve(sourceArg || '')
const template = path.resolve(templateArg || '')
const destination = path.resolve(destinationArg || '')
if (!sourceArg || !templateArg || !destinationArg || !/(wo07-r10-native-copy2|wo07-r11-native-store-phase2)/i.test(source) || !template.includes(`${path.sep}wo07-r9-owned-source`) || !destination.includes(`${path.sep}wo07-r12-pending-client`)) {
  throw new Error('usage: node prepare-pending-client.js <stopped-r10-or-r11-store-root> <r9-config-template> <new-r12-client-root>')
}
const sourceStore = path.join(source, 'data', 'store')
if (!fs.existsSync(path.join(sourceStore, 'CURRENT')) || !fs.existsSync(path.join(template, 'config.toml'))) throw new Error('native source or config template missing')
if (fs.existsSync(destination)) throw new Error(`refusing to overwrite destination: ${destination}`)
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')
const targetStore = path.join(destination, 'data', 'store')
fs.mkdirSync(path.join(destination, 'data', 'network'), { recursive: true })
fs.cpSync(sourceStore, targetStore, { recursive: true, errorOnExist: true })
const slash = value => value.replaceAll('\\', '/')
let config = fs.readFileSync(path.join(template, 'config.toml'), 'utf8')
config = config
  .replaceAll(slash(path.join(template, 'data', 'store')), slash(targetStore))
  .replaceAll(slash(path.join(template, 'data', 'network')), slash(path.join(destination, 'data', 'network')))
  .replace('127.0.0.1:19087', '127.0.0.1:19110')
  .replace(/\/tcp\/19150/g, '/tcp/19180')
  .replace(/bootnodes\s*=\s*\[[\s\S]*?\]/m, 'bootnodes = []')
  .replace(/^max_outbound_peers\s*=.*$/m, 'max_outbound_peers = 1')
if (config.includes(slash(path.join(template, 'data', 'store'))) || !config.includes('bootnodes = []') || !config.includes('max_outbound_peers = 1')) throw new Error('isolated offline config validation failed')
fs.writeFileSync(path.join(destination, 'config.toml'), config, { flag: 'wx' })
const files = []
const walk = dir => {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const file = path.join(dir, entry.name)
    if (entry.isDirectory()) walk(file)
    else files.push({ file, relative: path.relative(sourceStore, file) })
  }
}
walk(sourceStore)
for (const item of files) if (hash(item.file) !== hash(path.join(targetStore, item.relative))) throw new Error(`copy hash mismatch: ${item.relative}`)
process.stdout.write(`${JSON.stringify({ sourceStore, destinationStore: targetStore, fileCount: files.length, bytes: files.reduce((n, item) => n + fs.statSync(item.file).size, 0), allHashesMatch: true, freshNetworkDirectory: true, bootnodes: 0, rpc: '127.0.0.1:19110', p2p: '127.0.0.1:19180' }, null, 2)}\n`)
