#!/usr/bin/env python3
"""
Test script for APNIC parser and CIDR generation
"""

import json
import tempfile
import os
from parse_apnic_data import APNICParser
from generate_cidr_lists import generate_cidr_list, validate_cidr, ip_to_sort_key

def test_sample_data():
    """Test with sample APNIC data"""
    
    # Sample APNIC data
    sample_data = """# APNIC|CN|ipv4|1.0.1.0|256|20110414|allocated
# APNIC|CN|ipv4|1.0.2.0|512|20110414|allocated
# APNIC|US|ipv4|8.8.8.0|256|19920301|allocated
# APNIC|JP|ipv6|2001:200::|32|19990801|allocated
# APNIC|CN|ipv6|2001:db8::|32|20010101|allocated
# APNIC|AU|asn|1221|1|19930901|allocated
apnic|CN|ipv4|1.0.1.0|256|20110414|allocated
apnic|CN|ipv4|1.0.2.0|512|20110414|allocated
apnic|US|ipv4|8.8.8.0|256|19920301|allocated
apnic|JP|ipv6|2001:200::|32|19990801|allocated
apnic|CN|ipv6|2001:db8::|32|20010101|allocated
apnic|AU|asn|1221|1|19930901|allocated"""
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create parser instance
        parser = APNICParser()
        parser.output_dir = temp_dir
        
        # Parse sample data
        print("Testing data parsing...")
        parsed_data = parser.parse_data(sample_data)
        
        # Print results
        print(f"IPv4 entries: {len(parsed_data['ipv4'])}")
        print(f"IPv6 entries: {len(parsed_data['ipv6'])}")
        print(f"ASN entries: {len(parsed_data['asn'])}")
        
        # Test CIDR generation
        print("\nTesting CIDR generation...")
        ipv4_cidr = generate_cidr_list(parsed_data, 'ipv4')
        ipv6_cidr = generate_cidr_list(parsed_data, 'ipv6')
        
        print(f"IPv4 CIDR entries: {len(ipv4_cidr)}")
        for cidr in ipv4_cidr:
            print(f"  {cidr}")
            
        print(f"IPv6 CIDR entries: {len(ipv6_cidr)}")
        for cidr in ipv6_cidr:
            print(f"  {cidr}")
        
        # Test validation
        print("\nTesting CIDR validation...")
        test_cidrs = [
            "1.0.1.0/24",
            "2001:db8::/32",
            "invalid-cidr",
            "1.2.3.4/33",  # Invalid prefix length
            "2001:db8::/129"  # Invalid IPv6 prefix length
        ]
        
        for cidr in test_cidrs:
            is_valid = validate_cidr(cidr)
            print(f"  {cidr}: {'✓' if is_valid else '✗'}")
        
        # Test sorting
        print("\nTesting IP sorting...")
        test_ips = [
            "1.0.1.0/24",
            "8.8.8.0/24",
            "2001:200::/32",
            "2001:db8::/32"
        ]
        
        sorted_ips = sorted(test_ips, key=ip_to_sort_key)
        print("Sorted IPs:")
        for ip in sorted_ips:
            print(f"  {ip}")
        
        print("\nAll tests completed successfully!")

if __name__ == "__main__":
    test_sample_data() 