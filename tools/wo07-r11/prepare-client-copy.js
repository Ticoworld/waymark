const crypto = require('node:crypto')
const fs = require('node:fs')
const path = require('node:path')

const [sourceArg, configTemplateArg, destinationArg] = process.argv.slice(2)
const source = path.resolve(sourceArg || '')
const template = path.resolve(configTemplateArg || '')
const destination = path.resolve(destinationArg || '')
if (!sourceArg || !configTemplateArg || !destinationArg || !source.includes(`${path.sep}wo07-r10-native-copy2`) || !template.includes(`${path.sep}wo07-r9-owned-source`) || !destination.includes(`${path.sep}wo07-r11-native-store`)) {
  throw new Error('usage: node prepare-client-copy.js <stopped-r10-native-copy> <r9-testnet-config-template> <new-r11-native-store>')
}
const sourceStore = path.join(source, 'data', 'store')
if (!fs.existsSync(path.join(sourceStore, 'CURRENT')) || !fs.existsSync(path.join(template, 'config.toml'))) throw new Error('source store/config template missing')
if (fs.existsSync(destination)) throw new Error(`refusing to overwrite destination: ${destination}`)
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')
fs.mkdirSync(path.join(destination, 'data', 'network'), { recursive: true })
fs.cpSync(sourceStore, path.join(destination, 'data', 'store'), { recursive: true, errorOnExist: true })
const slash = value => value.replaceAll('\\', '/')
let config = fs.readFileSync(path.join(template, 'config.toml'), 'utf8')
config = config
  .replaceAll(slash(path.join(template, 'data', 'store')), slash(path.join(destination, 'data', 'store')))
  .replaceAll(slash(path.join(template, 'data', 'network')), slash(path.join(destination, 'data', 'network')))
  .replace(/\/tcp\/19150/g, '/tcp/19170')
  .replace('127.0.0.1:19087', '127.0.0.1:19100')
if (config.includes(slash(path.join(template, 'data', 'store'))) || config.includes('127.0.0.1:19087') || config.includes('bootnodes = []')) throw new Error('expected peer-enabled isolated config was not produced')
fs.writeFileSync(path.join(destination, 'config.toml'), config, { flag: 'wx' })
const files = []
const walk = dir => {
  for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
    const file = path.join(dir, item.name)
    if (item.isDirectory()) walk(file)
    else files.push({ relative: path.relative(sourceStore, file), bytes: fs.statSync(file).size, sourceHash: hash(file), copyHash: hash(path.join(destination, 'data', 'store', path.relative(sourceStore, file))) })
  }
}
walk(sourceStore)
if (files.some(file => file.sourceHash !== file.copyHash)) throw new Error('native store copy hash mismatch')
process.stdout.write(`${JSON.stringify({ sourceStore, destinationStore: path.join(destination, 'data', 'store'), fileCount: files.length, bytes: files.reduce((n, file) => n + file.bytes, 0), allHashesMatch: true, freshNetworkDirectory: true, rpc: '127.0.0.1:19100', p2p: '127.0.0.1:19170', bootnodesEnabled: true, maxOutboundPeers: 4 }, null, 2)}\n`)
