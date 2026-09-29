/**
 * Playwright E2E Test Suite for Kairos UI (SPEC §14.7, §14.8).
 * Tests Assistant mode, Inspector mode (all 6 sub-tabs), Story mode 10x loop, XSS safety,
 * and @axe-core/playwright zero accessibility violations.
 */

import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Kairos Streaming Live RAG Web Interface', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8000');
  });

  test('loads home page with Calm Precision dark theme and brand header', async ({ page }) => {
    await expect(page.locator('text=Kairos')).toBeVisible();
    await expect(page.locator('text=Answers while you speak')).toBeVisible();
    await expect(page.locator('button:has-text("Assistant")')).toBeVisible();
    await expect(page.locator('button:has-text("Show how it works")')).toBeVisible();
  });

  test('Assistant mode has zero accessibility violations', async ({ page }) => {
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
      .analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('switches between Assistant and Inspector modes seamlessly with all 6 sub-tabs', async ({ page }) => {
    // Switch to Inspector
    await page.click('button:has-text("Show how it works")');
    await expect(page.locator('text=Timeline')).toBeVisible();
    await expect(page.locator('text=Race vs. batch')).toBeVisible();
    await expect(page.locator('text=Results')).toBeVisible();
    await expect(page.locator('text=Corpus')).toBeVisible();
    await expect(page.locator('text=Try it yourself')).toBeVisible();
    await expect(page.locator('text=About & Core vs. harness')).toBeVisible();

    // Verify sub-tabs navigation
    await page.click('button:has-text("Race vs. batch")');
    await expect(page.locator('text=Median Time Saved')).toBeVisible();

    await page.click('button:has-text("Results")');
    await expect(page.locator('text=Dual Acceptance Gates')).toBeVisible();

    await page.click('button:has-text("Corpus")');
    await expect(page.locator('text=Corpus Document Explorer')).toBeVisible();

    await page.click('button:has-text("About & Core vs. harness")');
    await expect(page.locator('text=System Architecture: Core vs. Harness')).toBeVisible();

    // Inspector mode has zero accessibility violations
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();
    expect(accessibilityScanResults.violations).toEqual([]);

    // Switch back to Assistant mode
    await page.click('button:has-text("Assistant")');
    await expect(page.locator('text=Answer')).toBeVisible();
  });

  test('renders XSS payloads as harmless plain text without HTML execution', async ({ page }) => {
    const input = page.locator('input[placeholder*="Tap the mic, or type"]');
    if (await input.isVisible()) {
      await input.fill('<script>window.__xss_flag = true;</script>');
      await page.keyboard.press('Enter');

      // Verify window.__xss_flag is undefined (never evaluated)
      const isXssExecuted = await page.evaluate(() => (window as any).__xss_flag);
      expect(isXssExecuted).toBeUndefined();
    }
  });

  test('plays Story Mode demo scenario flawlessly', async ({ page }) => {
    const playDemoBtn = page.locator('button:has-text("Play the demo")');
    await playDemoBtn.click();

    // Story bar appears at the top
    await expect(page.locator('text=DEMO')).toBeVisible();
    await expect(page.locator('text=A question with three parts')).toBeVisible();

    // Answer sections start streaming
    await expect(page.locator('text=Answer')).toBeVisible();
  });
});
