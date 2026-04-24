"""
Auto port forwarding using UPnP - reads port from server.properties.
"""

import socket
import logging
from typing import Optional

try:
    from miniupnpc import UPnP
    HAS_MINIUPNPC = True
except ImportError:
    HAS_MINIUPNPC = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_server_port() -> int:
    """Get port from server.properties."""
    try:
        from server_properties import ServerProperties
        props = ServerProperties()
        return props.get_port()
    except:
        return 25565


class PortForwarder:
    """Automatic port forwarding using UPnP."""
    
    def __init__(self, port: int = None):
        if port is None:
            port = get_server_port()
        
        self.port = port
        self.protocol = "TCP"
        self.upnp: Optional[UPnP] = None
        self.external_ip: Optional[str] = None
    
    def discover(self) -> bool:
        """Discover UPnP devices."""
        if not HAS_MINIUPNPC:
            logger.warning("miniupnpc not installed, skipping port forwarding")
            return False
        
        try:
            self.upnp = UPnP()
            self.upnp.discover()
            self.upnp.selectigd()
            logger.info("UPnP device found: %s", self.upnp.lanaddr)
            return True
        except Exception as e:
            logger.warning("UPnP discovery failed: %s", e)
            return False
    
    def open_port(self, description: str = "MinecraftServer") -> bool:
        """Open port on router."""
        if not self.upnp and not self.discover():
            return False
        
        try:
            # First try to close existing mapping
            try:
                self.upnp.deleteportmapping(self.port, self.protocol)
            except:
                pass
            
            self.upnp.addportmapping(
                self.port,
                self.protocol,
                self.upnp.lanaddr,
                description
            )
            self.external_ip = self.upnp.externalipaddress()
            logger.info("Port %s/%s opened successfully", self.port, self.protocol)
            return True
        except Exception as e:
            logger.error("Failed to open port: %s", e)
            return False
    
    def close_port(self) -> bool:
        """Close port on router."""
        if not self.upnp:
            return False
        
        try:
            self.upnp.deleteportmapping(self.port, self.protocol)
            logger.info("Port %s closed", self.port)
            return True
        except Exception as e:
            logger.error("Failed to close port: %s", e)
            return False
    
    def get_external_ip(self) -> Optional[str]:
        """Get external IP address."""
        if not self.upnp and not self.discover():
            return None
        return self.upnp.externalipaddress() if self.upnp else None


def auto_forward() -> tuple[bool, Optional[str]]:
    """Helper function to automatically forward port from server.properties."""
    forwarder = PortForwarder()
    if forwarder.open_port():
        return True, forwarder.get_external_ip()
    return False, None