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
from dubbo.codec.encoder import Object

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
                # 兼容旧方式调用 - 使用正确的 dubbo-python2 API
                if params is None:
                    result = dubbo_client.call(method)
                else:
                    # 对于兼容模式，params 作为 args 参数传递
                    result = dubbo_client.call(method, params)
            else:
                # 使用带类型的参数调用
                result = self._call_with_types(dubbo_client, method, params, param_types)
            
            self.logger.debug(f"Dubbo协议调用服务成功: {interface}.{method}")
            return {"success": True, "result": result, "message": "调用成功"}
            
        except Exception as e:
            self.logger.error(f"Dubbo协议调用服务异常: {str(e)}", exc_info=True)
            return {"success": False, "result": None, "message": f"调用异常: {str(e)}"}
    
    def _is_object_type(self, param_type: str) -> bool:
        """
        判断参数类型是否为对象类型
        
        Args:
            param_type: 参数类型字符串
            
        Returns:
            是否为对象类型
        """
        # 基本类型不是对象类型
        basic_types = {
            'java.lang.String', 'java.lang.Integer', 'java.lang.Long', 
            'java.lang.Float', 'java.lang.Double', 'java.lang.Boolean',
            'java.lang.Byte', 'java.lang.Short', 'java.lang.Character',
            'int', 'long', 'float', 'double', 'boolean', 'byte', 'short', 'char'
        }
        
        # 集合类型也不是普通对象类型
        collection_types = {
            'java.util.List', 'java.util.ArrayList', 'java.util.LinkedList',
            'java.util.Map', 'java.util.HashMap', 'java.util.LinkedHashMap',
            'java.util.Set', 'java.util.HashSet', 'java.util.LinkedHashSet'
        }
        
        # 去除泛型信息进行判断
        clean_type = param_type.split('<')[0].strip()
        
        return (clean_type not in basic_types and 
                clean_type not in collection_types and
                not clean_type.startswith('['))  # 数组类型
    
    def _is_map_type(self, param_type: str) -> bool:
        """
        判断参数类型是否为Map类型
        
        Args:
            param_type: 参数类型字符串
            
        Returns:
            是否为Map类型
        """
        clean_type = param_type.split('<')[0].strip()
        map_types = {
            'java.util.Map', 'java.util.HashMap', 'java.util.LinkedHashMap',
            'java.util.TreeMap', 'java.util.ConcurrentHashMap'
        }
        return clean_type in map_types
    
    def _is_list_type(self, param_type: str) -> bool:
        """
        判断参数类型是否为List类型
        
        Args:
            param_type: 参数类型字符串
            
        Returns:
            是否为List类型
        """
        clean_type = param_type.split('<')[0].strip()
        list_types = {
            'java.util.List', 'java.util.ArrayList', 'java.util.LinkedList',
            'java.util.Vector', 'java.util.Stack'
        }
        return clean_type in list_types
    
    def _convert_dict_to_object(self, value: dict, param_type: str) -> Object:
        """
        将 Python 字典转换为 dubbo Object，递归处理嵌套的字典和列表
        
        Args:
            value: Python 字典
            param_type: Java 类型名
            
        Returns:
            Object 实例
        """
        # 清理泛型信息，获取纯净的类名
        clean_type = param_type.split('<')[0].strip()
        
        # 创建 Object 实例
        obj = Object(clean_type)
        
        # 递归处理字典中的所有键值对
        for key, val in value.items():
            converted_val = self._convert_nested_value(val)
            obj[key] = converted_val
        
        self.logger.debug(f"转换字典为Object: {clean_type} -> {obj}")
        return obj
    
    def _convert_nested_value(self, value):
        """
        递归转换嵌套的值，将Python字典转换为Object，保持其他类型不变
        
        Args:
            value: 要转换的值
            
        Returns:
            转换后的值
        """
        if isinstance(value, dict):
            # 对于嵌套字典，转换为通用的Object类型
            return self._convert_dict_to_object(value, "java.lang.Object")
        elif isinstance(value, list):
            # 对于列表，递归处理每个元素
            return [self._convert_nested_value(item) for item in value]
        else:
            # 其他类型（基本类型）保持不变
            return value
    
    def _convert_list_to_arraylist(self, value: list, param_type: str) -> list:
        """
        保持Python列表不变，直接返回
        
        Args:
            value: Python 列表
            param_type: Java 类型名，如 "java.util.List<java.lang.String>"
            
        Returns:
            原始Python列表
        """
        # 确保列表元素是正确的类型
        if 'java.lang.String' in param_type:
            # 确保所有元素都是字符串类型
            converted_list = [str(item) for item in value]
        else:
            converted_list = value
        
        self.logger.debug(f"List参数保持原样: {param_type} -> 包含 {len(converted_list)} 个元素: {converted_list}")
        return converted_list
    
    def _convert_list_to_java_collection(self, value: list, param_type: str) -> Object:
        """
        将Python列表转换为Java Collection对象，使用特殊的序列化类型
        
        Args:
            value: Python列表
            param_type: Java List类型名（如java.util.List、java.util.ArrayList等）
            
        Returns:
            Object实例，代表Java Collection对象
        """
        # 清理泛型信息，获取纯净的类名
        clean_type = param_type.split('<')[0].strip()
        
        # 对于List接口，使用ArrayList作为实现类
        if clean_type == "java.util.List":
            clean_type = "java.util.ArrayList"
        
        # 创建一个标准的Java ArrayList对象
        collection_obj = Object(clean_type)
        
        # 使用标准的ArrayList字段结构
        # elementData是ArrayList内部存储数组的字段名
        collection_obj['elementData'] = value
        collection_obj['size'] = len(value)
        
        self.logger.debug(f"转换Python列表为Java Collection: {param_type} -> {clean_type}对象（{len(value)}个元素）")
        return collection_obj
    
    def _call_with_types(
        self, 
        client: DubboClient, 
        method: str, 
        params: Any, 
        param_types: Optional[List[str]]
    ) -> Any:
        """
        根据参数类型调用Dubbo服务
        
        Args:
            client: Dubbo客户端实例
            method: 方法名
            params: 参数值（单值或数组）
            param_types: 参数类型列表（可为None表示传统调用）
            
        Returns:
            调用结果
        """
        # 处理传统调用（无类型信息）
        if param_types is None:
            self.logger.debug("使用传统调用方式（无类型信息）")
            if params is None:
                return client.call(method)
            else:
                return client.call(method, params)
        
        # 处理无参数调用
        if len(param_types) == 0:
            return client.call(method)
        elif len(param_types) == 1:
            # 单参数调用
            converted_params = params
            
            # 如果参数是字典
            if isinstance(params, dict):
                if self._is_object_type(param_types[0]):
                    # 对象类型：转换为Object
                    converted_params = self._convert_dict_to_object(params, param_types[0])
                    self.logger.debug(f"单参数对象转换: {param_types[0]} -> {type(converted_params)}")
                elif self._is_map_type(param_types[0]):
                    # Map类型：也需要转换为Object，因为Hessian编码器不支持原生dict
                    converted_params = self._convert_dict_to_object(params, param_types[0])
                    self.logger.debug(f"单参数Map类型: {param_types[0]} -> 转换为Object")
            
            # 如果参数是列表 - 对于List类型，转换为Java Collection对象
            elif isinstance(params, list):
                if self._is_list_type(param_types[0]):
                    # List类型：转换为Java Collection对象以解决Hessian序列化问题
                    converted_params = self._convert_list_to_java_collection(params, param_types[0])
                    self.logger.debug(f"单参数List类型: {param_types[0]} -> 转换为Java Collection对象")
                else:
                    # 非List类型的列表，保持原样
                    converted_params = params
            
            return client.call(method, converted_params, param_types)
        else:
            # 多参数调用 - params 必须是列表
            if not isinstance(params, (list, tuple)):
                raise ValueError(f"多参数调用时，params必须是列表或元组类型")
            
            if len(params) != len(param_types):
                raise ValueError(f"参数数量({len(params)})与类型数量({len(param_types)})不匹配")
            
            # 转换参数列表中的对象类型参数
            converted_params = []
            for i, (param, param_type) in enumerate(zip(params, param_types)):
                if isinstance(param, dict):
                    if self._is_object_type(param_type):
                        # 对象类型：转换为Object
                        converted_param = self._convert_dict_to_object(param, param_type)
                        self.logger.debug(f"多参数对象转换[{i}]: {param_type} -> {type(converted_param)}")
                        converted_params.append(converted_param)
                    elif self._is_map_type(param_type):
                        # Map类型：也需要转换为Object，因为Hessian编码器不支持原生dict
                        converted_param = self._convert_dict_to_object(param, param_type)
                        self.logger.debug(f"多参数Map类型[{i}]: {param_type} -> 转换为Object")
                        converted_params.append(converted_param)
                    else:
                        converted_params.append(param)
                elif isinstance(param, list):
                    if self._is_list_type(param_type):
                        # List类型：转换为Java Collection对象以解决Hessian序列化问题
                        converted_param = self._convert_list_to_java_collection(param, param_type)
                        self.logger.debug(f"多参数List类型[{i}]: {param_type} -> 转换为Java Collection对象")
                        converted_params.append(converted_param)
                    else:
                        converted_params.append(param)
                else:
                    converted_params.append(param)
            
            return client.call(method, converted_params, param_types)


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
        # 检查service_uri是否为None
        if service_uri is None:
            raise ValueError("服务URI不能为空")
        
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