import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const workspace = "C:/Users/deepu/OneDrive/Desktop/Rane/dms_portal_copy/tmp/manual_update_20260810";
const sourcePptx = `${workspace}/template-starter.pptx`;
const outputPptx = `${workspace}/template-starter-legibility.pptx`;
const layoutDir = `${workspace}/template-starter-legibility-layout`;

await fs.mkdir(layoutDir, { recursive: true });
const presentation = await PresentationFile.importPptx(await FileBlob.load(sourcePptx));
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
    if (record.kind === "image") target.frame = { ...target.frame, top: record.bbox[1] + delta };
    else target.position = { ...target.position, top: record.bbox[1] + delta };
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
    setRecordFrame(record, {
      left: isShadow ? 54.67 : 50.67,
      top: (isSecond ? secondTop : firstTop) + (isShadow ? 4 : 0),
      width: 692.4,
      height: 250,
    });
  }
}

// Slide 6: turn the two inherited portrait screenshot slots into one seamless,
// full-width registration screenshot made from two adjacent cropped halves.
const registrationScreens = recordsFor(6, "image")
  .filter((record) => record.bbox[2] > 300)
  .sort((a, b) => a.bbox[0] - b.bbox[0]);
setRecordFrame(registrationScreens[0], { left: 50.67, top: 168.73, width: 346.2, height: 299.2 });
setRecordFrame(registrationScreens[1], { left: 396.87, top: 168.73, width: 346.2, height: 299.2 });
const registrationLeft = presentation.resolve(registrationScreens[0].id);
registrationLeft.fit = "cover";
registrationLeft.crop = { left: 0, top: 0, right: 0.5, bottom: 0 };
registrationLeft.geometry = "rect";
registrationLeft.borderRadius = 0;
const registrationRight = presentation.resolve(registrationScreens[1].id);
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

const dashboardScreens = recordsFor(7, "image")
  .filter((record) => record.bbox[2] > 500)
  .sort((a, b) => a.bbox[1] - b.bbox[1]);
setRecordFrame(dashboardScreens[0], { left: 21.17, top: 169.93, width: 750.99, height: 250 });
setRecordFrame(dashboardScreens[1], { left: 21.17, top: 430, width: 750.99, height: 250 });
setRecordFrame(textRecord(7, "Figure 3 - Dashboard summary, quick actions and filters"), {
  left: 50.67,
  top: 683,
  width: 692.4,
  height: 25.47,
});
shiftRecordsVertically(7, 497, 850, 222);

for (const [slide, captionOne, captionTwo] of [
  [18, "Figure 10 - Procedure category cards", "Figure 11 - Standard Manual category cards"],
  [19, "Figure 12 - Plant-based Master Records", "Figure 13 - Customer Records"],
]) {
  const screenshots = recordsFor(slide, "image")
    .filter((record) => record.bbox[2] > 300)
    .sort((a, b) => a.bbox[0] - b.bbox[0]);
  expandStackedScreenshotFrames(slide, 169.07, 451.07);
  setRecordFrame(screenshots[0], { left: 55.22, top: 170.4, width: 683.28, height: 247.33 });
  setRecordFrame(screenshots[1], { left: 55.22, top: 452.4, width: 683.28, height: 247.33 });
  setRecordFrame(textRecord(slide, captionOne), { left: 50.67, top: 421.5, width: 692.4, height: 25.47 });
  setRecordFrame(textRecord(slide, captionTwo), { left: 50.67, top: 703.5, width: 692.4, height: 25.47 });
  shiftRecordsVertically(slide, 302, 600, 432);
}

const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(outputPptx);
for (let index = 0; index < presentation.slides.items.length; index += 1) {
  const slide = presentation.slides.getItem(index);
  const number = String(index + 1).padStart(2, "0");
  await fs.writeFile(
    path.join(layoutDir, `starter-slide-${number}.layout.json`),
    await (await slide.export({ format: "layout" })).text(),
    "utf8",
  );
}

console.log(JSON.stringify({ outputPptx, layoutDir, slides: presentation.slides.items.length }));
