#!/usr/bin/env python3
"""
Generate CIDR lists from parsed APNIC data
"""

import json
import os
from typing import Dict, List

def load_data(data_file: str) -> Dict:
    """Load parsed data"""
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_cidr_list(data: Dict, ip_type: str = 'ipv4', country: str = None) -> List[str]:
    """Generate CIDR list"""
    cidr_list = []
    
    for entry in data[ip_type]:
        if country and entry['country'] != country:
            continue
            
        if 'cidr' in entry:
            cidr_list.append(entry['cidr'])
            
    return sorted(cidr_list, key=lambda x: tuple(int(n) for n in x.split('/')[0].split('.')))

def save_cidr_list(cidr_list: List[str], output_file: str):
    """Save CIDR list to file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for cidr in cidr_list:
            f.write(f"{cidr}\n")

def main():
    data_file = "data/apnic_data.json"
    
    if not os.path.exists(data_file):
        print(f"Data file {data_file} not found. Please run parse_apnic_data.py first.")
        return
        
    data = load_data(data_file)
    
    # Create output directory
    os.makedirs("data/cidr_lists", exist_ok=True)
    
    # Generate all IPv4 CIDR list
    all_ipv4_cidr = generate_cidr_list(data, 'ipv4')
    save_cidr_list(all_ipv4_cidr, "data/cidr_lists/all_ipv4.txt")
    print(f"Generated all IPv4 CIDR list: {len(all_ipv4_cidr)} entries")
    
    # Generate all IPv6 CIDR list
    all_ipv6_cidr = generate_cidr_list(data, 'ipv6')
    save_cidr_list(all_ipv6_cidr, "data/cidr_lists/all_ipv6.txt")
    print(f"Generated all IPv6 CIDR list: {len(all_ipv6_cidr)} entries")
    
    # Generate China IPv4 CIDR list
    cn_ipv4_cidr = generate_cidr_list(data, 'ipv4', 'CN')
    save_cidr_list(cn_ipv4_cidr, "data/cidr_lists/cn_ipv4.txt")
    print(f"Generated China IPv4 CIDR list: {len(cn_ipv4_cidr)} entries")
    
    # Generate China IPv6 CIDR list
    cn_ipv6_cidr = generate_cidr_list(data, 'ipv6', 'CN')
    save_cidr_list(cn_ipv6_cidr, "data/cidr_lists/cn_ipv6.txt")
    print(f"Generated China IPv6 CIDR list: {len(cn_ipv6_cidr)} entries")
    
    # Generate CIDR lists grouped by country
    countries_ipv4 = {}
    countries_ipv6 = {}
    
    for entry in data['ipv4']:
        country = entry['country']
        if country not in countries_ipv4:
            countries_ipv4[country] = []
        if 'cidr' in entry:
            countries_ipv4[country].append(entry['cidr'])
            
    for entry in data['ipv6']:
        country = entry['country']
        if country not in countries_ipv6:
            countries_ipv6[country] = []
        if 'cidr' in entry:
            countries_ipv6[country].append(entry['cidr'])
    
    # Save IPv4 list for each country
    for country, cidr_list in countries_ipv4.items():
        sorted_cidr = sorted(cidr_list, key=lambda x: tuple(int(n) for n in x.split('/')[0].split('.')))
        save_cidr_list(sorted_cidr, f"data/cidr_lists/{country.lower()}_ipv4.txt")
        
    # Save IPv6 list for each country
    for country, cidr_list in countries_ipv6.items():
        sorted_cidr = sorted(cidr_list, key=lambda x: x.split('/')[0])
        save_cidr_list(sorted_cidr, f"data/cidr_lists/{country.lower()}_ipv6.txt")
    
    print(f"Generated CIDR lists for {len(countries_ipv4)} countries (IPv4)")
    print(f"Generated CIDR lists for {len(countries_ipv6)} countries (IPv6)")
    print("All CIDR lists saved to data/cidr_lists/")

if __name__ == "__main__":
    main() 