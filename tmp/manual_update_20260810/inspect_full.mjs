import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const source = "C:/Users/deepu/Downloads/DMS_Portal_User_Manual_Updated.pptx";
const output = "C:/Users/deepu/OneDrive/Desktop/Rane/dms_portal_copy/tmp/manual_update_20260810/template-inspect/template-inspect.ndjson";

const presentation = await PresentationFile.importPptx(await FileBlob.load(source));
const snapshot = await presentation.inspect({
  kind: "slide,textbox,shape,image,table,chart,notes,layout",
  maxChars: 500000,
});
await fs.writeFile(output, `${snapshot.ndjson.trim()}\n`, "utf8");
console.log(JSON.stringify({ output, truncated: snapshot.truncated, metadata: snapshot.metadata }));
