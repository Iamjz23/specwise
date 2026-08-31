import cron from 'node-cron';
import { exec } from 'child_process';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('Price Scraper Scheduler Started');
console.log('Will scrape prices every 12 hours (at 00:00 and 12:00 UTC)');

// Schedule scraper to run every 12 hours (at midnight and noon UTC)
cron.schedule('0 0,12 * * *', async () => {
  console.log('\n=== Running scheduled price scrape ===');
  console.log('Time:', new Date().toISOString());
  
  try {
    exec('node scraper.js', (error, stdout, stderr) => {
      if (error) {
        console.error(`Scraper error: ${error.message}`);
        return;
      }
      if (stderr) {
        console.error(`Scraper stderr: ${stderr}`);
        return;
      }
      console.log(`Scraper output:\n${stdout}`);
      
      // Log to file
      const logFile = join(__dirname, 'scrape-log.txt');
      const logEntry = `\n[${new Date().toISOString()}] Scheduled scrape completed successfully\n`;
      fs.appendFileSync(logFile, logEntry);
    });
  } catch (err) {
    console.error('Failed to start scraper:', err);
  }
});

console.log('Scheduler is running. Press Ctrl+C to stop.');

// Keep the process alive
process.on('SIGINT', () => {
  console.log('\nScheduler stopped.');
  process.exit(0);
});
