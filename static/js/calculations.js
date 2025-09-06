/**
 * Calculations JavaScript - Infrastructure Billing System
 * Real-time calculation utilities and mathematical functions
 */

class CalculationEngine {
    constructor() {
        this.precision = 2;
        this.currencySymbol = '₹';
        this.init();
    }
    
    init() {
        console.log('🧮 Calculation Engine initialized');
    }
    
    /**
     * Calculate amount from quantity and rate
     * @param {number} quantity - The quantity value
     * @param {number} rate - The rate per unit
     * @returns {number} Calculated amount
     */
    calculateAmount(quantity, rate) {
        const qty = parseFloat(quantity) || 0;
        const rt = parseFloat(rate) || 0;
        return this.roundToPrecision(qty * rt);
    }
    
    /**
     * Calculate percentage
     * @param {number} value - The value
     * @param {number} total - The total value
     * @returns {number} Percentage
     */
    calculatePercentage(value, total) {
        if (total === 0) return 0;
        return this.roundToPrecision((parseFloat(value) / parseFloat(total)) * 100);
    }
    
    /**
     * Calculate deviation between two values
     * @param {number} original - Original value (work order)
     * @param {number} actual - Actual value (bill quantity)
     * @returns {object} Deviation details
     */
    calculateDeviation(original, actual) {
        const orig = parseFloat(original) || 0;
        const act = parseFloat(actual) || 0;
        const deviation = act - orig;
        const percentage = orig !== 0 ? this.calculatePercentage(deviation, orig) : 0;
        
        return {
            deviation: this.roundToPrecision(deviation),
            percentage: this.roundToPrecision(percentage),
            type: deviation > 0 ? 'excess' : (deviation < 0 ? 'less' : 'equal')
        };
    }
    
    /**
     * Round number to specified precision
     * @param {number} value - Value to round
     * @param {number} precision - Decimal places
     * @returns {number} Rounded value
     */
    roundToPrecision(value, precision = this.precision) {
        const factor = Math.pow(10, precision);
        return Math.round(parseFloat(value) * factor) / factor;
    }
    
    /**
     * Format currency
     * @param {number} value - Value to format
     * @returns {string} Formatted currency string
     */
    formatCurrency(value) {
        const formatted = this.roundToPrecision(value).toLocaleString('en-IN', {
            minimumFractionDigits: this.precision,
            maximumFractionDigits: this.precision
        });
        return `${this.currencySymbol} ${formatted}`;
    }
    
    /**
     * Format number with commas
     * @param {number} value - Value to format
     * @returns {string} Formatted number string
     */
    formatNumber(value) {
        return this.roundToPrecision(value).toLocaleString('en-IN', {
            minimumFractionDigits: this.precision,
            maximumFractionDigits: this.precision
        });
    }
    
    /**
     * Validate numerical input
     * @param {string|number} value - Value to validate
     * @returns {object} Validation result
     */
    validateNumber(value) {
        const num = parseFloat(value);
        const result = {
            isValid: true,
            value: num,
            error: null
        };
        
        if (isNaN(num)) {
            result.isValid = false;
            result.error = 'Not a valid number';
            result.value = 0;
        } else if (num < 0) {
            result.isValid = false;
            result.error = 'Cannot be negative';
            result.value = 0;
        } else if (num > 999999999) {
            result.isValid = false;
            result.error = 'Value too large';
            result.value = 999999999;
        }
        
        return result;
    }
    
    /**
     * Calculate totals for multiple items
     * @param {Array} items - Array of items with quantity and rate
     * @returns {object} Total calculations
     */
    calculateTotals(items) {
        let totalQuantity = 0;
        let totalAmount = 0;
        let itemCount = 0;
        
        items.forEach(item => {
            const qty = parseFloat(item.quantity) || 0;
            const rate = parseFloat(item.rate) || 0;
            const amount = this.calculateAmount(qty, rate);
            
            totalQuantity += qty;
            totalAmount += amount;
            
            if (qty > 0) {
                itemCount++;
            }
        });
        
        return {
            totalQuantity: this.roundToPrecision(totalQuantity),
            totalAmount: this.roundToPrecision(totalAmount),
            itemCount: itemCount,
            averageRate: itemCount > 0 ? this.roundToPrecision(totalAmount / totalQuantity) : 0
        };
    }
    
    /**
     * Calculate tax amounts
     * @param {number} baseAmount - Base amount
     * @param {number} taxPercentage - Tax percentage
     * @returns {object} Tax calculations
     */
    calculateTax(baseAmount, taxPercentage) {
        const base = parseFloat(baseAmount) || 0;
        const taxPercent = parseFloat(taxPercentage) || 0;
        const taxAmount = (base * taxPercent) / 100;
        const totalAmount = base + taxAmount;
        
        return {
            baseAmount: this.roundToPrecision(base),
            taxPercentage: taxPercent,
            taxAmount: this.roundToPrecision(taxAmount),
            totalAmount: this.roundToPrecision(totalAmount)
        };
    }
    
    /**
     * Convert numbers to words (for bill amounts)
     * @param {number} amount - Amount to convert
     * @returns {string} Amount in words
     */
    numberToWords(amount) {
        const ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine'];
        const teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'];
        const tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];
        const scales = ['', 'Thousand', 'Lakh', 'Crore'];
        
        if (amount === 0) return 'Zero Rupees Only';
        
        const num = Math.floor(amount);
        const decimal = Math.round((amount - num) * 100);
        
        let result = this.convertToWords(num, ones, teens, tens, scales);
        
        if (result) {
            result += ' Rupees';
            if (decimal > 0) {
                result += ' and ' + this.convertToWords(decimal, ones, teens, tens, []) + ' Paise';
            }
            result += ' Only';
        }
        
        return result || 'Zero Rupees Only';
    }
    
    convertToWords(num, ones, teens, tens, scales) {
        if (num === 0) return '';
        
        let result = '';
        let scaleIndex = 0;
        
        while (num > 0) {
            let chunk;
            if (scaleIndex === 0) {
                chunk = num % 1000;
                num = Math.floor(num / 1000);
            } else if (scaleIndex === 1) {
                chunk = num % 100;
                num = Math.floor(num / 100);
            } else {
                chunk = num % 100;
                num = Math.floor(num / 100);
            }
            
            if (chunk > 0) {
                let chunkWords = '';
                
                if (scaleIndex === 0) {
                    // Handle hundreds
                    if (chunk >= 100) {
                        chunkWords += ones[Math.floor(chunk / 100)] + ' Hundred ';
                        chunk %= 100;
                    }
                }
                
                // Handle tens and ones
                if (chunk >= 20) {
                    chunkWords += tens[Math.floor(chunk / 10)] + ' ';
                    chunk %= 10;
                }
                
                if (chunk >= 10) {
                    chunkWords += teens[chunk - 10] + ' ';
                } else if (chunk > 0) {
                    chunkWords += ones[chunk] + ' ';
                }
                
                if (scales[scaleIndex]) {
                    chunkWords += scales[scaleIndex] + ' ';
                }
                
                result = chunkWords + result;
            }
            
            scaleIndex++;
        }
        
        return result.trim();
    }
    
    /**
     * Generate calculation summary
     * @param {Array} workOrderItems - Work order items
     * @param {Array} billItems - Bill quantity items
     * @returns {object} Calculation summary
     */
    generateSummary(workOrderItems, billItems) {
        const woTotals = this.calculateTotals(workOrderItems);
        const billTotals = this.calculateTotals(billItems);
        const deviation = this.calculateDeviation(woTotals.totalAmount, billTotals.totalAmount);
        
        return {
            workOrder: woTotals,
            billQuantity: billTotals,
            deviation: deviation,
            summary: {
                totalItems: workOrderItems.length,
                filledItems: billItems.filter(item => parseFloat(item.quantity) > 0).length,
                completionPercentage: this.calculatePercentage(
                    billItems.filter(item => parseFloat(item.quantity) > 0).length,
                    workOrderItems.length
                )
            }
        };
    }
}

// Utility functions for global access
class BillCalculator {
    static instance = null;
    
    static getInstance() {
        if (!this.instance) {
            this.instance = new CalculationEngine();
        }
        return this.instance;
    }
    
    static calculate(quantity, rate) {
        return this.getInstance().calculateAmount(quantity, rate);
    }
    
    static format(value) {
        return this.getInstance().formatCurrency(value);
    }
    
    static validate(value) {
        return this.getInstance().validateNumber(value);
    }
    
    static toWords(amount) {
        return this.getInstance().numberToWords(amount);
    }
}

// Global functions for backward compatibility and template usage
function calculateItemAmount(quantity, rate) {
    return BillCalculator.calculate(quantity, rate);
}

function formatCurrency(value) {
    return BillCalculator.format(value);
}

function validateNumberInput(value) {
    return BillCalculator.validate(value);
}

function amountInWords(value) {
    return BillCalculator.toWords(value);
}

// Real-time calculation helpers
function updateItemCalculation(inputElement) {
    const calculator = BillCalculator.getInstance();
    const row = inputElement.closest('tr');
    
    if (!row) return;
    
    const quantityInput = row.querySelector('.qty-input');
    const rateValue = quantityInput?.dataset.rate || 0;
    const quantity = parseFloat(quantityInput?.value) || 0;
    
    const validation = calculator.validateNumber(quantity);
    if (!validation.isValid) {
        quantityInput.style.borderColor = '#dc3545';
        quantityInput.title = validation.error;
        return;
    } else {
        quantityInput.style.borderColor = '';
        quantityInput.title = '';
    }
    
    const amount = calculator.calculateAmount(quantity, rateValue);
    const amountSpan = row.querySelector('.amount-display');
    
    if (amountSpan) {
        amountSpan.textContent = calculator.formatNumber(amount);
    }
    
    // Trigger total recalculation
    updateTotalAmount();
}

function updateTotalAmount() {
    const calculator = BillCalculator.getInstance();
    const amountSpans = document.querySelectorAll('.amount-display');
    let total = 0;
    
    amountSpans.forEach(span => {
        const amount = parseFloat(span.textContent.replace(/,/g, '')) || 0;
        total += amount;
    });
    
    const totalSpan = document.getElementById('total-amount');
    if (totalSpan) {
        totalSpan.textContent = calculator.formatNumber(total);
    }
    
    // Update total in words if element exists
    const totalWordsSpan = document.getElementById('total-amount-words');
    if (totalWordsSpan) {
        totalWordsSpan.textContent = calculator.numberToWords(total);
    }
    
    return total;
}

// Auto-initialize when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize calculator
    window.billCalculator = BillCalculator.getInstance();
    
    // Bind calculation events to existing quantity inputs
    document.querySelectorAll('.qty-input:not(.locked-field)').forEach(input => {
        input.addEventListener('input', function() {
            updateItemCalculation(this);
        });
        
        input.addEventListener('change', function() {
            updateItemCalculation(this);
        });
    });
    
    // Initial calculation
    setTimeout(() => {
        document.querySelectorAll('.qty-input:not(.locked-field)').forEach(input => {
            if (input.value) {
                updateItemCalculation(input);
            }
        });
        updateTotalAmount();
    }, 100);
    
    console.log('🧮 Bill Calculator initialized and bound to inputs');
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        CalculationEngine, 
        BillCalculator,
        calculateItemAmount,
        formatCurrency,
        validateNumberInput,
        amountInWords
    };
}
