#!/usr/bin/env python3
"""
Delivery Time Tracking System
Tracks and improves delivery times based on historical data and real-time monitoring
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class DeliveryTimeTracker:
    def __init__(self, data_file):
        self.df = pd.read_csv(data_file)
        self.df['PO_Date'] = pd.to_datetime(self.df['PO_Date'])
        
        # Carrier performance baselines from historical data
        self.carrier_baselines = self.calculate_carrier_baselines()
        
    def calculate_carrier_baselines(self):
        """Calculate baseline delivery performance by carrier from historical data"""
        
        baselines = {}
        carrier_performance = self.df.groupby('carrier').agg({
            'lead_time_days': ['mean', 'std', 'min', 'max'],
            'supplier_name': 'count'
        }).round(2)
        
        for carrier in carrier_performance.index:
            if carrier and carrier != '0':  # Skip empty carriers
                stats = carrier_performance.loc[carrier]
                baselines[carrier] = {
                    'avg_delivery_days': stats[('lead_time_days', 'mean')],
                    'std_deviation': stats[('lead_time_days', 'std')],
                    'best_time': stats[('lead_time_days', 'min')],
                    'worst_time': stats[('lead_time_days', 'max')],
                    'reliability_score': self.calculate_reliability_score(stats),
                    'order_count': stats[('supplier_name', 'count')]
                }
        
        return baselines
    
    def calculate_reliability_score(self, stats):
        """Calculate reliability score based on consistency"""
        avg_time = stats[('lead_time_days', 'mean')]
        std_dev = stats[('lead_time_days', 'std')]
        
        if avg_time == 0:
            return 0
        
        # Lower standard deviation = higher reliability
        reliability = max(0, 100 - (std_dev / avg_time * 100))
        return round(reliability, 1)
    
    def track_delivery_performance(self):
        """Track current delivery performance vs targets"""
        
        performance_report = {
            'overall_metrics': self.calculate_overall_metrics(),
            'carrier_performance': self.analyze_carrier_performance(),
            'supplier_performance': self.analyze_supplier_performance(),
            'improvement_opportunities': self.identify_improvement_opportunities()
        }
        
        return performance_report
    
    def calculate_overall_metrics(self):
        """Calculate overall delivery metrics"""
        
        total_orders = len(self.df[self.df['lead_time_days'] > 0])
        avg_delivery_time = self.df[self.df['lead_time_days'] > 0]['lead_time_days'].mean()
        
        # Performance targets
        target_delivery_time = 7  # 7 days target
        on_time_orders = len(self.df[self.df['lead_time_days'] <= target_delivery_time])
        on_time_percentage = (on_time_orders / total_orders * 100) if total_orders > 0 else 0
        
        return {
            'total_tracked_orders': total_orders,
            'average_delivery_days': round(avg_delivery_time, 1),
            'target_delivery_days': target_delivery_time,
            'on_time_percentage': round(on_time_percentage, 1),
            'performance_vs_target': round(target_delivery_time - avg_delivery_time, 1)
        }
    
    def analyze_carrier_performance(self):
        """Analyze performance by carrier"""
        
        carrier_analysis = {}
        
        for carrier, baseline in self.carrier_baselines.items():
            carrier_orders = self.df[self.df['carrier'] == carrier]
            
            if len(carrier_orders) > 0:
                carrier_analysis[carrier] = {
                    'average_delivery_days': baseline['avg_delivery_days'],
                    'reliability_score': baseline['reliability_score'],
                    'order_volume': baseline['order_count'],
                    'performance_grade': self.grade_carrier_performance(baseline),
                    'improvement_potential': self.calculate_improvement_potential(baseline)
                }
        
        return carrier_analysis
    
    def grade_carrier_performance(self, baseline):
        """Grade carrier performance A-F"""
        
        avg_time = baseline['avg_delivery_days']
        reliability = baseline['reliability_score']
        
        # Combined score based on speed and reliability
        if avg_time <= 3 and reliability >= 90:
            return 'A'
        elif avg_time <= 5 and reliability >= 80:
            return 'B'
        elif avg_time <= 7 and reliability >= 70:
            return 'C'
        elif avg_time <= 10 and reliability >= 60:
            return 'D'
        else:
            return 'F'
    
    def calculate_improvement_potential(self, baseline):
        """Calculate potential for delivery time improvement"""
        
        current_avg = baseline['avg_delivery_days']
        best_time = baseline['best_time']
        
        if current_avg > 0 and best_time > 0:
            improvement_days = current_avg - best_time
            improvement_percentage = (improvement_days / current_avg) * 100
            return {
                'potential_days_saved': round(improvement_days, 1),
                'potential_improvement_percentage': round(improvement_percentage, 1)
            }
        
        return {'potential_days_saved': 0, 'potential_improvement_percentage': 0}
    
    def analyze_supplier_performance(self):
        """Analyze delivery performance by supplier"""
        
        supplier_performance = self.df.groupby('supplier_name').agg({
            'lead_time_days': ['mean', 'count'],
            'carrier': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'Unknown'
        }).round(2)
        
        supplier_analysis = {}
        
        for supplier in supplier_performance.index:
            stats = supplier_performance.loc[supplier]
            avg_time = stats[('lead_time_days', 'mean')]
            order_count = stats[('lead_time_days', 'count')]
            primary_carrier = stats[('carrier', '<lambda>')]
            
            supplier_analysis[supplier] = {
                'average_delivery_days': avg_time,
                'order_count': order_count,
                'primary_carrier': primary_carrier,
                'performance_rating': 'Good' if avg_time <= 7 else 'Needs Improvement'
            }
        
        return supplier_analysis
    
    def identify_improvement_opportunities(self):
        """Identify specific opportunities to improve delivery times"""
        
        opportunities = []
        
        # Opportunity 1: Slow carriers
        for carrier, baseline in self.carrier_baselines.items():
            if baseline['avg_delivery_days'] > 14:  # Slow carriers
                opportunities.append({
                    'type': 'Carrier Optimization',
                    'issue': f"{carrier} averages {baseline['avg_delivery_days']} days",
                    'recommendation': f"Consider switching from {carrier} to faster alternatives",
                    'potential_improvement': f"{baseline['avg_delivery_days'] - 7} days faster",
                    'priority': 'High' if baseline['avg_delivery_days'] > 21 else 'Medium'
                })
        
        # Opportunity 2: Inconsistent carriers
        for carrier, baseline in self.carrier_baselines.items():
            if baseline['reliability_score'] < 70:  # Unreliable carriers
                opportunities.append({
                    'type': 'Reliability Improvement',
                    'issue': f"{carrier} has {baseline['reliability_score']}% reliability",
                    'recommendation': f"Improve {carrier} consistency or find alternatives",
                    'potential_improvement': f"Reduce delivery variance by {baseline['std_deviation']:.1f} days",
                    'priority': 'Medium'
                })
        
        # Opportunity 3: Consolidation for speed
        supplier_counts = self.df['supplier_name'].value_counts()
        for supplier, count in supplier_counts.items():
            if count > 10:  # High-volume suppliers
                supplier_avg = self.df[self.df['supplier_name'] == supplier]['lead_time_days'].mean()
                if supplier_avg > 10:
                    opportunities.append({
                        'type': 'Supplier Consolidation',
                        'issue': f"{supplier} has {count} orders averaging {supplier_avg:.1f} days",
                        'recommendation': f"Negotiate faster delivery terms with {supplier}",
                        'potential_improvement': f"Reduce to 7-day standard",
                        'priority': 'Medium'
                    })
        
        return opportunities
    
    def generate_delivery_dashboard(self):
        """Generate comprehensive delivery time dashboard"""
        
        performance_data = self.track_delivery_performance()
        
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'summary': performance_data['overall_metrics'],
            'carrier_rankings': self.rank_carriers_by_performance(),
            'delivery_trends': self.analyze_delivery_trends(),
            'action_items': self.prioritize_delivery_improvements(),
            'performance_data': performance_data
        }
        
        return dashboard
    
    def rank_carriers_by_performance(self):
        """Rank carriers by overall performance"""
        
        rankings = []
        
        for carrier, baseline in self.carrier_baselines.items():
            # Combined performance score
            speed_score = max(0, 100 - (baseline['avg_delivery_days'] * 10))
            reliability_score = baseline['reliability_score']
            combined_score = (speed_score + reliability_score) / 2
            
            rankings.append({
                'carrier': carrier,
                'performance_score': round(combined_score, 1),
                'avg_delivery_days': baseline['avg_delivery_days'],
                'reliability_score': baseline['reliability_score'],
                'grade': self.grade_carrier_performance(baseline)
            })
        
        return sorted(rankings, key=lambda x: x['performance_score'], reverse=True)
    
    def analyze_delivery_trends(self):
        """Analyze delivery time trends over time"""
        
        if 'PO_Date' in self.df.columns:
            monthly_trends = self.df.groupby(
                self.df['PO_Date'].dt.to_period('M')
            )['lead_time_days'].mean().round(2)
            
            return {
                'monthly_averages': monthly_trends.to_dict(),
                'trend_direction': 'Improving' if len(monthly_trends) > 1 and monthly_trends.iloc[-1] < monthly_trends.iloc[0] else 'Stable'
            }
        
        return {'message': 'Insufficient date data for trend analysis'}
    
    def prioritize_delivery_improvements(self):
        """Prioritize delivery improvement actions"""
        
        opportunities = self.identify_improvement_opportunities()
        
        # Sort by priority and potential impact
        priority_order = {'High': 3, 'Medium': 2, 'Low': 1}
        prioritized = sorted(opportunities, key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        return prioritized[:5]  # Top 5 priorities

def main():
    """Execute delivery time tracking analysis"""
    
    print("⏰ DELIVERY TIME TRACKING SYSTEM")
    print("=" * 50)
    
    # Initialize tracker
    tracker = DeliveryTimeTracker('master_shipping_dataset_20250807_002133.csv')
    
    # Generate dashboard
    dashboard = tracker.generate_delivery_dashboard()
    
    # Save detailed report
    with open('delivery_time_tracking_report.json', 'w') as f:
        json.dump(dashboard, f, indent=2, default=str)
    
    # Display key metrics
    summary = dashboard['summary']
    print(f"📊 Total Orders Tracked: {summary['total_tracked_orders']}")
    print(f"⏱️  Average Delivery Time: {summary['average_delivery_days']} days")
    print(f"🎯 Target Delivery Time: {summary['target_delivery_days']} days")
    print(f"✅ On-Time Percentage: {summary['on_time_percentage']}%")
    
    print(f"\n🏆 TOP PERFORMING CARRIERS:")
    for i, carrier in enumerate(dashboard['carrier_rankings'][:3], 1):
        print(f"{i}. {carrier['carrier']} - Grade {carrier['grade']}")
        print(f"   ⏰ Avg: {carrier['avg_delivery_days']} days")
        print(f"   📊 Reliability: {carrier['reliability_score']}%")
    
    print(f"\n🎯 TOP IMPROVEMENT OPPORTUNITIES:")
    for i, action in enumerate(dashboard['action_items'][:3], 1):
        print(f"{i}. {action['type']}")
        print(f"   Issue: {action['issue']}")
        print(f"   Action: {action['recommendation']}")
        print(f"   Impact: {action['potential_improvement']}")
    
    print(f"\n✅ Delivery time tracking analysis complete!")
    print(f"📄 Detailed report: delivery_time_tracking_report.json")
    
    return dashboard

if __name__ == "__main__":
    main()