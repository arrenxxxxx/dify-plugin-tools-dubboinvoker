import json
import logging
import re
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple, Union
import random
import sys
import os
import time
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dubbo.client import DubboClient

from utils.registry_strategy import RegistryFactory

class ProtocolHandler:
    """协议处理基类，定义接口规范"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def invoke(
        self, 
        service_uri: str, 
        interface: str, 
        method: str, 
        params: Any, 
        param_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        调用服务方法
        
        Parameters:
            service_uri: 服务URI，包含协议、主机和端口
            interface: 接口名
            method: 方法名
            params: 参数
            param_types: 参数类型列表（可选）
            
        Returns:
            调用结果
        """
        raise NotImplementedError("子类必须实现此方法")


class DubboProtocolHandler(ProtocolHandler):
    """Dubbo原生协议（基于Hessian序列化）处理器"""
    
    def invoke(
        self, 
        service_uri: str, 
        interface: str, 
        method: str, 
        params: Any, 
        param_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        使用Dubbo原生协议调用服务
        
        Parameters:
            service_uri: Dubbo服务URI，格式: dubbo://host:port
            interface: 接口名
            method: 方法名
            params: 参数
            param_types: 参数类型列表（可选）
            
        Returns:
            调用结果
        """
        try:
            # 解析URI，提取host:port
            match = re.match(r'^(?:dubbo:\/\/)?([^\/]+)(?:\/.*)?$', service_uri)
            if not match:
                return {
                    "success": False, 
                    "result": None, 
                    "message": f"服务URI格式错误: {service_uri}, 应为dubbo://host:port或host:port"
                }
            
            host_port = match.group(1)
            
            # 验证host:port格式
            try:
                host, port = host_port.split(":")
                port = int(port)
            except ValueError:
                return {
                    "success": False, 
                    "result": None, 
                    "message": f"服务地址格式错误: {host_port}, 应为host:port格式"
                }
            
            # 创建DubboClient并调用服务
            dubbo_client = DubboClient(interface, version='', host=host_port)
            
            # 根据参数类型和参数值调用不同的方法
            if param_types is None:
                # 兼容旧方式调用
                if params is None:
                    result = dubbo_client.call(method)
                else:
                    result = dubbo_client.call(method, params)
            else:
                # 使用带类型的参数调用
                result = self._call_with_types(dubbo_client, method, params, param_types)
            
            self.logger.debug(f"Dubbo协议调用服务成功: {interface}.{method}")
            return {"success": True, "result": result, "message": "调用成功"}
            
        except Exception as e:
            self.logger.error(f"Dubbo协议调用服务异常: {str(e)}", exc_info=True)
            return {"success": False, "result": None, "message": f"调用异常: {str(e)}"}
    
    def _call_with_types(
        self, 
        client: DubboClient, 
        method: str, 
        params: Any, 
        param_types: List[str]
    ) -> Any:
        """
        根据参数类型调用Dubbo服务
        
        Args:
            client: Dubbo客户端实例
            method: 方法名
            params: 参数值（单值或数组）
            param_types: 参数类型列表
            
        Returns:
            调用结果
        """
        if len(param_types) == 1:
            # 单参数调用
            # 自动处理数组参数和单值参数
            if param_types[0].endswith("[]") and isinstance(params, list):
                # 数组参数
                return client.call(method, params, param_types)
            else:
                # 单值参数（包括对象）
                return client.call(method, params, param_types)
        else:
            # 多参数调用
            if not isinstance(params, list):
                raise ValueError(f"多参数调用时，params必须是列表类型")
            
            if len(params) != len(param_types):
                raise ValueError(f"参数数量({len(params)})与类型数量({len(param_types)})不匹配")
            
            return client.call(method, params, param_types)


class ProtocolFactory:
    """协议工厂，根据URI创建对应的协议处理器"""
    
    @staticmethod
    def create_protocol_handler(service_uri: str) -> ProtocolHandler:
        """
        创建协议处理器
        
        Parameters:
            service_uri: 服务URI，包含协议前缀
            
        Returns:
            协议处理器实例
        """
        # 如果没有指定协议，默认使用dubbo
        if "://" not in service_uri:
            service_uri = f"dubbo://{service_uri}"
        
        protocol = service_uri.split("://")[0].lower()
        
        if protocol == "dubbo":
            return DubboProtocolHandler()
        # 将来可以在这里添加其他协议处理器
        # elif protocol == "triple":
        #    return TripleProtocolHandler()
        # elif protocol == "rest":
        #    return RestProtocolHandler()
        else:
            raise ValueError(f"不支持的协议: {protocol}")


class DubboClientUtils:
    """Dubbo client util, call dubbo service"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def invoke_with_registry(
        self, 
        registry_address: str, 
        interface: str, 
        method: str, 
        params: Optional[Any] = None,
        param_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Invoke Dubbo service through registry
        
        Parameters:
            registry_address: registry address, format: zookeeper://host:port or nacos://host:port
            interface: interface name
            method: method name
            params: parameters
            param_types: parameter types (optional)
            
        Returns:
            call result
        """
        self.logger.debug(f"Invoke Dubbo service through registry: {registry_address}, {interface}, {method}, {params}, types={param_types}")
        
        # Parse registry address
        registry_type, address = self._parse_registry_address(registry_address)
        
        try:
            # Create registry strategy using factory method
            registry_strategy = RegistryFactory.create_registry(registry_type)
            
            # Get provider address from registry
            provider_uri = registry_strategy.get_provider(address, interface)
                
            self.logger.debug(f"Get provider from registry: {provider_uri}")
            
            # 使用获取到的提供者URI调用服务
            return self.invoke_service(provider_uri, interface, method, params, param_types)
        except Exception as e:
            self.logger.error(f"Failed to get provider from registry: {str(e)}", exc_info=True)
            return {"success": False, "result": None, "message": f"从注册中心获取服务提供者失败: {str(e)}"}

    def invoke_service(
        self, 
        service_uri: str, 
        interface: str, 
        method: str, 
        params: Optional[Any] = None,
        param_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        调用服务方法，支持多种协议
        
        Parameters:
            service_uri: 服务URI，包含协议前缀，如dubbo://host:port
            interface: 接口名
            method: 方法名
            params: 参数
            param_types: 参数类型列表（可选）
            
        Returns:
            调用结果
        """
        self.logger.debug(f"Invoke service: {service_uri}, {interface}.{method}, params: {params}, types={param_types}")
        
        try:
            # 创建协议处理器
            protocol_handler = ProtocolFactory.create_protocol_handler(service_uri)
            
            # 调用服务
            return protocol_handler.invoke(service_uri, interface, method, params, param_types)
        except Exception as e:
            self.logger.error(f"Service invocation exception: {str(e)}", exc_info=True)
            return {"success": False, "result": None, "message": f"调用服务异常: {str(e)}"}

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