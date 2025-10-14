#!/usr/bin/env python3
"""
Generate 25 additional test Excel files for comprehensive testing
"""

import pandas as pd
import numpy as np
import random
from pathlib import Path
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def generate_random_work_order_items(n_items=50):
    """Generate random work order items for testing"""
    # Sample descriptions
    descriptions = [
        "Excavation in ordinary soil including dressing of sides and bottom",
        "Providing and laying RCC M20 for foundation",
        "Brickwork in cement mortar 1:6",
        "Plastering in cement mortar 1:6",
        "Electrical wiring with copper cables",
        "Installation of LED lights",
        "Waterproofing treatment with bitumen",
        "Painting with emulsion paint",
        "Flooring with vitrified tiles",
        "Door frame installation",
        "Window frame installation",
        "Roofing with asbestos sheets",
        "Concrete mixing and pouring",
        "Steel reinforcement bars installation",
        "Sand filling and leveling",
        "Gravel base preparation",
        "Asphalt road construction",
        "Drainage pipe installation",
        "Septic tank construction",
        "Boundary wall construction",
        "Fencing with chain link",
        "Landscaping and gardening",
        "Tree planting and maintenance",
        "Irrigation system installation",
        "Solar panel installation",
        "Air conditioning unit installation",
        "Fire alarm system installation",
        "CCTV camera installation",
        "Network cabling",
        "Security door installation"
    ]
    
    # Sample units
    units = ["CuM", "SqM", "No", "Mtr", "Kg", "Ltr", "SqFt", "Rmt", "Nos"]
    
    # Generate items
    items = []
    for i in range(n_items):
        item = {
            "Item No.": f"{i+1:02d}",
            "Description": random.choice(descriptions),
            "Unit": random.choice(units),
            "Rate": round(random.uniform(50, 5000), 2),
            "Quantity Since": round(random.uniform(1, 100), 2)
        }
        items.append(item)
    
    return pd.DataFrame(items)

def generate_title_data(file_name):
    """Generate sample title data"""
    return {
        "Name of Work ;-": f"Test Infrastructure Project - {file_name}",
        "Agreement No.": f"AG-{random.randint(1000, 9999)}",
        "Reference to work order or Agreement :": f"WO-{random.randint(100, 999)}/{random.randint(2020, 2025)}",
        "Name of Contractor or supplier :": random.choice([
            "ABC Construction Ltd", 
            "XYZ Infrastructure Pvt Ltd", 
            "PQR Builders & Developers",
            "LMN Engineering Services"
        ]),
        "Bill Number": f"BILL-{random.randint(1000, 9999)}",
        "Running or Final": random.choice(["Running", "Final"]),
        "TENDER PREMIUM %": random.choice([0, 5, 10, 15]),
        "WORK ORDER AMOUNT RS.": random.randint(100000, 5000000),
        "Date of written order to commence work :": f"{random.randint(1, 28):02d}-{random.randint(1, 12):02d}-{random.randint(2020, 2024)}",
        "St. date of Start :": f"{random.randint(1, 28):02d}-{random.randint(1, 12):02d}-{random.randint(2020, 2024)}",
        "St. date of completion :": f"{random.randint(1, 28):02d}-{random.randint(1, 12):02d}-{random.randint(2021, 2025)}",
        "Date of actual completion of work :": f"{random.randint(1, 28):02d}-{random.randint(1, 12):02d}-{random.randint(2021, 2025)}",
        "Date of measurement :": f"{random.randint(1, 28):02d}-{random.randint(1, 12):02d}-{random.randint(2021, 2025)}"
    }

def create_excel_file(file_path, title_data, work_order_data):
    """Create an Excel file with the required sheets"""
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        # Title sheet
        title_df = pd.DataFrame(list(title_data.items()), columns=['Key', 'Value'])
        title_df.to_excel(writer, sheet_name='Title', index=False)
        
        # Work Order sheet
        work_order_data.to_excel(writer, sheet_name='Work Order', index=False)
        
        # Bill Quantity sheet (empty for now)
        bill_qty_df = pd.DataFrame(columns=['Item No.', 'Description', 'Unit', 'Quantity', 'Rate', 'Amount'])
        bill_qty_df.to_excel(writer, sheet_name='Bill Quantity', index=False)

def main():
    """Generate 25 additional test files"""
    print("Generating 25 additional test Excel files...")
    
    # Create directory if it doesn't exist
    input_dir = Path("INPUT_FILES")
    input_dir.mkdir(exist_ok=True)
    
    # Generate 25 files
    for i in range(1, 26):
        file_name = f"generated_test_file_{i:02d}.xlsx"
        file_path = input_dir / file_name
        
        print(f"Creating {file_name}...")
        
        # Generate data
        title_data = generate_title_data(file_name)
        work_order_data = generate_random_work_order_items(random.randint(20, 100))
        
        # Create Excel file
        create_excel_file(file_path, title_data, work_order_data)
        
        print(f"  ✓ Created with {len(work_order_data)} work items")
    
    print(f"\n✅ Successfully generated 25 additional test files in {input_dir}")

if __name__ == "__main__":
    main()