const fs = require('node:fs')
const path = require('node:path')

const [archivePath, outputPath] = process.argv.slice(2)
if (!archivePath || !outputPath) throw new Error('usage: node extract-neuron-asar.js <app.asar> <output-directory>')

const archive = fs.readFileSync(archivePath)
if (archive.readUInt32LE(0) !== 4) throw new Error('unsupported ASAR header format')
const headerLength = archive.readUInt32LE(12)
const header = JSON.parse(archive.subarray(16, 16 + headerLength).toString('utf8'))
const payloadStart = 16 + headerLength
const root = path.resolve(outputPath)

function extract(node, relative = '') {
  for (const [name, entry] of Object.entries(node.files || {})) {
    if (name.includes('/') || name === '.' || name === '..') throw new Error(`invalid ASAR entry: ${name}`)
    const child = path.resolve(root, relative, name)
    if (child !== root && !child.startsWith(root + path.sep)) throw new Error(`ASAR path escaped output: ${name}`)
    if (entry.files) {
      fs.mkdirSync(child, { recursive: true })
      extract(entry, path.join(relative, name))
      continue
    }
    if (entry.unpacked) throw new Error(`unexpected unpacked ASAR entry: ${path.join(relative, name)}`)
    const offset = Number(entry.offset)
    const size = Number(entry.size)
    const start = payloadStart + offset
    const end = start + size
    if (!Number.isSafeInteger(offset) || !Number.isSafeInteger(size) || start < payloadStart || end > archive.length) {
      throw new Error(`invalid ASAR range: ${path.join(relative, name)}`)
    }
    fs.mkdirSync(path.dirname(child), { recursive: true })
    fs.writeFileSync(child, archive.subarray(start, end), { flag: 'wx' })
  }
}

fs.mkdirSync(root, { recursive: true })
extract(header)
process.stdout.write(JSON.stringify({ archivePath, outputPath: root, files: countFiles(header), payloadBytes: archive.length - payloadStart }))

function countFiles(node) {
  return Object.values(node.files || {}).reduce((count, entry) => count + (entry.files ? countFiles(entry) : 1), 0)
}
