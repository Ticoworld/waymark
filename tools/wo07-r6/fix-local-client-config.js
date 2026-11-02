const fs = require('node:fs')
const path = require('node:path')

const root = path.resolve(process.argv[2] || '')
if (!root.includes(`${path.sep}wo07-r6-light-store`)) throw new Error('expected the WO07-R6 disposable store directory')
const configPath = path.join(root, 'config.toml')
let config = fs.readFileSync(configPath, 'utf8')
config = config
  .replace(/bootnodes\s*=\s*\[[\s\S]*?\n\]/, 'bootnodes = []')
  .replace('max_peers = 0', 'max_peers = 1')
  .replace('max_outbound_peers = 0', 'max_outbound_peers = 1')
fs.writeFileSync(configPath, config)
process.stdout.write(JSON.stringify({ configPath, bootnodesDisabled: /bootnodes\s*=\s*\[\s*\]/.test(config), maxOutboundPeers: /max_outbound_peers\s*=\s*1/.test(config) }))
