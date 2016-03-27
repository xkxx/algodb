#!/usr/bin/env node
'use strict'

let fs = require('fs');

let convert = (filename) => {
  let content = fs.readFileSync(filename, 'utf-8');
  fs.writeFileSync(filename + '.old', content, 'utf-8'); // backup
  let stream = fs.createWriteStream(filename);
  JSON.parse(content).forEach((row) => {
    stream.write(JSON.stringify(row) + '\n');
  });
  stream.end();
}
convert(process.argv[2]);
