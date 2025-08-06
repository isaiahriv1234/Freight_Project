// Dashboard JavaScript for data loading and chart rendering

// Chart instances
let monthlyTrendsChart, categoryChart, suppliersChart;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
});

// Load all dashboard data
async function loadDashboardData() {
    try {
        // Load spend summary
        const summaryResponse = await fetch('/api/spend-summary');
        const summary = await summaryResponse.json();
        updateMetricCards(summary);

        // Load monthly trends
        const trendsResponse = await fetch('/api/monthly-trends');
        const trends = await trendsResponse.json();
        createMonthlyTrendsChart(trends);

        // Load top suppliers
        const suppliersResponse = await fetch('/api/top-suppliers');
        const suppliers = await suppliersResponse.json();
        createSuppliersChart(suppliers);

        // Load category breakdown
        const categoryResponse = await fetch('/api/category-breakdown');
        const categories = await categoryResponse.json();
        createCategoryChart(categories);

    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Update metric cards with data
function updateMetricCards(summary) {
    document.getElementById('total-spend').textContent = formatCurrency(summary.total_spend);
    document.getElementById('total-orders').textContent = summary.total_orders.toLocaleString();
    document.getElementById('avg-order').textContent = formatCurrency(summary.avg_order_value);
    document.getElementById('total-suppliers').textContent = summary.unique_suppliers;
    document.getElementById('date-range').textContent = `${summary.date_range.start} to ${summary.date_range.end}`;
}

// Create monthly trends chart
function createMonthlyTrendsChart(data) {
    const ctx = document.getElementById('monthlyTrendsChart').getContext('2d');
    
    if (monthlyTrendsChart) {
        monthlyTrendsChart.destroy();
    }
    
    monthlyTrendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.months,
            datasets: [{
                label: 'Monthly Spend',
                data: data.amounts,
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// Create suppliers chart
function createSuppliersChart(data) {
    const ctx = document.getElementById('suppliersChart').getContext('2d');
    
    if (suppliersChart) {
        suppliersChart.destroy();
    }
    
    suppliersChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.suppliers,
            datasets: [{
                label: 'Total Spend',
                data: data.amounts,
                backgroundColor: [
                    '#0d6efd',
                    '#198754',
                    '#0dcaf0',
                    '#ffc107',
                    '#dc3545'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

// Create category chart
function createCategoryChart(data) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.categories,
            datasets: [{
                data: data.amounts,
                backgroundColor: [
                    '#0d6efd',
                    '#198754',
                    '#0dcaf0',
                    '#ffc107',
                    '#dc3545'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}