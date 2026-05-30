const { ClassicLevel } = require('classic-level');
const path = require('path');
const fs = require('fs');

// Source paths
const settingsDbPath = path.join('C:', 'Users', 'lenovo', 'Desktop', 'San', 'Fun_Projects', 'Coral Project', 'stayfree_temp_copy');

// Output files
const jsonOutputPath = path.join('C:', 'Users', 'lenovo', 'Desktop', 'San', 'Fun_Projects', 'Coral Project', 'stayfree_raw_dump.json');
const csvOutputPath = path.join('C:', 'Users', 'lenovo', 'Desktop', 'San', 'Fun_Projects', 'Coral Project', 'stayfree_clean_analytics.csv');

// Clean and convert string values (stripping Chromium binary noise)
function cleanValueString(buffer) {
  if (!Buffer.isBuffer(buffer)) return '';
  const text = buffer.toString('utf8');
  
  // If it's JSON, find start and parse
  const jsonStart = text.indexOf('{');
  const arrayStart = text.indexOf('[');
  const startIdx = (jsonStart !== -1 && arrayStart !== -1)
    ? Math.min(jsonStart, arrayStart)
    : (jsonStart !== -1 ? jsonStart : arrayStart);

  if (startIdx !== -1) {
    try {
      return JSON.parse(text.substring(startIdx));
    } catch (e) {
      // Not valid JSON
    }
  }
  
  // Return printable ASCII/UTF-8 character strings
  return text.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]/g, '').trim();
}

async function extractDb(dbPath, name) {
  console.log(`\n========================================\nOPENING DATABASE: ${name}\nPath: ${dbPath}\n========================================`);
  const data = {};
  
  if (!fs.existsSync(dbPath)) {
    console.log(`Database path does not exist: ${dbPath}`);
    return data;
  }
  
  const db = new ClassicLevel(dbPath, { keyEncoding: 'buffer', valueEncoding: 'buffer' });
  
  try {
    let count = 0;
    for await (const [key, value] of db.iterator()) {
      count++;
      const keyStr = key.toString('utf8').replace(/[\x00-\x1F]/g, '').trim();
      const finalKey = keyStr || `bin-key-${count}`;
      data[finalKey] = cleanValueString(value);
    }
    console.log(`Successfully extracted ${count} records from ${name}`);
  } catch (err) {
    console.error(`Error reading ${name}:`, err.message);
  } finally {
    await db.close();
  }
  
  return data;
}

async function main() {
  const result = {
    settings_db: {}
  };
  
  // 1. Extract Settings Database
  if (fs.existsSync(settingsDbPath)) {
    result.settings_db = await extractDb(settingsDbPath, 'Local Extension Settings');
  }
  
  // 2. Save Raw JSON Dump
  fs.writeFileSync(jsonOutputPath, JSON.stringify(result, null, 2), 'utf-8');
  console.log(`\nRaw database JSON dump written to:\n${jsonOutputPath}`);
  
  // 3. Map records to CSV output for Coral
  const csvRows = [];
  
  const addCsvRow = (domain, platform, durationSec, timestamp, source) => {
    if (!domain || domain === 'unknown') return;
    csvRows.push({
      domain_or_app: domain,
      platform: platform,
      duration_seconds: Number(durationSec).toFixed(2),
      date_or_timestamp: timestamp,
      source: source
    });
  };

  // Inspect settings keys
  for (const [k, v] of Object.entries(result.settings_db)) {
    // Array variable directly
    let targetArray = null;
    
    if (Array.isArray(v)) {
      targetArray = v;
    } else if (v && typeof v === 'object' && Array.isArray(v.value)) {
      // Chrome V8 wrapped array (like average-prev-sessions-total-usage...)
      targetArray = v.value;
    }
    
    if (targetArray) {
      targetArray.forEach(item => {
        if (item && typeof item === 'object') {
          const domain = item.domain || item.appId || item.appName;
          const platform = item.platform || (item.appId ? 'android' : 'web');
          
          let durationSec = 0;
          if (item.endedAt && item.startedAt) {
            durationSec = (item.endedAt - item.startedAt) / 1000;
          } else if (item.end && item.startedAt) {
            durationSec = (item.end - item.startedAt) / 1000;
          } else {
            durationSec = (item.timeSpent || item.active || 0) / 1000;
          }
          
          let timeStr = 'N/A';
          const rawTime = item.startedAt || item.date;
          if (rawTime) {
            try {
              timeStr = new Date(rawTime).toISOString();
            } catch (err) {
              timeStr = String(rawTime);
            }
          }
          
          addCsvRow(domain, platform, durationSec, timeStr, `Settings Key: ${k.substring(0, 30)}`);
        }
      });
    } else if (v && typeof v === 'object') {
      // If it's a key-value stats map of domain -> duration
      for (const [subkey, subval] of Object.entries(v)) {
        if (subval && typeof subval === 'object') {
          const durationSec = (subval.timeSpent || subval.active || 0) / 1000;
          if (durationSec > 0) {
            addCsvRow(subkey, 'web', durationSec, 'N/A', 'Settings Map Object');
          }
        }
      }
    }
  }

  // Write CSV file
  const headers = ['domain_or_app', 'platform', 'duration_seconds', 'date_or_timestamp', 'source'];
  const csvContent = [
    headers.join(','),
    ...csvRows.map(row => headers.map(h => {
      let val = row[h] !== undefined ? String(row[h]) : '';
      if (val.includes(',') || val.includes('"') || val.includes('\n')) {
        val = `"${val.replace(/"/g, '""')}"`;
      }
      return val;
    }).join(','))
  ].join('\n');

  fs.writeFileSync(csvOutputPath, csvContent, 'utf-8');
  console.log(`Cleaned CSV analytics written to:\n${csvOutputPath}`);
  console.log(`\nSuccessfully extracted ${csvRows.length} total usage database events!`);
}

main().catch(err => {
  console.error("Critical error in extractor main loop:", err);
});
