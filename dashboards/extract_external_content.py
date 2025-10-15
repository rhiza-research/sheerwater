#!/usr/bin/env python3
"""
Script to extract EXTERNAL content from JSON files to separate asset files
and create template files with placeholders.
"""

import json
import re
import sys
from pathlib import Path

# TODO: determine if the best markdown comment syntax is 
#   [comment]: # (EXTERNAL)
# or 
#   <!-- EXTERNAL -->


def parse_external_params(first_line):
    """
    Parse parameters from EXTERNAL({...}) format.

    Returns a dict with parsed params, or None if not in this format.
    Example: EXTERNAL({panel_id:"weekly-temperature-results", key: "params"})
    Returns: {"panel_id": "weekly-temperature-results", "key": "params"}
    """
    # Look for EXTERNAL({...}) pattern
    match = re.match(r'.*EXTERNAL\s*\(\s*\{([^}]+)\}\s*\)', first_line)
    if not match:
        return None

    params_str = match.group(1)
    params = {}

    # Parse key-value pairs (handle both "key":"value" and key:"value" and "key": "value")
    # Split by comma, then parse each pair
    pairs = re.split(r',\s*', params_str)
    for pair in pairs:
        # Match key:value where key and value can be quoted or unquoted
        kv_match = re.match(r'^\s*["\']?([^"\':\s]+)["\']?\s*:\s*["\']?([^"\']+)["\']?\s*$', pair)
        if kv_match:
            key = kv_match.group(1).strip()
            value = kv_match.group(2).strip()
            params[key] = value

    return params if params else None

def determine_file_extension(content):
    """Determine appropriate file extension based on content."""
    content_lower = content.lower().strip()

    if content_lower.startswith('function') or 'function(' in content_lower or content_lower.startswith('//'):
        return '.js'
    elif content_lower.startswith('<') or '<html' in content_lower:
        return '.html'
    elif content_lower.startswith('#') or content_lower.startswith('##'):
        return '.md'
    elif 'select' in content_lower and 'from' in content_lower:
        return '.sql'
    else:
        return '.txt'

def get_panel_info(root_data, current_path):
    """Extract panel ID and dashboard info from the current path context."""
    path_parts = current_path.split('.')

    # Extract dashboard UID from root
    dashboard_id = root_data.get('uid', root_data.get('id', 'dashboard'))

    # Find panel info from path
    panel_id = None

    # Look for panels[X] pattern in any part of the path
    for part in path_parts:
        if part.startswith('panels[') and part.endswith(']'):
            # Extract panel index from panels[X]
            index_str = part[7:-1]  # Remove 'panels[' and ']'
            try:
                panel_index = int(index_str)

                # Get the actual panel ID from the data
                panels = root_data.get('panels', [])
                if panel_index < len(panels):
                    panel_id = panels[panel_index].get('id')
                else:
                    panel_id = f"panel-{panel_index}"
            except (ValueError, IndexError, AttributeError):
                panel_id = f"panel-{index_str}"
            break

    return panel_id, dashboard_id

def split_multi_external_content(value):
    """
    Split content that contains multiple EXTERNAL markers.

    Returns a list of tuples: [(first_line, content), ...]
    where first_line contains the EXTERNAL marker and content is the rest.
    """
    lines = value.split('\n')
    segments = []
    current_first_line = None
    current_content = []

    for line in lines:
        if 'EXTERNAL' in line:
            # Check if there's content before EXTERNAL on the same line
            external_pos = line.find('EXTERNAL')
            before_external = line[:external_pos]

            # Look for comment markers (// or /* or #) right before EXTERNAL
            # If there's a comment marker, include it with EXTERNAL, not the previous segment
            comment_start = before_external.rfind('//')
            if comment_start == -1:
                comment_start = before_external.rfind('/*')
            if comment_start == -1:
                comment_start = before_external.rfind('#')

            if comment_start != -1:
                # There's a comment marker - split there
                actual_content = before_external[:comment_start].rstrip()
                external_line_start = before_external[comment_start:]
            else:
                # No comment marker - all before EXTERNAL is content
                actual_content = before_external.rstrip()
                external_line_start = ''

            # If there's actual content before the comment/EXTERNAL, add it to current segment
            if actual_content and current_first_line is not None:
                current_content.append(actual_content)

            # Save previous segment if exists
            if current_first_line is not None:
                segments.append((current_first_line, '\n'.join(current_content)))

            # Start new segment with the EXTERNAL part (including any comment marker)
            current_first_line = external_line_start + line[external_pos:]
            current_content = []
        else:
            # Add to current segment
            if current_first_line is not None:
                current_content.append(line)

    # Save last segment
    if current_first_line is not None:
        segments.append((current_first_line, '\n'.join(current_content)))

    return segments

def generate_filename_for_segment(seg_first_line, seg_content, key, current_path, root_data):
    """
    Generate filename for a single segment.

    Returns: (filename, content_with_marker)
    """
    params = parse_external_params(seg_first_line)

    # Check if it's already EXTERNAL:filename format
    if "EXTERNAL:" in seg_first_line:
        external_start = seg_first_line.find("EXTERNAL:")
        filename_part = seg_first_line[external_start + 9:]

        delimiters = [' ', '\t', '\n', ')', ']', '}']
        end_pos = len(filename_part)
        for delimiter in delimiters:
            pos = filename_part.find(delimiter)
            if pos != -1 and pos < end_pos:
                end_pos = pos

        filename = filename_part[:end_pos].strip()
        # Reconstruct full content
        content = seg_first_line + "\n" + seg_content
        return filename, content

    # Generate filename
    panel_id, dashboard_id = get_panel_info(root_data, current_path)

    # Override with parsed parameters if they exist
    if params:
        dashboard_id = params.get('dashboard_id', dashboard_id)
        panel_id = params.get('panel_id', panel_id)
        key_override = params.get('key')
        ext_override = params.get('ext')
    else:
        key_override = None
        ext_override = None

    # Use key_override if provided, otherwise use the current key
    filename_key = key_override if key_override else key

    # Don't add segment index - parameters should make filenames unique
    # if segment_idx is not None:
    #     filename_key = f"{filename_key}-{segment_idx}"

    # Generate file extension
    if ext_override:
        ext = ext_override if ext_override.startswith('.') else f".{ext_override}"
    else:
        ext = determine_file_extension(seg_content)

    # Generate filename
    if panel_id:
        if dashboard_id:
            filename = f"{dashboard_id}-{panel_id}-{filename_key}{ext}"
        else:
            filename = f"panel-{panel_id}-{filename_key}{ext}"
    else:
        # Fallback naming
        safe_path = current_path.replace('.', '-').replace('[', '-').replace(']', '')
        filename = f"{safe_path}{ext}"

    # Create new first line with filename, preserving parameters
    external_pos = seg_first_line.find("EXTERNAL")
    before_external = seg_first_line[:external_pos]
    after_external_start = external_pos + len("EXTERNAL")
    after_external = seg_first_line[after_external_start:]

    # Build the new EXTERNAL line with filename
    if params:
        # Keep the params in the output: EXTERNAL({...}):filename
        # Find the closing paren of EXTERNAL({...})
        paren_match = re.search(r'\([^)]*\{[^}]+\}\s*\)', after_external)
        if paren_match:
            params_part = paren_match.group(0)  # The ({...}) part
            after_params = after_external[paren_match.end():]
            new_first_line = f"{before_external}EXTERNAL{params_part}:{filename}{after_params}"
        else:
            # Fallback if pattern doesn't match
            new_first_line = f"{before_external}EXTERNAL:{filename}{after_external}"
    else:
        # No params, just add filename
        new_first_line = f"{before_external}EXTERNAL:{filename}{after_external}"

    content = new_first_line + "\n" + seg_content

    return filename, content

def process_multi_external_segments(segments, key, current_path, assets_dir, root_data, modifications, obj):
    """
    Process multiple EXTERNAL segments in a single value.
    Creates multiple asset files and a concatenation expression in jsonnet.
    """
    filenames = []
    local_var_names = []

    # Process each segment
    for idx, (seg_first_line, seg_content) in enumerate(segments):
        filename, content = generate_filename_for_segment(
            seg_first_line, seg_content, key, current_path, root_data
        )

        # Create assets directory if it doesn't exist
        assets_dir.mkdir(exist_ok=True)

        # Write content to file
        asset_file = assets_dir / filename
        with open(asset_file, 'w') as f:
            f.write(content)
        print(f"  Wrote segment {idx} to: {asset_file}")

        filenames.append(filename)

        # Generate local variable name (sanitize filename)
        var_name = filename.replace('-', '_').replace('.', '_')
        # Ensure variable name doesn't start with a number
        if var_name[0].isdigit():
            var_name = 'f_' + var_name
        local_var_names.append(var_name)

    # Create concatenation expression: var1 + var2 + var3
    concat_expr = ' + '.join(local_var_names)
    placeholder = f"__JSONNET_MULTI_IMPORT__{concat_expr}__"

    # Track modification with special multi-import marker
    modifications.append({
        'path': current_path,
        'original_value': None,  # Not needed for multi
        'new_value': placeholder,
        'filenames': filenames,
        'local_var_names': local_var_names,
        'is_multi': True
    })

    # Update the value in place
    obj[key] = placeholder

def extract_external_content(obj, path="", assets_dir=None, root_data=None, modifications=None):
    """
    Recursively traverse JSON and extract EXTERNAL content to files.

    Args:
        obj: Current JSON object/value
        path: Current JSON path
        assets_dir: Path to assets directory
        root_data: Root JSON data for context
        modifications: List to track modifications made
    """
    if modifications is None:
        modifications = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key

            #print(f"    Processing {current_path}: {type(value)} = {repr(value) if isinstance(value, str) else f'{type(value)} with {len(value) if hasattr(value, '__len__') else 'unknown'} items'}")

            # Check if this value contains EXTERNAL in the first line
            if isinstance(value, str):
                lines = value.split('\n', 1)
                first_line = lines[0]

                # Debug output for all strings
                #print(f"  Debug checking: {current_path} = {repr(first_line)}")

                if "EXTERNAL" in first_line:
                    print(f"Found EXTERNAL at: {current_path}")

                    # Check for multiple EXTERNAL markers in the value
                    segments = split_multi_external_content(value)

                    if len(segments) > 1:
                        print(f"  Found {len(segments)} EXTERNAL segments")
                        # Handle multiple EXTERNAL markers
                        process_multi_external_segments(
                            segments, key, current_path, assets_dir,
                            root_data, modifications, obj
                        )
                        continue  # Skip to next key

                    # Single EXTERNAL - process normally
                    params = parse_external_params(first_line)

                    # Check if it's EXTERNAL:filename format
                    if "EXTERNAL:" in first_line:
                        # Extract filename from first line, stopping at common delimiters
                        external_start = first_line.find("EXTERNAL:")
                        filename_part = first_line[external_start + 9:]

                        # Stop at common delimiter characters: ), ], }, space, tab, newline
                        delimiters = [' ', '\t', '\n', ')', ']', '}']
                        end_pos = len(filename_part)
                        for delimiter in delimiters:
                            pos = filename_part.find(delimiter)
                            if pos != -1 and pos < end_pos:
                                end_pos = pos

                        filename = filename_part[:end_pos].strip()
                        content = value  # Keep the entire original content including EXTERNAL line
                        print(f"  Named external reference: {filename}")
                    else:
                        # Just EXTERNAL or EXTERNAL({...}), generate filename and convert to named format
                        original_content = lines[1] if len(lines) > 1 else ""

                        # Get panel info from root data and path (default values)
                        panel_id, dashboard_id = get_panel_info(root_data, current_path)

                        # Override with parsed parameters if they exist
                        if params:
                            print(f"  Parsed params: {params}")
                            dashboard_id = params.get('dashboard_id', dashboard_id)
                            panel_id = params.get('panel_id', panel_id)
                            key_override = params.get('key')
                            ext_override = params.get('ext')
                        else:
                            key_override = None
                            ext_override = None

                        # Use key_override if provided, otherwise use the current key
                        filename_key = key_override if key_override else key

                        # Generate file extension
                        if ext_override:
                            ext = ext_override if ext_override.startswith('.') else f".{ext_override}"
                        else:
                            ext = determine_file_extension(original_content)

                        # Generate filename
                        if panel_id:
                            if dashboard_id:
                                filename = f"{dashboard_id}-{panel_id}-{filename_key}{ext}"
                            else:
                                filename = f"panel-{panel_id}-{filename_key}{ext}"
                        else:
                            # Fallback naming
                            safe_path = current_path.replace('.', '-').replace('[', '-').replace(']', '')
                            filename = f"{safe_path}{ext}"

                        print(f"  Generated filename: {filename}")

                        # Find EXTERNAL and replace it with EXTERNAL:filename, preserving surrounding text and params
                        # Handle cases like "EXTERNAL )" or "EXTERNAL({...})" or just "EXTERNAL"
                        external_pos = first_line.find("EXTERNAL")
                        before_external = first_line[:external_pos]

                        # Find what comes after EXTERNAL (like " )" or "({...})" or "")
                        after_external_start = external_pos + len("EXTERNAL")
                        after_external = first_line[after_external_start:]

                        # Build the new EXTERNAL line with filename, preserving parameters
                        if params:
                            # Keep the params in the output: EXTERNAL({...}):filename
                            # Find the closing paren of EXTERNAL({...})
                            paren_match = re.search(r'\([^)]*\{[^}]+\}\s*\)', after_external)
                            if paren_match:
                                params_part = paren_match.group(0)  # The ({...}) part
                                after_params = after_external[paren_match.end():]
                                new_first_line = f"{before_external}EXTERNAL{params_part}:{filename}{after_params}"
                            else:
                                # Fallback if pattern doesn't match
                                new_first_line = f"{before_external}EXTERNAL:{filename}{after_external}"
                        else:
                            # No params, just add filename
                            new_first_line = f"{before_external}EXTERNAL:{filename}{after_external}"

                        # Reconstruct content with new first line
                        if len(lines) > 1:
                            content = new_first_line + "\n" + lines[1]
                        else:
                            content = new_first_line

                    # Create a special marker for jsonnet importstr that we'll replace later
                    # Use relative path from src/ to local assets/
                    placeholder = f"__JSONNET_IMPORTSTR__./assets/{filename}__"

                    # Create assets directory if it doesn't exist
                    assets_dir.mkdir(exist_ok=True)

                    # Write content to file
                    asset_file = assets_dir / filename
                    with open(asset_file, 'w') as f:
                        f.write(content)
                    print(f"  Wrote content to: {asset_file}")

                    # Track modification
                    modifications.append({
                        'path': current_path,
                        'original_value': value,
                        'new_value': placeholder,
                        'filename': filename
                    })

                    # Update the value in place
                    obj[key] = placeholder

            # Always recursively process non-string values
            else:
                #print(f"    Recursing into {current_path} ({type(value)})")
                extract_external_content(value, current_path, assets_dir, root_data, modifications)

    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            current_path = f"{path}[{index}]"
            extract_external_content(item, current_path, assets_dir, root_data, modifications)

def process_json_file(json_file_path, base_dir=None):
    """
    Process a JSON file to extract EXTERNAL content and create template.

    Args:
        json_file_path: Path to the input JSON file
        base_dir: Optional base directory name to determine folder structure (e.g., "dashboards2")
    """
    json_path = Path(json_file_path)

    if not json_path.exists():
        print(f"Error: File not found: {json_file_path}")
        return False

    # Load JSON
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {json_file_path}")
        print(f"JSON Error: {e}")
        return False

    # Setup paths
    script_dir = Path(__file__).parent
    src_dir = script_dir / "src"
    assets_dir = src_dir / "assets"

    # Determine template directory based on base_dir
    template_dir = src_dir  # default

    if base_dir and base_dir in json_path.parts:
        # Find the base directory in the path and preserve structure after it
        base_index = json_path.parts.index(base_dir)
        if base_index < len(json_path.parts) - 2:  # -2 because we don't want the filename itself
            # Has subfolders after the base directory
            relative_parts = json_path.parts[base_index + 1:-1]  # Exclude the filename
            template_dir = src_dir / Path(*relative_parts)

    # Create the template directory if it doesn't exist
    template_dir.mkdir(parents=True, exist_ok=True)

    # Extract dashboard ID for display
    dashboard_id = data.get('uid', data.get('id', 'dashboard'))

    print(f"Processing: {json_file_path}")
    print(f"Dashboard ID: {dashboard_id}")
    print(f"Assets directory: {assets_dir}")
    print(f"Template directory: {template_dir}")
    print("=" * 50)

    # Extract external content
    modifications = []
    extract_external_content(data, assets_dir=assets_dir, root_data=data, modifications=modifications)

    # Create template filename in the appropriate subfolder
    template_path = template_dir / f"{json_path.stem}.jsonnet"

    # Save JSON as template, then fix importstr syntax if any modifications were made
    json_content = json.dumps(data, indent=2)

    if modifications:
        # Collect all unique imports (both single and multi)
        # Use a dict to track unique filename -> var_name mappings
        unique_imports = {}  # filename -> var_name

        # First, collect all files that need to be imported
        for mod in modifications:
            if mod.get('is_multi'):
                # Multi-import: add each file
                for var_name, filename in zip(mod['local_var_names'], mod['filenames']):
                    if filename not in unique_imports:
                        unique_imports[filename] = var_name
            else:
                # Single import: extract filename from placeholder
                filename = mod.get('filename')
                if filename:
                    var_name = filename.replace('-', '_').replace('.', '_')
                    # Ensure variable name doesn't start with a number
                    if var_name[0].isdigit():
                        var_name = 'f_' + var_name
                    if filename not in unique_imports:
                        unique_imports[filename] = var_name

        # Generate local variable declarations (sorted for consistency)
        local_vars = []
        for filename in sorted(unique_imports.keys()):
            var_name = unique_imports[filename]
            local_vars.append(f"local {var_name} = importstr './assets/{filename}';")

        # Replace multi-import placeholders with concatenation expressions
        for mod in modifications:
            if mod.get('is_multi'):
                # Replace __JSONNET_MULTI_IMPORT__var1 + var2__  with  var1 + var2
                placeholder = mod['new_value']
                concat_expr = placeholder.replace('__JSONNET_MULTI_IMPORT__', '').replace('__', '')
                json_content = json_content.replace(f'"{placeholder}"', concat_expr)

        # Replace single import markers with variable references
        for mod in modifications:
            if not mod.get('is_multi'):
                filename = mod.get('filename')
                if filename and filename in unique_imports:
                    placeholder = mod['new_value']
                    var_name = unique_imports[filename]
                    json_content = json_content.replace(f'"{placeholder}"', var_name)

        # Add local variables at the top if there are any
        if local_vars:
            jsonnet_content = '\n'.join(local_vars) + '\n\n' + json_content
        else:
            jsonnet_content = json_content
    else:
        # No modifications, just use the JSON as-is for jsonnet
        jsonnet_content = json_content

    with open(template_path, 'w') as f:
        f.write(jsonnet_content)

    print(f"\nCreated template: {template_path}")
    if modifications:
        print(f"Extracted {len(modifications)} external references:")
        for mod in modifications:
            if mod.get('is_multi'):
                print(f"  {mod['path']} -> {len(mod['filenames'])} segments: {', '.join(mod['filenames'])}")
            else:
                print(f"  {mod['path']} -> {mod['filename']}")
    else:
        print("No EXTERNAL references found - created jsonnet file without external assets.")

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python extract_external_content.py <json_file> [base_dir]")
        print("Example: python extract_external_content.py dashboard.json")
        print("Example: python extract_external_content.py ../../dashboards2/subfolder/file.json dashboards2")
        sys.exit(1)

    json_file = sys.argv[1]
    base_dir = sys.argv[2] if len(sys.argv) == 3 else None
    success = process_json_file(json_file, base_dir)

    if success:
        print("\n✓ Jsonnet template creation completed successfully")
    else:
        print("\n✗ Jsonnet template creation failed")
        sys.exit(1)