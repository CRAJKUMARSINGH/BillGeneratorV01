/**
 * Bill Entry JavaScript - Infrastructure Billing System
 * Handles form interactions, real-time calculations, and validation
 */

class BillEntryManager {
    constructor() {
        this.totalAmount = 0;
        this.items = [];
        this.isDraft = false;
        this.autoSaveInterval = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadDraft();
        this.calculateInitialTotal();
        this.startAutoSave();
        
        console.log('🧮 Bill Entry Manager initialized');
    }
    
    bindEvents() {
        // Quantity input changes
        document.querySelectorAll('.qty-input:not(.locked-field)').forEach(input => {
            input.addEventListener('input', (e) => this.handleQuantityChange(e));
            input.addEventListener('blur', (e) => this.validateInput(e));
            input.addEventListener('focus', (e) => this.highlightRow(e.target, true));
        });
        
        // Form submission
        const form = document.getElementById('bill-entry-form');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
        
        // Save draft button
        const saveDraftBtn = document.querySelector('.btn-save');
        if (saveDraftBtn) {
            saveDraftBtn.addEventListener('click', () => this.saveDraft());
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
        
        // Page unload warning
        window.addEventListener('beforeunload', (e) => this.handlePageUnload(e));
        
        // Auto-complete functionality
        this.setupAutoComplete();
    }
    
    handleQuantityChange(event) {
        const input = event.target;
        const index = input.dataset.index;
        const rate = parseFloat(input.dataset.rate) || 0;
        const quantity = parseFloat(input.value) || 0;
        
        // Validate quantity
        if (quantity < 0) {
            input.value = 0;
            this.showToast('Quantity cannot be negative', 'warning');
            return;
        }
        
        // Calculate amount
        const amount = quantity * rate;
        
        // Update amount display
        const amountSpan = document.getElementById(`amount_${index}`);
        if (amountSpan) {
            amountSpan.textContent = amount.toFixed(2);
            
            // Add visual feedback for changes
            amountSpan.style.backgroundColor = '#fff3cd';
            setTimeout(() => {
                amountSpan.style.backgroundColor = '';
            }, 1000);
        }
        
        // Update total
        this.calculateTotal();
        
        // Mark as modified
        this.markAsModified();
        
        // Highlight the row temporarily
        this.highlightRow(input, true);
        setTimeout(() => this.highlightRow(input, false), 2000);
    }
    
    calculateAmount(input) {
        // Legacy support for existing templates
        this.handleQuantityChange({ target: input });
    }
    
    calculateTotal() {
        let total = 0;
        const amountSpans = document.querySelectorAll('.amount-display');
        
        amountSpans.forEach(span => {
            const amount = parseFloat(span.textContent) || 0;
            total += amount;
        });
        
        this.totalAmount = total;
        
        // Update total display
        const totalSpan = document.getElementById('total-amount');
        if (totalSpan) {
            totalSpan.textContent = total.toFixed(2);
            
            // Add animation for total changes
            totalSpan.style.transform = 'scale(1.1)';
            totalSpan.style.transition = 'transform 0.3s ease';
            setTimeout(() => {
                totalSpan.style.transform = 'scale(1)';
            }, 300);
        }
        
        // Update summary info
        this.updateSummaryInfo();
    }
    
    calculateInitialTotal() {
        // Calculate total when page loads
        const inputs = document.querySelectorAll('.qty-input:not(.locked-field)');
        inputs.forEach(input => {
            if (input.value) {
                this.handleQuantityChange({ target: input });
            }
        });
        this.calculateTotal();
    }
    
    validateInput(event) {
        const input = event.target;
        const value = parseFloat(input.value);
        
        // Check for valid number
        if (isNaN(value) && input.value !== '') {
            input.value = '';
            this.showToast('Please enter a valid number', 'error');
            return false;
        }
        
        // Check for reasonable values (max 999999)
        if (value > 999999) {
            input.value = 999999;
            this.showToast('Quantity seems very high. Please verify.', 'warning');
        }
        
        return true;
    }
    
    highlightRow(input, highlight) {
        const row = input.closest('tr');
        if (row) {
            if (highlight) {
                row.style.backgroundColor = '#f0f8ff';
                row.style.border = '2px solid #667eea';
            } else {
                row.style.backgroundColor = '';
                row.style.border = '';
            }
        }
    }
    
    handleFormSubmit(event) {
        // Validate all inputs before submission
        const inputs = document.querySelectorAll('.qty-input:not(.locked-field)');
        let hasErrors = false;
        
        inputs.forEach(input => {
            if (!this.validateInput({ target: input })) {
                hasErrors = true;
            }
        });
        
        if (hasErrors) {
            event.preventDefault();
            this.showToast('Please fix validation errors before submitting', 'error');
            return;
        }
        
        // Show loading state
        const submitBtn = document.querySelector('.btn-generate');
        if (submitBtn) {
            const originalText = submitBtn.textContent;
            submitBtn.textContent = '🔄 Generating Documents...';
            submitBtn.disabled = true;
            
            // Add spinner
            const spinner = document.createElement('span');
            spinner.className = 'spinner';
            submitBtn.appendChild(spinner);
        }
        
        // Clear auto-save
        this.clearAutoSave();
        
        // Show progress message
        this.showProgressMessage();
    }
    
    showProgressMessage() {
        const progressDiv = document.createElement('div');
        progressDiv.className = 'progress-message';
        progressDiv.innerHTML = `
            <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                        background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                        text-align: center; z-index: 9999;">
                <div class="spinner" style="margin-bottom: 15px;"></div>
                <h3>📄 Generating Your Documents</h3>
                <p>Please wait while we process your bill and generate all documents...</p>
                <div class="progress-steps">
                    <div>✅ Processing quantities</div>
                    <div>🔄 Generating documents</div>
                    <div>⏳ Creating PDFs</div>
                    <div>📦 Packaging files</div>
                </div>
            </div>
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                        background: rgba(0,0,0,0.5); z-index: 9998;"></div>
        `;
        
        document.body.appendChild(progressDiv);
        
        // Animate progress steps
        const steps = progressDiv.querySelectorAll('.progress-steps div');
        steps.forEach((step, index) => {
            setTimeout(() => {
                step.style.color = '#28a745';
                step.innerHTML = step.innerHTML.replace('🔄', '✅').replace('⏳', '✅');
            }, (index + 1) * 1500);
        });
    }
    
    saveDraft() {
        const draftData = this.getDraftData();
        localStorage.setItem('billEntryDraft', JSON.stringify({
            data: draftData,
            timestamp: new Date().toISOString(),
            projectName: this.getProjectName()
        }));
        
        this.isDraft = false;
        this.showToast('Draft saved successfully! 💾', 'success');
    }
    
    loadDraft() {
        const draft = localStorage.getItem('billEntryDraft');
        if (draft) {
            try {
                const draftData = JSON.parse(draft);
                const timeDiff = new Date() - new Date(draftData.timestamp);
                const hoursSince = timeDiff / (1000 * 60 * 60);
                
                // Only load draft if it's less than 24 hours old
                if (hoursSince < 24) {
                    this.restoreDraft(draftData.data);
                    this.showToast(`Draft from ${new Date(draftData.timestamp).toLocaleString()} restored`, 'info');
                } else {
                    localStorage.removeItem('billEntryDraft');
                }
            } catch (e) {
                console.error('Error loading draft:', e);
                localStorage.removeItem('billEntryDraft');
            }
        }
    }
    
    getDraftData() {
        const data = {};
        const inputs = document.querySelectorAll('.qty-input:not(.locked-field)');
        
        inputs.forEach(input => {
            if (input.value) {
                data[input.name] = input.value;
            }
        });
        
        return data;
    }
    
    restoreDraft(draftData) {
        Object.keys(draftData).forEach(key => {
            const input = document.querySelector(`[name="${key}"]`);
            if (input) {
                input.value = draftData[key];
                this.handleQuantityChange({ target: input });
            }
        });
    }
    
    getProjectName() {
        const projectNameElement = document.querySelector('[data-project-name]');
        return projectNameElement ? projectNameElement.textContent : 'Unknown Project';
    }
    
    markAsModified() {
        this.isDraft = true;
    }
    
    startAutoSave() {
        this.autoSaveInterval = setInterval(() => {
            if (this.isDraft) {
                this.saveDraft();
                console.log('🔄 Auto-saved draft');
            }
        }, 60000); // Auto-save every minute
    }
    
    clearAutoSave() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
            this.autoSaveInterval = null;
        }
    }
    
    handleKeyboardShortcuts(event) {
        // Ctrl+S to save draft
        if (event.ctrlKey && event.key === 's') {
            event.preventDefault();
            this.saveDraft();
        }
        
        // Ctrl+Enter to submit form
        if (event.ctrlKey && event.key === 'Enter') {
            event.preventDefault();
            const form = document.getElementById('bill-entry-form');
            if (form) {
                form.submit();
            }
        }
        
        // Enter to move to next input
        if (event.key === 'Enter' && event.target.classList.contains('qty-input')) {
            event.preventDefault();
            const inputs = Array.from(document.querySelectorAll('.qty-input:not(.locked-field)'));
            const currentIndex = inputs.indexOf(event.target);
            const nextInput = inputs[currentIndex + 1];
            
            if (nextInput) {
                nextInput.focus();
                nextInput.select();
            }
        }
    }
    
    handlePageUnload(event) {
        if (this.isDraft) {
            const message = 'You have unsaved changes. Are you sure you want to leave?';
            event.returnValue = message;
            return message;
        }
    }
    
    setupAutoComplete() {
        // Common quantity values for quick entry
        const commonValues = ['0', '1', '10', '50', '100', '500', '1000'];
        
        document.querySelectorAll('.qty-input:not(.locked-field)').forEach(input => {
            input.addEventListener('focus', function() {
                // Could implement autocomplete dropdown here
            });
        });
    }
    
    updateSummaryInfo() {
        // Update any summary information
        const totalItems = document.querySelectorAll('.qty-input:not(.locked-field)').length;
        const filledItems = Array.from(document.querySelectorAll('.qty-input:not(.locked-field)')).filter(input => parseFloat(input.value) > 0).length;
        
        // Update completion percentage if element exists
        const completionElement = document.getElementById('completion-percentage');
        if (completionElement) {
            const percentage = totalItems > 0 ? Math.round((filledItems / totalItems) * 100) : 0;
            completionElement.textContent = `${percentage}% Complete (${filledItems}/${totalItems} items)`;
        }
    }
    
    showToast(message, type = 'info') {
        // Remove existing toast
        const existingToast = document.querySelector('.toast');
        if (existingToast) {
            existingToast.remove();
        }
        
        // Create toast
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div style="position: fixed; top: 20px; right: 20px; z-index: 9999;
                        background: ${this.getToastColor(type)}; color: white; 
                        padding: 15px 20px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                        max-width: 300px; animation: slideInRight 0.3s ease;">
                ${message}
                <button onclick="this.parentElement.remove()" style="background: none; border: none; color: white; float: right; font-size: 18px; cursor: pointer;">&times;</button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast && toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }
    
    getToastColor(type) {
        const colors = {
            'success': '#28a745',
            'error': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8'
        };
        return colors[type] || colors.info;
    }
}

// Utility functions for backward compatibility
function calculateAmount(input) {
    if (window.billEntryManager) {
        window.billEntryManager.calculateAmount(input);
    }
}

function calculateTotal() {
    if (window.billEntryManager) {
        window.billEntryManager.calculateTotal();
    }
}

function saveDraft() {
    if (window.billEntryManager) {
        window.billEntryManager.saveDraft();
    } else {
        alert('Draft saved successfully! ✅\n\nYou can continue filling quantities or come back later.');
    }
}

// Add CSS for animations
const animationCSS = `
    <style>
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .progress-steps div {
            margin: 5px 0;
            color: #666;
            transition: color 0.3s ease;
        }
        
        .qty-input.highlight {
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.5) !important;
            border-color: #667eea !important;
        }
        
        .completion-info {
            background: #e8f5e9;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            text-align: center;
            color: #28a745;
            font-weight: bold;
        }
    </style>
`;

// Inject animation CSS
document.head.insertAdjacentHTML('beforeend', animationCSS);

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.billEntryManager = new BillEntryManager();
    
    // Add completion info element if it doesn't exist
    const totalSection = document.querySelector('.total-section');
    if (totalSection && !document.getElementById('completion-percentage')) {
        const completionDiv = document.createElement('div');
        completionDiv.className = 'completion-info';
        completionDiv.innerHTML = '<div id="completion-percentage">Calculating completion...</div>';
        totalSection.insertBefore(completionDiv, totalSection.firstChild);
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { BillEntryManager };
}
