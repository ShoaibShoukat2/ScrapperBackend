"""
Analytics and Event Logging API
File: api/analytics.py
"""

from flask import Blueprint, request, jsonify
from utils.save_load import data_manager
import pandas as pd
import uuid
from datetime import datetime

analytics_bp = Blueprint('analytics', __name__)

# Load analytics data
analytics_df = data_manager.load_analytics()

@analytics_bp.route('/log-event', methods=['POST'])
def log_event():
    """Log a user event (click, hover, view, etc.)"""
    global analytics_df
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['project_id', 'event_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create event record
        event = {
            'event_id': str(uuid.uuid4()),
            'project_id': data['project_id'],
            'event_type': data['event_type'],
            'user_id': data.get('user_id', 'anonymous'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add to DataFrame
        new_event = pd.DataFrame([event])
        analytics_df = pd.concat([analytics_df, new_event], ignore_index=True)
        
        # Save to CSV
        data_manager.save_analytics(analytics_df)
        
        return jsonify({
            'message': 'Event logged successfully',
            'event': event
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/get-data', methods=['GET'])
def get_all_events():
    """Get all analytics events"""
    try:
        # Optional filtering
        event_type = request.args.get('event_type')
        user_id = request.args.get('user_id')
        
        filtered_df = analytics_df.copy()
        
        if event_type:
            filtered_df = filtered_df[filtered_df['event_type'] == event_type]
        
        if user_id:
            filtered_df = filtered_df[filtered_df['user_id'] == user_id]
        
        return jsonify({
            'events': filtered_df.to_dict(orient='records'),
            'total': len(filtered_df)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/analytics/project/<project_id>', methods=['GET'])
def get_project_analytics(project_id):
    """Get analytics for a specific project/program"""
    try:
        project_events = analytics_df[analytics_df['project_id'] == project_id]
        
        if len(project_events) == 0:
            return jsonify({
                'project_id': project_id,
                'events': [],
                'total_events': 0,
                'event_breakdown': {}
            }), 200
        
        # Calculate event type breakdown
        event_breakdown = project_events['event_type'].value_counts().to_dict()
        
        return jsonify({
            'project_id': project_id,
            'events': project_events.to_dict(orient='records'),
            'total_events': len(project_events),
            'event_breakdown': event_breakdown
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Get summary analytics grouped by event type and project"""
    try:
        if len(analytics_df) == 0:
            return jsonify({
                'total_events': 0,
                'by_event_type': {},
                'by_project': {},
                'top_projects': []
            }), 200
        
        # Group by event type
        by_event_type = analytics_df['event_type'].value_counts().to_dict()
        
        # Group by project
        by_project = analytics_df.groupby('project_id').size().to_dict()
        
        # Top 10 projects by event count
        top_projects = (
            analytics_df['project_id']
            .value_counts()
            .head(10)
            .to_dict()
        )
        
        # Time-based analysis
        analytics_df_copy = analytics_df.copy()
        analytics_df_copy['timestamp'] = pd.to_datetime(analytics_df_copy['timestamp'])
        analytics_df_copy['date'] = analytics_df_copy['timestamp'].dt.date
        
        events_by_date = (
            analytics_df_copy.groupby('date')
            .size()
            .to_dict()
        )
        
        # Convert date keys to strings for JSON serialization
        events_by_date = {str(k): v for k, v in events_by_date.items()}
        
        return jsonify({
            'total_events': len(analytics_df),
            'by_event_type': by_event_type,
            'by_project': by_project,
            'top_projects': [
                {'project_id': pid, 'event_count': count}
                for pid, count in top_projects.items()
            ],
            'events_by_date': events_by_date
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/analytics/user/<user_id>', methods=['GET'])
def get_user_analytics(user_id):
    """Get analytics for a specific user"""
    try:
        user_events = analytics_df[analytics_df['user_id'] == user_id]
        
        if len(user_events) == 0:
            return jsonify({
                'user_id': user_id,
                'events': [],
                'total_events': 0
            }), 200
        
        # User activity breakdown
        event_breakdown = user_events['event_type'].value_counts().to_dict()
        projects_viewed = user_events['project_id'].nunique()
        
        return jsonify({
            'user_id': user_id,
            'total_events': len(user_events),
            'projects_viewed': projects_viewed,
            'event_breakdown': event_breakdown,
            'events': user_events.to_dict(orient='records')
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/analytics/export', methods=['GET'])
def export_analytics():
    """Export analytics data"""
    try:
        from flask import send_file
        
        export_path = 'data/analytics_export.csv'
        analytics_df.to_csv(export_path, index=False)
        
        return send_file(
            export_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'analytics_export_{datetime.now().strftime("%Y%m%d")}.csv'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/analytics/clear', methods=['DELETE'])
def clear_analytics():
    """Clear all analytics data (use with caution)"""
    global analytics_df
    
    try:
        # Create backup before clearing
        backup_path = f'data/analytics_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        analytics_df.to_csv(backup_path, index=False)
        
        # Clear data
        analytics_df = pd.DataFrame(columns=[
            'event_id', 'project_id', 'event_type', 'user_id', 'timestamp'
        ])
        
        data_manager.save_analytics(analytics_df)
        
        return jsonify({
            'message': 'Analytics data cleared',
            'backup_created': backup_path
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500