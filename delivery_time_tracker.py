#!/usr/bin/env python3
"""
Delivery Time Tracking System
Monitors delivery performance, tracks SLAs, and provides time-based insights
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class DeliveryTimeTracker:
    def __init__(self, data_path: str = 'Data/SLO CFS Spend Data 2024/Cleaned_Procurement_Data.csv'):
        """Initialize delivery time tracker"""
        self.df = pd.read_csv(data_path)
        self.df['PO_Date'] = pd.to_datetime(self.df['PO_Date'])
        
        # Calculate estimated delivery dates
        self.df['Estimated_Delivery_Date'] = self.df['PO_Date'] + pd.to_timedelta(self.df['Lead_Time_Days'], unit='D')
        
        # Define SLA targets by carrier
        self.sla_targets = {
            'UPS': 5,
            'FedEx': 4,
            'Ground': 7,
            'Freight': 14,
            'Electronic': 1
        }
    
    def get_delivery_performance_summary(self) -> Dict:
        """Get overall delivery performance metrics"""
        total_orders = len(self.df)
        avg_lead_time = self.df['Lead_Time_Days'].mean()
        
        # Calculate SLA performance
        sla_performance = {}
        total_on_time = 0
        
        for carrier in self.df['Carrier'].unique():
            if pd.isna(carrier):
                continue
                
            carrier_orders = self.df[self.df['Carrier'] == carrier]
            sla_target = self.sla_targets.get(carrier, 7)
            on_time_orders = len(carrier_orders[carrier_orders['Lead_Time_Days'] <= sla_target])
            total_carrier_orders = len(carrier_orders)
            
            if total_carrier_orders > 0:
                on_time_percentage = (on_time_orders / total_carrier_orders) * 100
                sla_performance[carrier] = {
                    'on_time_orders': on_time_orders,
                    'total_orders': total_carrier_orders,
                    'on_time_percentage': on_time_percentage,
                    'sla_target_days': sla_target,
                    'avg_actual_days': carrier_orders['Lead_Time_Days'].mean()
                }
                total_on_time += on_time_orders
        
        overall_on_time_percentage = (total_on_time / total_orders) * 100 if total_orders > 0 else 0
        
        return {
            'total_orders': total_orders,
            'overall_avg_lead_time': avg_lead_time,
            'overall_on_time_percentage': overall_on_time_percentage,
            'carrier_sla_performance': sla_performance,
            'performance_grade': self._calculate_performance_grade(overall_on_time_percentage),
            'improvement_opportunities': self._identify_improvement_opportunities(sla_performance)
        }
    
    def track_real_time_deliveries(self) -> Dict:
        """Track current and upcoming deliveries"""
        today = datetime.now().date()
        
        # Simulate current deliveries (in real system, this would come from tracking APIs)
        recent_orders = self.df[self.df['PO_Date'] >= datetime.now() - timedelta(days=30)]
        
        # Categorize deliveries
        overdue_deliveries = []
        due_today = []
        due_this_week = []
        
        for _, order in recent_orders.iterrows():
            estimated_delivery = order['Estimated_Delivery_Date'].date()
            days_difference = (estimated_delivery - today).days
            
            if days_difference < 0:
                overdue_deliveries.append({
                    'po_id': order['PO_ID'],
                    'supplier': order['Supplier_Name'],
                    'carrier': order['Carrier'],
                    'days_overdue': abs(days_difference),
                    'order_value': order['Total_Amount']
                })
            elif days_difference == 0:
                due_today.append({
                    'po_id': order['PO_ID'],
                    'supplier': order['Supplier_Name'],
                    'carrier': order['Carrier'],
                    'order_value': order['Total_Amount']
                })
            elif days_difference <= 7:
                due_this_week.append({
                    'po_id': order['PO_ID'],
                    'supplier': order['Supplier_Name'],
                    'carrier': order['Carrier'],
                    'estimated_delivery': estimated_delivery.strftime('%Y-%m-%d'),
                    'order_value': order['Total_Amount']
                })
        
        return {
            'overdue_deliveries': sorted(overdue_deliveries, key=lambda x: x['days_overdue'], reverse=True),
            'due_today': due_today,
            'due_this_week': due_this_week,
            'total_overdue': len(overdue_deliveries),
            'total_due_today': len(due_today),
            'total_due_this_week': len(due_this_week)
        }
    
    def predict_delivery_times(self, carrier: str, order_value: float, supplier: str = None) -> Dict:
        """Predict delivery time for new orders"""
        # Filter historical data for similar orders
        carrier_data = self.df[self.df['Carrier'] == carrier]
        
        if supplier:
            supplier_data = carrier_data[carrier_data['Supplier_Name'] == supplier]
            if not supplier_data.empty:
                carrier_data = supplier_data
        
        if carrier_data.empty:
            return {
                'predicted_days': self.sla_targets.get(carrier, 7),
                'confidence': 'Low',
                'reasoning': 'No historical data available'
            }
        
        # Calculate prediction based on historical performance
        avg_lead_time = carrier_data['Lead_Time_Days'].mean()
        std_lead_time = carrier_data['Lead_Time_Days'].std()
        
        # Adjust for order value (larger orders might take longer)
        value_factor = 1.0
        if order_value > 10000:
            value_factor = 1.2
        elif order_value > 5000:
            value_factor = 1.1
        
        predicted_days = avg_lead_time * value_factor
        
        # Determine confidence based on data availability
        confidence = 'High' if len(carrier_data) > 10 else 'Medium' if len(carrier_data) > 5 else 'Low'
        
        return {
            'predicted_days': round(predicted_days, 1),
            'confidence': confidence,
            'min_expected': round(predicted_days - std_lead_time, 1) if not pd.isna(std_lead_time) else predicted_days,
            'max_expected': round(predicted_days + std_lead_time, 1) if not pd.isna(std_lead_time) else predicted_days,
            'historical_avg': round(avg_lead_time, 1),
            'reasoning': f'Based on {len(carrier_data)} historical orders'
        }
    
    def generate_delivery_alerts(self) -> List[Dict]:
        """Generate alerts for delivery issues"""
        alerts = []
        
        # Get real-time delivery status
        delivery_status = self.track_real_time_deliveries()
        
        # Overdue delivery alerts
        for overdue in delivery_status['overdue_deliveries'][:5]:  # Top 5 overdue
            alerts.append({
                'type': 'overdue_delivery',
                'priority': 'high' if overdue['days_overdue'] > 3 else 'medium',
                'title': f"Overdue Delivery: PO {overdue['po_id']}",
                'description': f"{overdue['supplier']} via {overdue['carrier']} - {overdue['days_overdue']} days overdue",
                'action_required': f"Contact {overdue['carrier']} for delivery status update",
                'impact': f"${overdue['order_value']:,.2f} order value"
            })
        
        # SLA performance alerts
        performance = self.get_delivery_performance_summary()
        for carrier, perf in performance['carrier_sla_performance'].items():
            if perf['on_time_percentage'] < 80:  # Below 80% on-time
                alerts.append({
                    'type': 'sla_performance',
                    'priority': 'medium',
                    'title': f"Poor SLA Performance: {carrier}",
                    'description': f"Only {perf['on_time_percentage']:.1f}% on-time delivery rate",
                    'action_required': f"Review {carrier} service agreement and performance",
                    'impact': f"{perf['total_orders']} orders affected"
                })
        
        # Delivery time trend alerts
        trend_alerts = self._analyze_delivery_trends()
        alerts.extend(trend_alerts)
        
        return sorted(alerts, key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], reverse=True)
    
    def _analyze_delivery_trends(self) -> List[Dict]:
        """Analyze delivery time trends for alerts"""
        alerts = []
        
        # Compare recent vs historical performance
        recent_cutoff = datetime.now() - timedelta(days=30)
        recent_orders = self.df[self.df['PO_Date'] >= recent_cutoff]
        historical_orders = self.df[self.df['PO_Date'] < recent_cutoff]
        
        if not recent_orders.empty and not historical_orders.empty:
            recent_avg = recent_orders['Lead_Time_Days'].mean()
            historical_avg = historical_orders['Lead_Time_Days'].mean()
            
            if recent_avg > historical_avg * 1.2:  # 20% increase
                alerts.append({
                    'type': 'delivery_trend',
                    'priority': 'medium',
                    'title': 'Delivery Times Increasing',
                    'description': f'Recent avg: {recent_avg:.1f} days vs historical: {historical_avg:.1f} days',
                    'action_required': 'Investigate causes of delivery delays',
                    'impact': 'Customer satisfaction risk'
                })
        
        return alerts
    
    def _calculate_performance_grade(self, on_time_percentage: float) -> str:
        """Calculate performance grade based on on-time percentage"""
        if on_time_percentage >= 95:
            return 'A+'
        elif on_time_percentage >= 90:
            return 'A'
        elif on_time_percentage >= 85:
            return 'B+'
        elif on_time_percentage >= 80:
            return 'B'
        elif on_time_percentage >= 75:
            return 'C+'
        elif on_time_percentage >= 70:
            return 'C'
        else:
            return 'D'
    
    def _identify_improvement_opportunities(self, sla_performance: Dict) -> List[str]:
        """Identify opportunities to improve delivery performance"""
        opportunities = []
        
        # Find worst performing carriers
        worst_performers = []
        for carrier, perf in sla_performance.items():
            if perf['on_time_percentage'] < 85:
                worst_performers.append((carrier, perf['on_time_percentage']))
        
        if worst_performers:
            worst_performers.sort(key=lambda x: x[1])
            worst_carrier = worst_performers[0][0]
            opportunities.append(f"Replace or renegotiate with {worst_carrier} (lowest on-time rate)")
        
        # Identify carriers exceeding SLA targets
        for carrier, perf in sla_performance.items():
            if perf['avg_actual_days'] > perf['sla_target_days'] * 1.5:
                opportunities.append(f"Set more realistic SLA targets for {carrier}")
        
        # General recommendations
        if len([p for p in sla_performance.values() if p['on_time_percentage'] < 90]) > 1:
            opportunities.append("Implement carrier performance monitoring dashboard")
            opportunities.append("Consider diversifying carrier portfolio")
        
        return opportunities[:5]  # Top 5 opportunities
    
    def get_delivery_dashboard_data(self) -> Dict:
        """Get comprehensive data for delivery tracking dashboard"""
        return {
            'performance_summary': self.get_delivery_performance_summary(),
            'real_time_deliveries': self.track_real_time_deliveries(),
            'delivery_alerts': self.generate_delivery_alerts(),
            'monthly_trends': self._get_monthly_delivery_trends(),
            'carrier_comparison': self._get_carrier_comparison()
        }
    
    def _get_monthly_delivery_trends(self) -> Dict:
        """Get monthly delivery performance trends"""
        monthly_performance = self.df.groupby(self.df['PO_Date'].dt.to_period('M')).agg({
            'Lead_Time_Days': 'mean',
            'PO_ID': 'count'
        }).round(2)
        
        return {
            'months': [str(month) for month in monthly_performance.index],
            'avg_lead_times': monthly_performance['Lead_Time_Days'].tolist(),
            'order_volumes': monthly_performance['PO_ID'].tolist()
        }
    
    def _get_carrier_comparison(self) -> Dict:
        """Get carrier performance comparison data"""
        comparison = {}
        
        for carrier in self.df['Carrier'].unique():
            if pd.isna(carrier):
                continue
                
            carrier_data = self.df[self.df['Carrier'] == carrier]
            sla_target = self.sla_targets.get(carrier, 7)
            
            comparison[carrier] = {
                'avg_lead_time': carrier_data['Lead_Time_Days'].mean(),
                'sla_target': sla_target,
                'total_orders': len(carrier_data),
                'on_time_rate': len(carrier_data[carrier_data['Lead_Time_Days'] <= sla_target]) / len(carrier_data) * 100
            }
        
        return comparison

def main():
    """Demo delivery time tracker"""
    print("⏱️ Delivery Time Tracker Demo")
    print("=" * 40)
    
    tracker = DeliveryTimeTracker()
    
    # Get performance summary
    performance = tracker.get_delivery_performance_summary()
    print(f"\n📊 Delivery Performance Summary:")
    print(f"Overall On-Time Rate: {performance['overall_on_time_percentage']:.1f}%")
    print(f"Performance Grade: {performance['performance_grade']}")
    print(f"Average Lead Time: {performance['overall_avg_lead_time']:.1f} days")
    
    # Show carrier performance
    print(f"\n🚛 Carrier SLA Performance:")
    for carrier, perf in performance['carrier_sla_performance'].items():
        print(f"  {carrier}: {perf['on_time_percentage']:.1f}% on-time ({perf['avg_actual_days']:.1f} avg days)")
    
    # Show real-time status
    real_time = tracker.track_real_time_deliveries()
    print(f"\n⏰ Real-Time Delivery Status:")
    print(f"  Overdue: {real_time['total_overdue']} orders")
    print(f"  Due Today: {real_time['total_due_today']} orders")
    print(f"  Due This Week: {real_time['total_due_this_week']} orders")
    
    # Show alerts
    alerts = tracker.generate_delivery_alerts()
    print(f"\n🚨 Delivery Alerts ({len(alerts)} total):")
    for alert in alerts[:3]:
        print(f"  {alert['priority'].upper()}: {alert['title']}")
    
    # Test prediction
    prediction = tracker.predict_delivery_times('UPS', 2500)
    print(f"\n🔮 Delivery Prediction (UPS, $2500 order):")
    print(f"  Predicted: {prediction['predicted_days']} days")
    print(f"  Confidence: {prediction['confidence']}")

if __name__ == "__main__":
    main()