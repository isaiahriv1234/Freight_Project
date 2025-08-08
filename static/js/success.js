// Success Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeSuccess();
});

function initializeSuccess() {
    // Load order details from localStorage or URL parameters
    loadOrderDetails();
    
    // Set up event listeners
    setupEventListeners();
}

function loadOrderDetails() {
    // Try to get order details from localStorage first
    const orderData = localStorage.getItem('orderData');
    
    if (orderData) {
        try {
            const data = JSON.parse(orderData);
            displayOrderDetails(data);
        } catch (error) {
            console.error('Error parsing order data:', error);
        }
    } else {
        // Generate mock order details for demonstration
        const mockOrderData = {
            order_id: `ORDER-${Math.floor(Math.random() * 90000) + 10000}`,
            tracking_number: generateTrackingNumber(),
            delivery_date: '3-5 business days',
            shipping_cost: '$150.00',
            total_cost: '$155.00'
        };
        
        displayOrderDetails(mockOrderData);
        
        // Store for future use
        localStorage.setItem('orderData', JSON.stringify(mockOrderData));
    }
}

function displayOrderDetails(data) {
    const orderIdElement = document.getElementById('order-id');
    const trackingNumberElement = document.getElementById('tracking-number');
    const deliveryDateElement = document.getElementById('delivery-date');
    
    if (orderIdElement) {
        orderIdElement.textContent = data.order_id;
    }
    
    if (trackingNumberElement) {
        trackingNumberElement.textContent = data.tracking_number;
    }
    
    if (deliveryDateElement) {
        deliveryDateElement.textContent = data.delivery_date;
    }
}

function generateTrackingNumber() {
    return Math.floor(Math.random() * 9000000000000000) + 1000000000000000;
}

function setupEventListeners() {
    // Set up button event listeners
    const trackButton = document.querySelector('button[onclick="trackShipment()"]');
    const printButton = document.querySelector('button[onclick="printReceipt()"]');
    const emailButton = document.querySelector('button[onclick="emailConfirmation()"]');
    
    if (trackButton) {
        trackButton.addEventListener('click', trackShipment);
    }
    
    if (printButton) {
        printButton.addEventListener('click', printReceipt);
    }
    
    if (emailButton) {
        emailButton.addEventListener('click', emailConfirmation);
    }
}

function trackShipment() {
    const trackingNumber = document.getElementById('tracking-number').textContent;
    
    // Store tracking number for tracking page
    localStorage.setItem('lastTrackingNumber', trackingNumber);
    
    // Redirect to tracking page
    window.location.href = `/tracking?tracking=${trackingNumber}`;
}

function printReceipt() {
    const orderData = localStorage.getItem('orderData');
    let data;
    
    if (orderData) {
        data = JSON.parse(orderData);
    } else {
        data = {
            order_id: document.getElementById('order-id').textContent,
            tracking_number: document.getElementById('tracking-number').textContent,
            delivery_date: document.getElementById('delivery-date').textContent,
            shipping_cost: '$150.00',
            total_cost: '$155.00'
        };
    }
    
    const printContent = generateReceiptContent(data);
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
}

function emailConfirmation() {
    const orderData = localStorage.getItem('orderData');
    let data;
    
    if (orderData) {
        data = JSON.parse(orderData);
    } else {
        data = {
            order_id: document.getElementById('order-id').textContent,
            tracking_number: document.getElementById('tracking-number').textContent,
            delivery_date: document.getElementById('delivery-date').textContent,
            shipping_cost: '$150.00',
            total_cost: '$155.00'
        };
    }
    
    const emailBody = generateEmailContent(data);
    
    // Open email client
    window.open(`mailto:?subject=Shipping Confirmation - ${data.order_id}&body=${encodeURIComponent(emailBody)}`);
}

function generateReceiptContent(data) {
    return `
<!DOCTYPE html>
<html>
<head>
    <title>Shipping Receipt</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            line-height: 1.6;
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            border-bottom: 2px solid #1a4d2e;
            padding-bottom: 20px;
        }
        .header h1 { 
            color: #1a4d2e; 
            margin: 0;
        }
        .header h2 { 
            color: #666; 
            margin: 10px 0 0 0;
            font-size: 1.2rem;
        }
        .section { 
            margin-bottom: 25px; 
        }
        .section h3 { 
            color: #1a4d2e; 
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 10px;
        }
        th, td { 
            padding: 8px; 
            text-align: left; 
            border-bottom: 1px solid #ddd; 
        }
        th { 
            background-color: #f8f9fa; 
            font-weight: bold;
        }
        .total { 
            font-weight: bold; 
            font-size: 1.1rem;
            color: #1a4d2e;
        }
        .footer { 
            margin-top: 30px; 
            text-align: center; 
            color: #666;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Cal Poly Freight Shipping</h1>
        <h2>Shipping Receipt</h2>
    </div>
    
    <div class="section">
        <h3>Order Information</h3>
        <table>
            <tr><td>Order ID:</td><td>${data.order_id}</td></tr>
            <tr><td>Tracking Number:</td><td>${data.tracking_number}</td></tr>
            <tr><td>Order Date:</td><td>${new Date().toLocaleDateString()}</td></tr>
            <tr><td>Estimated Delivery:</td><td>${data.delivery_date}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h3>Shipping Details</h3>
        <table>
            <tr><td>Shipping Cost:</td><td>${data.shipping_cost}</td></tr>
            <tr><td>Insurance:</td><td>$5.00</td></tr>
            <tr class="total"><td>Total:</td><td>${data.total_cost}</td></tr>
        </table>
    </div>
    
    <div class="footer">
        <p>Thank you for choosing Cal Poly Freight Shipping!</p>
        <p>For tracking updates, visit our website or contact customer service.</p>
    </div>
</body>
</html>
    `;
}

function generateEmailContent(data) {
    return `
Dear Customer,

Thank you for your order with Cal Poly Freight Shipping!

Order Details:
- Order ID: ${data.order_id}
- Tracking Number: ${data.tracking_number}
- Estimated Delivery: ${data.delivery_date}
- Total Cost: ${data.total_cost}

You can track your shipment at any time using the tracking number above.

If you have any questions, please don't hesitate to contact our customer service team.

Thank you for choosing Cal Poly Freight Shipping!

Best regards,
The Cal Poly Freight Shipping Team
    `.trim();
}

// Export functions for global access
window.trackShipment = trackShipment;
window.printReceipt = printReceipt;
window.emailConfirmation = emailConfirmation; 