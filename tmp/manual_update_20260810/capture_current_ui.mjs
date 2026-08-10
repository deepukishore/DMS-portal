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

const page = await browser.newPage({
  viewport: { width: 1900, height: 826 },
  deviceScaleFactor: 1,
});

async function settle() {
  await page.waitForLoadState("networkidle");
  await page.evaluate(async () => {
    if (document.fonts?.ready) await document.fonts.ready;
  });
  await page.waitForTimeout(350);
}

async function save(name) {
  await settle();
  await page.screenshot({ path: `${outputDir}/${name}.png`, fullPage: false });
}

async function scrollToSelector(selector, offset = 84) {
  await page.locator(selector).first().waitFor({ state: "visible" });
  await page.evaluate(({ selector, offset }) => {
    const element = document.querySelector(selector);
    const scroller = document.querySelector("#main-content");
    const top = element.getBoundingClientRect().top
      - scroller.getBoundingClientRect().top
      + scroller.scrollTop
      - offset;
    scroller.scrollTo({ top: Math.max(0, top), behavior: "instant" });
  }, { selector, offset });
}

async function scrollContent(top) {
  await page.evaluate(value => {
    document.querySelector("#main-content").scrollTo({ top: value, behavior: "instant" });
  }, top);
}

await page.goto(`${baseUrl}/login`);
await page.locator('input[name="email"]').first().fill("diva@example.com");
await page.locator('input[name="password"]').fill("Pass@12345");
await Promise.all([
  page.waitForURL(/\/dashboard/),
  page.locator('button[type="submit"]').first().click(),
]);
if (await page.locator("#welcome-close").isVisible()) {
  await page.locator("#welcome-close").click();
}
await save("01_dashboard_library_coverage");

await scrollToSelector("#quick-actions-heading", 100);
await save("02_dashboard_shortcuts");

await scrollToSelector("#activity-heading", 100);
await save("03_dashboard_activity");

await scrollToSelector("#dashboard-search", 84);
await save("04_dashboard_search_documents");

await page.goto(`${baseUrl}/document-library`);
await save("05_library_folders");

await page.goto(`${baseUrl}/document-library/qms`);
await save("06_qms_document_types_top");
await scrollContent(300);
await save("07_qms_document_types_all");

await page.goto(`${baseUrl}/document-library/csr?primary=customer_manual`);
await scrollToSelector(".surface-panel", 82);
await save("08_csr_customer_folders");

await page.goto(`${baseUrl}/document-library/core_tools_manuals`);
await save("09_core_tools_top");
await scrollContent(260);
await save("10_core_tools_all");

await browser.close();
