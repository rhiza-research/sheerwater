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
                        # Just EXTERNAL, generate filename and convert to named format
                        original_content = lines[1] if len(lines) > 1 else ""

                        # Get panel info from root data and path
                        panel_id, dashboard_id = get_panel_info(root_data, current_path)

                        # Generate filename
                        ext = determine_file_extension(original_content)
                        if panel_id:
                            if dashboard_id:
                                filename = f"{dashboard_id}-{panel_id}-{key}{ext}"
                            else:
                                filename = f"panel-{panel_id}-{key}{ext}"
                        else:
                            # Fallback naming
                            safe_path = current_path.replace('.', '-').replace('[', '-').replace(']', '')
                            filename = f"{safe_path}{ext}"

                        print(f"  Generated filename: {filename}")

                        # Find EXTERNAL and replace it with EXTERNAL:filename, preserving surrounding text
                        # Handle cases like "EXTERNAL )" or just "EXTERNAL"
                        external_pos = first_line.find("EXTERNAL")
                        before_external = first_line[:external_pos]

                        # Find what comes after EXTERNAL (like " )" or "")
                        after_external_start = external_pos + len("EXTERNAL")
                        after_external = first_line[after_external_start:]

                        # Create new first line with filename, preserving the structure
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
        # Replace special markers with proper jsonnet importstr syntax
        jsonnet_content = re.sub(
            r'"__JSONNET_IMPORTSTR__([^_]+)__"',
            r"importstr '\1'",
            json_content
        )
    else:
        # No modifications, just use the JSON as-is for jsonnet
        jsonnet_content = json_content

    with open(template_path, 'w') as f:
        f.write(jsonnet_content)

    print(f"\nCreated template: {template_path}")
    if modifications:
        print(f"Extracted {len(modifications)} external references:")
        for mod in modifications:
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