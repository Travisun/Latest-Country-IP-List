# APNIC IP List

This project automatically downloads and parses APNIC (Asia Pacific Network Information Centre) IP address allocation data.

## Features

- Automatically downloads the latest IP allocation data from APNIC's official FTP server
- Parses IPv4, IPv6, and ASN allocation records
- Groups data by country/region
- Calculates IP address ranges and CIDR notation
- Generates statistics
- Supports GitHub Actions for automatic updates

## Data Source

Data is sourced from APNIC's official FTP server:
- URL: http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest
- Update frequency: Daily
- Format: Text file with `|` delimiter

## Output Files

Parsed data is saved in the `data/` directory:

### JSON Format Data
- `apnic_data.json` - Complete parsed data
- `ipv4_by_country.json` - IPv4 data grouped by country
- `ipv6_by_country.json` - IPv6 data grouped by country
- `stats.json` - Statistics

### CIDR Format Lists
- `cidr_lists/all_ipv4.txt` - CIDR list of all IPv4 addresses
- `cidr_lists/all_ipv6.txt` - CIDR list of all IPv6 addresses
- `cidr_lists/{country}_ipv4.txt` - CIDR list of IPv4 addresses for each country
- `cidr_lists/{country}_ipv6.txt` - CIDR list of IPv6 addresses for each country

## Data Format

Each record contains the following fields:

```json
{
  "registry": "apnic",
  "country": "US",
  "type": "ipv4",
  "start": "8.0.1.0",
  "count": 256,
  "date": "20010414",
  "status": "allocated",
  "end": "8.0.1.255",
  "cidr": "8.0.1.0/24"
}
```

## Automation

### GitHub Actions

The project is configured with GitHub Actions workflow that supports:

1. **Scheduled Updates**: Automatically runs at 2:00 AM daily
2. **Manual Trigger**: Can be manually triggered from the GitHub Actions page

### Local Execution

```bash
# Install dependencies
pip install -r requirements.txt

# Run parsing script
python scripts/parse_apnic_data.py

# Generate CIDR lists
python scripts/generate_cidr_lists.py

# Run tests
python scripts/test_parser.py
```

## License

This project follows APNIC's data usage terms. For APNIC data usage conditions, please refer to:
- http://www.apnic.net/db/rir-stats-format.html
- ftp://ftp.apnic.net/pub/apnic/stats/apnic/README.TXT

## Contributing

Issues and Pull Requests are welcome to improve this project. 