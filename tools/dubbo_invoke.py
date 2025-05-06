import json
import logging
import time
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dubbo_utils import dubbo_client_utils


class DubboInvokeTool(Tool):
    """用于调用Dubbo服务的工具"""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """执行Dubbo服务调用"""
        
        # 获取参数
        registry_address = tool_parameters.get("registry_address", "")
        service_address = tool_parameters.get("service_address", "")
        interface = tool_parameters.get("interface", "")
        method = tool_parameters.get("method", "")
        input_params = tool_parameters.get("params", None)
        
        # 验证参数
        if not interface:
            yield self.create_text_message("错误: 必须提供接口名称")
            return
            
        if not method:
            yield self.create_text_message("错误: 必须提供方法名")
            return
            
        if not registry_address and not service_address:
            yield self.create_text_message("错误: 必须提供注册中心地址或服务地址")
            return
            
        # 如果两者都提供了，使用服务地址
        if registry_address and service_address:
            logging.warning("同时提供了注册中心地址和服务地址，将优先使用服务地址")
        
        try:
            # 计时开始
            start_time = time.time()
            
            # 参数处理
            param_objects = None
            
            if input_params is not None:
                if input_params == "":
                    # 空字符串情况
                    param_objects = None
                    logging.info("检测到空字符串参数")
                elif input_params.strip():
                    params_str = input_params.strip()
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
            
            # 执行调用
            if service_address:
                logging.info(f"开始调用服务: {service_address}, {interface}.{method}, 参数: {param_objects}")
                result = dubbo_client_utils.invoke_dubbo_service(service_address, interface, method, param_objects)
            else:
                logging.info(f"开始通过注册中心调用服务: {registry_address}, {interface}.{method}, 参数: {param_objects}")
                result = dubbo_client_utils.invoke_with_registry(registry_address, interface, method, param_objects)
                
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