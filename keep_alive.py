#!/usr/bin/env python3
"""
Production Keep-Alive Script for Render
Sends periodic health check requests to prevent cold starts.

Usage:
    python keep_alive.py --url https://your-app.onrender.com --interval 600

Or set environment variables:
    KEEP_ALIVE_URL=https://your-app.onrender.com
    KEEP_ALIVE_INTERVAL=600
"""

import os
import sys
import time
import argparse
import logging
from typing import Optional
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class KeepAliveService:
    """Production-grade keep-alive service for Render deployments."""
    
    def __init__(self, url: str, interval: int = 600, timeout: int = 30):
        """
        Initialize keep-alive service.
        
        Args:
            url: Full URL to your Render service (e.g., https://app.onrender.com)
            interval: Ping interval in seconds (default: 600 = 10 minutes)
            timeout: Request timeout in seconds (default: 30)
        """
        self.url = url.rstrip('/')
        self.interval = interval
        self.timeout = timeout
        self.health_endpoint = f"{self.url}/health"
        self.running = False
        
        # Validate URL
        if not self.url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
    
    def ping(self) -> bool:
        """
        Send a health check ping to the service.
        
        Returns:
            True if ping successful, False otherwise
        """
        try:
            response = requests.get(
                self.health_endpoint,
                timeout=self.timeout,
                headers={'User-Agent': 'Render-KeepAlive/1.0'}
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Ping successful: {response.status_code}")
                return True
            else:
                logger.warning(f"⚠️  Ping returned status {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ Ping timeout after {self.timeout}s")
            return False
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Connection error - service may be down")
            return False
        except Exception as e:
            logger.error(f"❌ Ping failed: {str(e)}")
            return False
    
    def run(self):
        """Run keep-alive service continuously."""
        self.running = True
        logger.info(f"🚀 Starting keep-alive service")
        logger.info(f"   URL: {self.url}")
        logger.info(f"   Interval: {self.interval}s ({self.interval/60:.1f} minutes)")
        logger.info(f"   Health endpoint: {self.health_endpoint}")
        
        consecutive_failures = 0
        max_failures = 3
        
        while self.running:
            try:
                success = self.ping()
                
                if success:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    if consecutive_failures >= max_failures:
                        logger.error(
                            f"⚠️  {consecutive_failures} consecutive failures. "
                            f"Service may be experiencing issues."
                        )
                
                # Sleep until next ping
                logger.info(f"⏳ Next ping in {self.interval}s ({datetime.now()})")
                time.sleep(self.interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Shutting down keep-alive service...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error: {str(e)}")
                time.sleep(self.interval)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Keep-alive service for Render deployments"
    )
    parser.add_argument(
        '--url',
        type=str,
        default=os.getenv('KEEP_ALIVE_URL'),
        help='Render service URL (or set KEEP_ALIVE_URL env var)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=int(os.getenv('KEEP_ALIVE_INTERVAL', '600')),
        help='Ping interval in seconds (default: 600 = 10 minutes)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    
    args = parser.parse_args()
    
    if not args.url:
        logger.error("❌ URL required. Set --url or KEEP_ALIVE_URL environment variable.")
        sys.exit(1)
    
    service = KeepAliveService(
        url=args.url,
        interval=args.interval,
        timeout=args.timeout
    )
    
    service.run()


if __name__ == "__main__":
    main()
