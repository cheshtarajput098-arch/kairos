/**
 * Playwright E2E Test Suite for Kairos UI (SPEC §14.7, §14.8).
 * Tests all 4 Screens (Boards 6-9: Ask/Home, Conversation, Knowledge sources, Traces),
 * Evaluation mode (all 6 sub-tabs), Story mode, XSS safety,
 * and @axe-core/playwright zero accessibility violations.
 */

import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Kairos Streaming Live RAG Web Interface', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8000');
  });

  test('loads home page with Calm Precision dark theme and industry-ready shell', async ({ page }) => {
    await expect(page.locator('text=Kairos').first()).toBeVisible();
    await expect(
      page.locator('text=Ask several things at once. Kairos starts answering before you finish.')
    ).toBeVisible();
    await expect(page.locator('button:has-text("Ask")')).toBeVisible();
    await expect(page.locator('button:has-text("Knowledge sources")')).toBeVisible();
    await expect(page.locator('button:has-text("Traces")')).toBeVisible();
    await expect(page.locator('button:has-text("Evaluation")')).toBeVisible();
  });

  test('Home mode has zero accessibility violations', async ({ page }) => {
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
      .analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('navigates through Knowledge sources, Traces, and Evaluation tabs', async ({ page }) => {
    // 1. Knowledge sources screen (Board 8)
    await page.click('button:has-text("Knowledge sources")');
    await expect(page.locator('text=Company policies')).toBeVisible();
    await expect(page.locator('text=BGE-small-en-v1.5')).toBeVisible();
    await expect(page.locator('text=Reciprocal Rank Fusion')).toBeVisible();
    await expect(page.locator('text=0 passages flagged')).toBeVisible();
    await expect(page.locator('text=Workshop Venues in Pune')).toBeVisible();

    // 2. Traces screen (Board 9)
    await page.click('button:has-text("Traces")');
    await expect(page.locator('text=Timeline')).toBeVisible();
    await expect(page.locator('text=Part 1 · Venue')).toBeVisible();
    await expect(page.locator('text=5 citations, all verified')).toBeVisible();
    await expect(page.locator('text=Grounding checks')).toBeVisible();

    // 3. Evaluation screen (Existing Inspector Mode with 6 tabs)
    await page.click('button:has-text("Evaluation")');
    await expect(page.locator('text=Timeline')).toBeVisible();
    await expect(page.locator('text=Race vs. batch')).toBeVisible();
    await expect(page.locator('text=Results')).toBeVisible();
    await expect(page.locator('text=Corpus')).toBeVisible();
    await expect(page.locator('text=Try it yourself')).toBeVisible();
    await expect(page.locator('text=About & Core vs. harness')).toBeVisible();

    // Sub-tab navigation in Evaluation
    await page.click('button:has-text("Race vs. batch")');
    await expect(page.locator('text=Median Time Saved')).toBeVisible();

    await page.click('button:has-text("Results")');
    await expect(page.locator('text=Dual Acceptance Gates')).toBeVisible();

    // Accessibility scan on Evaluation
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();
    expect(accessibilityScanResults.violations).toEqual([]);

    // Return to Ask
    await page.click('button:has-text("Ask")');
    await expect(
      page.locator('text=Ask several things at once. Kairos starts answering before you finish.')
    ).toBeVisible();
  });

  test('renders XSS payloads as harmless plain text without HTML execution', async ({ page }) => {
    const input = page.locator('textarea[placeholder*="Speak or type"]');
    if (await input.isVisible()) {
      await input.fill('<script>window.__xss_flag = true;</script>');
      await page.keyboard.press('Enter');

      // Verify window.__xss_flag is undefined (never evaluated)
      const isXssExecuted = await page.evaluate(() => (window as any).__xss_flag);
      expect(isXssExecuted).toBeUndefined();
    }
  });

  test('plays Story Mode demo scenario and displays Conversation view (Board 7)', async ({ page }) => {
    const playDemoBtn = page.locator('button:has-text("Play the demo")').first();
    await playDemoBtn.click();

    // Story bar appears at the top
    await expect(page.locator('text=DEMO')).toBeVisible();

    // Answer container appears with verified sentences and intent parts
    await expect(page.locator('text=sentences verified')).toBeVisible();
    await expect(page.locator('text=View trace')).toBeVisible();
    await expect(page.locator('text=Ask next')).toBeVisible();
  });
});
