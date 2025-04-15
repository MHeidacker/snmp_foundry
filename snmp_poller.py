#!/usr/bin/env python3

import os
import time
import json
import logging
from typing import Dict, List, Any
import requests
import backoff
from dotenv import load_dotenv
from pysnmp.hlapi import (
    SnmpEngine, CommunityData, UdpTransportTarget,
    ContextData, ObjectType, ObjectIdentity, getNextRequestObject,
    usmHMACMD5AuthProtocol, usmDESPrivProtocol
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SNMPPoller:
    def __init__(self):
        load_dotenv()
        
        # SNMP Configuration
        self.snmp_target = os.getenv('SNMP_TARGET', '127.0.0.1')
        self.snmp_port = int(os.getenv('SNMP_PORT', '1161'))
        self.snmp_community = os.getenv('SNMP_COMMUNITY', 'public')
        self.oids = os.getenv('OIDS', '').split(',')
        self.poll_interval = int(os.getenv('POLL_INTERVAL', '5'))
        
        # API Configuration
        self.api_endpoint = os.getenv('API_ENDPOINT')
        self.api_key = os.getenv('API_KEY')
        
        if not self.api_endpoint:
            raise ValueError("API_ENDPOINT must be specified in environment variables")
        
        if not self.oids:
            raise ValueError("OIDS must be specified in environment variables")

    def get_snmp_data(self, oid: str) -> Dict[str, Any]:
        """
        Poll a single OID and return the result.
        """
        try:
            iterator = getNextRequestObject(
                SnmpEngine(),
                CommunityData(self.snmp_community, mpModel=1),
                UdpTransportTarget((self.snmp_target, self.snmp_port)),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            
            error_indication, error_status, error_index, var_binds = next(iterator)
            
            if error_indication:
                logger.error(f"SNMP Error: {error_indication}")
                return None
                
            if error_status:
                logger.error(f"SNMP Error: {error_status}")
                return None
                
            for var_bind in var_binds:
                oid, value = var_bind
                return {
                    "timestamp": time.time(),
                    "source_ip": self.snmp_target,
                    "source_port": self.snmp_port,
                    "oid": str(oid),
                    "value": str(value),
                    "unit": "unknown"  # Could be enhanced with MIB parsing
                }
                
        except Exception as e:
            logger.error(f"Error polling OID {oid}: {str(e)}")
            return None

    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException),
        max_tries=3
    )
    def send_to_api(self, data: Dict[str, Any]) -> None:
        """
        Send data to the configured API endpoint with retry logic.
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}' if self.api_key else ''
        }
        
        response = requests.post(
            self.api_endpoint,
            json=data,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        logger.debug(f"Successfully sent data to API: {data}")

    def run_forever(self) -> None:
        """
        Main polling loop that runs indefinitely.
        """
        logger.info(f"Starting SNMP polling for target {self.snmp_target}:{self.snmp_port}")
        
        while True:
            start_time = time.time()
            
            for oid in self.oids:
                try:
                    data = self.get_snmp_data(oid)
                    if data:
                        self.send_to_api(data)
                except Exception as e:
                    logger.error(f"Error in polling loop for OID {oid}: {str(e)}")
            
            # Calculate sleep time to maintain consistent polling interval
            elapsed = time.time() - start_time
            sleep_time = max(0, self.poll_interval - elapsed)
            time.sleep(sleep_time)

def main():
    try:
        poller = SNMPPoller()
        poller.run_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down SNMP poller...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 