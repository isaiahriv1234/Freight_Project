// Shipping Form Specific JavaScript

// Form state management
let formState = {
    items: [],
    currentStep: 1,
    totalSteps: 4
};

// Initialize form
document.addEventListener('DOMContentLoaded', function() {
    initializeForm();
    setupEventListeners();
});

function initializeForm() {
    // Set up form validation
    setupFormValidation();
    
    // Initialize location dropdowns
    setupLocationDropdowns();
    
    // Set up insurance options
    setupInsuranceOptions();
}

function setupEventListeners() {
    // Location change events
    const locationSelects = document.querySelectorAll('#dropoff-location, #pickup-location');
    locationSelects.forEach(select => {
        select.addEventListener('change', function() {
            updateSpecificLocations(this);
        });
    });
    
    // Form submission
    const continueBtn = document.querySelector('.btn-primary');
    if (continueBtn) {
        continueBtn.addEventListener('click', handleContinue);
    }
    
    // Add item button
    const addItemBtn = document.querySelector('.btn-outline-primary');
    if (addItemBtn) {
        addItemBtn.addEventListener('click', addItem);
    }
}

function setupFormValidation() {
    const requiredFields = document.querySelectorAll('select[required], input[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', validateField);
        field.addEventListener('input', clearValidation);
    });
}

function setupLocationDropdowns() {
    const locations = {
        'cal-poly-campus': [
            'Building 1 - Engineering',
            'Building 2 - Science', 
            'Building 3 - Business',
            'Building 4 - Agriculture'
        ],
        'san-luis-obispo': [
            'Downtown SLO',
            'Cal Poly Campus',
            'Airport Area'
        ],
        'pismo-beach': [
            'Pismo Beach Pier',
            'Downtown Pismo',
            'Shell Beach'
        ],
        'arroyo-grande': [
            'Downtown Arroyo Grande',
            'Village Center',
            'Industrial Area'
        ]
    };
    
    // Store locations for later use
    window.locationOptions = locations;
}

function updateSpecificLocations(mainSelect) {
    const specificSelect = mainSelect.id === 'dropoff-location' 
        ? document.getElementById('dropoff-specific')
        : document.getElementById('pickup-specific');
    
    const selectedLocation = mainSelect.value;
    const options = window.locationOptions[selectedLocation] || [];
    
    // Clear existing options
    specificSelect.innerHTML = '<option value="">Select Location (nearest to farthest)</option>';
    
    // Add new options
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option.toLowerCase().replace(/\s+/g, '-');
        optionElement.textContent = option;
        specificSelect.appendChild(optionElement);
    });
}

function setupInsuranceOptions() {
    const insuranceSelect = document.getElementById('insurance');
    if (insuranceSelect) {
        insuranceSelect.addEventListener('change', function() {
            if (this.value === 'custom') {
                showCustomInsuranceInput();
            } else {
                hideCustomInsuranceInput();
            }
        });
    }
}

function showCustomInsuranceInput() {
    const insuranceSection = document.querySelector('.form-section:last-of-type');
    const existingCustomInput = document.querySelector('.custom-insurance-input');
    
    if (!existingCustomInput) {
        const customInput = document.createElement('div');
        customInput.className = 'form-group custom-insurance-input';
        customInput.innerHTML = `
            <label for="custom-insurance-amount">Custom Insurance Amount ($)</label>
            <input type="number" class="form-control" id="custom-insurance-amount" 
                   placeholder="Enter amount" min="1" max="10000">
        `;
        insuranceSection.appendChild(customInput);
    }
}

function hideCustomInsuranceInput() {
    const customInput = document.querySelector('.custom-insurance-input');
    if (customInput) {
        customInput.remove();
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
    } else {
        field.classList.add('is-valid');
        hideFieldError(field);
        return true;
    }
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

function handleContinue() {
    if (validateForm()) {
        // Show loading state
        const continueBtn = document.querySelector('.btn-primary');
        const originalText = continueBtn.innerHTML;
        continueBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Calculating...';
        continueBtn.disabled = true;
        
        // Collect form data
        const formData = collectFormData();
        
        // Send to backend
        fetch('/api/calculate-quote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Store quote data
                localStorage.setItem('quoteData', JSON.stringify(data.quote));
                // Redirect to quote page
                window.location.href = '/quote';
            } else {
                throw new Error(data.message || 'Error calculating quote');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error calculating quote: ' + error.message);
        })
        .finally(() => {
            // Restore button state
            continueBtn.innerHTML = originalText;
            continueBtn.disabled = false;
        });
    }
}

function validateForm() {
    const requiredFields = [
        'dropoff-location',
        'dropoff-specific', 
        'pickup-location',
        'pickup-specific'
    ];
    
    let isValid = true;
    
    requiredFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field && !validateField(field)) {
            isValid = false;
        }
    });
    
    // Validate at least one item
    const items = collectItems();
    if (items.length === 0) {
        alert('Please add at least one item to ship');
        isValid = false;
    }
    
    return isValid;
}

function collectFormData() {
    return {
        dropoff: {
            location: document.getElementById('dropoff-location').value,
            specific: document.getElementById('dropoff-specific').value
        },
        pickup: {
            location: document.getElementById('pickup-location').value,
            specific: document.getElementById('pickup-specific').value
        },
        items: collectItems(),
        insurance: document.getElementById('insurance').value,
        customInsuranceAmount: document.getElementById('custom-insurance-amount')?.value
    };
}

function collectItems() {
    const items = [];
    const itemRows = document.querySelectorAll('.item-details .row');
    
    itemRows.forEach(row => {
        const inputs = row.querySelectorAll('input, select');
        if (inputs.length >= 5) {
            const item = {
                name: inputs[0].value,
                packageType: inputs[1].value,
                length: parseFloat(inputs[2].value) || 0,
                height: parseFloat(inputs[3].value) || 0,
                weight: parseFloat(inputs[4].value) || 0
            };
            
            // Only add if item has required fields
            if (item.name && item.packageType && item.length > 0 && item.height > 0 && item.weight > 0) {
                items.push(item);
            }
        }
    });
    
    return items;
}

// Export functions for global access
window.validateForm = validateForm;
window.collectFormData = collectFormData;
window.collectItems = collectItems; 