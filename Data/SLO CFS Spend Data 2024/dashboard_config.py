#!/usr/bin/env python3
"""
Real-time Procurement Dashboard Configuration
Provides live tracking of supplier diversity performance and cost optimization metrics
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output
import numpy as np
from datetime import datetime, timedelta

class ProcurementDashboard:
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = self.load_data()
        
    def load_data(self):
        """Load and prepare data for dashboard"""
        df = pd.read_csv(self.data_path)
        df['PO_Date'] = pd.to_datetime(df['PO_Date'])
        df['Month'] = df['PO_Date'].dt.to_period('M')
        return df
    
    def create_diversity_metrics_chart(self):
        """Create supplier diversity performance chart"""
        diversity_data = self.df.groupby(['Month', 'Supplier_Diversity_Category'])['Total_Amount'].sum().reset_index()
        
        fig = px.bar(diversity_data, 
                    x='Month', 
                    y='Total_Amount', 
                    color='Supplier_Diversity_Category',
                    title='Monthly Supplier Diversity Spend',
                    labels={'Total_Amount': 'Spend ($)', 'Month': 'Month'})
        
        # Add diversity goals as horizontal lines
        diversity_goals = {'DVBE': 0.03, 'OSB': 0.25, 'MB': 0.05}
        total_monthly_spend = diversity_data.groupby('Month')['Total_Amount'].sum()
        
        for category, goal_pct in diversity_goals.items():
            goal_amounts = total_monthly_spend * goal_pct
            fig.add_scatter(x=goal_amounts.index.astype(str), 
                          y=goal_amounts.values,
                          mode='lines',
                          name=f'{category} Goal',
                          line=dict(dash='dash'))
        
        return fig
    
    def create_shipping_optimization_chart(self):
        """Create shipping cost optimization tracking chart"""
        shipping_data = self.df.groupby(['Month', 'Carrier']).agg({
            'Shipping_Cost': 'sum',
            'Total_Amount': 'sum'
        }).reset_index()
        
        shipping_data['Shipping_Ratio'] = shipping_data['Shipping_Cost'] / shipping_data['Total_Amount'] * 100
        
        fig = px.line(shipping_data, 
                     x='Month', 
                     y='Shipping_Ratio', 
                     color='Carrier',
                     title='Shipping Cost Ratio by Carrier Over Time',
                     labels={'Shipping_Ratio': 'Shipping Cost Ratio (%)', 'Month': 'Month'})
        
        # Add target line at 10%
        fig.add_hline(y=10, line_dash="dash", line_color="red", 
                     annotation_text="Target: 10%")
        
        return fig
    
    def create_consolidation_opportunities_chart(self):
        """Create consolidation opportunities tracking"""
        # Calculate weekly consolidation opportunities
        self.df['Week'] = self.df['PO_Date'].dt.to_period('W')
        
        consolidation_data = self.df.groupby(['Week', 'Supplier_Name']).agg({
            'PO_ID': 'count',
            'Shipping_Cost': 'sum'
        }).reset_index()
        
        # Find opportunities (multiple orders per supplier per week)
        opportunities = consolidation_data[consolidation_data['PO_ID'] > 1]
        opportunities['Potential_Savings'] = opportunities['Shipping_Cost'] * 0.3
        
        weekly_savings = opportunities.groupby('Week')['Potential_Savings'].sum().reset_index()
        weekly_savings['Week_str'] = weekly_savings['Week'].astype(str)
        
        fig = px.bar(weekly_savings, 
                    x='Week_str', 
                    y='Potential_Savings',
                    title='Weekly Consolidation Savings Opportunities',
                    labels={'Potential_Savings': 'Potential Savings ($)', 'Week_str': 'Week'})
        
        return fig
    
    def create_top_suppliers_chart(self):
        """Create top suppliers by spend chart"""
        top_suppliers = self.df.groupby(['Supplier_Name', 'Supplier_Diversity_Category'])['Total_Amount'].sum().reset_index()
        top_suppliers = top_suppliers.nlargest(15, 'Total_Amount')
        
        fig = px.bar(top_suppliers, 
                    x='Total_Amount', 
                    y='Supplier_Name', 
                    color='Supplier_Diversity_Category',
                    orientation='h',
                    title='Top 15 Suppliers by Spend',
                    labels={'Total_Amount': 'Total Spend ($)', 'Supplier_Name': 'Supplier'})
        
        return fig
    
    def create_kpi_cards(self):
        """Create KPI summary cards"""
        total_spend = self.df['Total_Amount'].sum()
        total_shipping = self.df['Shipping_Cost'].sum()
        shipping_ratio = (total_shipping / total_spend * 100)
        
        # Diversity metrics
        diversity_spend = self.df.groupby('Supplier_Diversity_Category')['Total_Amount'].sum()
        dvbe_pct = (diversity_spend.get('DVBE', 0) / total_spend * 100)
        osb_pct = (diversity_spend.get('OSB', 0) / total_spend * 100)
        mb_pct = (diversity_spend.get('MB', 0) / total_spend * 100)
        
        # Consolidation opportunities
        weekly_multi_orders = self.df.groupby(['Supplier_Name', self.df['PO_Date'].dt.to_period('W')]).size()
        consolidation_opps = len(weekly_multi_orders[weekly_multi_orders > 1])
        
        kpis = {
            'total_spend': f"${total_spend:,.0f}",
            'shipping_ratio': f"{shipping_ratio:.1f}%",
            'dvbe_pct': f"{dvbe_pct:.1f}%",
            'osb_pct': f"{osb_pct:.1f}%",
            'mb_pct': f"{mb_pct:.1f}%",
            'consolidation_opps': consolidation_opps
        }
        
        return kpis
    
    def create_dashboard_layout(self):
        """Create the dashboard layout"""
        kpis = self.create_kpi_cards()
        
        app = dash.Dash(__name__)
        
        app.layout = html.Div([
            html.H1("Procurement Optimization Dashboard", 
                   style={'textAlign': 'center', 'marginBottom': 30}),
            
            # KPI Cards Row
            html.Div([
                html.Div([
                    html.H3("Total Spend"),
                    html.H2(kpis['total_spend'], style={'color': '#1f77b4'})
                ], className='kpi-card', style={'width': '15%', 'display': 'inline-block', 'margin': '10px', 'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'textAlign': 'center'}),
                
                html.Div([
                    html.H3("Shipping Ratio"),
                    html.H2(kpis['shipping_ratio'], style={'color': '#ff7f0e'})
                ], className='kpi-card', style={'width': '15%', 'display': 'inline-block', 'margin': '10px', 'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'textAlign': 'center'}),
                
                html.Div([
                    html.H3("DVBE %"),
                    html.H2(kpis['dvbe_pct'], style={'color': '#2ca02c'})
                ], className='kpi-card', style={'width': '15%', 'display': 'inline-block', 'margin': '10px', 'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'textAlign': 'center'}),
                
                html.Div([
                    html.H3("OSB %"),
                    html.H2(kpis['osb_pct'], style={'color': '#d62728'})
                ], className='kpi-card', style={'width': '15%', 'display': 'inline-block', 'margin': '10px', 'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'textAlign': 'center'}),
                
                html.Div([
                    html.H3("MB %"),
                    html.H2(kpis['mb_pct'], style={'color': '#9467bd'})
                ], className='kpi-card', style={'width': '15%', 'display': 'inline-block', 'margin': '10px', 'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'textAlign': 'center'}),
                
                html.Div([
                    html.H3("Consolidation Opps"),
                    html.H2(str(kpis['consolidation_opps']), style={'color': '#8c564b'})
                ], className='kpi-card', style={'width': '15%', 'display': 'inline-block', 'margin': '10px', 'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'textAlign': 'center'})
            ], style={'textAlign': 'center', 'marginBottom': 30}),
            
            # Charts Row 1
            html.Div([
                html.Div([
                    dcc.Graph(figure=self.create_diversity_metrics_chart())
                ], style={'width': '50%', 'display': 'inline-block'}),
                
                html.Div([
                    dcc.Graph(figure=self.create_shipping_optimization_chart())
                ], style={'width': '50%', 'display': 'inline-block'})
            ]),
            
            # Charts Row 2
            html.Div([
                html.Div([
                    dcc.Graph(figure=self.create_consolidation_opportunities_chart())
                ], style={'width': '50%', 'display': 'inline-block'}),
                
                html.Div([
                    dcc.Graph(figure=self.create_top_suppliers_chart())
                ], style={'width': '50%', 'display': 'inline-block'})
            ]),
            
            # Auto-refresh component
            dcc.Interval(
                id='interval-component',
                interval=300*1000,  # Update every 5 minutes
                n_intervals=0
            )
        ])
        
        return app

def create_automated_alerts():
    """Create automated alerts for procurement issues"""
    alerts = {
        'shipping_cost_alert': {
            'condition': 'shipping_ratio > 15%',
            'message': 'High shipping costs detected. Consider consolidation.',
            'severity': 'warning'
        },
        'diversity_goal_alert': {
            'condition': 'dvbe_percentage < 3%',
            'message': 'DVBE spending below 3% goal.',
            'severity': 'info'
        },
        'consolidation_alert': {
            'condition': 'weekly_multi_orders > 10',
            'message': 'Multiple consolidation opportunities available.',
            'severity': 'info'
        },
        'supplier_concentration_alert': {
            'condition': 'top_supplier_percentage > 40%',
            'message': 'High supplier concentration risk detected.',
            'severity': 'warning'
        }
    }
    
    return alerts

def generate_automated_recommendations():
    """Generate automated procurement recommendations"""
    recommendations = {
        'cost_optimization': [
            "Negotiate volume discounts with top 5 suppliers",
            "Implement blanket POs for recurring items",
            "Consolidate shipments from same geographic regions",
            "Review and optimize carrier selection based on performance"
        ],
        'diversity_enhancement': [
            "Identify diverse suppliers for top spending categories",
            "Set up supplier diversity scorecards",
            "Implement diverse supplier mentoring programs",
            "Track and report diversity metrics monthly"
        ],
        'process_automation': [
            "Automate reordering for items with >4 annual orders",
            "Implement electronic catalogs for common items",
            "Set up approval workflows for different spend levels",
            "Create automated consolidation alerts"
        ],
        'risk_mitigation': [
            "Diversify supplier base for critical items",
            "Implement supplier performance scorecards",
            "Create backup supplier relationships",
            "Monitor supplier financial health"
        ]
    }
    
    return recommendations

if __name__ == "__main__":
    # Initialize dashboard
    dashboard = ProcurementDashboard('/Users/isaiahrivera/Desktop/Summer_Camp/Freight_Project/Data/SLO CFS Spend Data 2024/Cleaned_Procurement_Data.csv')
    
    # Create and run dashboard
    app = dashboard.create_dashboard_layout()
    
    print("Starting Procurement Optimization Dashboard...")
    print("Dashboard will be available at: http://127.0.0.1:8050/")
    print("Features:")
    print("- Real-time supplier diversity tracking")
    print("- Shipping cost optimization monitoring")
    print("- Consolidation opportunity identification")
    print("- Automated alerts and recommendations")
    
    # Uncomment to run the dashboard
    # app.run_server(debug=True)