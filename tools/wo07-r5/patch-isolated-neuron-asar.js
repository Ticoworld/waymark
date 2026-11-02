const fs = require('node:fs')
const crypto = require('node:crypto')

const [sourcePath, destinationPath] = process.argv.slice(2)
if (!sourcePath || !destinationPath) {
  throw new Error('usage: node patch-isolated-neuron-asar.js source.asar destination.asar')
}

const source = fs.readFileSync(sourcePath)
const headerJsonLength = source.readUInt32LE(12)
const oldHeaderText = source.subarray(16, 16 + headerJsonLength).toString('utf8')
const header = JSON.parse(oldHeaderText)

function entryAt(relativePath) {
  let entry = header
  for (const part of relativePath.split('/')) entry = entry.files[part]
  return entry
}

const mainPath = 'dist/main.js'
const mainEntry = entryAt(mainPath)
const oldMainOffset = Number(mainEntry.offset)
const oldMainSize = mainEntry.size
const payloadStart = 16 + headerJsonLength
const oldMain = source.subarray(payloadStart + oldMainOffset, payloadStart + oldMainOffset + oldMainSize)
const injection = 'electron_1.app.setPath("userData", process.env.WO07_R5_USER_DATA);\n'
const needle = 'const app_1 = tslib_1.__importDefault(require("./controllers/app"));'
if (!oldMain.toString('utf8').includes(needle)) throw new Error('unexpected Neuron v0.204.1 main.js')
const newMain = Buffer.from(oldMain.toString('utf8').replace(needle, `${injection}${needle}`))
const delta = newMain.length - oldMainSize
const newPayload = Buffer.concat([
  source.subarray(payloadStart, payloadStart + oldMainOffset),
  newMain,
  source.subarray(payloadStart + oldMainOffset + oldMainSize),
])

const hash = crypto.createHash('sha256').update(newMain).digest('hex')
mainEntry.size = newMain.length
mainEntry.integrity.hash = hash
mainEntry.integrity.blocks = [hash]

function updateOffsets(node) {
  for (const child of Object.values(node.files || {})) {
    if (child.files) {
      updateOffsets(child)
    } else if (!child.unpacked && child.offset !== undefined) {
      const offset = Number(child.offset)
      if (offset > oldMainOffset) child.offset = String(offset + delta)
    }
  }
}

updateOffsets(header)
const newHeader = Buffer.from(JSON.stringify(header))
const prefix = Buffer.alloc(16)
prefix.writeUInt32LE(4, 0)
prefix.writeUInt32LE(newHeader.length + 8, 4)
prefix.writeUInt32LE(newHeader.length + 4, 8)
prefix.writeUInt32LE(newHeader.length, 12)
fs.writeFileSync(destinationPath, Buffer.concat([prefix, newHeader, newPayload]))

const output = fs.readFileSync(destinationPath)
const outputHeaderLength = output.readUInt32LE(12)
const outputHeader = JSON.parse(output.subarray(16, 16 + outputHeaderLength).toString('utf8'))
let check = outputHeader
for (const part of mainPath.split('/')) check = check.files[part]
const outputMainOffset = Number(check.offset)
const outputMain = output.subarray(
  16 + outputHeaderLength + outputMainOffset,
  16 + outputHeaderLength + outputMainOffset + check.size
)
if (crypto.createHash('sha256').update(outputMain).digest('hex') !== hash) {
  throw new Error('patched entry integrity check failed')
}
if (!outputMain.toString('utf8').includes('WO07_R5_USER_DATA')) {
  throw new Error('isolated userData override missing from patched entry')
}
process.stdout.write(JSON.stringify({
  mainPath,
  originalBytes: oldMainSize,
  patchedBytes: newMain.length,
  archiveBytes: output.length,
  headerBytes: newHeader.length,
  patchedMainSha256: hash,
  userDataOverrideVerified: true,
}))
