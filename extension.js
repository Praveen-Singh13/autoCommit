// The module 'vscode' contains the VS Code extensibility API
const vscode = require('vscode');

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
	console.log('AutoCommit extension is now active!');

	// Register the manual trigger command
	const disposable = vscode.commands.registerCommand('autocommit.triggerCommit', function () {
		// Placeholder — Python invocation will be added in Phase 5
		vscode.window.showInformationMessage('AutoCommit triggered!');
	});

	context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
	activate,
	deactivate
}
