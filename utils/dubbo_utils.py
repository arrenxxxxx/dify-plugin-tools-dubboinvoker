import json
import logging
import re
import urllib.parse
from typing import Any, Dict, Optional, Tuple, Union
import random
import sys
import os
import time
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dubbo.client import DubboClient

from utils.registry_strategy import RegistryFactory

class DubboClientUtils:
    """Dubbo client util, call dubbo service"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def invoke_with_registry(
        self, 
        registry_address: str, 
        interface: str, 
        method: str, 
        params: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invoke Dubbo service through registry
        
        Parameters:
            registry_address: registry address, format: zookeeper://host:port or nacos://host:port
            interface: interface name
            method: method name
            params: JSON formatted parameter string
            
        Returns:
            call result
        """
        self.logger.debug(f"Invoke Dubbo service through registry: {registry_address}, {interface}, {method}, {params}")
        
        # Parse registry address
        registry_type, address = self._parse_registry_address(registry_address)
        
        try:
            # Create registry strategy using factory method
            registry_strategy = RegistryFactory.create_registry(registry_type)
            
            # Get provider address from registry
            provider_host = registry_strategy.get_provider(address, interface)
                
            self.logger.debug(f"Get provider from registry: {provider_host}")
            
            # Directly invoke using the obtained provider address
            return self.invoke_dubbo_service(provider_host, interface, method, params)
        except Exception as e:
            self.logger.error(f"Failed to get provider from registry: {str(e)}", exc_info=True)
            return {"success": False, "result": None, "message": f"Failed to get provider from registry: {str(e)}"}

    def invoke_dubbo_service(
        self, 
        service_address: str, 
        interface: str, 
        method: str, 
        params: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        invoke Dubbo service (not through registry)
        
        Parameters:
            service_address: service address, format: host:port
            interface: interface name
            method: method name
            params: JSON formatted parameter string
            
        Returns:
            call result
        """
        self.logger.debug(f"Invoke Dubbo service: {service_address}, {interface}, {method}, {params}")
        
        try:
            # Valid address
            try:
                host, port = service_address.split(":")
                port = int(port)
            except ValueError:
                raise ValueError(f"Service address format error: {service_address}, should be host:port format")
            
            # Create DubboClient
            dubbo_client = DubboClient(interface,version='', host=service_address)
            if (params == None):
                result = dubbo_client.call(method)
            else:
                result = dubbo_client.call(method, params)
            
            self.logger.debug(f"Directly invoke Dubbo service successfully: {interface}.{method}")
            return {"success": True, "result": result, "message": "Invoke successfully"}
        except Exception as e:
            self.logger.error(f"Directly invoke Dubbo service exception: {str(e)}", exc_info=True)
            return {"success": False, "result": None, "message": f"调用异常: {str(e)}"}

    def _parse_registry_address(self, registry_address: str) -> Tuple[str, str]:
        """解析注册中心地址，返回(类型, 地址)元组"""
        match = re.match(r'^([a-z]+)://(.+)$', registry_address)
        if not match:
            raise ValueError(f"注册中心地址格式错误: {registry_address}")
        
        registry_type = match.group(1)
        address = match.group(2)
        
        return registry_type, address

# 单例实例
dubbo_client_utils = DubboClientUtils() 