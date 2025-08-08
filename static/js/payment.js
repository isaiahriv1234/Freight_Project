// Payment Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializePayment();
});

function initializePayment() {
    // Load payment data
    loadPaymentData();
    
    // Set up form validation
    setupFormValidation();
    
    // Set up input formatting
    setupInputFormatting();
    
    // Set up event listeners
    setupEventListeners();
}

function loadPaymentData() {
    // Load selected shipping option
    const selectedOption = localStorage.getItem('selectedShippingOption');
    if (selectedOption) {
        try {
            const option = JSON.parse(selectedOption);
            updateOrderSummary(option);
        } catch (error) {
            console.error('Error parsing shipping option:', error);
        }
    }
    
    // Load quote data for insurance cost
    const quoteData = localStorage.getItem('quoteData');
    if (quoteData) {
        try {
            const data = JSON.parse(quoteData);
            updateInsuranceCost(data.insurance);
        } catch (error) {
            console.error('Error parsing quote data:', error);
        }
    }
}

function updateOrderSummary(shippingOption) {
    const shippingCostElement = document.getElementById('shipping-cost');
    const totalCostElement = document.getElementById('total-cost');
    
    if (shippingCostElement && totalCostElement) {
        const shippingCost = parseFloat(shippingOption.price.replace('$', '').replace(',', ''));
        const insuranceCost = parseFloat(document.getElementById('insurance-cost').textContent.replace('$', ''));
        const totalCost = shippingCost + insuranceCost;
        
        shippingCostElement.textContent = `$${shippingCost.toFixed(2)}`;
        totalCostElement.textContent = `$${totalCost.toFixed(2)}`;
    }
}

function updateInsuranceCost(insuranceType) {
    const insuranceCostElement = document.getElementById('insurance-cost');
    if (insuranceCostElement) {
        const insuranceCosts = {
            'basic': 5,
            'standard': 15,
            'premium': 30,
            'custom': 20
        };
        
        const cost = insuranceCosts[insuranceType] || 5;
        insuranceCostElement.textContent = `$${cost.toFixed(2)}`;
        
        // Update total cost
        updateTotalCost();
    }
}

function updateTotalCost() {
    const shippingCost = parseFloat(document.getElementById('shipping-cost').textContent.replace('$', ''));
    const insuranceCost = parseFloat(document.getElementById('insurance-cost').textContent.replace('$', ''));
    const totalCost = shippingCost + insuranceCost;
    
    document.getElementById('total-cost').textContent = `$${totalCost.toFixed(2)}`;
}

function setupFormValidation() {
    const form = document.getElementById('payment-form');
    if (form) {
        const inputs = form.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', validateField);
            input.addEventListener('input', clearValidation);
        });
    }
}

function setupInputFormatting() {
    // Card number formatting
    const cardNumberInput = document.getElementById('card-number');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', formatCardNumber);
    }
    
    // Expiration date formatting
    const expirationInput = document.getElementById('expiration-date');
    if (expirationInput) {
        expirationInput.addEventListener('input', formatExpirationDate);
    }
    
    // Security code formatting
    const securityCodeInput = document.getElementById('security-code');
    if (securityCodeInput) {
        securityCodeInput.addEventListener('input', formatSecurityCode);
    }
}

function setupEventListeners() {
    // Payment method selection
    const paymentMethods = document.querySelectorAll('input[name="payment-method"]');
    paymentMethods.forEach(method => {
        method.addEventListener('change', handlePaymentMethodChange);
    });
    
    // Submit button
    const submitBtn = document.querySelector('.btn-primary');
    if (submitBtn) {
        submitBtn.addEventListener('click', submitPayment);
    }
}

function formatCardNumber(input) {
    let value = input.target.value.replace(/\D/g, '');
    value = value.replace(/(\d{4})(?=\d)/g, '$1 ');
    input.target.value = value;
}

function formatExpirationDate(input) {
    let value = input.target.value.replace(/\D/g, '');
    if (value.length >= 2) {
        value = value.substring(0, 2) + '/' + value.substring(2);
    }
    input.target.value = value;
}

function formatSecurityCode(input) {
    let value = input.target.value.replace(/\D/g, '');
    input.target.value = value;
}

function handlePaymentMethodChange(event) {
    const selectedMethod = event.target.value;
    const paymentForm = document.getElementById('payment-form');
    
    // Show/hide form fields based on payment method
    if (selectedMethod === 'credit-card') {
        paymentForm.style.display = 'block';
    } else {
        // For other payment methods, hide the form
        paymentForm.style.display = 'none';
    }
}

function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name || field.id;
    
    // Remove existing validation classes
    field.classList.remove('is-valid', 'is-invalid');
    
    if (!value) {
        field.classList.add('is-invalid');
        showFieldError(field, `${fieldName.replace(/-/g, ' ')} is required`);
        return false;
    }
    
    // Additional validation based on field type
    if (field.id === 'card-number') {
        if (!isValidCardNumber(value)) {
            field.classList.add('is-invalid');
            showFieldError(field, 'Please enter a valid card number');
            return false;
        }
    }
    
    if (field.id === 'expiration-date') {
        if (!isValidExpirationDate(value)) {
            field.classList.add('is-invalid');
            showFieldError(field, 'Please enter a valid expiration date (MM/YY)');
            return false;
        }
    }
    
    if (field.id === 'security-code') {
        if (!isValidSecurityCode(value)) {
            field.classList.add('is-invalid');
            showFieldError(field, 'Please enter a valid security code');
            return false;
        }
    }
    
    field.classList.add('is-valid');
    hideFieldError(field);
    return true;
}

function clearValidation(field) {
    field.classList.remove('is-valid', 'is-invalid');
    hideFieldError(field);
}

function showFieldError(field, message) {
    // Remove existing error message
    hideFieldError(field);
    
    // Create error message element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    // Insert after the field
    field.parentNode.appendChild(errorDiv);
}

function hideFieldError(field) {
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
}

function isValidCardNumber(cardNumber) {
    // Remove spaces and check if it's a valid card number
    const cleanNumber = cardNumber.replace(/\s/g, '');
    return cleanNumber.length >= 13 && cleanNumber.length <= 19;
}

function isValidExpirationDate(expirationDate) {
    const pattern = /^(0[1-9]|1[0-2])\/([0-9]{2})$/;
    if (!pattern.test(expirationDate)) return false;
    
    const [month, year] = expirationDate.split('/');
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear() % 100;
    const currentMonth = currentDate.getMonth() + 1;
    
    const expYear = parseInt(year);
    const expMonth = parseInt(month);
    
    if (expYear < currentYear) return false;
    if (expYear === currentYear && expMonth < currentMonth) return false;
    
    return true;
}

function isValidSecurityCode(securityCode) {
    return securityCode.length >= 3 && securityCode.length <= 4;
}

function submitPayment() {
    if (validatePaymentForm()) {
        // Show loading state
        const submitBtn = document.querySelector('.btn-primary');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        submitBtn.disabled = true;
        
        // Collect payment data
        const paymentData = collectPaymentData();
        
        // Send to backend
        fetch('/api/process-payment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(paymentData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Redirect to success page
                window.location.href = '/payment-success';
            } else {
                throw new Error(data.message || 'Payment failed');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Payment failed: ' + error.message);
        })
        .finally(() => {
            // Restore button state
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        });
    }
}

function validatePaymentForm() {
    const form = document.getElementById('payment-form');
    const inputs = form.querySelectorAll('input, textarea');
    
    let isValid = true;
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    // Check if payment method is selected
    const selectedMethod = document.querySelector('input[name="payment-method"]:checked');
    if (!selectedMethod) {
        alert('Please select a payment method');
        isValid = false;
    }
    
    return isValid;
}

function collectPaymentData() {
    const selectedMethod = document.querySelector('input[name="payment-method"]:checked').value;
    const shippingOption = localStorage.getItem('selectedShippingOption');
    const quoteData = localStorage.getItem('quoteData');
    
    const paymentData = {
        payment_method: selectedMethod,
        shipping_option: shippingOption ? JSON.parse(shippingOption) : null,
        quote_data: quoteData ? JSON.parse(quoteData) : null,
        card_data: {}
    };
    
    // Only include card data if credit card is selected
    if (selectedMethod === 'credit-card') {
        paymentData.card_data = {
            card_number: document.getElementById('card-number').value,
            expiration_date: document.getElementById('expiration-date').value,
            security_code: document.getElementById('security-code').value,
            cardholder_name: document.getElementById('cardholder-name').value,
            billing_address: document.getElementById('billing-address').value
        };
    }
    
    return paymentData;
}

// Export functions for global access
window.submitPayment = submitPayment; 