"""
ApplyBoard Program Scraper
File: scraper/applyboard_scraper.py
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import uuid
from datetime import datetime
import os
from urllib.parse import urljoin

class ApplyBoardScraper:
    def __init__(self, base_url="https://applyboard.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def scrape_programs(self, max_programs=50):
        """
        Scrape programs from ApplyBoard
        Returns a pandas DataFrame with program data
        """
        programs = []
        
        try:
            # Mock scraping with realistic data structure
            # In production, replace with actual scraping logic
            programs_data = self._mock_scrape_data(max_programs)
            programs.extend(programs_data)
            
        except Exception as e:
            print(f"Error scraping programs: {e}")
            
        return pd.DataFrame(programs)
    
    def _mock_scrape_data(self, count=50):
        """
        Generate mock program data for testing
        In production, replace with actual scraping logic
        """
        universities = [
            "University of Toronto", "McGill University", "University of British Columbia",
            "University of Waterloo", "McMaster University", "University of Alberta",
            "Simon Fraser University", "University of Calgary", "Queen's University",
            "Western University", "York University", "Dalhousie University"
        ]
        
        programs = [
            "Computer Science", "Business Administration", "Engineering",
            "Data Science", "Artificial Intelligence", "Software Engineering",
            "Information Technology", "Digital Marketing", "Finance",
            "Accounting", "Mechanical Engineering", "Civil Engineering"
        ]
        
        degree_types = ["Bachelor's", "Master's", "Diploma", "Certificate", "PhD"]
        countries = ["Canada", "USA", "UK", "Australia"]
        intakes = ["Fall 2025", "Winter 2026", "Spring 2025", "Summer 2025"]
        
        mock_programs = []
        
        for i in range(count):
            university = universities[i % len(universities)]
            program = programs[i % len(programs)]
            degree = degree_types[i % len(degree_types)]
            
            program_data = {
                'program_id': str(uuid.uuid4()),
                'program_name': f"{degree} in {program}",
                'university': university,
                'degree_type': degree,
                'duration': f"{2 + (i % 3)} years" if "Bachelor" in degree or "Master" in degree else "1 year",
                'tuition_fee': f"${15000 + (i * 1000) % 30000}",
                'application_fee': f"${100 + (i * 10) % 200}",
                'start_date': intakes[i % len(intakes)].split()[0] + " " + intakes[i % len(intakes)].split()[1],
                'deadline': f"202{5 + i % 2}-{(i % 12) + 1:02d}-15",
                'country': countries[i % len(countries)],
                'requirements': f"GPA: {3.0 + (i % 10) * 0.1:.1f}, Bachelor's degree for graduate programs",
                'english_test_required': "IELTS 6.5 or TOEFL 90" if i % 3 == 0 else "IELTS 7.0 or TOEFL 100",
                'description': f"This program offers comprehensive training in {program.lower()} with hands-on experience and industry connections. Students will develop critical skills needed for success in the modern workforce.",
                'url': f"https://applyboard.com/programs/{program.lower().replace(' ', '-')}-{i}",
                'intake': intakes[i % len(intakes)],
                'scraped_at': datetime.now().isoformat()
            }
            
            mock_programs.append(program_data)
        
        return mock_programs
    
    def scrape_program_details(self, program_url):
        """
        Scrape detailed information from a single program page
        """
        try:
            response = self.session.get(program_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract program details
            # This is a template - adjust selectors based on actual site structure
            details = {
                'description': self._extract_text(soup, 'div.program-description'),
                'requirements': self._extract_text(soup, 'div.requirements'),
                'tuition_fee': self._extract_text(soup, 'span.tuition'),
                'duration': self._extract_text(soup, 'span.duration'),
            }
            
            return details
            
        except Exception as e:
            print(f"Error scraping program details: {e}")
            return {}
    
    def _extract_text(self, soup, selector):
        """Helper to safely extract text from BeautifulSoup element"""
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else ""
    
    def save_to_csv(self, df, filepath='data/programs.csv'):
        """Save DataFrame to CSV"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_csv(filepath, index=False)
        print(f"Saved {len(df)} programs to {filepath}")
        
    def load_from_csv(self, filepath='data/programs.csv'):
        """Load DataFrame from CSV"""
        if os.path.exists(filepath):
            return pd.read_csv(filepath)
        return pd.DataFrame()