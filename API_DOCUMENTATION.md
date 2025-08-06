# Freight Optimization System - API Documentation

## Backend Ready for Frontend Integration

All 4 pain points solved with complete backend API endpoints.

## Available Dashboards & Routes

### Main Dashboards
- `/` - Historical spend analysis dashboard
- `/automation` - Automated shipping optimization dashboard  
- `/executive` - Executive-level reporting dashboard
- `/challenge` - Challenge readiness analysis dashboard
- `/delivery` - Delivery time tracking dashboard
- `/centralized-purchasing` - Centralized purchasing workflow dashboard

## API Endpoints

### Historical Analysis
- `GET /api/spend-summary` - Total spend metrics
- `GET /api/monthly-trends` - Monthly spending trends
- `GET /api/top-suppliers` - Top suppliers by spend
- `GET /api/category-breakdown` - Spending by category

### Shipping Optimization
- `GET /api/shipping-recommendations?order_value=1000&weight_category=medium&urgency=standard` - Carrier recommendations
- `GET /api/carrier-performance` - Carrier performance summary
- `GET /api/shipping-savings` - Cost savings analysis
- `GET /api/ups-rates?order_value=1000&weight=5.0&dest_city=LA&dest_state=CA&dest_zip=90210` - UPS rates

### Consolidation Management
- `GET /api/consolidation-opportunities?days_window=7` - Consolidation opportunities
- `GET /api/consolidation-summary` - Consolidation summary metrics
- `GET /api/consolidation-strategy?supplier=SUPPLIER_NAME` - Strategy recommendations

### Supplier Diversity
- `GET /api/diversity-summary` - Diversity performance summary
- `GET /api/diverse-suppliers` - Diverse supplier identification
- `GET /api/diversity-goals?target=25.0` - Goal tracking
- `GET /api/diversity-trends` - Monthly diversity trends

### Automation Engine
- `POST /api/auto-carrier-select` - Automated carrier selection
- `GET /api/automation-alerts` - Cost-saving alerts
- `GET /api/shipping-rules` - Automated shipping rules
- `GET /api/automation-dashboard` - Complete automation data

### Executive Reporting
- `GET /api/executive-report` - Executive dashboard report
- `GET /api/consolidation-visibility` - Enhanced consolidation visibility
- `GET /api/diversity-visibility` - Enhanced diversity visibility

### Challenge Analysis
- `GET /api/challenge-readiness` - Challenge readiness analysis
- `GET /api/cost-comparison` - Cost calculator comparison
- `GET /api/data-completeness` - Data completeness analysis

### Delivery Tracking
- `GET /api/delivery-dashboard` - Delivery tracking dashboard data
- `GET /api/delivery-performance` - Delivery performance summary
- `GET /api/predict-delivery?carrier=UPS&order_value=1000&supplier=SUPPLIER` - Delivery prediction
- `GET /api/delivery-alerts` - Delivery alerts

### Centralized Purchasing
- `POST /api/submit-purchase-request` - Submit new purchase request
- `POST /api/approve-request` - Process approval decisions

## Sample Request/Response Examples

### Submit Purchase Request
```json
POST /api/submit-purchase-request
{
  "requester": "John Smith",
  "department": "Engineering", 
  "supplier": "DEEP BLUE INTEGRATION",
  "description": "Network Equipment",
  "total_amount": 2500.00,
  "urgency": "standard",
  "diversity_category": "DVBE"
}

Response:
{
  "request_id": "PR-20241205-001",
  "status": "pending_approval",
  "approval_level": "manager",
  "recommended_carrier": "Ground",
  "estimated_shipping": 45.00,
  "total_estimated_cost": 2545.00
}
```

### Auto Carrier Selection
```json
POST /api/auto-carrier-select
{
  "order_value": 1500,
  "weight": 8.0,
  "urgency": "standard",
  "dest_city": "Los Angeles",
  "dest_state": "CA",
  "dest_zip": "90210"
}

Response:
{
  "recommended_carrier": "UPS",
  "estimated_cost": 15.50,
  "estimated_days": 3,
  "cost_savings": 5.25,
  "automation_confidence": 95,
  "reasoning": "Historical analysis recommends UPS"
}
```

## Key Data Models

### Purchase Request
- `request_id`: Unique identifier
- `requester`: Person submitting request
- `department`: Requesting department
- `supplier`: Supplier name
- `total_amount`: Order value
- `status`: approval status
- `recommended_carrier`: Optimal shipping carrier

### Consolidation Opportunity
- `supplier`: Supplier name
- `order_count`: Number of orders to consolidate
- `potential_savings`: Dollar savings amount
- `current_shipping`: Current shipping cost
- `consolidated_shipping`: Optimized shipping cost

### Diversity Metrics
- `category`: DVBE, OSB, Non-Diverse
- `spend_amount`: Total spend in category
- `percentage`: Percentage of total spend
- `goal_status`: Progress toward diversity goals

## Frontend Integration Notes

1. **CORS**: May need to configure CORS headers for frontend requests
2. **Authentication**: Currently no auth - add as needed
3. **Error Handling**: All endpoints return JSON with error messages
4. **Real-time Updates**: Consider WebSocket for live dashboard updates
5. **File Uploads**: No file upload endpoints currently - add if needed

## Running the Backend
```bash
python app.py
# Server runs on http://127.0.0.1:5000
```

All endpoints are ready for your frontend team to integrate!