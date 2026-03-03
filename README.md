# Unicode Checker

Unicode Checker is a Visual Studio Code extension that scans files and folders for invisible, formatting, and non-allowed Unicode characters.

It is especially useful for researchers and developers who want to prevent hidden characters (zero-width, non-breaking spaces, directional markers, etc.) from breaking compilation, diffs, or downstream processing.

The extension runs a bundled Python scanner on selected files or folders, highlights problematic characters inside the editor, reports diagnostics in the Problems panel, and marks affected files in the Explorer with a badge.

---

## 🚀 Features

- Scan single files from the editor
- Scan multiple selected files from the Explorer
- Recursively scan entire folders
- Detect invisible and formatting Unicode characters
- Highlight offending characters in the editor
- Report issues in the Problems panel
- Mark affected files in the Explorer with a badge
- Works with UTF-8 text (including English and German character sets)

---

## 📋 Usage

### Scan from Explorer

1. Select one or more files or folders.
2. Right-click.
3. Choose **Check Unicode / Invisible Characters**.
4. The extension scans all selected items recursively.
5. Problems are shown in the Problems panel.
6. Files containing issues receive a badge in the Explorer.

### Scan from Editor

1. Open a file in the editor.
2. Right-click inside the editor.
3. Choose **Check Unicode / Invisible Characters**.
4. The active file is scanned.

---

## ⚙️ Requirements

- Python 3 must be installed.
- `python3` (or `python`) must be available in your system PATH.

---

## 🧑‍💻 Development Setup

1. Clone the repository.
2. Open the extension root folder in VS Code.
3. Install dependencies:

```bash
   npm install
```

## Compile Extension

```bash
    npm run compile
```

## Packaging Extension

```bash
    npm install -g @vscode/vsce
    vsce package
```

## Installing Extension

```bash
    code --install-extension unicode-check-0.0.1.vsix
```
