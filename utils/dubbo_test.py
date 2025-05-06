import logging
import sys
import json
import time
from dubbo_utils import dubbo_client_utils

# 配置日志
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_dubbo_invoke_with_registry(registry_address, interface, method, params=None):
    """
    测试通过注册中心调用Dubbo服务
    
    参数:
        registry_address: 注册中心地址，格式如 zookeeper://host:port、nacos://host:port
        interface: 接口名称
        method: 方法名
        params: JSON格式的参数字符串
    """
    logger.info(f"开始测试调用: {registry_address}, {interface}.{method}, 参数: {params}")
    
    try:
        # 调用服务
        result = dubbo_client_utils.invoke_with_registry(registry_address, interface, method, params)
        
        # 打印结果
        logger.info(f"调用结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        return result
    except Exception as e:
        logger.error(f"调用失败: {str(e)}", exc_info=True)
        return {"success": False, "result": None, "message": f"调用异常: {str(e)}"}

def test_dubbo_invoke_direct(service_address, interface, method, params=None):
    """
    测试直接调用Dubbo服务（不通过注册中心）
    
    参数:
        service_address: 服务地址，格式如 host:port
        interface: 接口名称
        method: 方法名
        params: JSON格式的参数字符串
    """
    logger.info(f"开始测试直接调用: {service_address}, {interface}.{method}, 参数: {params}")
    
    try:
        # 调用服务
        result = dubbo_client_utils.invoke_dubbo_service(service_address, interface, method, params)
        
        # 打印结果
        logger.info(f"调用结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        return result
    except Exception as e:
        logger.error(f"调用失败: {str(e)}", exc_info=True)
        return {"success": False, "result": None, "message": f"调用异常: {str(e)}"}

def test_dubbo_invoke_no_params(service_address, interface, method):
    """
    测试调用无参数的Dubbo方法
    
    参数:
        service_address: 服务地址，格式如 host:port
        interface: 接口名称
        method: 方法名
    """
    logger.info(f"开始测试调用无参数方法: {service_address}, {interface}.{method}")
    
    try:
        
        # 直接调用无参数方法
        start_time = time.time()
        result = dubbo_client_utils.invoke_dubbo_service(service_address, interface, method)
        elapsed_time = time.time() - start_time
        logger.info(f"调用成功，耗时: {elapsed_time:.2f}秒")
        
        logger.info(f"调用结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"调用失败: {str(e)}", exc_info=True)
        return {"success": False, "message": str(e)}

def test_dubbo_invoke_string_param(service_address, interface, method, string_param):
    """
    测试使用纯字符串参数调用Dubbo方法
    
    参数:
        service_address: 服务地址，格式如 host:port
        interface: 接口名称
        method: 方法名
        string_param: 字符串参数值
    """
    logger.info(f"开始测试调用(纯字符串参数): {service_address}, {interface}.{method}, 参数: '{string_param}'")
    
    try:
        # 直接传递字符串参数，不进行JSON转换
        logger.info(f"直接调用字符串参数: {string_param}")
        start_time = time.time()
        result = dubbo_client_utils.invoke_dubbo_service(service_address, interface, method, string_param)
        elapsed_time = time.time() - start_time
        
        logger.info(f"调用成功，耗时: {elapsed_time:.2f}秒")
        logger.info(f"调用结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"调用失败: {str(e)}", exc_info=True)
        return {"success": False, "result": None, "message": f"调用异常: {str(e)}"}

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) < 3:
        print("用法:")
        print("1. python dubbo_test.py <zk|direct> <address> <interface> <method> [params]")
        print("2. python dubbo_test.py noparam <address> <interface> <method>")
        print("3. python dubbo_test.py string <address> <interface> <method> <string_param>")
        print("\n示例:")
        print("- 使用ZooKeeper: python dubbo_test.py zk zookeeper://10.236.161.168:80 com.example.DemoService sayHello '{\"name\":\"John\"}'")
        print("- 直接调用: python dubbo_test.py direct 10.236.161.168:20880 com.example.DemoService sayHello '{\"name\":\"John\"}'")
        print("- 无参数调用: python dubbo_test.py noparam 10.236.161.168:20880 com.example.DemoService getCurrentDate")
        print("- 字符串参数: python dubbo_test.py string 10.236.161.168:20880 com.example.DemoService sayHello John")
        sys.exit(1)
    
    # 获取参数
    mode = sys.argv[1]
    
    if mode.lower() == "noparam":
        if len(sys.argv) < 5:
            print("无参数调用模式需要提供: <address> <interface> <method>")
            sys.exit(1)
        
        address = sys.argv[2]
        interface = sys.argv[3]
        method = sys.argv[4]
        test_dubbo_invoke_no_params(address, interface, method)
    elif mode.lower() == "string":
        if len(sys.argv) < 6:
            print("字符串参数调用模式需要提供: <address> <interface> <method> <string_param>")
            sys.exit(1)
            
        address = sys.argv[2]
        interface = sys.argv[3]
        method = sys.argv[4]
        string_param = sys.argv[5]
        test_dubbo_invoke_string_param(address, interface, method, string_param)
    else:
        if len(sys.argv) < 5:
            print("常规调用模式需要提供: <zk|direct> <address> <interface> <method> [params]")
            sys.exit(1)
            
        address = sys.argv[2]
        interface = sys.argv[3]
        method = sys.argv[4]
        input_params = sys.argv[5] if len(sys.argv) > 5 else None

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
                    param_objects = json.loads('{"name":"bob","age":18}')
                    logging.info(f"解析为JSON参数: {param_objects}")
                except json.JSONDecodeError as e:
                    logging.error(f"参数解析为JSON失败: {e}")
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
        
        # 执行测试
        if mode.lower() == "registry":
            test_dubbo_invoke_with_registry(address, interface, method, param_objects)
        elif mode.lower() == "direct":
            test_dubbo_invoke_direct(address, interface, method, param_objects)
        else:
            print(f"不支持的模式: {mode}，只支持 'zk'、'direct'、'noparam' 或 'string'")
            sys.exit(1) 