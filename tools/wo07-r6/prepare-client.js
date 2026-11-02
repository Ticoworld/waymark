const fs = require('node:fs')
const path = require('node:path')

const [r3Root, isolatedRoot] = process.argv.slice(2)
if (!r3Root || !isolatedRoot) throw new Error('usage: node prepare-client.js <r3-isolated-root> <new-isolated-root>')
const source = path.resolve(r3Root)
const destination = path.resolve(isolatedRoot)
if (!fs.existsSync(path.join(source, 'data/store/CURRENT'))) throw new Error('R3 source store is missing')
if (fs.existsSync(destination)) throw new Error(`refusing to overwrite existing test directory: ${destination}`)

fs.mkdirSync(destination, { recursive: true })
fs.mkdirSync(path.join(destination, 'data'), { recursive: true })
fs.cpSync(path.join(source, 'data/store'), path.join(destination, 'data/store'), { recursive: true, errorOnExist: true })
fs.mkdirSync(path.join(destination, 'data/network'), { recursive: true })

let config = fs.readFileSync(path.join(source, 'config/testnet-isolated.toml'), 'utf8')
config = config
  .replaceAll(path.resolve(source, 'data/store').replaceAll('\\', '/'), path.join(destination, 'data/store').replaceAll('\\', '/'))
  .replaceAll(path.resolve(source, 'data/network').replaceAll('\\', '/'), path.join(destination, 'data/network').replaceAll('\\', '/'))
  .replace('127.0.0.1:19055', '127.0.0.1:19065')
  .replace('127.0.0.1/tcp/19119', '127.0.0.1/tcp/19129')
  .replace('max_peers = 16', 'max_peers = 0')
  .replace('max_outbound_peers = 4', 'max_outbound_peers = 0')
fs.writeFileSync(path.join(destination, 'config.toml'), config, { flag: 'wx' })

const copiedFiles = []
function visit(dir) {
  for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, item.name)
    if (item.isDirectory()) visit(full)
    else copiedFiles.push({ path: path.relative(destination, full), bytes: fs.statSync(full).size })
  }
}
visit(path.join(destination, 'data/store'))
process.stdout.write(JSON.stringify({ destination, storeFileCount: copiedFiles.length, storeBytes: copiedFiles.reduce((sum, file) => sum + file.bytes, 0), config: path.join(destination, 'config.toml') }))
