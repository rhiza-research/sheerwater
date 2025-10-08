

# how to build dashboards

# this will extract the external content and create a jsonnet file from a dashboard json file exported from grafana.
Any content in the dashboard json that contains EXTERNAL on the first line will be extracted and saved to the assets folder.
There are two ways to use the external content:
1. EXTERNAL
    - this export the content to assets/[dashboard_id]-[panel_id]-[key].[ext]
2. EXTERNAL:filename
    - this exports the content to assets/filename

## Comment Type Examples

The EXTERNAL tag works with any comment syntax as long as "EXTERNAL" appears in the first line. Here are examples of supported comment types:

### JavaScript/TypeScript Comments
```javascript
// EXTERNAL:my-script.js
function myFunction() {
    return 'Hello World';
}
```

### Python Comments
```python
# EXTERNAL:my-script.py
def my_function():
    return 'Hello World'
```

### SQL Comments
```sql
-- EXTERNAL:my-query.sql
SELECT * FROM users WHERE active = true;
```

### HTML Comments
```html
<!-- EXTERNAL:my-content.html -->
<div>Hello World</div>
```

### Markdown Comments
```markdown
[comment]: # (EXTERNAL:my-content.md)
# My Content
This is some markdown content.
```

### Assembly Comments
```assembly
; EXTERNAL:my-code.asm
mov eax, 42
ret
```

### CSS Comments
```css
/* EXTERNAL:my-styles.css */
.container {
    background: blue;
}
```

### Auto-Generated Filenames
If you use plain `EXTERNAL` without a filename, the script will automatically generate a filename based on the dashboard UID, panel ID, and field name:

```javascript
// EXTERNAL
function autoNamed() {
    return 'This will be saved as dashboard-uid-panel-id-fieldname.js';
}
```

This will create a jsonnet file from the dashboard json file named dashboard.jsonnet in the same folder as the dashboard json file. After this is done the json file can be deleted.
```bash
python3 extract_external_content.py dashboard.json
```

To build the dashboard, run the following command:
```bash
jsonnet dashboard.jsonnet > ../build/dashboard.json
```
This will load the external assets back into the jsonnet and save it to the build folder.


The EXTERNAL tag is saved in the content and plain EXTERNAL tags are converted to EXTERNAL:filename tags so that when the jsonnet is converted back to json we know what the filename is. This allows us to to go full circle and take a raw dashboard json file from grafana (with a dashboard that was created in the grafana UI) and convert it into a jsonnet file with any external content exported to asset files automatically. Then the jsonnet file can be converted back to json and imported into grafana. The built json dashboard can then be re-processed to be converted into jsonnet again. This allows you to build dashboards in the grafana UI, and add EXTERNAL:filename tags to any content that you want to load content from an existing saved file, or to automatically write the content you add to the panel into that external file. You can then view the diff in git and edit the external files, regenerate the json and import it to grafana again. I think this roundtrip editability makes the process of building dashboards very natural.

TODO: derermine how to handle a case where you might want to edit external panel content directly in grafana. If that external content is in only one panel that is fine but if it is in multiple locations then one panel will overwrite the other. In that case we need a way to indicate that an external panel has been edited directly in grafana and that it should overwrite the external file content. Maybe the default should be that the EXTERNAL tag is EXTERNAL:RO: or something like that so that when we reprocess the content we know that we should populate this field with the content from the external file, but we should not overwrite the external file content with the current panel content. If the user removes the RO tag then we should overwrite the external file content with the current panel content.

IDEA: maybe the external tag can take a few parameters. that would allow us to do something like overwrite part of the filename generation but leave the rest of the automatic filename. If you want to share content within a dashboard, but not share it with other dashboards you would want to generate a filename that includes the dashboard-id but not necessarily need to find and put that in yourself. In this case maybe the external tag could be something like EXTERNAL:panel_id=shared so the script still automatically generates a filename for this content but it replaces the panel-id portion of the filename formula with "shared". This would allow you to share content within a dashboard, but still keep the filename organized so its easy to see which content is related. When the file is written the panel_id param would be replaced with the actual filename so this would only be needed on first write for an empty panel. 

NOTE: I am using panel to mean a value in the generate json. This is likely confusing but I don't exactly know what to call a textarea entry field in a grafana panel. This parsing system actually doesnt have to be in a panel, it could be used for any value content in the json where you can enter a newline and have the first line contain the word EXTERNAL and also have that line be commented out so that grafana doesnt show it.