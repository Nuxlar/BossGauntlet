#!/usr/bin/env python3
"""
Mod setup script — renames and updates a NewMod template to your mod's name.

Usage:
    python setup_mod.py <ModName> [--author <AuthorName>] [--version <Version>]
                                  [--description <Description>] [--website <URL>]

Examples:
    python setup_mod.py MyCoolMod
    python setup_mod.py MyCoolMod --author MyTeam --version 1.0.0 --description "My cool mod"
"""

import os
import re
import sys
import shutil
import argparse

TEMPLATE_NAME = "NewMod"


def read_file(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def replace_in_file(path, replacements):
    """Apply a dict of {old: new} replacements to a file."""
    content = read_file(path)
    for old, new in replacements.items():
        content = content.replace(old, new)
    write_file(path, content)
    print(f"  Updated: {path}")


def main():
    parser = argparse.ArgumentParser(description="Set up a new mod from the NewMod template.")
    parser.add_argument("mod_name", help="Your mod's name (no spaces recommended)")
    parser.add_argument("--author",      default="", help="Thunderstore team/author name")
    parser.add_argument("--version",     default="1.0.0", help="Mod version (default: 1.0.0)")
    parser.add_argument("--description", default="", help="Short mod description for manifest.json")
    parser.add_argument("--website",     default="", help="Website URL for manifest.json")
    args = parser.parse_args()

    mod_name    = args.mod_name
    author      = args.author
    version     = args.version
    description = args.description
    website     = args.website

    # Determine the root directory (same folder as this script)
    root = os.path.dirname(os.path.abspath(__file__))

    print(f"\n=== Setting up mod: {mod_name} ===\n")

    # ------------------------------------------------------------------ #
    # 1. Rename NewMod.sln
    # ------------------------------------------------------------------ #
    old_sln = os.path.join(root, f"{TEMPLATE_NAME}.sln")
    new_sln = os.path.join(root, f"{mod_name}.sln")

    if not os.path.exists(old_sln):
        sys.exit(f"ERROR: Could not find '{old_sln}'. "
                 "Make sure this script is in the same directory as NewMod.sln.")

    os.rename(old_sln, new_sln)
    print(f"  Renamed: {TEMPLATE_NAME}.sln → {mod_name}.sln")

    # ------------------------------------------------------------------ #
    # 2. Update contents of the .sln file
    # ------------------------------------------------------------------ #
    replace_in_file(new_sln, {
        TEMPLATE_NAME: mod_name,
        f"{TEMPLATE_NAME}\\{TEMPLATE_NAME}.csproj": f"{mod_name}\\{mod_name}.csproj",
    })

    # ------------------------------------------------------------------ #
    # 3. Rename the NewMod folder
    # ------------------------------------------------------------------ #
    old_folder = os.path.join(root, TEMPLATE_NAME)
    new_folder = os.path.join(root, mod_name)

    if os.path.isdir(new_folder):
        print(f"  Folder '{mod_name}/' already exists, skipping rename.")
    elif not os.path.isdir(old_folder):
        sys.exit(f"ERROR: Could not find folder '{old_folder}'.")
    else:
        os.rename(old_folder, new_folder)
        print(f"  Renamed folder: {TEMPLATE_NAME}/ → {mod_name}/")

    # ------------------------------------------------------------------ #
    # 4. Rename NewMod.csproj inside the folder
    # ------------------------------------------------------------------ #
    old_csproj = os.path.join(new_folder, f"{TEMPLATE_NAME}.csproj")
    new_csproj = os.path.join(new_folder, f"{mod_name}.csproj")

    if os.path.exists(new_csproj):
        print(f"  {mod_name}.csproj already exists, skipping rename.")
    elif not os.path.exists(old_csproj):
        sys.exit(f"ERROR: Could not find '{old_csproj}'.")
    else:
        os.rename(old_csproj, new_csproj)
        print(f"  Renamed: {TEMPLATE_NAME}.csproj → {mod_name}.csproj")

    # ------------------------------------------------------------------ #
    # 5. Update Log.cs — namespace + MOD_NAME constant
    # ------------------------------------------------------------------ #
    log_cs = os.path.join(new_folder, "Log.cs")
    if os.path.exists(log_cs):
        replace_in_file(log_cs, {
            f"namespace {TEMPLATE_NAME}": f"namespace {mod_name}",
            f"const string MOD_NAME = nameof({TEMPLATE_NAME});":
                f"const string MOD_NAME = nameof({mod_name});",
        })
    else:
        print(f"  WARNING: Log.cs not found at '{log_cs}', skipping.")

    # ------------------------------------------------------------------ #
    # 6. Update Main.cs — namespace + plugin metadata
    # ------------------------------------------------------------------ #
    main_cs = os.path.join(new_folder, "Main.cs")
    if os.path.exists(main_cs):
        content = read_file(main_cs)

        # Namespace
        content = content.replace(
            f"namespace {TEMPLATE_NAME}", f"namespace {mod_name}"
        )

        # PluginName — replace whatever string is currently there
        content = re.sub(
            r'((?:public\s+)?const\s+string\s+PluginName\s*=\s*")[^"]*(")',
            rf'\g<1>{mod_name}\g<2>',
            content
        )

        # PluginAuthor — replace whatever string is currently there
        if author:
            content = re.sub(
                r'((?:public\s+)?const\s+string\s+PluginAuthor\s*=\s*")[^"]*(")',
                rf'\g<1>{author}\g<2>',
                content
            )

        # PluginVersion — replace whatever string is currently there
        if version:
            content = re.sub(
                r'((?:public\s+)?const\s+string\s+PluginVersion\s*=\s*")[^"]*(")',
                rf'\g<1>{version}\g<2>',
                content
            )

        write_file(main_cs, content)
        print(f"  Updated: {main_cs}")
    else:
        print(f"  WARNING: Main.cs not found at '{main_cs}', skipping.")

    # ------------------------------------------------------------------ #
    # 7. Update manifest.json
    # ------------------------------------------------------------------ #
    manifest = os.path.join(root, "manifest.json")
    if os.path.exists(manifest):
        content = read_file(manifest)
        # Replace each field individually so we don't clobber unrelated values
        def set_json_field(text, key, value):
            # Matches: "key": "anything"
            return re.sub(
                rf'("{re.escape(key)}":\s*)"[^"]*"',
                rf'\1"{value}"',
                text
            )

        content = set_json_field(content, "name",        mod_name)
        content = set_json_field(content, "version_number", version)
        content = set_json_field(content, "website_url", website)
        if description:
            content = set_json_field(content, "description", description)

        write_file(manifest, content)
        print(f"  Updated: manifest.json")
    else:
        print(f"  WARNING: manifest.json not found at '{manifest}', skipping.")

    print(f"\nDone! Your mod '{mod_name}' is ready to go.\n")


if __name__ == "__main__":
    main()