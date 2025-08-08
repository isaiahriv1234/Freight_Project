// Tracking Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeTracking();
});

function initializeTracking() {
    // Set up tracking number input
    const trackingInput = document.getElementById('tracking-number');
    if (trackingInput) {
        // Add event listener for Enter key
        trackingInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                trackShipment();
            }
        });
        
        // Add event listener for search icon click
        const searchIcon = trackingInput.parentNode.querySelector('i');
        if (searchIcon) {
            searchIcon.addEventListener('click', trackShipment);
        }
    }
}

function trackShipment() {
    const trackingNumber = document.getElementById('tracking-number').value.trim();
    
    if (!trackingNumber) {
        alert('Please enter a tracking number');
        return;
    }
    
    // Show loading state
    showLoadingState();
    
    // Call backend API
    fetch('/api/track-shipment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            tracking_number: trackingNumber
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayTrackingResults(data.tracking_info);
        } else {
            showError('Tracking information not found. Please check your tracking number.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Error retrieving tracking information. Please try again.');
    })
    .finally(() => {
        hideLoadingState();
    });
}

function showLoadingState() {
    const trackerInput = document.querySelector('.tracker-input input');
    const searchIcon = document.querySelector('.tracker-input i');
    
    if (trackerInput) {
        trackerInput.disabled = true;
        trackerInput.style.opacity = '0.6';
    }
    
    if (searchIcon) {
        searchIcon.className = 'fas fa-spinner fa-spin';
    }
}

function hideLoadingState() {
    const trackerInput = document.querySelector('.tracker-input input');
    const searchIcon = document.querySelector('.tracker-input i');
    
    if (trackerInput) {
        trackerInput.disabled = false;
        trackerInput.style.opacity = '1';
    }
    
    if (searchIcon) {
        searchIcon.className = 'fas fa-search';
    }
}

function displayTrackingResults(trackingInfo) {
    const resultsContainer = document.getElementById('tracking-results');
    const statusElement = document.getElementById('tracking-status');
    const timelineElement = document.getElementById('tracking-timeline');
    
    if (!resultsContainer || !statusElement || !timelineElement) {
        return;
    }
    
    // Update status
    statusElement.textContent = trackingInfo.status || 'In Transit';
    statusElement.className = `tracking-status ${getStatusClass(trackingInfo.status)}`;
    
    // Build timeline
    timelineElement.innerHTML = buildTimelineHTML(trackingInfo.events || []);
    
    // Show results
    resultsContainer.style.display = 'block';
    
    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
}

function getStatusClass(status) {
    const statusMap = {
        'Delivered': 'status-delivered',
        'Out for Delivery': 'status-out-for-delivery',
        'In Transit': 'status-in-transit',
        'Pending': 'status-pending',
        'Exception': 'status-exception'
    };
    
    return statusMap[status] || 'status-in-transit';
}

function buildTimelineHTML(events) {
    if (!events || events.length === 0) {
        return '<p class="text-muted">No tracking events available.</p>';
    }
    
    let timelineHTML = '';
    
    events.forEach((event, index) => {
        const isLatest = index === 0;
        const iconClass = getEventIconClass(event.type);
        const statusClass = isLatest ? 'current' : 'completed';
        
        timelineHTML += `
            <div class="timeline-item">
                <div class="timeline-icon ${statusClass}">
                    <i class="${iconClass}"></i>
                </div>
                <div class="timeline-content">
                    <div class="timeline-title">${event.title}</div>
                    <div class="timeline-location">${event.location}</div>
                    <div class="timeline-time">${formatDateTime(event.timestamp)}</div>
                </div>
            </div>
        `;
    });
    
    return timelineHTML;
}

function getEventIconClass(eventType) {
    const iconMap = {
        'pickup': 'fas fa-truck',
        'in_transit': 'fas fa-shipping-fast',
        'out_for_delivery': 'fas fa-truck-loading',
        'delivered': 'fas fa-check-circle',
        'exception': 'fas fa-exclamation-triangle',
        'pending': 'fas fa-clock'
    };
    
    return iconMap[eventType] || 'fas fa-info-circle';
}

function formatDateTime(timestamp) {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showError(message) {
    // Create error alert
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert after tracker card
    const trackerContainer = document.querySelector('.tracker-container');
    if (trackerContainer) {
        trackerContainer.parentNode.insertBefore(alertDiv, trackerContainer.nextSibling);
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Mock tracking data for demonstration
function getMockTrackingData(trackingNumber) {
    return {
        success: true,
        tracking_info: {
            tracking_number: trackingNumber,
            carrier: 'FedEx',
            status: 'In Transit',
            estimated_delivery: '2024-08-12',
            events: [
                {
                    type: 'in_transit',
                    title: 'Package in transit',
                    location: 'Memphis, TN',
                    timestamp: '2024-08-10T14:30:00Z'
                },
                {
                    type: 'pickup',
                    title: 'Package picked up',
                    location: 'San Luis Obispo, CA',
                    timestamp: '2024-08-09T10:15:00Z'
                },
                {
                    type: 'pending',
                    title: 'Shipment created',
                    location: 'Cal Poly Campus',
                    timestamp: '2024-08-09T09:00:00Z'
                }
            ]
        }
    };
}

// Export functions for global access
window.trackShipment = trackShipment;
window.getMockTrackingData = getMockTrackingData; 