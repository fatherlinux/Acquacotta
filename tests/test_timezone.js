/**
 * Automated timezone handling tests using Puppeteer
 *
 * Tests that entries are created and displayed correctly when
 * browser timezone differs from configured app timezone.
 *
 * Run with: node tests/test_timezone.js
 * Requires: Running acquacotta-dev container on localhost:5000
 */

const puppeteer = require('puppeteer');

const APP_URL = 'http://localhost:5000';

// Test results tracking
let passed = 0;
let failed = 0;
const results = [];

function log(msg) {
    console.log(`[TEST] ${msg}`);
}

function assert(condition, testName) {
    if (condition) {
        passed++;
        results.push({ name: testName, pass: true });
        log(`✓ ${testName}`);
    } else {
        failed++;
        results.push({ name: testName, pass: false });
        log(`✗ ${testName}`);
    }
}

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function runTests() {
    log('Starting timezone tests...');

    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    try {
        // Test 1: Browser timezone emulation and Automatic option
        await testAutomaticTimezone(browser);

        // Test 2: Different timezones - PM entry appears in PM section
        await testPMEntryWithDifferentTimezones(browser);

        // Test 3: Timer start/stop creates entry with correct timezone
        await testTimerWithDifferentTimezones(browser);

        // Test 4: Same timezone - entries display correctly
        await testSameTimezone(browser);

    } catch (e) {
        log(`Test error: ${e.message}`);
        console.error(e);
    } finally {
        await browser.close();
    }

    // Summary
    console.log('\n' + '='.repeat(50));
    log(`Results: ${passed} passed, ${failed} failed`);
    process.exit(failed > 0 ? 1 : 0);
}

async function testAutomaticTimezone(browser) {
    log('\n--- Test: Automatic timezone option ---');

    const page = await browser.newPage();

    // Emulate Brussels timezone
    await page.emulateTimezone('Europe/Brussels');
    await page.goto(APP_URL, { waitUntil: 'networkidle0' });
    await sleep(1000);

    // Open settings (click nav button with data-view="settings")
    await page.click('nav button[data-view="settings"]');
    await sleep(500);

    // Check the Automatic option text contains Brussels
    const automaticOption = await page.$eval(
        '#timezone option[value="auto"]',
        el => el.textContent
    );

    assert(
        automaticOption.includes('Europe/Brussels'),
        'Automatic option shows detected browser timezone (Brussels)'
    );

    // Change emulated timezone and refresh
    await page.close();

    const page2 = await browser.newPage();
    await page2.emulateTimezone('America/New_York');
    await page2.goto(APP_URL, { waitUntil: 'networkidle0' });
    await sleep(1000);

    await page2.click('nav button[data-view="settings"]');
    await sleep(500);

    const automaticOption2 = await page2.$eval(
        '#timezone option[value="auto"]',
        el => el.textContent
    );

    assert(
        automaticOption2.includes('America/New_York'),
        'Automatic option shows detected browser timezone (New York)'
    );

    await page2.close();
}

async function testPMEntryWithDifferentTimezones(browser) {
    log('\n--- Test: PM entry with different timezones ---');

    const page = await browser.newPage();

    // Browser is Brussels, app will be set to New York
    await page.emulateTimezone('Europe/Brussels');
    await page.goto(APP_URL, { waitUntil: 'networkidle0' });
    await sleep(1000);

    // Open settings and set timezone to America/New_York
    await page.click('nav button[data-view="settings"]');
    await sleep(500);

    await page.select('#timezone', 'America/New_York');
    await sleep(300);

    // Go back to timer view to see week grid
    await page.click('nav button[data-view="timer"]');
    await sleep(500);

    // Find and click a PM + button (afternoon section)
    // Use evaluate to click since the button might be small
    const clicked = await page.evaluate(() => {
        const pmSections = document.querySelectorAll('.week-day-section:nth-child(2)');
        for (const section of pmSections) {
            const label = section.querySelector('.week-day-section-label');
            if (label && (label.textContent.includes('PM') || label.textContent.includes('Afternoon'))) {
                const btn = section.querySelector('.week-section-add-btn');
                if (btn) {
                    btn.click();
                    return true;
                }
            }
        }
        return false;
    });

    if (clicked) {
        await sleep(500);

        // Modal should be open - check that time is in PM range (12:00 or later)
        const timeValue = await page.$eval('#add-time', el => el.value);
        const hour = parseInt(timeValue.split(':')[0]);

        assert(
            hour >= 12,
            `PM + button sets time to PM (got ${timeValue})`
        );

        // Submit the entry
        await page.click('#add-submit');
        await sleep(1000);

        // Check that entry appears in PM section (not AM)
        const pmHasEntry = await page.evaluate(() => {
            const sections = document.querySelectorAll('.week-day-section');
            for (const section of sections) {
                const label = section.querySelector('.week-day-section-label');
                if (label && (label.textContent.includes('PM') || label.textContent.includes('Afternoon'))) {
                    // Check if section has pomodoro entries (not just "—")
                    const content = section.textContent;
                    return !content.includes('—') || section.querySelectorAll('.week-pomo').length > 0;
                }
            }
            return false;
        });

        assert(
            pmHasEntry,
            'Entry appears in PM section after adding via PM + button'
        );
    } else {
        log('Warning: Could not find PM + button');
    }

    await page.close();
}

async function testTimerWithDifferentTimezones(browser) {
    log('\n--- Test: Timer start/stop with different timezones ---');

    const page = await browser.newPage();

    // Browser is Tokyo, app will be set to Los Angeles (big difference)
    await page.emulateTimezone('Asia/Tokyo');
    await page.goto(APP_URL, { waitUntil: 'networkidle0' });
    await sleep(1000);

    // Set timezone to America/Los_Angeles
    await page.click('nav button[data-view="settings"]');
    await sleep(500);
    await page.select('#timezone', 'America/Los_Angeles');
    await sleep(300);

    // Go back to timer view
    await page.click('nav button[data-view="timer"]');
    await sleep(500);

    // Get the current displayed time (should be in LA timezone)
    const clockTime = await page.$eval('#clock-time', el => el.textContent);
    log(`Clock shows: ${clockTime} (should be LA time)`);

    // Start the timer
    await page.click('#btn-start');
    await sleep(1000);

    // Stop the timer immediately
    await page.click('#btn-stop');
    await sleep(1000);

    // Check that an entry was created
    // Navigate to history to verify
    await page.click('nav button[data-view="history"]');
    await sleep(1000);

    const historyContent = await page.$eval('#history-list', el => el.textContent);

    // Should have at least one entry (might say "No entries" if empty)
    const hasEntry = !historyContent.includes('No entries');

    assert(
        hasEntry,
        'Timer creates entry when stopped'
    );

    await page.close();
}

async function testSameTimezone(browser) {
    log('\n--- Test: Same timezone (browser = app) ---');

    const page = await browser.newPage();

    // Both browser and app will be Brussels
    await page.emulateTimezone('Europe/Brussels');
    await page.goto(APP_URL, { waitUntil: 'networkidle0' });
    await sleep(1000);

    // Set timezone to Brussels explicitly
    await page.click('nav button[data-view="settings"]');
    await sleep(500);
    await page.select('#timezone', 'Europe/Brussels');
    await sleep(300);

    // Go back to timer view
    await page.click('nav button[data-view="timer"]');
    await sleep(500);

    // Add a PM entry using evaluate
    const clicked = await page.evaluate(() => {
        const sections = document.querySelectorAll('.week-day-section');
        for (const section of sections) {
            const label = section.querySelector('.week-day-section-label');
            if (label && (label.textContent.includes('PM') || label.textContent.includes('Afternoon'))) {
                const btn = section.querySelector('.week-section-add-btn');
                if (btn) {
                    btn.click();
                    return true;
                }
            }
        }
        return false;
    });

    if (clicked) {
        await sleep(500);

        const timeValue = await page.$eval('#add-time', el => el.value);
        const hour = parseInt(timeValue.split(':')[0]);

        assert(
            hour >= 12,
            `Same TZ: PM + button sets time to PM (got ${timeValue})`
        );

        // Cancel instead of adding (to avoid polluting data)
        await page.click('#add-modal .modal-actions .secondary');
        await sleep(300);
    }

    await page.close();
}

// Run the tests
runTests();
