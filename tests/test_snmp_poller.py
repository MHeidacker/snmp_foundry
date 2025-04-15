import os
import pytest
from unittest.mock import patch, MagicMock
from snmp_poller import SNMPPoller

@pytest.fixture
def mock_env_vars():
    """Set up test environment variables"""
    os.environ['SNMP_TARGET'] = '127.0.0.1'
    os.environ['SNMP_PORT'] = '1161'
    os.environ['SNMP_COMMUNITY'] = 'public'
    os.environ['OIDS'] = '1.3.6.1.2.1.1.1.0'
    os.environ['POLL_INTERVAL'] = '5'
    os.environ['API_ENDPOINT'] = 'http://example.com/api'
    yield
    # Clean up
    for key in ['SNMP_TARGET', 'SNMP_PORT', 'SNMP_COMMUNITY', 'OIDS', 'POLL_INTERVAL', 'API_ENDPOINT']:
        os.environ.pop(key, None)

def test_snmp_poller_init(mock_env_vars):
    """Test SNMPPoller initialization with environment variables"""
    poller = SNMPPoller()
    assert poller.snmp_target == '127.0.0.1'
    assert poller.snmp_port == 1161
    assert poller.snmp_community == 'public'
    assert poller.oids == ['1.3.6.1.2.1.1.1.0']
    assert poller.poll_interval == 5
    assert poller.api_endpoint == 'http://example.com/api'

@patch('snmp_poller.getNextRequestObject')
def test_get_snmp_data(mock_get_next, mock_env_vars):
    """Test SNMP data retrieval"""
    # Mock SNMP response
    mock_var_bind = MagicMock()
    mock_var_bind.__iter__.return_value = [('1.3.6.1.2.1.1.1.0', 'Test System')]
    mock_iterator = MagicMock()
    mock_iterator.__next__.return_value = (None, None, None, [mock_var_bind])
    mock_get_next.return_value = mock_iterator

    poller = SNMPPoller()
    data = poller.get_snmp_data('1.3.6.1.2.1.1.1.0')

    assert data is not None
    assert data['source_ip'] == '127.0.0.1'
    assert data['source_port'] == 1161
    assert 'timestamp' in data
    assert data['value'] == 'Test System'

@patch('requests.post')
def test_send_to_api(mock_post, mock_env_vars):
    """Test API data forwarding"""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    poller = SNMPPoller()
    test_data = {
        'timestamp': 1234567890,
        'source_ip': '127.0.0.1',
        'source_port': 1161,
        'oid': '1.3.6.1.2.1.1.1.0',
        'value': 'Test System',
        'unit': 'unknown'
    }

    # Should not raise any exceptions
    poller.send_to_api(test_data)
    
    mock_post.assert_called_once_with(
        'http://example.com/api',
        json=test_data,
        headers={'Content-Type': 'application/json', 'Authorization': ''},
        timeout=10
    ) 