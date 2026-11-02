const fs = require('node:fs')
const path = require('node:path')

const [sourceArg, destinationArg] = process.argv.slice(2)
const source = path.resolve(sourceArg || '')
const destination = path.resolve(destinationArg || '')
if (!sourceArg || !destinationArg || !destination.includes(`${path.sep}wo07-r9-owned-source`)) {
  throw new Error('usage: node prepare-testnet-client.js <r7-imported-store-root> <new-wo07-r9-owned-source-root>')
}
if (!fs.existsSync(path.join(source, 'data/store/CURRENT')) || !fs.existsSync(path.join(source, 'config.toml'))) throw new Error('R7 authority source is incomplete')
if (fs.existsSync(destination)) throw new Error(`refusing to overwrite existing destination: ${destination}`)
fs.mkdirSync(path.join(destination, 'data/network'), { recursive: true })
fs.cpSync(path.join(source, 'data/store'), path.join(destination, 'data/store'), { recursive: true, errorOnExist: true })
const slash = value => value.replaceAll('\\', '/')
let config = fs.readFileSync(path.join(source, 'config.toml'), 'utf8')
config = config
  .replaceAll(slash(path.join(source, 'data/store')), slash(path.join(destination, 'data/store')))
  .replaceAll(slash(path.join(source, 'data/network')), slash(path.join(destination, 'data/network')))
  .replace('127.0.0.1:19076', '127.0.0.1:19087')
  .replace('127.0.0.1/tcp/19140', '127.0.0.1/tcp/19150')
if (config.includes(slash(path.join(source, 'data/store'))) || config.includes('127.0.0.1:19076')) throw new Error('failed to isolate copied-client configuration')
fs.writeFileSync(path.join(destination, 'config.toml'), config, { flag: 'wx' })
const files = []
function walk(dir) {
  for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, item.name)
    if (item.isDirectory()) walk(full)
    else files.push({ path: path.relative(destination, full), bytes: fs.statSync(full).size })
  }
}
walk(path.join(destination, 'data/store'))
process.stdout.write(`${JSON.stringify({ source, destination, storeFiles: files.length, storeBytes: files.reduce((sum, item) => sum + item.bytes, 0), rpc: '127.0.0.1:19087', p2p: '127.0.0.1:19150' })}\n`)
