# SNMP Data Generator and API Forwarder

A Python-based SNMP polling and forwarding system that continuously collects SNMP data from a local SNMP simulator (snmpsim) and forwards it to a configurable API endpoint.

## Features

- Polls SNMP data using SNMPv2c
- Configurable OIDs and polling intervals
- Forwards data to REST API endpoints
- Automatic retries with exponential backoff
- Environment-based configuration
- Detailed logging
- Continuous Integration/Deployment with GitHub Actions
- Automated testing and code quality checks

## Prerequisites

- Python 3.7 or higher
- Running SNMP simulator (snmpsim) instance
- API endpoint to receive the data

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/snmp_foundry.git
cd snmp_foundry
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

Configure the following environment variables in your `.env` file:

- `SNMP_TARGET`: SNMP agent IP address (default: 127.0.0.1)
- `SNMP_PORT`: SNMP agent port (default: 1161)
- `SNMP_COMMUNITY`: SNMP community string (default: public)
- `OIDS`: Comma-separated list of OIDs to poll
- `POLL_INTERVAL`: Polling interval in seconds (default: 5)
- `API_ENDPOINT`: Target API endpoint URL
- `API_KEY`: API authentication key (optional)

## Usage

1. Start the SNMP poller:
```bash
python snmp_poller.py
```

2. The script will continuously:
   - Poll configured OIDs from the SNMP agent
   - Format the data as JSON
   - Forward to the specified API endpoint
   - Retry on failures with exponential backoff

## Data Format

The forwarded JSON payload format:

```json
{
  "timestamp": 1713188847.115,
  "source_ip": "127.0.0.1",
  "source_port": 1161,
  "oid": "1.3.6.1.2.1.2.2.1.10.1",
  "value": "1294824",
  "unit": "unknown"
}
```

## CI/CD Pipeline

The project includes a GitHub Actions workflow that:

1. Runs on every push to main and pull requests
2. Tests against Python 3.7, 3.8, 3.9, and 3.10
3. Performs the following checks:
   - Linting with flake8
   - Type checking with mypy
   - Unit tests with pytest
   - Code coverage reporting
4. Creates deployment artifacts on successful merge to main

### Running Tests Locally

To run the same checks as the CI pipeline:

```bash
# Install test dependencies
pip install pytest pytest-cov flake8 mypy

# Run linting
flake8 .

# Run type checking
mypy snmp_poller.py

# Run tests with coverage
pytest tests/ --cov=.
```

## Error Handling

- SNMP polling errors are logged and skipped
- API forwarding failures trigger automatic retries
- All errors are logged with timestamps and details

## License

This project is licensed under the MIT License - see the LICENSE file for details.