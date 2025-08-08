// Shipping Interface JavaScript

// Chatbot functionality
function toggleChat() {
    // Toggle chatbot visibility or open chat window
    console.log('Chatbot toggled');
    // You can implement a chat modal or slide-out panel here
}

// Form validation
function validateShippingForm() {
    const dropoffLocation = document.getElementById('dropoff-location').value;
    const pickupLocation = document.getElementById('pickup-location').value;
    
    if (!dropoffLocation || !pickupLocation) {
        alert('Please select both drop-off and pick-up locations');
        return false;
    }
    
    return true;
}

// Add item functionality
function addItem() {
    const itemDetails = document.querySelector('.item-details');
    const newItemRow = document.createElement('div');
    newItemRow.className = 'row mt-3';
    newItemRow.innerHTML = `
        <div class="col-md-2">
            <div class="detail-field">
                <label>Item</label>
                <input type="text" class="form-control" placeholder="Item name">
            </div>
        </div>
        <div class="col-md-2">
            <div class="detail-field">
                <label>Package Type</label>
                <select class="form-control">
                    <option value="">Select</option>
                    <option value="box">Box</option>
                    <option value="envelope">Envelope</option>
                    <option value="tube">Tube</option>
                    <option value="pallet">Pallet</option>
                </select>
            </div>
        </div>
        <div class="col-md-2">
            <div class="detail-field">
                <label>Length</label>
                <input type="number" class="form-control" placeholder="inches">
            </div>
        </div>
        <div class="col-md-2">
            <div class="detail-field">
                <label>Height</label>
                <input type="number" class="form-control" placeholder="inches">
            </div>
        </div>
        <div class="col-md-2">
            <div class="detail-field">
                <label>Weight</label>
                <input type="number" class="form-control" placeholder="lbs">
            </div>
        </div>
        <div class="col-md-2">
            <div class="detail-field">
                <button class="btn btn-sm btn-outline-danger" onclick="removeItem(this)">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
    
    itemDetails.insertBefore(newItemRow, itemDetails.querySelector('.add-item'));
}

// Remove item functionality
function removeItem(button) {
    button.closest('.row').remove();
}

// Continue to quote functionality
function continueToQuote() {
    if (validateShippingForm()) {
        // Collect form data
        const formData = {
            dropoff: {
                location: document.getElementById('dropoff-location').value,
                specific: document.getElementById('dropoff-specific').value
            },
            pickup: {
                location: document.getElementById('pickup-location').value,
                specific: document.getElementById('pickup-specific').value
            },
            items: collectItems(),
            insurance: document.getElementById('insurance').value
        };
        
        // Send to backend for quote calculation
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
                // Store quote data and redirect to quote page
                localStorage.setItem('quoteData', JSON.stringify(data.quote));
                window.location.href = '/quote';
            } else {
                alert('Error calculating quote: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error calculating quote. Please try again.');
        });
    }
}

// Collect all items from the form
function collectItems() {
    const items = [];
    const itemRows = document.querySelectorAll('.item-details .row');
    
    itemRows.forEach(row => {
        const inputs = row.querySelectorAll('input, select');
        if (inputs.length >= 5) {
            const item = {
                name: inputs[0].value,
                packageType: inputs[1].value,
                length: inputs[2].value,
                height: inputs[3].value,
                weight: inputs[4].value
            };
            
            if (item.name && item.packageType && item.length && item.height && item.weight) {
                items.push(item);
            }
        }
    });
    
    return items;
}

// Initialize shipping interface
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners for form validation
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(control => {
        control.addEventListener('change', function() {
            validateField(this);
        });
    });
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

// Validate individual field
function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name || field.id;
    
    if (!value) {
        field.classList.add('is-invalid');
        return false;
    } else {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        return true;
    }
}

// Search functionality
function performSearch(query) {
    // Implement search functionality
    console.log('Searching for:', query);
    // You can implement search across shipping options, tracking numbers, etc.
}

// Navigation functionality
function navigateTo(page) {
    window.location.href = page;
}

// Export functions for global access
window.toggleChat = toggleChat;
window.addItem = addItem;
window.removeItem = removeItem;
window.continueToQuote = continueToQuote;
window.performSearch = performSearch;
window.navigateTo = navigateTo; 