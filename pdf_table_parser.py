# pdf_table_parser.py
import pdfplumber
import pandas as pd
from pathlib import Path
import re
from datetime import datetime
import json

class ScheduleTableParser:
    def __init__(self, pdf_path):
        self.pdf_path = Path(pdf_path)
        self.projects = []
        self.debug = True
        self.column_positions = []
        
    def parse(self):
        """Parse the entire PDF and return structured project data"""
        with pdfplumber.open(self.pdf_path) as pdf:
            if len(pdf.pages) > 0:
                self._parse_first_page(pdf.pages[0])
            
            for page_num, page in enumerate(pdf.pages[1:], start=2):
                self._parse_continuation_page(page, page_num)
                
        return self.projects
    
    def _parse_first_page(self, page):
        """Parse the first page with better column detection"""
        # Extract table if available
        tables = page.extract_tables()
        
        if tables and len(tables[0]) > 6:
            print("Using table extraction method")
            self._parse_using_table(tables[0])
        else:
            print("Using spatial analysis method")
            self._parse_using_spatial_analysis(page)
    
    def _parse_using_table(self, table):
        """Parse using extracted table data"""
        # Expected structure:
        # Row 0: Communities (might be split across cells)
        # Row 1: Communities continued or Estates/Landing
        # Row 2: Addresses (346/354, etc.)
        # Row 3: Streets (Stockton, Merrick, etc.)
        # Row 4: Lots
        # Row 5: Square footage
        # Row 6: Features
        # Row 7+: Schedule data
        
        if len(table) < 7:
            print("Table too small, switching to spatial analysis")
            return
        
        # Find the row with addresses (contains pattern like 346/354)
        address_row_idx = None
        for i, row in enumerate(table[:7]):
            if any(cell and re.search(r'\d{3,4}/\d{3,4}', str(cell)) for cell in row):
                address_row_idx = i
                break
        
        if address_row_idx is None:
            print("Could not find address row")
            return
        
        print(f"Address row found at index {address_row_idx}")
        
        # Extract data relative to address row
        addresses = [cell for cell in table[address_row_idx][1:] if cell and re.search(r'\d{3,4}/\d{3,4}', str(cell))]
        
        # Get other rows relative to address row
        communities = []
        streets = []
        lots = []
        sqft = []
        features = []
        
        # Communities (2 rows above addresses)
        if address_row_idx >= 2:
            comm_row1 = table[address_row_idx - 2][1:]
            comm_row2 = table[address_row_idx - 1][1:]
            
            # Combine community names
            for i in range(len(addresses)):
                comm1 = str(comm_row1[i]) if i < len(comm_row1) and comm_row1[i] else ''
                comm2 = str(comm_row2[i]) if i < len(comm_row2) and comm_row2[i] else ''
                community = f"{comm1} {comm2}".strip()
                communities.append(community)
        
        # Streets (1 row below addresses)
        if address_row_idx + 1 < len(table):
            streets = [str(cell) if cell else '' for cell in table[address_row_idx + 1][1:]]
        
        # Lots (2 rows below addresses)
        if address_row_idx + 2 < len(table):
            lot_row = table[address_row_idx + 2][1:]
            for cell in lot_row:
                if cell and 'Lots' in str(cell):
                    # Extract just the numbers
                    match = re.search(r'Lots\s*(\d+/\d+|\d+)', str(cell))
                    if match:
                        lots.append(match.group(1))
                else:
                    lots.append('')
        
        # Square footage (3 rows below addresses)
        if address_row_idx + 3 < len(table):
            sqft_row = table[address_row_idx + 3][1:]
            for cell in sqft_row:
                if cell and re.search(r'\d{4}', str(cell)):
                    # Extract first 4-digit number
                    match = re.search(r'(\d{4})', str(cell))
                    if match:
                        sqft.append(match.group(1))
                else:
                    sqft.append('')
        
        # Features (4 rows below addresses)
        if address_row_idx + 4 < len(table):
            features = [str(cell) if cell else '' for cell in table[address_row_idx + 4][1:]]
        
        # Create projects
        for i, addr in enumerate(addresses):
            if '/' in addr:
                addr_parts = addr.split('/')
                
                # Get corresponding data
                comm = communities[i] if i < len(communities) else ''
                street = streets[i] if i < len(streets) else ''
                lot = lots[i] if i < len(lots) else ''
                sq = sqft[i] if i < len(sqft) else ''
                feat = features[i] if i < len(features) else ''
                
                # Split lots if needed
                lot_parts = lot.split('/') if '/' in lot else [lot, lot]
                
                # Create project for each unit
                for j, unit_addr in enumerate(addr_parts):
                    project = {
                        'project_id': unit_addr.strip(),
                        'customer_name': '',
                        'customer_email': '',
                        'address': f"{unit_addr.strip()} {street.strip()}",
                        'community': comm.replace('Estates', 'Estates').replace('Landing', 'Landing').strip(),
                        'lots': lot_parts[j] if j < len(lot_parts) else lot_parts[0],
                        'sqft': sq,
                        'features': feat,
                        'current_phase': '',
                        'schedule': [],
                        'column_index': i,
                        'is_duplex': True,
                        'duplex_pair': addr
                    }
                    self.projects.append(project)
        
        # Parse schedule data (rows after features)
        schedule_start_row = address_row_idx + 5
        for row_idx in range(schedule_start_row, len(table)):
            row = table[row_idx]
            if row[0]:  # Date column
                date_match = re.search(r'(\d{1,2}-\w{3})', str(row[0]))
                if date_match:
                    date_str = date_match.group(1)
                    date_obj = self._parse_date(date_str)
                    
                    if date_obj:
                        # Process tasks for each column
                        for col_idx, task in enumerate(row[1:]):
                            if task and str(task).strip() and col_idx < len(addresses):
                                # Find projects with this column index
                                for project in self.projects:
                                    if project['column_index'] == col_idx:
                                        project['schedule'].append({
                                            'date': date_obj.strftime('%Y-%m-%d'),
                                            'task': str(task).strip(),
                                            'phase': self._categorize_task(str(task))
                                        })
    
    def _parse_using_spatial_analysis(self, page):
        """Fallback spatial analysis method with better column detection"""
        words = page.extract_words(keep_blank_chars=True, x_tolerance=3, y_tolerance=3)
        
        # Group words by y-coordinate
        rows = {}
        for word in words:
            y = round(word['top'])
            if y not in rows:
                rows[y] = []
            rows[y].append(word)
        
        sorted_rows = sorted(rows.items())
        
        # Find key rows by content
        address_row_y = None
        address_row_words = []
        
        for y, row_words in sorted_rows:
            row_text = ' '.join([w['text'] for w in row_words])
            # Look for the row with multiple addresses
            if row_text.count('/') >= 3 and re.search(r'\d{3,4}/\d{3,4}', row_text):
                address_row_y = y
                address_row_words = sorted(row_words, key=lambda w: w['x0'])
                break
        
        if not address_row_y:
            print("Could not find address row")
            return
        
        # Extract addresses and their x-positions
        addresses = []
        for word in address_row_words:
            if re.search(r'\d{3,4}/\d{3,4}', word['text']):
                addresses.append({
                    'text': word['text'],
                    'x': word['x0'],
                    'x_end': word['x0'] + word['width']
                })
        
        print(f"Found {len(addresses)} address columns")
        
        # Now extract data for each column based on x-position
        for col_idx, addr_info in enumerate(addresses):
            addr = addr_info['text']
            x_start = addr_info['x'] - 20  # Some tolerance
            x_end = addr_info['x_end'] + 50  # More tolerance on the right
            
            # Extract data for this column from each row
            community = self._extract_column_data(sorted_rows, address_row_y - 110, address_row_y - 100, x_start, x_end)
            street = self._extract_column_data(sorted_rows, address_row_y + 8, address_row_y + 12, x_start, x_end)
            lots = self._extract_column_data(sorted_rows, address_row_y + 18, address_row_y + 25, x_start, x_end)
            sqft = self._extract_column_data(sorted_rows, address_row_y + 30, address_row_y + 35, x_start, x_end)
            features = self._extract_column_data(sorted_rows, address_row_y + 40, address_row_y + 50, x_start, x_end)
            
            # Clean up extracted data
            community = community.replace('Estates', ' Estates').replace('Landing', ' Landing').strip()
            
            # Extract lot numbers
            lot_match = re.search(r'(\d+/\d+|\d+)', lots)
            lots_clean = lot_match.group(1) if lot_match else ''
            
            # Extract square footage
            sqft_match = re.search(r'(\d{4})', sqft)
            sqft_clean = sqft_match.group(1) if sqft_match else ''
            
            # Create projects for duplex
            if '/' in addr:
                addr_parts = addr.split('/')
                lot_parts = lots_clean.split('/') if '/' in lots_clean else [lots_clean, lots_clean]
                
                for j, unit_addr in enumerate(addr_parts):
                    project = {
                        'project_id': unit_addr.strip(),
                        'customer_name': '',
                        'customer_email': '',
                        'address': f"{unit_addr.strip()} {street.strip()}",
                        'community': community,
                        'lots': lot_parts[j] if j < len(lot_parts) else lot_parts[0],
                        'sqft': sqft_clean,
                        'features': features.strip(),
                        'current_phase': '',
                        'schedule': [],
                        'column_index': col_idx,
                        'x_start': x_start,
                        'x_end': x_end,
                        'is_duplex': True,
                        'duplex_pair': addr
                    }
                    self.projects.append(project)
        
        # Parse schedule data
        self._parse_schedule_spatial(sorted_rows, address_row_y + 60)
    
    def _extract_column_data(self, sorted_rows, y_start, y_end, x_start, x_end):
        """Extract data from a specific column and y-range"""
        result = []
        
        for y, row_words in sorted_rows:
            if y_start <= y <= y_end:
                for word in row_words:
                    if x_start <= word['x0'] <= x_end:
                        result.append(word['text'])
        
        return ' '.join(result)
    
    def _parse_schedule_spatial(self, sorted_rows, schedule_start_y):
        """Parse schedule data using spatial positioning"""
        for y, row_words in sorted_rows:
            if y < schedule_start_y:
                continue
            
            row_words.sort(key=lambda w: w['x0'])
            if not row_words:
                continue
            
            # Check for date
            first_words = ' '.join([w['text'] for w in row_words[:2]])
            date_match = re.search(r'(\d{1,2}-\w{3})', first_words)
            
            if date_match:
                date_str = date_match.group(1)
                date_obj = self._parse_date(date_str)
                
                if date_obj:
                    # Assign tasks to projects based on x position
                    for word in row_words[1:]:  # Skip date
                        # Find which project this belongs to
                        for project in self.projects:
                            if 'x_start' in project and project['x_start'] <= word['x0'] <= project['x_end']:
                                task = word['text'].strip()
                                if task and task not in ['', '-']:
                                    project['schedule'].append({
                                        'date': date_obj.strftime('%Y-%m-%d'),
                                        'task': task,
                                        'phase': self._categorize_task(task)
                                    })
                                break
    
    def _parse_continuation_page(self, page, page_num):
        """Parse continuation pages"""
        print(f"Parsing page {page_num}...")
        
        # Try table extraction first
        tables = page.extract_tables()
        
        if tables:
            for table in tables:
                for row in table:
                    if row[0]:  # Check first column for date
                        date_match = re.search(r'(\d{1,2}-\w{3})', str(row[0]))
                        if date_match:
                            date_str = date_match.group(1)
                            date_obj = self._parse_date(date_str)
                            
                            if date_obj:
                                # Add tasks to corresponding projects
                                for col_idx, task in enumerate(row[1:]):
                                    if task and str(task).strip():
                                        # Find projects with this column index
                                        for project in self.projects:
                                            if project['column_index'] == col_idx:
                                                project['schedule'].append({
                                                    'date': date_obj.strftime('%Y-%m-%d'),
                                                    'task': str(task).strip(),
                                                    'phase': self._categorize_task(str(task))
                                                })
    
    def _parse_date(self, date_str):
        """Parse date string to datetime object"""
        try:
            return datetime.strptime(f"{date_str}-2024", "%d-%b-%Y")
        except:
            return None
    
    def _categorize_task(self, task):
        """Categorize task into construction phase"""
        task_lower = task.lower()
        
        phase_keywords = {
            'foundation': ['foundation', 'concrete', 'slab', 'footing', 'foundy', 'pour slab', 'pour foundy'],
            'framing': ['frame', 'framing', 'lumber', 'walls', 'nailing'],
            'roofing': ['roof', 'shingle', 'roofing'],
            'electrical': ['electrical', 'elec', 'wire', 'electric'],
            'plumbing': ['plumb', 'pipe', 'water', 'finish plumbing'],
            'hvac': ['hvac', 'heat', 'air', 'duct'],
            'insulation': ['insulation', 'insulate'],
            'drywall': ['drywall', 'sheetrock', 'hang', 'tape', 'texture', 'double', 'flush', 'pva'],
            'flooring': ['floor', 'lvp', 'carpet', 'tile'],
            'painting': ['paint', 'primer'],
            'cabinets': ['cabinet', 'c-tops', 'b-splsh', 'countertop', 'cabinet install'],
            'finishing': ['finish', 'trim', 'detail', 'cleaning'],
            'inspection': ['inspection', 'final inspection', 'insp'],
            'move': ['move', 'clean/move']
        }
        
        for phase, keywords in phase_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                return phase
        
        return 'other'
    
    def save_parsed_data(self, output_path):
        """Save parsed data to JSON"""
        # Also create a summary
        print("\nProject Summary:")
        print(f"Total projects: {len(self.projects)}")
        
        # Group by community
        by_community = {}
        for proj in self.projects:
            comm = proj['community'] or 'Unknown'
            if comm not in by_community:
                by_community[comm] = []
            by_community[comm].append(proj)
        
        for comm, projs in by_community.items():
            print(f"\n{comm}:")
            for proj in projs:
                print(f"  - {proj['address']} (Lot {proj['lots']}): {len(proj['schedule'])} schedule items")
        
        with open(output_path, 'w') as f:
            json.dump({
                'projects': self.projects,
                'parsed_date': datetime.now().isoformat(),
                'summary': {
                    'total_projects': len(self.projects),
                    'by_community': {k: len(v) for k, v in by_community.items()}
                }
            }, f, indent=2)
        print(f"\nSaved parsed data to {output_path}")


# Test the parser
if __name__ == "__main__":
    pdf_path = r"G:\My Drive\Project Dashboard\Public\Master Schedule\Master Schedule.pdf"
    
    parser = ScheduleTableParser(pdf_path)
    projects = parser.parse()
    
    print(f"\nFound {len(projects)} projects:")
    
    # Display first 8 projects in detail
    for i, project in enumerate(projects[:8]):
        print(f"\nProject {i+1}:")
        print(f"  Address: {project['address']}")
        print(f"  Community: {project['community']}")
        print(f"  Lots: {project['lots']}")
        print(f"  Sqft: {project['sqft']} sq ft")
        print(f"  Features: {project['features']}")
        print(f"  Schedule items: {len(project['schedule'])}")
        if project['schedule']:
            print("  Sample tasks:")
            for task in project['schedule'][:3]:
                print(f"    {task['date']}: {task['task']} ({task['phase']})")
    
    # Save to file
    parser.save_parsed_data("parsed_schedule.json")