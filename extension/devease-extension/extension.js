// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require('vscode');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed

/**
 * @param {vscode.ExtensionContext} context
 */

global.analysisResults = null;

async function sendToBackend(files) {
    try {
		const fileContents = files.map(file => ({
			filename: path.basename(file),
			path: file,
			content: fs.readFileSync(file, 'utf8')
		}));
        const response = await axios.post("http://127.0.0.1:8000/analyze", {
            files: fileContents
        });

        console.log(response.data);

        vscode.window.showInformationMessage("Backend analysis done!");
		global.analysisResults = response.data;
    } catch (error) {
        console.error(error);

        vscode.window.showErrorMessage("Backend error");
    }
}


function activate(context) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('"devease-extension" is now active!');

	let disposable = vscode.commands.registerCommand('devease-extension.DevEaseAnalyzer', async function () {
		const workspaceFolders = vscode.workspace.workspaceFolders;
		if (!workspaceFolders) {
			vscode.window.showErrorMessage('No workspace folder is open.');
			return;
		}

		const projectPath = workspaceFolders[0].uri.fsPath;

		vscode.window.showInformationMessage(`Analyzing project at: ${projectPath}`);

		let files = getAllFiles(projectPath);

		vscode.window.showInformationMessage(`Found ${files.length} files in the project.`);

		console.log("Files:", files);

		await sendToBackend(files);

		// vscode.window.showInformationMessage('Analysis complete!');
	});

	let panelCommand = vscode.commands.registerCommand(
    'devease-extension.openPanel',
    function () {

        const panel = vscode.window.createWebviewPanel(
            'deveasePanel',
            'DevEase Dashboard',
            vscode.ViewColumn.One,
            {
                enableScripts: true
            }
        );

        // OPTION 1: EMBED YOUR FRONTEND WEBSITE
        panel.webview.html = `
            <html>
                <body style="margin:0; padding:0; overflow:hidden;">
                    <iframe
                        src="http://localhost:5173/dashboard"
                        style="width:100%; height:100vh; border:none;">
                    </iframe>
					<script>
					window.addEventListener('message', (event) => {
						console.log(event.data);
					});
					</script>
                </body>
            </html>
        `;
    }
);

context.subscriptions.push(panelCommand);

	context.subscriptions.push(disposable);
}

// This method is called when your extension is deactivated
function deactivate() {}

function getAllFiles(dirPath, arrayOfFiles = []) {
	const files = fs.readdirSync(dirPath);

	files.forEach(function (file) {
		const fullPath = path.join(dirPath, file);

		if(fs.statSync(fullPath).isDirectory()) {
			getAllFiles(fullPath, arrayOfFiles);
		} else {
			arrayOfFiles.push(fullPath);
		}
	});
	return arrayOfFiles;
}

module.exports = {
	activate,
	deactivate
}
