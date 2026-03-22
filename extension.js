const vscode = require('vscode');
const { execFile, execSync } = require('child_process');
const path = require('path');

/**
 * Run the AutoCommit Python pipeline.
 * @param {string} workspacePath - Absolute path to the Git workspace
 * @param {string} extensionPath - Absolute path to the extension directory
 * @returns {Promise<{status: string, message: string, commit_message?: string}>}
 */
function runAutoCommit(workspacePath, extensionPath) {
	return new Promise((resolve, reject) => {
		const config = vscode.workspace.getConfiguration('autocommit');
		const pythonPath = config.get('pythonPath', 'python');
		const scriptPath = path.join(extensionPath, 'python', 'main.py');

		// Pass settings to Python via environment variables (secure — never written to disk)
		const env = Object.assign({}, process.env, {
			AUTOCOMMIT_API_KEY: config.get('apiKey', ''),
			AUTOCOMMIT_API_PROVIDER: config.get('apiProvider', 'gemini'),
			AUTOCOMMIT_MODEL: config.get('model', 'gemini-2.0-flash'),
		});

		execFile(pythonPath, [scriptPath, workspacePath], { env, timeout: 30000 }, (error, stdout, stderr) => {
			// Log stderr (progress messages) to the output channel
			if (stderr) {
				console.log('[AutoCommit]', stderr);
			}

			// Parse JSON from stdout
			if (stdout && stdout.trim()) {
				try {
					const result = JSON.parse(stdout.trim());
					resolve(result);
					return;
				} catch {
					// JSON parse failed — fall through to error handling
				}
			}

			if (error) {
				// Handle Python not found
				if (error.code === 'ENOENT') {
					reject(new Error(`Python not found at "${pythonPath}". Please install Python or update the autocommit.pythonPath setting.`));
					return;
				}
				reject(new Error(error.message || 'AutoCommit process failed'));
				return;
			}

			reject(new Error('No output from AutoCommit script'));
		});
	});
}

/**
 * Get the current workspace folder path, or null if none.
 */
function getWorkspacePath() {
	const folders = vscode.workspace.workspaceFolders;
	if (!folders || folders.length === 0) {
		return null;
	}
	return folders[0].uri.fsPath;
}

// ──────────────────────────────────────────────
// Extension lifecycle
// ──────────────────────────────────────────────

/** @type {vscode.StatusBarItem} */
let statusBarItem;

/** @type {string} */
let extensionDir;

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
	console.log('AutoCommit extension is now active!');
	extensionDir = context.extensionPath;

	// ── Status bar item ──
	statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
	statusBarItem.text = '$(git-commit) AutoCommit';
	statusBarItem.tooltip = 'Click to auto-commit with AI message';
	statusBarItem.command = 'autocommit.triggerCommit';
	statusBarItem.show();
	context.subscriptions.push(statusBarItem);

	// ── Command palette trigger ──
	const disposable = vscode.commands.registerCommand('autocommit.triggerCommit', async function () {
		const workspacePath = getWorkspacePath();
		if (!workspacePath) {
			vscode.window.showWarningMessage('AutoCommit: No workspace folder is open.');
			return;
		}

		statusBarItem.text = '$(sync~spin) AutoCommit...';

		try {
			const result = await vscode.window.withProgress(
				{
					location: vscode.ProgressLocation.Notification,
					title: 'AutoCommit',
					cancellable: false,
				},
				async (progress) => {
					progress.report({ message: 'Detecting changes...' });
					return await runAutoCommit(workspacePath, extensionDir);
				}
			);

			if (result.status === 'success') {
				if (result.commit_message) {
					vscode.window.showInformationMessage(`AutoCommit ✅ ${result.commit_message}`);
				} else {
					vscode.window.showInformationMessage(`AutoCommit: ${result.message}`);
				}
			} else {
				vscode.window.showErrorMessage(`AutoCommit ❌ ${result.message}`);
			}
		} catch (err) {
			vscode.window.showErrorMessage(`AutoCommit ❌ ${err.message}`);
		} finally {
			statusBarItem.text = '$(git-commit) AutoCommit';
		}
	});

	context.subscriptions.push(disposable);
}

/**
 * Called when the extension is deactivated (e.g. VS Code closing).
 * Runs a synchronous auto-commit if the setting is enabled.
 */
function deactivate() {
	const config = vscode.workspace.getConfiguration('autocommit');
	const commitOnClose = config.get('commitOnClose', true);

	if (!commitOnClose) {
		return;
	}

	const workspacePath = getWorkspacePath();
	if (!workspacePath || !extensionDir) {
		return;
	}

	const pythonPath = config.get('pythonPath', 'python');
	const scriptPath = path.join(extensionDir, 'python', 'main.py');

	const env = Object.assign({}, process.env, {
		AUTOCOMMIT_API_KEY: config.get('apiKey', ''),
		AUTOCOMMIT_API_PROVIDER: config.get('apiProvider', 'gemini'),
		AUTOCOMMIT_MODEL: config.get('model', 'gemini-2.0-flash'),
	});

	try {
		execSync(`"${pythonPath}" "${scriptPath}" "${workspacePath}"`, {
			env,
			timeout: 15000,
			stdio: 'ignore',
		});
	} catch (e) {
		// Silently fail on close — nothing we can show the user at this point
		console.error('[AutoCommit] deactivate commit failed:', e.message);
	}
}

module.exports = {
	activate,
	deactivate
}
