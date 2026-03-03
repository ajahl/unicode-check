import * as vscode from "vscode";
import * as cp from "child_process";
import * as path from "path";

let diagnosticCollection: vscode.DiagnosticCollection;
let extensionContext: vscode.ExtensionContext;
const filesWithProblems = new Set<string>();

const decorationEmitter = new vscode.EventEmitter<vscode.Uri | vscode.Uri[]>();
vscode.window.registerFileDecorationProvider({
  onDidChangeFileDecorations: decorationEmitter.event,
  provideFileDecoration(uri: vscode.Uri) {
    // Only show a badge for file paths that were flagged
    if (filesWithProblems.has(uri.toString())) {
      return {
        badge: "!",
        tooltip: "Unicode issues detected",
        color: new vscode.ThemeColor("editorWarning.foreground"),
      };
    }
    return;
  },
});

export function activate(context: vscode.ExtensionContext) {
  extensionContext = context;

  diagnosticCollection =
    vscode.languages.createDiagnosticCollection("CheckUnicode");

  context.subscriptions.push(diagnosticCollection);

  context.subscriptions.push(
    vscode.commands.registerCommand(
      "extension.checkUnicode",
      (...args: any[]) => {
        handleSelectionOrActiveEditor(args);
      },
    ),
  );
}

async function handleSelectionOrActiveEditor(args: any[]) {
  const primary: vscode.Uri | undefined = args[0];
  const selected: vscode.Uri[] = Array.isArray(args[1]) ? args[1] : [];

  const urisToCheck = selected.length > 0 ? selected : primary ? [primary] : [];

  if (urisToCheck.length === 0) {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showInformationMessage("Open or select a file first");
      return;
    }
    runChecker(editor.document);
    return;
  }

  for (const uri of urisToCheck) {
    const stat = await vscode.workspace.fs.stat(uri);

    if ((stat.type & vscode.FileType.Directory) !== 0) {
      await processFolderRecursive(uri);
    } else {
      const document = await vscode.workspace.openTextDocument(uri);
      runChecker(document);
    }
  }
}

async function processFolderRecursive(folderUri: vscode.Uri) {
  const entries = await vscode.workspace.fs.readDirectory(folderUri);

  for (const [name, type] of entries) {
    const entryUri = vscode.Uri.joinPath(folderUri, name);

    if ((type & vscode.FileType.Directory) !== 0) {
      await processFolderRecursive(entryUri);
    } else if ((type & vscode.FileType.File) !== 0) {
      const document = await vscode.workspace.openTextDocument(entryUri);
      runChecker(document);
    }
  }
}

export function deactivate() {
  diagnosticCollection?.dispose();
}

function runChecker(document: vscode.TextDocument) {
  diagnosticCollection.delete(document.uri);

  const scriptPath = path.join(
    extensionContext.extensionPath,
    "scripts",
    "unicode_checker.py",
  );

  const python = "python3";
  const filePath = document.fileName;

  cp.exec(`${python} "${scriptPath}" "${filePath}"`, (err, stdout, stderr) => {
    if (err && (<any>err).code !== 0) {
      vscode.window.showErrorMessage(`Checker error: ${stderr}`);
      return;
    }

    const diagnostics: vscode.Diagnostic[] = [];
    let hasIssues = false;
    filesWithProblems.delete(document.uri.toString());

    const lines = stdout.split(/\r?\n/);

    for (const line of lines) {
      const parts = line.match(/^(.*?):(\d+):(\d+) (.+?) U\+([0-9A-F]+) (.*)$/);

      if (!parts) {
        continue;
      }
      hasIssues = true;
      const lineNum = Number(parts[2]) - 1;
      const colNum = Number(parts[3]) - 1;
      const message = `${parts[4]} U+${parts[5]} ${parts[6]}`;

      const range = new vscode.Range(lineNum, colNum, lineNum, colNum + 1);
      const diag = new vscode.Diagnostic(
        range,
        message,
        vscode.DiagnosticSeverity.Information,
      );
      diagnostics.push(diag);
    }

    if (hasIssues) {
      filesWithProblems.add(document.uri.toString());
      decorationEmitter.fire(document.uri);
    }
    diagnosticCollection.set(document.uri, diagnostics);
  });
}
