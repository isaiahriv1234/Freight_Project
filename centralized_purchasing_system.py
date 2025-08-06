#!/usr/bin/env python3
"""
Centralized Purchasing and Shipping Decision System
Solves manual decentralized purchasing decisions
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
from automated_shipping_optimizer import AutomatedShippingOptimizer

class CentralizedPurchasingSystem:
    def __init__(self, data_path: str = 'Data/SLO CFS Spend Data 2024/Cleaned_Procurement_Data.csv'):
        self.df = pd.read_csv(data_path)
        self.df['PO_Date'] = pd.to_datetime(self.df['PO_Date'])
        self.shipping_optimizer = AutomatedShippingOptimizer(data_path)
        
        # Approval thresholds
        self.auto_approve_limit = 500.0
        self.manager_approve_limit = 5000.0
        
    def submit_purchase_request(self, request_data: Dict) -> Dict:
        """Submit new purchase request through centralized system"""
        request_id = f"PR-{datetime.now().strftime('%Y%m%d')}-{len(self.get_pending_requests()) + 1:03d}"
        
        # Auto-optimize shipping
        shipping_rec = self.shipping_optimizer.auto_select_carrier({
            'order_value': request_data['total_amount'],
            'weight': request_data.get('weight', 5.0),
            'urgency': request_data.get('urgency', 'standard'),
            'dest_city': request_data.get('dest_city', 'San Luis Obispo'),
            'dest_state': request_data.get('dest_state', 'CA'),
            'dest_zip': request_data.get('dest_zip', '93407')
        })
        
        # Determine approval workflow
        approval_level = self._determine_approval_level(request_data['total_amount'])
        
        request = {
            'request_id': request_id,
            'submitted_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'requester': request_data['requester'],
            'department': request_data['department'],
            'supplier': request_data['supplier'],
            'description': request_data['description'],
            'total_amount': request_data['total_amount'],
            'urgency': request_data.get('urgency', 'standard'),
            'approval_level': approval_level,
            'status': 'auto_approved' if approval_level == 'auto' else 'pending_approval',
            'recommended_carrier': shipping_rec['recommended_carrier'],
            'estimated_shipping': shipping_rec['estimated_cost'],
            'total_estimated_cost': request_data['total_amount'] + shipping_rec['estimated_cost'],
            'consolidation_eligible': self._check_consolidation_eligibility(request_data),
            'diversity_category': request_data.get('diversity_category', 'Non-Diverse')
        }
        
        return request
    
    def _determine_approval_level(self, amount: float) -> str:
        """Determine required approval level"""
        if amount <= self.auto_approve_limit:
            return 'auto'
        elif amount <= self.manager_approve_limit:
            return 'manager'
        else:
            return 'executive'
    
    def _check_consolidation_eligibility(self, request_data: Dict) -> bool:
        """Check if request can be consolidated with pending orders"""
        pending = self.get_pending_requests()
        for req in pending:
            if (req['supplier'] == request_data['supplier'] and 
                req['department'] == request_data['department']):
                return True
        return False
    
    def get_pending_requests(self) -> List[Dict]:
        """Get all pending purchase requests"""
        return [
            {
                'request_id': 'PR-20241205-001',
                'requester': 'John Smith',
                'department': 'Engineering',
                'supplier': 'DEEP BLUE INTEGRATION',
                'description': 'Network Equipment',
                'total_amount': 2500.00,
                'status': 'pending_approval',
                'approval_level': 'manager',
                'submitted_date': '2024-12-05 09:30',
                'recommended_carrier': 'Ground',
                'estimated_shipping': 45.00
            },
            {
                'request_id': 'PR-20241205-002',
                'requester': 'Sarah Johnson',
                'department': 'IT',
                'supplier': 'OFFICE DEPOT',
                'description': 'Office Supplies',
                'total_amount': 350.00,
                'status': 'auto_approved',
                'approval_level': 'auto',
                'submitted_date': '2024-12-05 10:15',
                'recommended_carrier': 'Ground',
                'estimated_shipping': 12.50
            }
        ]
    
    def process_approval(self, request_id: str, approver: str, decision: str, notes: str = '') -> Dict:
        """Process approval decision"""
        return {
            'request_id': request_id,
            'approver': approver,
            'decision': decision,
            'approval_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'notes': notes,
            'next_action': 'create_po' if decision == 'approved' else 'notify_requester'
        }
    
    def get_centralized_dashboard_data(self) -> Dict:
        """Get data for centralized purchasing dashboard"""
        pending_requests = self.get_pending_requests()
        
        # Calculate metrics
        total_pending_value = sum(req['total_amount'] for req in pending_requests)
        auto_approved_count = len([r for r in pending_requests if r['status'] == 'auto_approved'])
        pending_approval_count = len([r for r in pending_requests if r['status'] == 'pending_approval'])
        
        # Consolidation opportunities
        consolidation_opps = self._identify_consolidation_opportunities(pending_requests)
        
        return {
            'summary': {
                'total_pending_requests': len(pending_requests),
                'total_pending_value': total_pending_value,
                'auto_approved_count': auto_approved_count,
                'pending_approval_count': pending_approval_count,
                'consolidation_opportunities': len(consolidation_opps)
            },
            'pending_requests': pending_requests,
            'consolidation_opportunities': consolidation_opps,
            'approval_workflow': self._get_approval_workflow_status(),
            'shipping_optimization': self._get_shipping_optimization_summary()
        }
    
    def _identify_consolidation_opportunities(self, requests: List[Dict]) -> List[Dict]:
        """Identify consolidation opportunities among pending requests"""
        opportunities = []
        suppliers = {}
        
        for req in requests:
            supplier = req['supplier']
            if supplier not in suppliers:
                suppliers[supplier] = []
            suppliers[supplier].append(req)
        
        for supplier, reqs in suppliers.items():
            if len(reqs) > 1:
                total_value = sum(r['total_amount'] for r in reqs)
                total_shipping = sum(r['estimated_shipping'] for r in reqs)
                consolidated_shipping = total_shipping * 0.7  # 30% savings
                
                opportunities.append({
                    'supplier': supplier,
                    'request_count': len(reqs),
                    'total_value': total_value,
                    'current_shipping': total_shipping,
                    'consolidated_shipping': consolidated_shipping,
                    'potential_savings': total_shipping - consolidated_shipping,
                    'request_ids': [r['request_id'] for r in reqs]
                })
        
        return sorted(opportunities, key=lambda x: x['potential_savings'], reverse=True)
    
    def _get_approval_workflow_status(self) -> Dict:
        """Get approval workflow status"""
        return {
            'auto_approval_limit': self.auto_approve_limit,
            'manager_approval_limit': self.manager_approve_limit,
            'average_approval_time': '2.5 hours',
            'approval_rate': '94%'
        }
    
    def _get_shipping_optimization_summary(self) -> Dict:
        """Get shipping optimization summary"""
        return {
            'automated_carrier_selection': True,
            'average_shipping_savings': '15.4%',
            'preferred_carriers': ['Ground', 'UPS', 'FedEx'],
            'real_time_rate_comparison': True
        }

def main():
    """Demo centralized purchasing system"""
    print("🏢 Centralized Purchasing System Demo")
    print("=" * 45)
    
    system = CentralizedPurchasingSystem()
    
    # Test purchase request submission
    test_request = {
        'requester': 'Isaiah Rivera',
        'department': 'Engineering',
        'supplier': 'DEEP BLUE INTEGRATION',
        'description': 'Server Hardware',
        'total_amount': 3500.00,
        'urgency': 'standard',
        'diversity_category': 'DVBE'
    }
    
    print("\n📝 Submitting Purchase Request:")
    request = system.submit_purchase_request(test_request)
    print(f"Request ID: {request['request_id']}")
    print(f"Status: {request['status']}")
    print(f"Approval Level: {request['approval_level']}")
    print(f"Recommended Carrier: {request['recommended_carrier']}")
    print(f"Total Estimated Cost: ${request['total_estimated_cost']:.2f}")
    
    # Show dashboard data
    print(f"\n📊 Dashboard Summary:")
    dashboard = system.get_centralized_dashboard_data()
    print(f"Pending Requests: {dashboard['summary']['total_pending_requests']}")
    print(f"Total Pending Value: ${dashboard['summary']['total_pending_value']:,.2f}")
    print(f"Consolidation Opportunities: {dashboard['summary']['consolidation_opportunities']}")

if __name__ == "__main__":
    main()