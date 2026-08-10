import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const workspace = "C:/Users/deepu/OneDrive/Desktop/Rane/dms_portal_copy/tmp/manual_update_20260810";
const starterPath = `${workspace}/template-starter-legibility.pptx`;
const screenshotDir = `${workspace}/current-screenshots`;
const registrationScreenshot = "C:/Users/deepu/OneDrive/Pictures/Screenshots/Screenshot 2026-08-10 143320.png";
const outputPptx = "C:/Users/deepu/OneDrive/Desktop/Rane/dms_portal_copy/output/pptx/DMS_Portal_User_Manual_Updated_Rev1.5.pptx";
const renderDir = `${workspace}/final-render`;
const layoutDir = `${workspace}/final-layout`;

await fs.mkdir(path.dirname(outputPptx), { recursive: true });
await fs.mkdir(renderDir, { recursive: true });
await fs.mkdir(layoutDir, { recursive: true });

const presentation = await PresentationFile.importPptx(await FileBlob.load(starterPath));
const snapshot = await presentation.inspect({
  kind: "slide,textbox,shape,image,table,chart,notes,layout",
  maxChars: 500000,
});
const records = snapshot.ndjson
  .trim()
  .split(/\r?\n/)
  .filter(Boolean)
  .map((line) => JSON.parse(line));

function recordsFor(slide, kind) {
  return records.filter((record) => record.slide === slide && record.kind === kind);
}

function textRecord(slide, fragment) {
  const match = recordsFor(slide, "textbox").find(
    (record) => typeof record.text === "string" && record.text.includes(fragment),
  );
  if (!match) throw new Error(`Text not found on slide ${slide}: ${fragment}`);
  return match;
}

function replaceText(slide, oldText, newText) {
  const record = textRecord(slide, oldText);
  const target = presentation.resolve(record.id);
  target.text.replace(oldText, newText);
}

function headerTableRecord(slide) {
  const tables = recordsFor(slide, "table");
  if (!tables.length) throw new Error(`No table found on slide ${slide}`);
  return tables.reduce((best, current) => (current.bbox[1] < best.bbox[1] ? current : best));
}

function mainTableRecord(slide) {
  const header = headerTableRecord(slide);
  const tables = recordsFor(slide, "table").filter((record) => record.id !== header.id);
  if (!tables.length) throw new Error(`No main table found on slide ${slide}`);
  return tables.reduce((best, current) => {
    const bestArea = best.bbox[2] * best.bbox[3];
    const currentArea = current.bbox[2] * current.bbox[3];
    return currentArea > bestArea ? current : best;
  });
}

async function imageBytes(fileName) {
  const filePath = path.isAbsolute(fileName) ? fileName : `${screenshotDir}/${fileName}`;
  const bytes = await fs.readFile(filePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function replaceImageByRecord(record, fileName, alt) {
  const image = presentation.resolve(record.id);
  const oldFrame = image.frame;
  const oldCrop = image.crop;
  const oldGeometry = image.geometry;
  const oldBorderRadius = image.borderRadius;
  const oldRotation = image.rotation;
  const oldFlipHorizontal = image.flipHorizontal;
  const oldFlipVertical = image.flipVertical;
  const oldLockAspectRatio = image.lockAspectRatio;
  image.replace({
    blob: await imageBytes(fileName),
    contentType: "image/png",
    alt,
    fit: "cover",
  });
  image.frame = oldFrame;
  image.crop = oldCrop;
  image.geometry = oldGeometry;
  image.borderRadius = oldBorderRadius;
  image.rotation = oldRotation;
  image.flipHorizontal = oldFlipHorizontal;
  image.flipVertical = oldFlipVertical;
  image.lockAspectRatio = oldLockAspectRatio;
}

function setRecordFrame(record, frame) {
  const target = presentation.resolve(record.id);
  if (record.kind === "image") target.frame = frame;
  else target.position = frame;
}

function shiftRecordsVertically(slide, minTop, maxTop, delta) {
  const movableKinds = new Set(["shape", "textbox", "image"]);
  for (const record of records) {
    if (record.slide !== slide || !movableKinds.has(record.kind) || !record.bbox) continue;
    if (record.bbox[1] < minTop || record.bbox[1] >= maxTop) continue;
    const target = presentation.resolve(record.id);
    if (record.kind === "image") {
      target.frame = { ...target.frame, top: record.bbox[1] + delta };
    } else {
      target.position = { ...target.position, top: record.bbox[1] + delta };
    }
  }
}

function expandStackedScreenshotFrames(slide, firstTop, secondTop) {
  const frameShapes = recordsFor(slide, "shape")
    .filter((record) => record.bbox[1] >= 165 && record.bbox[1] <= 178 && record.bbox[2] > 300)
    .sort((a, b) => a.bbox[0] - b.bbox[0] || a.bbox[1] - b.bbox[1]);
  if (frameShapes.length !== 6) {
    throw new Error(`Expected six inherited screenshot frame shapes on slide ${slide}, found ${frameShapes.length}`);
  }
  for (const record of frameShapes) {
    const isSecond = record.bbox[0] > 400;
    const isShadow = record.bbox[0] > (isSecond ? 408 : 52);
    const top = (isSecond ? secondTop : firstTop) + (isShadow ? 4 : 0);
    const left = isShadow ? 54.67 : 50.67;
    setRecordFrame(record, { left, top, width: 692.4, height: 250 });
  }
}

// Controlled-document metadata on every page.
const coverTable = presentation.resolve(recordsFor(1, "table")[0].id);
coverTable.cells.set(1, 0, "DMS-UM-001");
coverTable.cells.set(1, 1, "1.5");
coverTable.cells.set(1, 2, "10-Aug-2026");
coverTable.cells.set(1, 3, "DMS Team");
coverTable.cells.set(0, 2, "EFFECTIVE");

for (let slide = 2; slide <= 27; slide += 1) {
  const table = presentation.resolve(headerTableRecord(slide).id);
  table.cells.set(0, 0, "Document: DMS-UM-001");
  table.cells.set(0, 1, "Revision: 1.5");
  table.cells.set(1, 0, "Effective: 10-Aug-2026");
  table.cells.set(1, 1, `Page: ${slide} of 27`);
}

const controlTable = presentation.resolve(mainTableRecord(2).id);
controlTable.cells.set(2, 1, "1.5");
controlTable.cells.set(2, 2, "Effective");
controlTable.cells.set(2, 3, "10-Aug-2026");
controlTable.cells.set(
  4,
  3,
  "Portal UI, current Flask code, local database and supplied workflow screenshots",
);

const accessTable = presentation.resolve(mainTableRecord(3).id);
accessTable.cells.set(3, 1, "SOPs, IATF audit plans, Records and IATF Standards.");
accessTable.cells.set(3, 2, "No approval decision.");
accessTable.cells.set(4, 1, "Records only.");
accessTable.cells.set(4, 2, "No approval decision.");

// Cover: replace the legacy dashboard view with the current landing page.
await replaceImageByRecord(
  recordsFor(1, "image")[0],
  "01_dashboard_library_coverage.png",
  "Current Smart DMS Master Dashboard",
);

// Slide 6: current registration page, shown as one full-width desktop view.
replaceText(6, "Create account: identity and organization fields", "Figure 2 - Current employee registration page");
replaceText(6, "Password confirmation and submission controls", "Full registration form visible in one screen without page scrolling");
const registrationImages = recordsFor(6, "image")
  .filter((record) => record.bbox[2] > 300)
  .sort((a, b) => a.bbox[0] - b.bbox[0]);
await replaceImageByRecord(registrationImages[0], registrationScreenshot, "Current employee registration page, left half");
await replaceImageByRecord(registrationImages[1], registrationScreenshot, "Current employee registration page, right half");
const registrationLeft = presentation.resolve(registrationImages[0].id);
registrationLeft.frame = { left: 50.67, top: 168.73, width: 346.2, height: 299.2 };
registrationLeft.fit = "cover";
registrationLeft.crop = { left: 0, top: 0, right: 0.5, bottom: 0 };
registrationLeft.geometry = "rect";
registrationLeft.borderRadius = 0;
const registrationRight = presentation.resolve(registrationImages[1].id);
registrationRight.frame = { left: 396.87, top: 168.73, width: 346.2, height: 299.2 };
registrationRight.fit = "cover";
registrationRight.crop = { left: 0.5, top: 0, right: 0, bottom: 0 };
registrationRight.geometry = "rect";
registrationRight.borderRadius = 0;
setRecordFrame(textRecord(6, "Create account: identity and organization fields"), {
  left: 50.67,
  top: 478,
  width: 692.4,
  height: 20,
});
setRecordFrame(textRecord(6, "Password confirmation and submission controls"), {
  left: 50.67,
  top: 502,
  width: 692.4,
  height: 20,
});

// Slide 7: current dashboard coverage, shortcuts, activity and search behavior.
replaceText(7, "The dashboard is the main operational view for documents, filters and quick actions.", "The dashboard is shown in two complete views: library shortcuts first, then activity and search.");
replaceText(7, "Figure 3 - Dashboard summary, quick actions and filters", "Figure 3 - Dashboard overview (top) and activity/search (bottom)");
replaceText(7, "Documents Summarty", "Review library coverage");
replaceText(7, "Check total, pending, approved and archived document counts.", "Review 119 plant and 58 customer documents across six library areas.");
replaceText(7, "Open Upload Documents, Pending Items, Document Library or Graphics Report.", "Open Uploads, Pending, Library, Approvals, Reports or Revision History.");
replaceText(7, "Search and filter", "Review activity");
replaceText(7, "Filter by text, plant, department, customer and approval status.", "Use the 14-day trend and Recently viewed list to reopen work.");
replaceText(7, "Open a document", "Search and filter");
replaceText(7, "Use row actions to view, download or bookmark. Deletion is restricted and moves the item to Archive.", "Search metadata; filter by plant, department, customer and status.");
replaceText(7, "Export the current view", "Manage the current view");
replaceText(7, "Use CSV export when a filtered list is required for offline review.", "Set page size, use authorized row actions, or export the filtered CSV.");
replaceText(7, "Reset filters before concluding that a document is missing. Status and department filters can hide valid records.", "Reset filters before concluding that a document is missing. Counts and visibility are access-aware and reflect the current database.");
const dashboardScreens = recordsFor(7, "image")
  .filter((record) => record.bbox[2] > 500)
  .sort((a, b) => a.bbox[1] - b.bbox[1]);
const dashboardLayoutAlreadyExpanded = dashboardScreens[0].bbox[3] > 200;
await replaceImageByRecord(dashboardScreens[0], "01_dashboard_library_coverage.png", "Dashboard library coverage and shortcuts");
await replaceImageByRecord(dashboardScreens[1], "03_dashboard_activity.png", "Dashboard activity, recently viewed documents and search");
setRecordFrame(dashboardScreens[0], { left: 21.17, top: 169.93, width: 750.99, height: 250 });
setRecordFrame(dashboardScreens[1], { left: 21.17, top: 430, width: 750.99, height: 250 });
setRecordFrame(textRecord(7, "Figure 3 - Dashboard summary, quick actions and filters"), {
  left: 50.67,
  top: 683,
  width: 692.4,
  height: 25.47,
});
if (!dashboardLayoutAlreadyExpanded) shiftRecordsVertically(7, 497, 850, 222);

// Slide 17: current library landing page and folder behavior.
replaceText(17, "The library organizes controlled content by category and access hierarchy.", "The library landing page shows six access-aware folders; each folder opens on a dedicated page.");
replaceText(17, "Figure 9 - Document Library category browser", "Figure 9 - Current Document Library folder landing page");
replaceText(17, "Select QMS, Customer Procedures, Standard Manuals, Awards and other configured categories.", "Select QMS, CSR, Core Tools, Score Card, EOHMS, or Awards and Certifications.");
replaceText(17, "Drill into the hierarchy", "Read access-aware counts");
replaceText(17, "Choose the required QMS level, document group, plant, department or subfolder.", "Counts show approved files visible to your access level and department.");
replaceText(17, "Open the file", "Open the folder page");
replaceText(17, "View inline when supported or download the approved source file.", "Open a card to enter its dedicated page and breadcrumb trail.");
replaceText(17, "Use your access level correctly", "Follow the step bar");
replaceText(17, "L3 is limited to procedure-related groups; L4 is limited to checklists and checksheets.", "Select a type, customer or subfolder, then browse approved files.");
replaceText(17, "Use the document from the library instead of a locally saved copy when the latest revision is required.", "Use the controlled library copy when the latest revision is required; folder counts and choices reflect your access.");
await replaceImageByRecord(
  recordsFor(17, "image").find((record) => record.bbox[2] > 500),
  "05_library_folders.png",
  "Current Document Library landing page with six folders",
);

// Slide 18: current QMS group page.
replaceText(18, "Open Procedures and Standard Manuals", "Browse QMS Document Types");
replaceText(18, "Category cards provide a shorter route to frequently used controlled documents.", "QMS opens as a dedicated, access-aware folder page with seven document groups.");
replaceText(18, "Figure 10 - Procedure category cards", "Figure 10 - QMS document type selection");
replaceText(18, "Figure 11 - Standard Manual category cards", "Figure 11 - Complete QMS group list");
replaceText(18, "Select the entry card", "Open the QMS folder");
replaceText(18, "Open the required procedure or manual family.", "From Document Library, select Quality Management System.");
replaceText(18, "Choose plant and department where shown", "Select one of seven groups");
replaceText(18, "Use the repository hierarchy to reach the correct controlled location.", "Choose Manuals, Procedures, SOPs, Records or an IATF reference/report group.");
replaceText(18, "Select the document", "Follow the required hierarchy");
replaceText(18, "Open the approved file and confirm its revision before use.", "SOPs and Records use plant/department; audits use audit folders and plant.");
replaceText(18, "Return through breadcrumbs", "Browse approved files");
replaceText(18, "Use the page breadcrumb or category browser to move back without losing context.", "Confirm document number, revision and location before opening the file.");
replaceText(18, "If a card is empty", "Access-aware navigation");
replaceText(18, "Confirm your QMS access level and selected plant/department. Then contact the document owner if the file is still unavailable.", "L1/L2 see all QMS groups; L3 sees SOPs, audit plans, Records and IATF Standards; L4 sees Records only.");
const qmsScreens = recordsFor(18, "image")
  .filter((record) => record.bbox[2] > 300)
  .sort((a, b) => a.bbox[1] - b.bbox[1] || a.bbox[0] - b.bbox[0]);
const qmsLayoutAlreadyExpanded = qmsScreens[0].bbox[2] > 600;
await replaceImageByRecord(qmsScreens[0], "06_qms_document_types_top.png", "QMS document type selection page");
await replaceImageByRecord(qmsScreens[1], "07_qms_document_types_all.png", "Complete QMS document group list");
if (!qmsLayoutAlreadyExpanded) expandStackedScreenshotFrames(18, 169.07, 451.07);
setRecordFrame(qmsScreens[0], { left: 55.22, top: 170.4, width: 683.28, height: 247.33 });
setRecordFrame(qmsScreens[1], { left: 55.22, top: 452.4, width: 683.28, height: 247.33 });
setRecordFrame(textRecord(18, "Figure 10 - Procedure category cards"), {
  left: 50.67,
  top: 421.5,
  width: 692.4,
  height: 25.47,
});
setRecordFrame(textRecord(18, "Figure 11 - Standard Manual category cards"), {
  left: 50.67,
  top: 703.5,
  width: 692.4,
  height: 25.47,
});
if (!qmsLayoutAlreadyExpanded) shiftRecordsVertically(18, 302, 600, 432);

// Slide 19: current customer-logo folders and core-tool groups.
replaceText(19, "Use Plant and Customer Repositories", "Browse Customer and Core Tools");
replaceText(19, "Use these views when the retrieval question begins with a plant, department or customer.", "Customer requirements and core-tool references now open as dedicated library pages.");
replaceText(19, "Figure 12 - Plant-based Master Records", "Figure 12 - Customer Manual folders by customer");
replaceText(19, "Figure 13 - Customer Records", "Figure 13 - Core Tools Manual cards");
presentation.resolve(textRecord(19, "Master Records\nChoose").id).text.replace("Master Records", "Customer Specific Requirements");
replaceText(19, "Choose a plant, then a department, and open the required controlled record.", "Choose CSR Matrix, Customer Manual or Customer Initiatives; customer folders use logo cards.");
presentation.resolve(textRecord(19, "Customer Records\nChoose").id).text.replace("Customer Records", "Customer Score Card");
replaceText(19, "Choose the customer card, review the available files and open the required record.", "Use the separate Score Card area and choose the required customer folder.");
replaceText(19, "Confirm context", "Core Tools Manuals");
replaceText(19, "Check the plant, department, customer, document number and revision before use.", "Choose APQP, Control Plan, FMEA, IATF Manual, MSA, PPAP or SPC.");
replaceText(19, "View only", "Return through breadcrumbs");
replaceText(19, "These repository pages are for retrieval. Use Upload Documents to submit new controlled files.", "Use the breadcrumb or All folders button to return without losing library context.");
replaceText(19, "Search strategy", "Folder navigation");
replaceText(19, "Use the dashboard for broad metadata search; use repository pages for structured browsing by ownership.", "Use the dashboard for broad metadata search and Document Library for controlled, structured browsing.");
const libraryScreens = recordsFor(19, "image")
  .filter((record) => record.bbox[2] > 300)
  .sort((a, b) => a.bbox[1] - b.bbox[1] || a.bbox[0] - b.bbox[0]);
const libraryLayoutAlreadyExpanded = libraryScreens[0].bbox[2] > 600;
await replaceImageByRecord(libraryScreens[0], "08_csr_customer_folders.png", "Customer Manual folders with customer logos");
await replaceImageByRecord(libraryScreens[1], "10_core_tools_all.png", "Core Tools Manual groups");
if (!libraryLayoutAlreadyExpanded) expandStackedScreenshotFrames(19, 169.07, 451.07);
setRecordFrame(libraryScreens[0], { left: 55.22, top: 170.4, width: 683.28, height: 247.33 });
setRecordFrame(libraryScreens[1], { left: 55.22, top: 452.4, width: 683.28, height: 247.33 });
setRecordFrame(textRecord(19, "Figure 12 - Plant-based Master Records"), {
  left: 50.67,
  top: 421.5,
  width: 692.4,
  height: 25.47,
});
setRecordFrame(textRecord(19, "Figure 13 - Customer Records"), {
  left: 50.67,
  top: 703.5,
  width: 692.4,
  height: 25.47,
});
if (!libraryLayoutAlreadyExpanded) shiftRecordsVertically(19, 302, 600, 432);

// Refresh every data-bearing administrative screenshot from the current local app.
const currentPageImages = [
  [10, "11_pending_items_current.png", "Current Pending Items queue and approval totals"],
  [16, "12_track_approvals_current.png", "Current Track Approvals totals and workflow timeline"],
  [20, "13_graphics_report_current.png", "Current Graphics Report metrics and chart"],
  [21, "14_revision_history_current.png", "Current Revision History list and filters"],
  [22, "15_archive_current.png", "Current Archive list"],
  [23, "16_system_log_current.png", "Current System Log and action filters"],
  [24, "17_people_current.png", "Current People and Access summary with personal rows obscured"],
  [25, "18_notifications_current.png", "Current notification panel opened from the dashboard"],
  [26, "19_profile_current.png", "Current profile and activity page with personal details obscured"],
];
for (const [slideNumber, fileName, alt] of currentPageImages) {
  const largeImage = recordsFor(slideNumber, "image")
    .filter((record) => record.bbox[2] > 500)
    .sort((a, b) => b.bbox[2] * b.bbox[3] - a.bbox[2] * a.bbox[3])[0];
  if (!largeImage) throw new Error(`No page screenshot found on slide ${slideNumber}`);
  await replaceImageByRecord(largeImage, fileName, alt);
}

const pptxBlob = await PresentationFile.exportPptx(presentation);
await pptxBlob.save(outputPptx);

for (let index = 0; index < 27; index += 1) {
  const slide = presentation.slides.getItem(index);
  const number = String(index + 1).padStart(2, "0");
  await writeBlob(`${renderDir}/slide-${number}.png`, await presentation.export({ slide, format: "png", scale: 1 }));
  await fs.writeFile(
    `${layoutDir}/slide-${number}.layout.json`,
    await (await slide.export({ format: "layout" })).text(),
    "utf8",
  );
}
await writeBlob(`${workspace}/final-montage.webp`, await presentation.export({ format: "webp", montage: true, scale: 0.45 }));

const finalInspect = await presentation.inspect({
  kind: "slide,textbox,shape,image,table,chart,notes,layout",
  maxChars: 500000,
});
await fs.writeFile(`${workspace}/final-inspect.ndjson`, `${finalInspect.ndjson.trim()}\n`, "utf8");

console.log(JSON.stringify({ outputPptx, slides: 27, renderDir, layoutDir }));
