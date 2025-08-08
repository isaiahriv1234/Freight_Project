// Quote Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeQuote();
});

function initializeQuote() {
    // Load quote data from localStorage if available
    loadQuoteData();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize shipping options
    setupShippingOptions();
}

function loadQuoteData() {
    const quoteData = localStorage.getItem('quoteData');
    if (quoteData) {
        try {
            const data = JSON.parse(quoteData);
            displayQuoteData(data);
        } catch (error) {
            console.error('Error parsing quote data:', error);
        }
    }
}

function displayQuoteData(data) {
    // Update delivery estimate
    updateDeliveryEstimate(data);
    
    // Update shipping options
    updateShippingOptions(data);
}

function updateDeliveryEstimate(data) {
    const dateElement = document.querySelector('.estimate-details .date');
    const timeElement = document.querySelector('.estimate-details .time');
    
    if (dateElement && timeElement) {
        // Calculate estimated delivery date
        const deliveryDate = calculateDeliveryDate();
        dateElement.textContent = deliveryDate;
        timeElement.textContent = 'Latest by the end of the day';
    }
}

function calculateDeliveryDate() {
    const today = new Date();
    const deliveryDate = new Date(today);
    deliveryDate.setDate(today.getDate() + 3); // 3 days from now
    
    return deliveryDate.toLocaleDateString('en-US', {
        weekday: 'long',
        month: 'long',
        day: 'numeric'
    });
}

function updateShippingOptions(data) {
    const optionsContainer = document.querySelector('.options-container');
    if (!optionsContainer) return;
    
    // Clear existing options
    optionsContainer.innerHTML = '';
    
    // Get carrier options from data
    const carriers = data.carrier_options || ['FedEx', 'UPS', 'USPS'];
    const deliveryEstimates = data.delivery_estimates || {
        'standard': '3-5 business days',
        'express': '1-2 business days',
        'overnight': 'Next business day'
    };
    
    // Create shipping options
    const options = [
        { carrier: 'FedEx', time: '3 - 4 Days', price: '$150.00', type: 'standard' },
        { carrier: 'FedEx', time: '1 - 2 Days', price: '$180.00', type: 'express' },
        { carrier: 'FedEx', time: 'Overnight', price: '$250.00', type: 'overnight' }
    ];
    
    options.forEach((option, index) => {
        const optionCard = createOptionCard(option, index === 0);
        optionsContainer.appendChild(optionCard);
    });
}

function createOptionCard(option, isSelected = false) {
    const card = document.createElement('div');
    card.className = `option-card ${isSelected ? 'selected' : ''}`;
    card.innerHTML = `
        <div class="option-header">
            <span class="carrier">${option.carrier}</span>
            <span class="delivery-time">${option.time}</span>
            <span class="price">${option.price}</span>
        </div>
    `;
    
    // Add click event
    card.addEventListener('click', () => selectOption(card, option));
    
    return card;
}

function selectOption(selectedCard, option) {
    // Remove selection from all cards
    document.querySelectorAll('.option-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Add selection to clicked card
    selectedCard.classList.add('selected');
    
    // Store selected option
    localStorage.setItem('selectedShippingOption', JSON.stringify(option));
}

function setupEventListeners() {
    // Action buttons
    setupActionButtons();
    
    // Continue button
    const continueBtn = document.querySelector('.btn-primary');
    if (continueBtn) {
        continueBtn.addEventListener('click', continueToPayment);
    }
}

function setupActionButtons() {
    // Email Quote button
    const emailBtn = document.querySelector('.action-btn:nth-child(1)');
    if (emailBtn) {
        emailBtn.addEventListener('click', emailQuote);
    }
    
    // Copy Link button
    const copyBtn = document.querySelector('.action-btn:nth-child(2)');
    if (copyBtn) {
        copyBtn.addEventListener('click', copyQuoteLink);
    }
    
    // Print Quote button
    const printBtn = document.querySelector('.action-btn:nth-child(3)');
    if (printBtn) {
        printBtn.addEventListener('click', printQuote);
    }
}

function setupShippingOptions() {
    // Add click events to existing option cards
    document.querySelectorAll('.option-card').forEach((card, index) => {
        card.addEventListener('click', () => {
            selectOption(card, {
                carrier: 'FedEx',
                time: card.querySelector('.delivery-time').textContent,
                price: card.querySelector('.price').textContent
            });
        });
    });
}

function emailQuote() {
    const quoteData = localStorage.getItem('quoteData');
    if (quoteData) {
        const data = JSON.parse(quoteData);
        const emailBody = generateQuoteEmail(data);
        
        // Open email client
        window.open(`mailto:?subject=Shipping Quote&body=${encodeURIComponent(emailBody)}`);
    } else {
        alert('No quote data available');
    }
}

function copyQuoteLink() {
    const currentUrl = window.location.href;
    navigator.clipboard.writeText(currentUrl).then(() => {
        showNotification('Quote link copied to clipboard!');
    }).catch(() => {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = currentUrl;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Quote link copied to clipboard!');
    });
}

function printQuote() {
    const quoteData = localStorage.getItem('quoteData');
    if (quoteData) {
        const data = JSON.parse(quoteData);
        const printContent = generatePrintContent(data);
        
        const printWindow = window.open('', '_blank');
        printWindow.document.write(printContent);
        printWindow.document.close();
        printWindow.print();
    } else {
        alert('No quote data available');
    }
}

function continueToPayment() {
    const selectedOption = localStorage.getItem('selectedShippingOption');
    if (!selectedOption) {
        alert('Please select a shipping option');
        return;
    }
    
    // Store selected option for payment page
    localStorage.setItem('selectedShippingOption', selectedOption);
    
    // Redirect to payment page
    window.location.href = '/payment';
}

function generateQuoteEmail(data) {
    return `
Shipping Quote from Cal Poly Freight Shipping

Shipment Details:
- Drop-off: ${data.dropoff_location}
- Pick-up: ${data.pickup_location}
- Total Weight: ${data.total_weight} lbs
- Total Items: ${data.total_items}
- Estimated Cost: $${data.estimated_cost}

Selected Shipping Option:
- Carrier: FedEx
- Delivery Time: 3-4 Days
- Cost: $150.00

Thank you for choosing Cal Poly Freight Shipping!
    `.trim();
}

function generatePrintContent(data) {
    return `
<!DOCTYPE html>
<html>
<head>
    <title>Shipping Quote</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .section { margin-bottom: 20px; }
        .section h3 { color: #1a4d2e; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Cal Poly Freight Shipping</h1>
        <h2>Shipping Quote</h2>
    </div>
    
    <div class="section">
        <h3>Shipment Details</h3>
        <table>
            <tr><td>Drop-off Location:</td><td>${data.dropoff_location}</td></tr>
            <tr><td>Pick-up Location:</td><td>${data.pickup_location}</td></tr>
            <tr><td>Total Weight:</td><td>${data.total_weight} lbs</td></tr>
            <tr><td>Total Items:</td><td>${data.total_items}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h3>Shipping Options</h3>
        <table>
            <tr><th>Carrier</th><th>Delivery Time</th><th>Cost</th></tr>
            <tr><td>FedEx</td><td>3-4 Days</td><td>$150.00</td></tr>
            <tr><td>FedEx</td><td>1-2 Days</td><td>$180.00</td></tr>
            <tr><td>FedEx</td><td>Overnight</td><td>$250.00</td></tr>
        </table>
    </div>
</body>
</html>
    `;
}

function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: var(--dark-green);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Export functions for global access
window.continueToPayment = continueToPayment;
window.emailQuote = emailQuote;
window.copyQuoteLink = copyQuoteLink;
window.printQuote = printQuote; 