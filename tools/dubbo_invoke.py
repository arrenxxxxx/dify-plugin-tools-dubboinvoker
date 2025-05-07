import json
import logging
import time
from collections.abc import Generator
from typing import Any, List, Dict, Optional, Union

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dubbo_utils import dubbo_client_utils


class DubboInvokeTool(Tool):
    """用于调用Dubbo服务的工具"""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """执行Dubbo服务调用"""
        
        # 获取参数
        registry_address = tool_parameters.get("registry_address", "")
        service_uri = tool_parameters.get("service_uri", "")
        interface = tool_parameters.get("interface", "")
        method = tool_parameters.get("method", "")
        
        # 获取参数相关字段
        input_params = tool_parameters.get("params", None)
        parameter_types = tool_parameters.get("parameter_types", None)
        parameter_values = tool_parameters.get("parameter_values", None)
        
        # 验证参数
        if not interface:
            yield self.create_text_message("错误: 必须提供接口名称")
            return
            
        if not method:
            yield self.create_text_message("错误: 必须提供方法名")
            return
            
        if not registry_address and not service_uri:
            yield self.create_text_message("错误: 必须提供注册中心地址或服务URI")
            return
            
        # 如果两者都提供了，使用服务URI
        if registry_address and service_uri:
            logging.warning("同时提供了注册中心地址和服务URI，将优先使用服务URI")
        
        try:
            # 计时开始
            start_time = time.time()
            
            # 处理参数
            param_objects, param_types = self._process_parameters(
                input_params, parameter_types, parameter_values
            )
            
            # 执行调用
            if service_uri:
                logging.info(f"开始调用服务: {service_uri}, {interface}.{method}, 参数: {param_objects}, 类型: {param_types}")
                result = dubbo_client_utils.invoke_service(
                    service_uri, interface, method, param_objects, param_types
                )
            else:
                logging.info(f"开始通过注册中心调用服务: {registry_address}, {interface}.{method}, 参数: {param_objects}, 类型: {param_types}")
                result = dubbo_client_utils.invoke_with_registry(
                    registry_address, interface, method, param_objects, param_types
                )
                
            # 计算耗时
            elapsed_time = time.time() - start_time
            logging.info(f"Dubbo服务调用完成，耗时: {elapsed_time:.2f}秒")
            
            # 判断调用是否成功
            if result.get("success", False):
                logging.info("调用成功")
                # 返回结果
                yield self.create_text_message(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                # 调用失败
                error_message = f"调用Dubbo服务失败: {result.get('message', '未知错误')}"
                logging.error(error_message)
                yield self.create_text_message(error_message)
            
        except Exception as e:
            error_message = f"调用Dubbo服务异常: {str(e)}"
            logging.error(error_message, exc_info=True)
            yield self.create_text_message(error_message)
    
    def _process_parameters(
        self, 
        legacy_params: Optional[str], 
        parameter_types: Optional[str], 
        parameter_values: Optional[str]
    ) -> tuple[Any, Optional[List[str]]]:
        """
        处理参数，支持新旧两种参数格式
        
        Args:
            legacy_params: 传统格式参数字符串 
            parameter_types: 参数类型字符串，逗号分隔
            parameter_values: 参数值的JSON字符串
            
        Returns:
            tuple: (处理后的参数对象, 参数类型列表)
        """
        # 检查是否使用新参数格式
        if parameter_types is not None and parameter_values is not None:
            return self._process_typed_parameters(parameter_types, parameter_values)
        
        # 使用传统参数格式
        return self._process_legacy_parameters(legacy_params), None
    
    def _process_typed_parameters(
        self, parameter_types: str, parameter_values: str
    ) -> tuple[Any, List[str]]:
        """
        处理带类型的参数
        
        Args:
            parameter_types: 参数类型字符串，逗号分隔
            parameter_values: 参数值的JSON字符串
            
        Returns:
            tuple: (处理后的参数对象, 参数类型列表)
        """
        # 解析参数类型列表
        types_list = [t.strip() for t in parameter_types.split(",") if t.strip()]
        
        # 解析参数值
        try:
            values = json.loads(parameter_values)
        except json.JSONDecodeError as e:
            logging.error(f"参数值JSON解析失败: {e}")
            raise ValueError(f"参数值必须是有效的JSON格式: {e}")
        
        # 根据类型数量确定如何处理参数值
        if len(types_list) == 1:
            # 单参数类型
            # 不管values是否为数组，都作为一个参数处理
            return values, types_list
        else:
            # 多参数类型
            if not isinstance(values, list):
                raise ValueError(f"多参数调用时，parameter_values必须是JSON数组")
            
            if len(values) != len(types_list):
                raise ValueError(f"参数值数量({len(values)})与参数类型数量({len(types_list)})不匹配")
            
            return values, types_list
    
    def _process_legacy_parameters(self, legacy_params: Optional[str]) -> Any:
        """
        处理传统格式的参数
        
        Args:
            legacy_params: 参数字符串
            
        Returns:
            处理后的参数对象
        """
        param_objects = None
        
        if legacy_params is not None:
            if legacy_params == "":
                # 空字符串情况
                param_objects = None
                logging.info("检测到空字符串参数")
            elif legacy_params.strip():
                params_str = legacy_params.strip()
                # 尝试解析为JSON
                try:
                    param_objects = json.loads(params_str)
                    logging.info(f"解析为JSON参数: {param_objects}")
                except json.JSONDecodeError:
                    # 不是有效的JSON，检查是否为带引号的字符串
                    if ((params_str.startswith('"') and params_str.endswith('"')) or 
                        (params_str.startswith("'") and params_str.endswith("'"))):
                        # 去掉外层引号
                        param_objects = params_str[1:-1]
                        logging.info(f"检测到字符串参数: {param_objects}")
                    else:
                        # 作为普通字符串处理
                        param_objects = params_str
                        logging.info(f"作为普通字符串处理: {param_objects}")
        
        return param_objects