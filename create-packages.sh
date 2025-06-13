#!/bin/bash

# Store the original working directory
ORIG_DIR="$(pwd)"

# Create temporary directory
TEMP_DIR=$(mktemp -d)
mkdir -p "$TEMP_DIR/delta-installer"

# Copy necessary files
cp install.sh "$TEMP_DIR/delta-installer/"
cp install-macos.sh "$TEMP_DIR/delta-installer/"
cp requirements.txt "$TEMP_DIR/delta-installer/"
cp -r img "$TEMP_DIR/delta-installer/"

# Create Linux package
cd "$TEMP_DIR"
tar czf delta-installer-linux.tar.gz delta-installer/
cat > delta-installer-linux.sh << 'EOF'
#!/bin/bash
TEMP_DIR=$(mktemp -d)
ARCHIVE=$(awk '/^__ARCHIVE_BELOW__/ {print NR + 1; exit 0; }' "$0")
tail -n +$ARCHIVE "$0" | tar xz -C "$TEMP_DIR"
cd "$TEMP_DIR/delta-installer"
bash install.sh
rm -rf "$TEMP_DIR"
exit 0
__ARCHIVE_BELOW__
EOF
cat delta-installer-linux.tar.gz >> delta-installer-linux.sh
chmod +x delta-installer-linux.sh

# Create macOS package
cd "$TEMP_DIR"
tar czf delta-installer-macos.tar.gz delta-installer/
cat > delta-installer-macos.sh << 'EOF'
#!/bin/bash
TEMP_DIR=$(mktemp -d)
ARCHIVE=$(awk '/^__ARCHIVE_BELOW__/ {print NR + 1; exit 0; }' "$0")
tail -n +$ARCHIVE "$0" | tar xz -C "$TEMP_DIR"
cd "$TEMP_DIR/delta-installer"
bash install-macos.sh
rm -rf "$TEMP_DIR"
exit 0
__ARCHIVE_BELOW__
EOF
cat delta-installer-macos.tar.gz >> delta-installer-macos.sh
chmod +x delta-installer-macos.sh

# Move packages to original directory
mv delta-installer-linux.sh "$ORIG_DIR/delta-installer-linux.sh"
mv delta-installer-macos.sh "$ORIG_DIR/delta-installer-macos.sh"

# Cleanup
cd "$ORIG_DIR"
rm -rf "$TEMP_DIR"

echo "Packages created successfully in the current directory!" 