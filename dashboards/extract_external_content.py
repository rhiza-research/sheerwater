#!/usr/bin/env python3
"""
Script to extract EXTERNAL content from JSON files to separate asset files
and create template files with placeholders.
"""

import json
import re
import sys
from pathlib import Path


def parse_external_params(line):
    """
    Parse parameters from EXTERNAL({...}) format.

    Example: EXTERNAL({panel_id:"weekly-results", key: "params"})
    Returns: {"panel_id": "weekly-results", "key": "params"}

    Supported parameters:
    - dashboard_id: Override dashboard ID in filename
    - panel_id: Override panel ID in filename
    - key: Override key in filename
    - ext: Override file extension (e.g., "js", "md", "sql")
    """
    match = re.match(r'.*EXTERNAL\s*\(\s*\{([^}]+)\}\s*\)', line)
    if not match:
        return None

    # Parse key:value pairs (handles both quoted and unquoted values)
    params = {}
    for pair in re.split(r',\s*', match.group(1)):
        kv_match = re.match(r'^\s*["\']?([^"\':\s]+)["\']?\s*:\s*["\']?([^"\']+)["\']?\s*$', pair)
        if kv_match:
            params[kv_match.group(1).strip()] = kv_match.group(2).strip()
    return params if params else None


def determine_file_extension(content):
    """
    Determine appropriate file extension based on content analysis.

    Analyzes the content to detect the type of code or markup and returns
    the appropriate file extension. Used when no extension is specified
    in EXTERNAL parameters.

    Detection patterns:
    - .js: JS keywords (function, const, let, var), comments (//), arrow functions (=>),
           console.log, or return statements
    - .html: Starts with '<' or contains '<html'
    - .md: Starts with '#' or '##' (markdown headers)
    - .sql: Contains both 'select' and 'from' keywords
    - .txt: Default fallback for unrecognized content

    Args:
        content: The content string to analyze

    Returns:
        File extension string including the leading dot (e.g., '.js', '.sql')
    """
    content_lower = content.lower().strip()

    # JavaScript: multiple indicators
    # Check for JS keywords, syntax patterns, and comments
    js_indicators = [
        content_lower.startswith('function'),
        content_lower.startswith('const '),
        content_lower.startswith('let '),
        content_lower.startswith('var '),
        content_lower.startswith('//'),
        'function(' in content_lower,
        '=>' in content_lower,  # Arrow functions
        'console.log' in content_lower,
        content_lower.startswith('return {'),
        ' = {' in content_lower and '\n' in content,  # Object assignment (multi-line)
    ]
    if any(js_indicators):
        return '.js'
    # HTML: angle brackets or html tag
    elif content_lower.startswith('<') or '<html' in content_lower:
        return '.html'
    # Markdown: starts with header markers
    elif content_lower.startswith('#') or content_lower.startswith('##'):
        return '.md'
    # SQL: contains SELECT...FROM pattern
    elif 'select' in content_lower and 'from' in content_lower:
        return '.sql'
    # Default fallback
    return '.txt'


def extract_filename_from_external_line(line):
    """
    Extract existing filename from EXTERNAL marker line.

    Detects and extracts filenames from various EXTERNAL formats to prevent
    filename duplication on subsequent runs. Critical for idempotency.

    Supported formats:
    - EXTERNAL:filename.js
    - EXTERNAL({panel_id:"foo"}):filename.js
    - // EXTERNAL:filename.js (with comment prefix)
    - [comment]: # (EXTERNAL:filename.md) (markdown comment)

    Args:
        line: The line containing the EXTERNAL marker

    Returns:
        The filename string if found, None otherwise

    Examples:
        >>> extract_filename_from_external_line("// EXTERNAL:colors.js")
        "colors.js"
        >>> extract_filename_from_external_line("EXTERNAL({key:'foo'}):data.sql")
        "data.sql"
    """
    params = parse_external_params(line)

    # Quick check: must have both EXTERNAL keyword and colon delimiter
    if "EXTERNAL" not in line or ":" not in line:
        return None

    external_pos = line.find("EXTERNAL")
    after_external = line[external_pos + 8:]  # Skip "EXTERNAL" (8 chars)

    if params:
        # With parameters: look for ):filename pattern
        # Matches: EXTERNAL({...}):filename (stops at whitespace or delimiters)
        match = re.search(r'\([^)]*\{[^}]+\}\s*\)\s*:([^ \t\n\r:)}\]]+)', after_external)
        return match.group(1).strip() if match else None
    elif after_external.startswith(':'):
        # Without parameters: just :filename
        # Matches: EXTERNAL:filename (stops at whitespace or delimiters)
        match = re.match(r':([^ \t\n\r:)}\]]+)', after_external)
        return match.group(1).strip() if match else None

    return None


def generate_filename(content, key, root_data, path, params=None):
    """
    Generate a filename for external content based on dashboard context.

    Builds filenames using dashboard ID, panel ID (if in a panel), and field key
    to create unique, descriptive filenames. Parameters can override any component.

    Filename patterns:
    - With panel: {dashboard_id}-{panel_id}-{key}{ext}
    - Without panel: {dashboard_id}-{key}{ext}

    Args:
        content: The content to be saved (used for extension detection)
        key: The JSON field key (e.g., "script", "query", "content")
        root_data: The complete dashboard JSON (to extract dashboard/panel IDs)
        path: JSON path to this field (e.g., "panels[0].options.script")
        params: Optional dict from EXTERNAL({...}) to override values

    Returns:
        Generated filename string

    Examples:
        >>> # Panel script: ee2jzeymn1o8wf-5-script.js
        >>> generate_filename("function foo() {}", "script", data, "panels[0].options.script")

        >>> # Dashboard-level query: ee2jzeymn1o8wf-query.sql
        >>> generate_filename("SELECT * FROM foo", "query", data, "templating.query")

        >>> # With params override: weekly-results-params.js
        >>> generate_filename("...", "script", data, "panels[0].options.script",
        ...                   {"panel_id": "weekly-results", "key": "params"})
    """
    # Extract dashboard ID from root JSON (prefer 'uid' over numeric 'id')
    dashboard_id = root_data.get('uid', root_data.get('id', 'dashboard'))

    # Extract panel ID from path if this content is within a panel
    panel_id = None
    for part in path.split('.'):
        if part.startswith('panels['):
            try:
                panel_index = int(part[7:-1])  # Extract index from "panels[N]"
                panels = root_data.get('panels', [])
                if panel_index < len(panels):
                    panel_id = panels[panel_index].get('id')
            except:
                pass  # Ignore malformed panel indices

    # Apply parameter overrides if provided
    if params:
        dashboard_id = params.get('dashboard_id', dashboard_id)
        panel_id = params.get('panel_id', panel_id)
        key = params.get('key', key)
        ext = params.get('ext')
        # Ensure extension has leading dot
        if ext and not ext.startswith('.'):
            ext = '.' + ext
    else:
        ext = None

    # Determine extension from content if not specified
    if not ext:
        ext = determine_file_extension(content)

    # Build filename with panel ID if available
    if panel_id:
        return f"{dashboard_id}-{panel_id}-{key}{ext}"
    return f"{dashboard_id}-{key}{ext}"


def create_external_line(original_line, filename):
    """
    Create EXTERNAL line with filename, preserving all formatting.

    Reconstructs the EXTERNAL marker line with the (possibly new) filename while
    preserving the comment prefix, parameters, and any trailing content. This is
    critical for maintaining proper comment syntax in different file types.

    Preservation requirements:
    - Prefix: Comment markers like '//', '--', '[comment]: # ('
    - Parameters: EXTERNAL({...}) block if present
    - Suffix: Closing delimiters like ')', newlines, etc.

    Args:
        original_line: The original line containing EXTERNAL marker
        filename: The filename to insert (new or existing)

    Returns:
        Reconstructed EXTERNAL line string

    Examples:
        >>> create_external_line("// EXTERNAL", "colors.js")
        "// EXTERNAL:colors.js"

        >>> create_external_line("-- EXTERNAL({key:'foo'}):old.sql", "new.sql")
        "-- EXTERNAL({key:'foo'}):new.sql"

        >>> create_external_line("[comment]: # (EXTERNAL)", "readme.md")
        "[comment]: # (EXTERNAL:readme.md)"
    """
    params = parse_external_params(original_line)
    external_pos = original_line.find("EXTERNAL")
    before_external = original_line[:external_pos]  # Preserve comment prefix

    # Determine what comes after the filename position
    existing_filename = extract_filename_from_external_line(original_line)

    if existing_filename:
        # Replace existing filename, preserve everything after it
        filename_pos = original_line.find(existing_filename)
        if filename_pos != -1:
            after_filename = original_line[filename_pos + len(existing_filename):]
        else:
            after_filename = ''
    else:
        # No existing filename, find suffix after EXTERNAL/params
        if params:
            # After params block: EXTERNAL({...})___suffix___
            match = re.search(r'EXTERNAL\s*\([^)]*\{[^}]+\}\s*\)', original_line)
            if match:
                after_filename = original_line[match.end():]
            else:
                after_filename = ''
        else:
            # After EXTERNAL keyword: EXTERNAL___suffix___
            after_filename = original_line[external_pos + 8:]  # 8 = len("EXTERNAL")

    # Reconstruct line with filename
    if params:
        # With parameters: prefix + EXTERNAL({...}) + :filename + suffix
        match = re.search(r'EXTERNAL\s*\([^)]*\{[^}]+\}\s*\)', original_line)
        if match:
            params_block = match.group(0)
            return f"{before_external}{params_block}:{filename}{after_filename}"

    # Without parameters: prefix + EXTERNAL + :filename + suffix
    return f"{before_external}EXTERNAL:{filename}{after_filename}"


def split_on_external(value):
    """
    Split a multi-line value into segments at EXTERNAL markers.

    Handles values containing multiple EXTERNAL markers by splitting them into
    separate segments. Each segment consists of an EXTERNAL marker line and the
    content following it until the next EXTERNAL marker or end of value.

    The EXTERNAL line is preserved exactly as-is to maintain formatting like
    comment markers, parameters, and any existing filenames.

    Args:
        value: Multi-line string potentially containing EXTERNAL markers

    Returns:
        List of (external_line, content) tuples where:
        - external_line: The complete line containing EXTERNAL marker
        - content: All lines following it until next EXTERNAL or end

    Examples:
        >>> value = '''// EXTERNAL:part1.js
        ... function foo() {}
        ... // EXTERNAL:part2.js
        ... function bar() {}'''
        >>> split_on_external(value)
        [('// EXTERNAL:part1.js', 'function foo() {}'),
         ('// EXTERNAL:part2.js', 'function bar() {}')]

        >>> value = '''-- EXTERNAL
        ... SELECT * FROM table'''
        >>> split_on_external(value)
        [('-- EXTERNAL', 'SELECT * FROM table')]
    """
    lines = value.split('\n')
    segments = []
    current_external_line = None
    current_content = []

    for line in lines:
        if 'EXTERNAL' in line:
            # Save previous segment if we were collecting one
            if current_external_line is not None:
                segments.append((current_external_line, '\n'.join(current_content)))

            # Start new segment - keep the entire EXTERNAL line as-is
            current_external_line = line
            current_content = []
        else:
            # Collect content lines after EXTERNAL marker
            if current_external_line is not None:
                current_content.append(line)

    # Don't forget the last segment
    if current_external_line is not None:
        segments.append((current_external_line, '\n'.join(current_content)))

    return segments


def process_external_value(value, key, path, assets_dir, root_data, modifications):
    """
    Process a JSON field value containing one or more EXTERNAL markers.

    This is the main processing function that orchestrates the extraction workflow:
    1. Split value into segments at EXTERNAL markers
    2. For each segment: extract/generate filename, write asset file, create placeholder
    3. Return placeholder(s) for jsonnet template substitution

    Handles both single EXTERNAL (one file) and multiple EXTERNALs (concatenation).

    Args:
        value: The JSON field value containing EXTERNAL marker(s)
        key: The JSON field name (e.g., "script", "query")
        path: Full JSON path to this field (e.g., "panels[0].options.script")
        assets_dir: Directory to write asset files to
        root_data: Complete dashboard JSON (for context)
        modifications: List to append modification records to

    Returns:
        Placeholder string to replace value in JSON:
        - Single segment: "__varname__"
        - Multiple segments: "__CONCAT__var1 + var2__"

    Side effects:
        - Writes asset files to assets_dir
        - Appends modification records to modifications list

    Examples:
        >>> # Single EXTERNAL
        >>> process_external_value("// EXTERNAL\\nfunction foo() {}", "script", ...)
        "__dashboard_id_panel_id_script_js__"

        >>> # Multiple EXTERNALs (concatenation)
        >>> process_external_value("// EXTERNAL:colors.js\\n...\\n// EXTERNAL:utils.js\\n...", ...)
        "__CONCAT__colors_js + utils_js__"
    """
    # Split into segments at EXTERNAL markers
    segments = split_on_external(value)
    var_names = []

    for external_line, content in segments:
        # Parse parameters if present
        params = parse_external_params(external_line)

        # Detect existing filename (for idempotency)
        filename = extract_filename_from_external_line(external_line)

        # Generate filename if this is first run
        if not filename:
            filename = generate_filename(content, key, root_data, path, params)

        # Reconstruct EXTERNAL line with filename, preserving formatting
        new_external_line = create_external_line(external_line, filename)
        full_content = new_external_line + '\n' + content

        # Write asset file with exactly one trailing newline
        assets_dir.mkdir(exist_ok=True, parents=True)
        asset_file = assets_dir / filename
        with open(asset_file, 'w') as f:
            f.write(full_content.rstrip('\n') + '\n')

        # Generate valid jsonnet variable name from filename
        var_name = filename.replace('-', '_').replace('.', '_')
        if var_name[0].isdigit():
            var_name = 'f_' + var_name  # Prefix if starts with digit
        var_names.append(var_name)

        # Track this modification for jsonnet generation
        modifications.append({
            'path': path,
            'filename': filename,
            'var_name': var_name
        })

    # Return appropriate placeholder format
    if len(var_names) == 1:
        return f"__{var_names[0]}__"
    # Multiple segments: concatenate with +
    return f"__CONCAT__{' + '.join(var_names)}__"


def extract_external_content(obj, path="", assets_dir=None, root_data=None, modifications=None):
    """
    Recursively traverse JSON structure to find and extract EXTERNAL content.

    Walks through the entire dashboard JSON looking for string values that start
    with EXTERNAL markers. When found, extracts them to separate asset files and
    replaces them with placeholders in the JSON.

    The function modifies the JSON in-place, replacing EXTERNAL content with
    placeholder strings that will later be converted to importstr statements.

    Args:
        obj: Current object being traversed (dict, list, or primitive)
        path: Current JSON path (e.g., "panels[0].options.script")
        assets_dir: Directory to write extracted asset files to
        root_data: The complete dashboard JSON (for context like dashboard ID)
        modifications: List accumulating all modifications made

    Side effects:
        - Modifies obj in-place, replacing EXTERNAL values with placeholders
        - Writes asset files to assets_dir
        - Appends modification records to modifications list
        - Prints progress messages to stdout

    Examples:
        >>> data = {"script": "// EXTERNAL\\nfunction foo() {}"}
        >>> extract_external_content(data, assets_dir=Path("assets"), root_data=data)
        Found EXTERNAL at: script
        >>> data
        {"script": "__dashboard_script_js__"}
    """
    if modifications is None:
        modifications = []

    if isinstance(obj, dict):
        # Traverse dictionary
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key

            # Check if value is a string starting with EXTERNAL
            if isinstance(value, str) and "EXTERNAL" in value.split('\n')[0]:
                print(f"Found EXTERNAL at: {current_path}")
                # Process and replace with placeholder
                obj[key] = process_external_value(value, key, current_path, assets_dir, root_data, modifications)
            else:
                # Recurse into nested structures
                extract_external_content(value, current_path, assets_dir, root_data, modifications)

    elif isinstance(obj, list):
        # Traverse list with indices
        for index, item in enumerate(obj):
            extract_external_content(item, f"{path}[{index}]", assets_dir, root_data, modifications)


def create_jsonnet(data, modifications):
    """
    Create final jsonnet template with imports and placeholder substitution.

    Transforms the modified JSON into a jsonnet file by:
    1. Collecting all unique asset files and generating local variable declarations
    2. Converting JSON to formatted string
    3. Replacing placeholders with variable references or concatenation expressions

    Placeholder formats handled:
    - "__varname__" -> varname (single import reference)
    - "__CONCAT__var1 + var2__" -> var1 + var2 (concatenation expression)

    Args:
        data: Modified dashboard JSON with placeholders
        modifications: List of modification records from extraction

    Returns:
        Complete jsonnet file content as string

    Examples:
        >>> modifications = [
        ...     {'filename': 'colors.js', 'var_name': 'colors_js'},
        ...     {'filename': 'script.js', 'var_name': 'script_js'}
        ... ]
        >>> create_jsonnet({"script": "__CONCAT__colors_js + script_js__"}, modifications)
        '''local colors_js = importstr './assets/colors.js';
        local script_js = importstr './assets/script.js';

        {
          "script": colors_js + script_js
        }'''
    """
    # Convert JSON to formatted string
    json_content = json.dumps(data, indent=2)

    if not modifications:
        # No EXTERNAL content found, return plain JSON
        return json_content

    # Deduplicate imports: same file may be referenced multiple times
    unique_imports = {}
    for mod in modifications:
        filename = mod['filename']
        var_name = mod['var_name']
        if filename not in unique_imports:
            unique_imports[filename] = var_name

    # Generate local variable declarations (sorted for consistency)
    local_vars = [f"local {var_name} = importstr './assets/{filename}';"
                  for filename, var_name in sorted(unique_imports.items())]

    # Replace placeholders with jsonnet expressions
    def replace_placeholder(match):
        content = match.group(1)  # Extract content between __ markers
        # CONCAT__ prefix indicates concatenation expression
        return content[8:] if content.startswith('CONCAT__') else content

    json_content = re.sub(r'"__(.+?)__"', replace_placeholder, json_content)

    # Combine imports and content
    return '\n'.join(local_vars) + '\n\n' + json_content if local_vars else json_content


def process_json_file(json_file_path, base_dir=None):
    """
    Main entry point: process a dashboard JSON file to extract EXTERNAL content.

    Orchestrates the complete workflow:
    1. Load and validate JSON file
    2. Set up directory structure
    3. Extract EXTERNAL content to asset files
    4. Generate jsonnet template with imports
    5. Write template file and print summary

    Args:
        json_file_path: Path to the Grafana dashboard JSON file
        base_dir: Optional base directory name for organizing output
                  (e.g., "dashboards2" to create src/dashboards2/ subdirectory)

    Returns:
        True if successful, False if errors occurred

    Directory structure created:
        dashboards/
        ├── src/
        │   ├── assets/           # All extracted content files
        │   │   ├── dashboard-id-panel-id-script.js
        │   │   ├── dashboard-id-query.sql
        │   │   └── ...
        │   ├── dashboard-name.jsonnet  # Generated template
        │   └── [base_dir]/       # If base_dir specified
        │       └── dashboard-name.jsonnet

    Examples:
        >>> # Basic usage
        >>> process_json_file("dashboard.json")
        Processing: dashboard.json
        Dashboard ID: ee2jzeymn1o8wf
        ...
        ✓ Jsonnet template creation completed successfully

        >>> # With base_dir for organization
        >>> process_json_file("../../dashboards2/home.json", "dashboards2")
        # Creates: src/dashboards2/home.jsonnet
    """
    json_path = Path(json_file_path)

    # Validate file exists
    if not json_path.exists():
        print(f"Error: File not found: {json_file_path}")
        return False

    # Load and parse JSON
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {json_file_path}")
        print(f"JSON Error: {e}")
        return False

    # Set up output directory structure
    script_dir = Path(__file__).parent
    src_dir = script_dir / "src"
    assets_dir = src_dir / "assets"  # All assets go in shared assets/ dir
    template_dir = src_dir  # Default: templates in src/

    # Use base_dir to create subdirectories if specified
    if base_dir and base_dir in json_path.parts:
        base_index = json_path.parts.index(base_dir)
        if base_index < len(json_path.parts) - 2:
            # Preserve directory structure after base_dir
            relative_parts = json_path.parts[base_index + 1:-1]
            template_dir = src_dir / Path(*relative_parts)

    template_dir.mkdir(parents=True, exist_ok=True)

    # Print processing header
    dashboard_id = data.get('uid', data.get('id', 'dashboard'))
    print(f"Processing: {json_file_path}")
    print(f"Dashboard ID: {dashboard_id}")
    print(f"Assets directory: {assets_dir}")
    print(f"Template directory: {template_dir}")
    print("=" * 50)

    # Extract EXTERNAL content to asset files
    modifications = []
    extract_external_content(data, assets_dir=assets_dir, root_data=data, modifications=modifications)

    # Generate jsonnet template
    jsonnet_content = create_jsonnet(data, modifications)

    # Write jsonnet template file
    template_path = template_dir / f"{json_path.stem}.jsonnet"
    with open(template_path, 'w') as f:
        f.write(jsonnet_content)

    # Print summary of what was extracted
    print(f"\nCreated template: {template_path}")
    if modifications:
        # Group by JSON path for clearer summary
        by_path = {}
        for mod in modifications:
            path = mod['path']
            if path not in by_path:
                by_path[path] = []
            by_path[path].append(mod['filename'])

        print(f"Extracted external content from {len(by_path)} locations:")
        for path, filenames in by_path.items():
            if len(filenames) > 1:
                # Multiple segments (concatenation)
                print(f"  {path} -> {len(filenames)} segments: {', '.join(filenames)}")
            else:
                # Single file
                print(f"  {path} -> {filenames[0]}")
    else:
        print("No EXTERNAL references found - created jsonnet file without external assets.")

    print("\n✓ Jsonnet template creation completed successfully")
    return True


if __name__ == "__main__":
    # Command-line interface
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python extract_external_content.py <json_file> [base_dir]")
        print("Example: python extract_external_content.py dashboard.json")
        print("Example: python extract_external_content.py ../../dashboards2/home.json dashboards2")
        sys.exit(1)

    # Parse arguments
    json_file = sys.argv[1]
    base_dir = sys.argv[2] if len(sys.argv) > 2 else None

    # Process the file and exit with appropriate status code
    success = process_json_file(json_file, base_dir)
    sys.exit(0 if success else 1)
