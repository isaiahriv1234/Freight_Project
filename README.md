# Freight_Project
Freight project for CPSLO/AWS DxHub CCAI Summer Camp

# Project Roles
UI Developer(s): Alicia
SWE: River, Ethan, Isaiah
ML: River, Ethan, Isaiah
Data Analyst/Finance: Justin

<img width="550" height="508" alt="Screenshot 2025-08-05 at 11 53 31 AM" src="https://github.com/user-attachments/assets/dbfafe17-d815-4be9-8fd2-a89b048266a2" />

## Data Dictionary - Cal Poly SLO Procurement Data

### Column Explanations

**Key Business Columns:**
- **Supplier Type**: DVB (Diverse Business), OSB (Other Small Business) - tracks diversity goals
- **Supplier Name**: Who Cal Poly buys from - identifies consolidation opportunities
- **PO Date**: When orders were placed - reveals ordering patterns for consolidation
- **Line Descr**: What was purchased - helps categorize shipments

**Financial Columns:**
- **Goods/Services/Construction/IT (Amt)**: Dollar amounts by category - determines shipment value for carrier selection
- **PO ID**: Purchase order number - groups items that ship together

**Shipping Relevance:**
- **NIGP**: Product classification codes - helps predict package size/weight
- **Act Per**: Accounting period (month) - shows seasonal shipping patterns

### Why This Data Matters for "Expedia for Shipping":

1. **Consolidation**: Multiple line items with same supplier + similar dates = combine shipments
2. **Carrier Selection**: High-value orders ($30K+ IT purchases) need different shipping than small supplies
3. **Route Optimization**: Supplier locations + delivery timing patterns
4. **Cost Analysis**: Current shipping costs vs EasyPost rates

### Key Insights:
- Cal Poly spends heavily on IT, construction services, and equipment
- Perfect for freight optimization since these have different shipping requirements
- Multiple consolidation opportunities identified in the data
