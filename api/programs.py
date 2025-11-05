"""
Program Management API
File: api/programs.py
"""

from flask import Blueprint, request, jsonify, send_file
from utils.save_load import data_manager
from scraper.applyboard_scraper import ApplyBoardScraper
import pandas as pd
import uuid
from datetime import datetime
import os

programs_bp = Blueprint('programs', __name__)

# Load programs data
programs_df = data_manager.load_programs()
applications_df = data_manager.load_applications()

@programs_bp.route('/auto-scrape', methods=['POST'])
def auto_scrape():
    """Trigger automatic scraping of ApplyBoard programs"""
    global programs_df
    
    try:
        data = request.get_json() or {}
        max_programs = data.get('max_programs', 50)
        
        scraper = ApplyBoardScraper()
        new_programs = scraper.scrape_programs(max_programs=max_programs)
        
        if len(new_programs) == 0:
            return jsonify({'error': 'No programs scraped'}), 400
        
        # Remove duplicates and merge with existing data
        if len(programs_df) > 0:
            # Keep existing programs that aren't in new scrape
            existing_ids = set(programs_df['program_id'].values)
            new_ids = set(new_programs['program_id'].values)
            
            # Update existing programs
            programs_df_filtered = programs_df[~programs_df['program_id'].isin(new_ids)]
            programs_df = pd.concat([programs_df_filtered, new_programs], ignore_index=True)
        else:
            programs_df = new_programs
        
        # Save to CSV
        data_manager.save_programs(programs_df)
        
        return jsonify({
            'message': 'Scraping completed successfully',
            'programs_scraped': len(new_programs),
            'total_programs': len(programs_df)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    



@programs_bp.route('/programs', methods=['GET'])
def get_programs():
    """Get all programs with optional pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Calculate pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        total = len(programs_df)
        programs_page = programs_df.iloc[start_idx:end_idx]
        
        return jsonify({
            'programs': programs_page.to_dict(orient='records'),
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@programs_bp.route('/programs', methods=['POST'])
def create_program():
    """Create a new program"""
    global programs_df
    
    try:
        data = request.get_json()
        
        # Generate program ID if not provided
        if 'program_id' not in data:
            data['program_id'] = str(uuid.uuid4())
        
        # Add timestamp
        data['scraped_at'] = datetime.now().isoformat()
        
        # Validate required fields
        required_fields = ['program_name', 'university', 'degree_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Add to DataFrame
        new_program = pd.DataFrame([data])
        programs_df = pd.concat([programs_df, new_program], ignore_index=True)
        
        # Save
        data_manager.save_programs(programs_df)
        
        return jsonify({
            'message': 'Program created successfully',
            'program': data
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@programs_bp.route('/programs/<program_id>', methods=['GET'])
def get_program(program_id):
    """Get a single program by ID"""
    try:
        program = programs_df[programs_df['program_id'] == program_id]
        
        if len(program) == 0:
            return jsonify({'error': 'Program not found'}), 404
        
        return jsonify({
            'program': program.iloc[0].to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@programs_bp.route('/programs/<program_id>', methods=['PATCH'])
def update_program(program_id):
    """Update a program"""
    global programs_df
    
    try:
        data = request.get_json()
        
        # Find program
        idx = programs_df[programs_df['program_id'] == program_id].index
        
        if len(idx) == 0:
            return jsonify({'error': 'Program not found'}), 404
        
        # Update fields
        for key, value in data.items():
            if key != 'program_id':  # Don't allow ID changes
                programs_df.at[idx[0], key] = value
        
        # Save
        data_manager.save_programs(programs_df)
        
        return jsonify({
            'message': 'Program updated successfully',
            'program': programs_df.iloc[idx[0]].to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@programs_bp.route('/programs/<program_id>', methods=['DELETE'])
def delete_program(program_id):
    """Delete a program"""
    global programs_df
    
    try:
        # Find and remove program
        initial_len = len(programs_df)
        programs_df = programs_df[programs_df['program_id'] != program_id]
        
        if len(programs_df) == initial_len:
            return jsonify({'error': 'Program not found'}), 404
        
        # Save
        data_manager.save_programs(programs_df)
        
        return jsonify({
            'message': 'Program deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@programs_bp.route('/programs/search', methods=['GET'])
def search_programs():
    """Search programs by name, university, or other fields"""
    try:
        query = request.args.get('q', '').lower()
        field = request.args.get('field', 'all')
        
        if not query:
            return jsonify({'error': 'Search query required'}), 400
        
        # Search across multiple fields
        if field == 'all':
            mask = (
                programs_df['program_name'].str.lower().str.contains(query, na=False) |
                programs_df['university'].str.lower().str.contains(query, na=False) |
                programs_df['degree_type'].str.lower().str.contains(query, na=False) |
                programs_df['country'].str.lower().str.contains(query, na=False)
            )
        else:
            if field not in programs_df.columns:
                return jsonify({'error': f'Invalid field: {field}'}), 400
            mask = programs_df[field].str.lower().str.contains(query, na=False)
        
        results = programs_df[mask]
        
        return jsonify({
            'results': results.to_dict(orient='records'),
            'count': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@programs_bp.route('/programs/import', methods=['POST'])
def import_programs():
    """Import programs from uploaded CSV"""
    global programs_df
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read CSV
        imported_df = pd.read_csv(file)
        
        # Merge with existing data
        programs_df = pd.concat([programs_df, imported_df], ignore_index=True)
        
        # Remove duplicates based on program_id
        programs_df = programs_df.drop_duplicates(subset=['program_id'], keep='last')
        
        # Save
        data_manager.save_programs(programs_df)
        
        return jsonify({
            'message': 'Programs imported successfully',
            'imported_count': len(imported_df),
            'total_programs': len(programs_df)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@programs_bp.route('/export-programs', methods=['GET'])
def export_programs():
    """Export programs to CSV"""
    try:
        export_path = 'data/programs_export.csv'
        programs_df.to_csv(export_path, index=False)
        
        return send_file(
            export_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'programs_export_{datetime.now().strftime("%Y%m%d")}.csv'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@programs_bp.route('/applied-to-program', methods=['POST'])
def apply_to_program():
    """Log a program application"""
    global applications_df
    
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'program_id' not in data or 'program_name' not in data:
            return jsonify({'error': 'program_id and program_name required'}), 400
        
        # Create application record
        application = {
            'application_id': str(uuid.uuid4()),
            'program_id': data['program_id'],
            'program_name': data['program_name'],
            'user_email': data.get('user_email', 'anonymous'),
            'applied_at': datetime.now().isoformat()
        }
        
        # Add to DataFrame
        new_app = pd.DataFrame([application])
        applications_df = pd.concat([applications_df, new_app], ignore_index=True)
        
        # Save
        data_manager.save_applications(applications_df)
        
        # Trigger email if email provided
        if 'user_email' in data and data['user_email'] != 'anonymous':
            # This will be handled by the emails API
            pass
        
        return jsonify({
            'message': 'Application recorded successfully',
            'application': application
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@programs_bp.route('/applications', methods=['GET'])
def get_applications():
    """Get all applications"""
    try:
        return jsonify({
            'applications': applications_df.to_dict(orient='records'),
            'total': len(applications_df)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500