import fs from "node:fs/promises";

const { chromium } = await import(
  "file:///C:/Users/deepu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs"
);

const outputDir = "C:/Users/deepu/OneDrive/Desktop/Rane/dms_portal_copy/tmp/manual_update_20260810/current-screenshots";
const edgePath = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const baseUrl = "http://127.0.0.1:5001";

await fs.mkdir(outputDir, { recursive: true });
const browser = await chromium.launch({
  executablePath: edgePath,
  headless: true,
  args: ["--disable-gpu", "--hide-scrollbars"],
});
const page = await browser.newPage({ viewport: { width: 1900, height: 826 }, deviceScaleFactor: 1 });

async function settle() {
  await page.waitForLoadState("networkidle");
  await page.evaluate(async () => {
    if (document.fonts?.ready) await document.fonts.ready;
  });
  await page.waitForTimeout(300);
}

async function capture(url, fileName, afterLoad) {
  await page.goto(`${baseUrl}${url}`);
  await settle();
  if (afterLoad) await afterLoad();
  await settle();
  await page.screenshot({ path: `${outputDir}/${fileName}.png`, fullPage: false });
}

await page.goto(`${baseUrl}/login`);
await page.locator('input[name="email"]').first().fill("diva@example.com");
await page.locator('input[name="password"]').fill("Pass@12345");
await Promise.all([
  page.waitForURL(/\/dashboard/),
  page.locator('button[type="submit"]').first().click(),
]);
if (await page.locator("#welcome-close").isVisible()) await page.locator("#welcome-close").click();

await capture("/approvals", "11_pending_items_current");
await capture("/tracking?scope=all", "12_track_approvals_current");
await capture("/graphics-report", "13_graphics_report_current");
await capture("/revision-history", "14_revision_history_current");
await capture("/archive", "15_archive_current");
await capture("/system-log", "16_system_log_current");
await capture("/people", "17_people_current", async () => {
  await page.addStyleTag({ content: ".people-table tbody { filter: blur(7px); }" });
});
await capture("/dashboard", "18_notifications_current", async () => {
  if (await page.locator("#welcome-close").isVisible()) await page.locator("#welcome-close").click();
  await page.locator("#notification-toggle").click();
});
await capture("/profile", "19_profile_current", async () => {
  await page.addStyleTag({ content: ".profile-avatar-img, .profile-hero-info, .profile-fields-grid, .profile-activity-card .log-table tbody { filter: blur(8px); }" });
});

await browser.close();
