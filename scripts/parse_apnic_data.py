#!/usr/bin/env python3
"""
All RIR IP List Parser
Downloads from APNIC and parses delegated IP data from all RIRs
"""

import requests
import ipaddress
import json
import os
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

class APNICParser:
    def __init__(self):
        self.apnic_urls = ["https://ftp.apnic.net/stats/afrinic/delegated-afrinic-extended-latest",
                           "https://ftp.apnic.net/stats/apnic/delegated-apnic-extended-latest",
                           "https://ftp.apnic.net/stats/arin/delegated-arin-extended-latest",
                           "https://ftp.apnic.net/stats/lacnic/delegated-lacnic-extended-latest",
                           "https://ftp.apnic.net/stats/ripe-ncc/delegated-ripencc-extended-latest"]
        self.output_dir = "data"
        
    def download_data(self, rirs) -> str:
        """Download APNIC data file"""
        print("Downloading data...")
        data = ""
        if rirs:
            urls = []
            for rir in rirs:
                for url in self.apnic_urls:
                    if rir in url[url.rindex("/")+1:]:
                        urls.append(url)
                        break
        else:
            urls = self.apnic_urls
        for url in urls:
            print(url[url.rindex("/")+1:])
            response = requests.get(url)
            response.raise_for_status()
            data += response.text
        return data
        
    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single line of data"""
        if line.startswith('#') or not line.strip():
            return None
            
        parts = line.split('|')
        if len(parts) < 7:
            return None
            
        registry, country, type_, start, count, date, status = parts[:7]
        
        if type_ not in ['ipv4', 'ipv6', 'asn']:
            return None
            
        # Validate count
        try:
            count_int = int(count) if count.isdigit() else 0
            if count_int <= 0:
                return None
        except ValueError:
            return None
            
        return {
            'registry': registry,
            'country': country,
            'type': type_,
            'start': start,
            'count': count_int,
            'date': date,
            'status': status
        }
        
    def calculate_ip_range(self, start_ip: str, count: int, ip_type: str) -> Dict[str, str]:
        """Calculate IP address range and CIDR notation"""
        try:
            if ip_type == 'ipv4':
                start = ipaddress.IPv4Address(start_ip)
                end = ipaddress.IPv4Address(int(start) + count - 1)
                
                # Calculate CIDR for IPv4
                if start == end:
                    cidr = f"{start_ip}/{32}"
                else:
                    cidr = ",".join([str(ipn) for ipn in ipaddress.summarize_address_range(start, end)])
                # Note the above creates cidr lists like "192.168.0.0/23,192.168.2.0/24" for
                # cases where count is not a power of 2. This is correct behavior
            elif ip_type == 'ipv6':
                # Note that for IPv6 the count field is actually the mask - see APNIC documentation
                start = ipaddress.IPv6Address(start_ip)
                cidr = f"{start_ip}/{count}"
                # Calculate End address for IPv6
                net = ipaddress.IPv6Network(cidr)
                end = ipaddress.IPv6Address(int(start) + net.num_addresses - 1)
                
            else:
                return {'start': start_ip, 'end': start_ip, 'cidr': start_ip}
                
            return {
                'start': str(start),
                'end': str(end),
                'cidr': cidr
            }
        except Exception as e:
            print(f"Error calculating IP range for {start_ip} (count: {count}, type: {ip_type}): {e}")
            return {'start': start_ip, 'end': start_ip, 'cidr': start_ip}
            
    def validate_ip_data(self, entry: Dict[str, Any]) -> bool:
        """Validate IP data entry"""
        try:
            if entry['type'] in ['ipv4', 'ipv6']:
                # Validate start IP
                if entry['type'] == 'ipv4':
                    ipaddress.IPv4Address(entry['start'])
                else:
                    ipaddress.IPv6Address(entry['start'])
                    
                # Validate count
                if entry['count'] <= 0:
                    return False
                    
                # Validate CIDR if present
                if 'cidr' in entry:
                    ipaddress.ip_network(entry['cidr'], strict=False)
                    
            return True
        except Exception:
            return False
            
    def parse_data(self, data: str, type: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse the entire data file"""
        print("Parsing data...")

        types = [type]
        if len(types) == 0:
            types = ['ipv4', 'ipv6']
        results = {
            'ipv4': [],
            'ipv6': [],
            'asn': [],
            'metadata': {
                'last_updated': datetime.now().isoformat(),
                'source': self.apnic_urls
            }
        }
        
        lines = data.split('\n')
        total_lines = len(lines)
        processed_lines = 0
        skipped_lines = 0
        
        for line in lines:
            processed_lines += 1
            if processed_lines % 10000 == 0:
                print(f"Processed {processed_lines}/{total_lines} lines...")
                
            parsed = self.parse_line(line)
            if parsed:
                if parsed['type'] in types:
                    ip_range = self.calculate_ip_range(
                        parsed['start'], 
                        parsed['count'], 
                        parsed['type']
                    )
                    parsed.update(ip_range)
                    
                    # Validate the entry
                    if not self.validate_ip_data(parsed):
                        skipped_lines += 1
                        continue
                        
                    results[parsed['type']].append(parsed)
            else:
                skipped_lines += 1
                
        print(f"Parsing completed. Processed: {processed_lines}, Skipped: {skipped_lines}")
        return results
        
    def save_data(self, data: Dict[str, Any]):
        """Save parsed data"""
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Save complete data
        with open(f"{self.output_dir}/apnic_data.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        # Save IPv4 data grouped by country
        ipv4_by_country = {}
        for entry in data['ipv4']:
            country = entry['country']
            if country not in ipv4_by_country:
                ipv4_by_country[country] = []
            ipv4_by_country[country].append(entry)
            
        with open(f"{self.output_dir}/ipv4_by_country.json", 'w', encoding='utf-8') as f:
            json.dump(ipv4_by_country, f, indent=2, ensure_ascii=False)
            
        # Save IPv6 data grouped by country
        ipv6_by_country = {}
        for entry in data['ipv6']:
            country = entry['country']
            if country not in ipv6_by_country:
                ipv6_by_country[country] = []
            ipv6_by_country[country].append(entry)
            
        with open(f"{self.output_dir}/ipv6_by_country.json", 'w', encoding='utf-8') as f:
            json.dump(ipv6_by_country, f, indent=2, ensure_ascii=False)
            
        # Generate statistics
        stats = {
            'total_ipv4_entries': len(data['ipv4']),
            'total_ipv6_entries': len(data['ipv6']),
            'total_asn_entries': len(data['asn']),
            'countries_with_ipv4': len(set(entry['country'] for entry in data['ipv4'])),
            'countries_with_ipv6': len(set(entry['country'] for entry in data['ipv6'])),
            'last_updated': data['metadata']['last_updated']
        }
        
        with open(f"{self.output_dir}/stats.json", 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
            
        print(f"Data saved to {self.output_dir}/")
        print(f"Statistics: {stats}")
        
    def run(self,rirs,type):
        """Run the complete parsing workflow"""
        try:
            # Download data
            raw_data = self.download_data(rirs)
            
            # Parse data
            parsed_data = self.parse_data(raw_data,type)
            
            # Save data
            self.save_data(parsed_data)
            
            print("APNIC data processing completed successfully!")
            
        except Exception as e:
            print(f"Error processing APNIC data: {e}")
            raise

if __name__ == "__main__":
    parser = APNICParser()
    argparser = argparse.ArgumentParser(description='PhishSTOP v0.3')
    argparser.add_argument('--dir', action='store', help='Output director (default ./data )')
    argparser.add_argument('--type', action='store', default='', help='ipv4 or ipv6 - default both')
    argparser.add_argument('rirs', nargs="*", action='store', default='', help='Which RIR data to use - default all')

    args = argparser.parse_args()

    if args.dir:
        parser.output_dir = args.dir
    type=''
    if args.type:
        if args.type[-1] == '4':
            type = 'ipv4'
        elif args.type[-1] == '6':
            type = 'ipv6'

    parser.run( args.rirs, type)