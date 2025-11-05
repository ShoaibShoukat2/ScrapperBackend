"""
Data Persistence Utilities
File: utils/save_load.py
"""

import pandas as pd
import os
from datetime import datetime

class DataManager:
    """Manages loading and saving of all DataFrames"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Define file paths
        self.programs_path = os.path.join(data_dir, 'programs.csv')
        self.analytics_path = os.path.join(data_dir, 'analytics.csv')
        self.emails_path = os.path.join(data_dir, 'emails.csv')
        self.chats_path = os.path.join(data_dir, 'chats.csv')
        self.applications_path = os.path.join(data_dir, 'applications.csv')
        
    def load_programs(self):
        """Load programs DataFrame"""
        if os.path.exists(self.programs_path):
            return pd.read_csv(self.programs_path)
        return pd.DataFrame(columns=[
            'program_id', 'program_name', 'university', 'degree_type',
            'duration', 'tuition_fee', 'application_fee', 'start_date',
            'deadline', 'country', 'requirements', 'english_test_required',
            'description', 'url', 'intake', 'scraped_at'
        ])
    
    def save_programs(self, df):
        """Save programs DataFrame"""
        df.to_csv(self.programs_path, index=False)
        print(f"✓ Saved {len(df)} programs")
        
    def load_analytics(self):
        """Load analytics DataFrame"""
        if os.path.exists(self.analytics_path):
            return pd.read_csv(self.analytics_path)
        return pd.DataFrame(columns=[
            'event_id', 'project_id', 'event_type', 'user_id', 'timestamp'
        ])
    
    def save_analytics(self, df):
        """Save analytics DataFrame"""
        df.to_csv(self.analytics_path, index=False)
        
    def load_emails(self):
        """Load emails DataFrame"""
        if os.path.exists(self.emails_path):
            return pd.read_csv(self.emails_path)
        return pd.DataFrame(columns=[
            'email_id', 'program_id', 'to', 'subject', 'timestamp', 'status'
        ])
    
    def save_emails(self, df):
        """Save emails DataFrame"""
        df.to_csv(self.emails_path, index=False)
        
    def load_chats(self):
        """Load chats DataFrame"""
        if os.path.exists(self.chats_path):
            return pd.read_csv(self.chats_path)
        return pd.DataFrame(columns=[
            'chat_id', 'user_id', 'messages', 'created_at', 'updated_at'
        ])
    
    def save_chats(self, df):
        """Save chats DataFrame"""
        df.to_csv(self.chats_path, index=False)
        
    def load_applications(self):
        """Load applications DataFrame"""
        if os.path.exists(self.applications_path):
            return pd.read_csv(self.applications_path)
        return pd.DataFrame(columns=[
            'application_id', 'program_id', 'program_name', 'user_email', 'applied_at'
        ])
    
    def save_applications(self, df):
        """Save applications DataFrame"""
        df.to_csv(self.applications_path, index=False)
        
    def backup_all(self):
        """Create backup of all data files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(self.data_dir, f'backup_{timestamp}')
        os.makedirs(backup_dir, exist_ok=True)
        
        files = [
            self.programs_path, self.analytics_path,
            self.emails_path, self.chats_path, self.applications_path
        ]
        
        for filepath in files:
            if os.path.exists(filepath):
                filename = os.path.basename(filepath)
                backup_path = os.path.join(backup_dir, filename)
                df = pd.read_csv(filepath)
                df.to_csv(backup_path, index=False)
                
        print(f"✓ Backup created at {backup_dir}")

# Global instance
data_manager = DataManager()