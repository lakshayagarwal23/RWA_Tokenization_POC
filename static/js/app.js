// app.js — RWA Tokenization Frontend (Enhanced: Always Show Verification Score in Modal)

class RWAApp {
    constructor() {
        this.baseURL = window.location.origin;
        this.currentWallet = null;
        this.currentAssets = [];
        this.currentAsset = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadStats();
        this.loadSampleWallet();
    }

    setupEventListeners() {
        const assetForm = document.getElementById('asset-form');
        const refreshBtn = document.getElementById('refresh-assets');
        const verifyBtn = document.getElementById('verify-btn');
        const tokenizeBtn = document.getElementById('tokenize-btn');

        if (assetForm) {
            assetForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitAsset();
            });
        }
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadUserAssets());
        }
        if (verifyBtn) {
            verifyBtn.addEventListener('click', () => this.verifyAsset());
        }
        if (tokenizeBtn) {
            tokenizeBtn.addEventListener('click', () => this.tokenizeAsset());
        }
    }

    loadSampleWallet() {
        const sampleWallet = '0x742d35Cc6e34d8d7C15fE14c123456789abcdef0';
        const walletInput = document.getElementById('wallet-address');
        const walletDisplay = document.getElementById('wallet-display');
        if (walletInput) walletInput.value = sampleWallet;
        this.currentWallet = sampleWallet;
        if (walletDisplay) walletDisplay.textContent = `${sampleWallet.slice(0, 6)}...${sampleWallet.slice(-4)}`;
        this.loadUserAssets();
    }

    async submitAsset() {
        const submitBtn = document.getElementById('submit-btn');
        const spinner = document.getElementById('submit-spinner');

        try {
            this.setLoading(submitBtn, spinner, true);

            const walletAddress = document.getElementById('wallet-address').value;
            const assetDescription = document.getElementById('asset-description').value;
            const email = document.getElementById('email').value;

            const response = await fetch(`${this.baseURL}/api/intake`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    wallet_address: walletAddress,
                    user_input: assetDescription,
                    email: email
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert('success', '✅ Asset submitted!');
                this.showFollowUpQuestions(result.follow_up_questions || []);
                this.resetForm();
                await this.loadUserAssets();
                await this.loadStats();
            } else {
                this.showAlert('danger', `Error: ${result.error}`);
            }
        } catch (error) {
            console.error('Error submitting asset:', error);
            this.showAlert('danger', 'Failed to submit asset. Please try again.');
        } finally {
            this.setLoading(submitBtn, spinner, false);
        }
    }

    async loadUserAssets() {
        const walletAddress = document.getElementById('wallet-address').value;
        if (!walletAddress) return;

        try {
            const response = await fetch(`${this.baseURL}/api/assets/${walletAddress}`);
            const result = await response.json();
            this.currentAssets = result.assets || [];
            this.renderAssets(this.currentAssets);
        } catch (error) {
            console.error('Error loading assets:', error);
        }
    }

    async loadStats() {
        try {
            const response = await fetch(`${this.baseURL}/api/stats`);
            const stats = await response.json();
            document.getElementById('total-assets').textContent = stats.total_assets || 0;
            document.getElementById('verified-assets').textContent = stats.verified_assets || 0;
            document.getElementById('tokenized-assets').textContent = stats.tokenized_assets || 0;
            document.getElementById('total-users').textContent = stats.total_users || 0;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    renderAssets(assets) {
        const assetsList = document.getElementById('assets-list');
        if (!assetsList) return;
        if (assets.length === 0) {
            assetsList.innerHTML = `
                <div class="text-center text-muted">
                    <p>No assets found. Submit your first asset above!</p>
                </div>
            `;
            return;
        }

        assetsList.innerHTML = assets.map(asset => `
            <div class="card mb-2">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="card-title">${this.getAssetTypeIcon(asset.asset_type)} ${asset.asset_type.replace('_', ' ').toUpperCase()}</h6>
                            <p class="card-text small">${(asset.description || '').substring(0, 80)}${asset.description && asset.description.length > 80 ? '...' : ''}</p>
                            <div class="d-flex gap-2">
                                <span class="badge bg-secondary">${asset.estimated_value?.toLocaleString() || 'N/A'} INR</span>
                                ${asset.token_id ? '<span class="badge bg-success">Tokenized</span>' : ''}
                            </div>
                        </div>
                        <button class="btn btn-outline-primary btn-sm" onclick="app.showAssetDetails('${asset.id}')">View</button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async showAssetDetails(assetId) {
        try {
            const response = await fetch(`${this.baseURL}/api/asset/${assetId}`);
            const result = await response.json();
            const asset = result.asset;
            const transactions = result.transactions || [];
            this.currentAsset = asset;

            // Find the latest verification transaction
            const verificationTx = transactions.find(tx => tx.transaction_type === 'verification');
            let verificationResult = null;
            if (verificationTx && verificationTx.details) {
                try {
                    verificationResult = typeof verificationTx.details === 'string'
                        ? JSON.parse(verificationTx.details)
                        : verificationTx.details;
                } catch (e) {
                    verificationResult = null;
                }
            }

            // Render asset info and verification results in modal
            document.getElementById('asset-modal-body').innerHTML = `
                <div id="verification-results-section" class="mb-3">
                    ${verificationResult ? `
                        <div class="alert alert-info">
                            <strong>Verification Score:</strong> ${(verificationResult.overall_score * 100).toFixed(1)}%<br>
                            <strong>Status:</strong> <span class="badge bg-${this.getStatusColor(verificationResult.status)}">${verificationResult.status}</span>
                            <hr>
                            <strong>Breakdown:</strong>
                            <ul>
                                <li>Basic Info: ${verificationResult.breakdown.basic_info}</li>
                                <li>Value Assessment: ${verificationResult.breakdown.value_assessment}</li>
                                <li>Jurisdiction: ${verificationResult.breakdown.jurisdiction}</li>
                                <li>Asset Specific: ${verificationResult.breakdown.asset_specific}</li>
                            </ul>
                            ${verificationResult.recommendations && verificationResult.recommendations.length > 0 ? `
                                <strong>Recommendations:</strong>
                                <ul>${verificationResult.recommendations.map(rec => `<li>${rec}</li>`).join('')}</ul>
                            ` : ''}
                        </div>
                    ` : `
                        <div class="alert alert-warning">No verification results available for this asset.</div>
                    `}
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <h6>Asset Information</h6>
                        <table class="table table-sm">
                            <tr><td><strong>Type:</strong></td><td>${asset.asset_type.replace('_', ' ')}</td></tr>
                            <tr><td><strong>Value:</strong></td><td>${asset.estimated_value?.toLocaleString() || 'N/A'} INR</td></tr>
                            <tr><td><strong>Location:</strong></td><td>${asset.location}</td></tr>
                            <tr><td><strong>Status:</strong></td><td><span class="badge bg-${this.getStatusColor(asset.verification_status)}">${asset.verification_status}</span></td></tr>
                            <tr><td><strong>Created:</strong></td><td>${asset.created_at ? new Date(asset.created_at).toLocaleDateString() : ''}</td></tr>
                            ${asset.token_id ? `<tr><td><strong>Token ID:</strong></td><td><code>${asset.token_id}</code></td></tr>` : ''}
                        </table>
                        <h6>Description</h6>
                        <p class="small">${asset.description}</p>
                    </div>
                    <div class="col-md-6">
                        <h6>Transaction History</h6>
                        ${transactions.length > 0 ? `
                            <div class="list-group">
                                ${transactions.map(tx => `
                                    <div class="list-group-item">
                                        <div class="d-flex justify-content-between">
                                            <h6 class="mb-1">${tx.transaction_type}</h6>
                                            <small>${tx.created_at ? new Date(tx.created_at).toLocaleDateString() : ''}</small>
                                        </div>
                                        <p class="mb-1"><span class="badge bg-${this.getStatusColor(tx.status)}">${tx.status}</span></p>
                                        ${tx.transaction_hash ? `<small>Hash: <code>${tx.transaction_hash.slice(0, 16)}...</code></small>` : ''}
                                    </div>
                                `).join('')}
                            </div>
                        ` : '<p class="text-muted">No transactions yet</p>'}
                    </div>
                </div>
            `;

            document.getElementById('verify-btn').disabled = false;
            document.getElementById('tokenize-btn').classList.toggle('d-none', asset.verification_status !== 'verified');
            new bootstrap.Modal(document.getElementById('asset-modal')).show();
        } catch (error) {
            console.error('Error loading asset details:', error);
            this.showAlert('danger', 'Failed to load asset details');
        }
    }

    async verifyAsset() {
        if (!this.currentAsset) return;

        try {
            const response = await fetch(`${this.baseURL}/api/verify/${this.currentAsset.id}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert('success', '✅ Asset verification completed!');
                await this.loadUserAssets();
                await this.loadStats();
                bootstrap.Modal.getInstance(document.getElementById('asset-modal')).hide();
                this.showVerificationResults(result.verification_result);
            } else {
                this.showAlert('danger', `Verification failed: ${result.error}`);
            }
        } catch (error) {
            console.error('Error verifying asset:', error);
            this.showAlert('danger', 'Failed to verify asset');
        }
    }

    async tokenizeAsset() {
        if (!this.currentAsset) return;

        try {
            const response = await fetch(`${this.baseURL}/api/tokenize/${this.currentAsset.id}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert('success', '🎉 Asset tokenized successfully!');
                await this.loadUserAssets();
                await this.loadStats();
                bootstrap.Modal.getInstance(document.getElementById('asset-modal')).hide();
                this.showTokenizationResults(result.tokenization_result);
            } else {
                this.showAlert('danger', `Tokenization failed: ${result.error}`);
            }
        } catch (error) {
            console.error('Error tokenizing asset:', error);
            this.showAlert('danger', 'Failed to tokenize asset');
        }
    }

    showVerificationResults(verificationResult) {
        const alertHtml = `
            <div class="alert alert-info alert-dismissible fade show" role="alert">
                <h6>🔍 Verification Results</h6>
                <p><strong>Overall Score:</strong> ${(verificationResult.overall_score * 100).toFixed(1)}%</p>
                <p><strong>Status:</strong> <span class="badge bg-${this.getStatusColor(verificationResult.status)}">${verificationResult.status}</span></p>
                ${verificationResult.recommendations && verificationResult.recommendations.length > 0 ? `
                    <p><strong>Recommendations:</strong></p>
                    <ul>${verificationResult.recommendations.map(rec => `<li>${rec}</li>`).join('')}</ul>
                ` : ''}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        document.getElementById('alerts').innerHTML = alertHtml;
    }

    showTokenizationResults(tokenizationResult) {
        const html = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                <h6>🎉 Tokenization Successful!</h6>
                <p><strong>Token ID:</strong> <code>${tokenizationResult.token_id}</code></p>
                <p><strong>Contract:</strong> <code>${tokenizationResult.contract_address}</code></p>
                <p><strong>Transaction:</strong> <code>${tokenizationResult.transaction_hash}</code></p>
                <p><strong>Network:</strong> ${tokenizationResult.network}</p>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        document.getElementById('alerts').innerHTML = html;
    }

    showFollowUpQuestions(questions) {
        if (!Array.isArray(questions) || questions.length === 0) return;
        const html = questions.map(q => `
            <div class="alert alert-info mb-2"><small><strong>💭 ${q}</strong></small></div>
        `).join('');
        document.getElementById('follow-up-questions').innerHTML = html;
        document.getElementById('follow-up-section').classList.remove('d-none');
        setTimeout(() => {
            document.getElementById('follow-up-section').classList.add('d-none');
        }, 10000);
    }

    showAlert(type, message) {
        const html = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        document.getElementById('alerts').innerHTML = html;
        setTimeout(() => {
            const alertEl = document.querySelector('.alert');
            if (alertEl) new bootstrap.Alert(alertEl).close();
        }, 7000);
    }

    resetForm() {
        const assetDesc = document.getElementById('asset-description');
        const emailInput = document.getElementById('email');
        if (assetDesc) assetDesc.value = '';
        if (emailInput) emailInput.value = '';
    }

    setLoading(button, spinner, isLoading) {
        if (!button || !spinner) return;
        button.disabled = isLoading;
        spinner.classList.toggle('d-none', !isLoading);
        if (button.id === 'submit-btn') {
            button.textContent = isLoading ? 'Processing...' : 'Submit Asset';
        }
    }

    getStatusColor(status) {
        const colors = {
            'pending': 'warning',
            'verified': 'success',
            'rejected': 'danger',
            'requires_review': 'info',
            'completed': 'success',
            'failed': 'danger'
        };
        return colors[status] || 'secondary';
    }

    getAssetTypeIcon(assetType) {
        const icons = {
            'real_estate': '🏠',
            'vehicle': '🚗',
            'artwork': '🎨',
            'equipment': '⚙️',
            'commodity': '📦',
            'unknown': '❓'
        };
        return icons[assetType] || '📄';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new RWAApp();
});
