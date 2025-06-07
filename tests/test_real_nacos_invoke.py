#!/usr/bin/env python3
"""
真实Nacos连接和Dubbo服务调用测试
用于测试与真实的Nacos注册中心连接并调用HelloFacade服务
"""
import sys
import os
import json
import logging
import time
from typing import Generator

# 添加父目录到路径中，以便导入tools模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.dubbo_invoke import DubboInvokeTool

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_real_nacos.log', encoding='utf-8')
    ]
)

class SimpleMessage:
    """简化的消息类，用于测试"""
    def __init__(self, message: str):
        self.message = message

class RealDubboInvokeTool(DubboInvokeTool):
    """真实的DubboInvokeTool，用于真实调用"""
    def __init__(self):
        pass
    
    def create_text_message(self, text: str) -> SimpleMessage:
        """创建简单的文本消息"""
        return SimpleMessage(text)

class RealNacosTest:
    """真实Nacos连接测试类"""
    
    def __init__(self):
        self.tool = RealDubboInvokeTool()
        self.nacos_registry = "nacos://192.168.3.111:8848"
        self.interface_name = "io.arrenxxxxx.dubbotesthub.api.HelloFacade"
        self.logger = logging.getLogger(__name__)
    
    def test_connection(self):
        """测试注册中心连接"""
        print("=" * 80)
        print("测试Nacos注册中心连接")
        print("=" * 80)
        print(f"注册中心地址: {self.nacos_registry}")
        print(f"接口名称: {self.interface_name}")
        print()
        
        try:
            # 尝试简单的无参数调用来测试连接
            tool_parameters = {
                "registry_address": self.nacos_registry,
                "interface": self.interface_name,
                "method": "sayHello"
            }
            
            print("📡 正在连接Nacos注册中心...")
            start_time = time.time()
            
            result_generator = self.tool._invoke(tool_parameters)
            messages = list(result_generator)
            
            elapsed_time = time.time() - start_time
            
            if messages and len(messages) > 0:
                message = messages[0].message
                print(f"⏱️  调用耗时: {elapsed_time:.2f}秒")
                print()
                
                # 尝试解析为JSON结果
                try:
                    result = json.loads(message)
                    if result.get("success", False):
                        print("✅ 连接成功！")
                        print(f"调用结果: {result['result']}")
                        return True
                    else:
                        print("❌ 调用失败")
                        print(f"错误信息: {result.get('message', '未知错误')}")
                        return False
                except json.JSONDecodeError:
                    # 不是JSON格式，可能是错误消息
                    print("❌ 连接失败")
                    print(f"错误信息: {message}")
                    return False
            else:
                print("❌ 没有收到响应")
                return False
                
        except Exception as e:
            print(f"❌ 连接异常: {str(e)}")
            self.logger.error(f"连接测试异常: {str(e)}", exc_info=True)
            return False
    
    def test_say_hello_no_params(self):
        """测试sayHello()无参数方法"""
        print("\n" + "=" * 60)
        print("测试 sayHello() - 无参数调用")
        print("=" * 60)
        
        tool_parameters = {
            "registry_address": self.nacos_registry,
            "interface": self.interface_name,
            "method": "sayHello"
        }
        
        return self._execute_test("sayHello()", tool_parameters)
    
    def test_say_hello_with_string(self):
        """测试sayHello(String name)方法"""
        print("\n" + "=" * 60)
        print("测试 sayHello(String name) - 字符串参数调用")
        print("=" * 60)
        
        tool_parameters = {
            "registry_address": self.nacos_registry,
            "interface": self.interface_name,
            "method": "sayHello",
            "parameter_types": "java.lang.String",
            "parameter_values": '"张三"'
        }
        
        return self._execute_test("sayHello(String)", tool_parameters)
    
    def test_say_hello_with_object(self):
        """测试sayHello(HelloRequest request)方法"""
        print("\n" + "=" * 60)
        print("测试 sayHello(HelloRequest request) - 对象参数调用")
        print("=" * 60)
        
        # 根据Java类定义创建正确的HelloRequest对象
        # Java类字段: name(String), age(Integer), message(String)
        hello_request = {
            "name": "lisi",
            "age": 25,
            "message": "hello"
        }
        
        tool_parameters = {
            "registry_address": self.nacos_registry,
            "interface": self.interface_name,
            "method": "sayHello",
            "parameter_types": "io.arrenxxxxx.dubbotesthub.api.HelloRequest",
            "parameter_values": json.dumps(hello_request)
        }
        
        return self._execute_test("sayHello(HelloRequest)", tool_parameters)
    
    def test_say_hello_list(self):
        """测试sayHelloList(List<String> names)方法"""
        print("\n" + "=" * 60)
        print("测试 sayHelloList(List<String> names) - 列表参数调用")
        print("=" * 60)
        
        names_list = ["lisi", "zhangsan", "wangwu"]
        
        tool_parameters = {
            "registry_address": self.nacos_registry,
            "interface": self.interface_name,
            "method": "sayHelloList",
            "parameter_types": "java.util.List<java.lang.String>",
            "parameter_values": json.dumps(names_list)
        }
        
        return self._execute_test("sayHelloList(List<String>)", tool_parameters)
    
    def test_say_hello_map(self):
        """测试sayHelloMap(Map<String, Object> paramMap)方法"""
        print("\n" + "=" * 60)
        print("测试 sayHelloMap(Map<String,Object> paramMap) - Map参数调用")
        print("=" * 60)
        
        param_map = {
            "user": "admin",
            "language": "zh-CN",
            "preferences": {
                "theme": "dark",
                "notifications": True
            }
        }
        
        tool_parameters = {
            "registry_address": self.nacos_registry,
            "interface": self.interface_name,
            "method": "sayHelloMap",
            "parameter_types": "java.util.Map<java.lang.String,java.lang.Object>",
            "parameter_values": json.dumps(param_map)
        }
        
        return self._execute_test("sayHelloMap(Map<String,Object>)", tool_parameters)
    
    def test_say_hello_list_object(self):
        """测试sayHelloListObject(List<HelloRequest> requests)方法"""
        print("\n" + "=" * 60)
        print("测试 sayHelloListObject(List<HelloRequest> requests) - 对象列表参数调用")
        print("=" * 60)
        
        # 创建HelloRequest对象列表
        requests_list = [
            {
                "name": "张三",
                "age": 25,
                "message": "第一个请求"
            },
            {
                "name": "李四",
                "age": 30,
                "message": "第二个请求"
            },
            {
                "name": "王五",
                "age": 28,
                "message": "第三个请求"
            }
        ]
        
        tool_parameters = {
            "registry_address": self.nacos_registry,
            "interface": self.interface_name,
            "method": "sayHelloListObject",
            "parameter_types": "java.util.List<io.arrenxxxxx.dubbotesthub.api.HelloRequest>",
            "parameter_values": json.dumps(requests_list)
        }
        
        return self._execute_test("sayHelloListObject(List<HelloRequest>)", tool_parameters)
    
    def test_say_hello_multiple_params(self):
        """测试sayHello(String name, Integer age, String message)方法"""
        print("\n" + "=" * 60)
        print("测试 sayHello(String, Integer, String) - 多参数调用")
        print("=" * 60)
        
        # 多参数调用，参数必须是JSON数组格式
        parameters_array = ["测试用户", 25, "多参数测试消息"]
        tool_parameters = {
            "registry_address": self.nacos_registry,
            "interface": self.interface_name,
            "method": "sayHello",
            "parameter_types": "java.lang.String,java.lang.Integer,java.lang.String",
            "parameter_values": json.dumps(parameters_array)
        }
        
        return self._execute_test("sayHello(String,Integer,String)", tool_parameters)
    
    def _execute_test(self, test_name: str, tool_parameters: dict) -> bool:
        """执行测试并返回结果"""
        try:
            print(f"📤 调用参数:")
            for key, value in tool_parameters.items():
                if key in ['parameter_values'] and len(str(value)) > 100:
                    print(f"  {key}: {str(value)[:100]}...")
                else:
                    print(f"  {key}: {value}")
            print()
            
            print("🚀 正在调用服务...")
            start_time = time.time()
            
            result_generator = self.tool._invoke(tool_parameters)
            messages = list(result_generator)
            
            elapsed_time = time.time() - start_time
            print(f"⏱️  调用耗时: {elapsed_time:.2f}秒")
            print()
            
            if messages and len(messages) > 0:
                message = messages[0].message
                
                # 尝试解析为JSON结果
                try:
                    result = json.loads(message)
                    if result.get("success", False):
                        print(f"✅ {test_name} 调用成功！")
                        print("📋 返回结果:")
                        print(json.dumps(result["result"], ensure_ascii=False, indent=2))
                        return True
                    else:
                        print(f"❌ {test_name} 调用失败")
                        print(f"错误信息: {result.get('message', '未知错误')}")
                        return False
                except json.JSONDecodeError:
                    # 不是JSON格式，可能是错误消息
                    print(f"❌ {test_name} 调用失败")
                    print(f"错误信息: {message}")
                    return False
            else:
                print(f"❌ {test_name} 没有收到响应")
                return False
                
        except Exception as e:
            print(f"❌ {test_name} 调用异常: {str(e)}")
            self.logger.error(f"{test_name} 调用异常: {str(e)}", exc_info=True)
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🔥 开始运行HelloFacade真实调用测试")
        print("=" * 80)
        print("⚠️  注意: 这是真实的Nacos连接测试，请确保:")
        print("   1. Nacos注册中心(192.168.3.111:8848)正在运行")
        print("   2. HelloFacade服务已注册到该注册中心")
        print("   3. 网络连接正常")
        print("=" * 80)
        
        # 首先测试连接
        if not self.test_connection():
            print("\n💥 连接测试失败，终止后续测试")
            return
        
        # 运行所有方法测试
        test_methods = [
            ("sayHello()", self.test_say_hello_no_params),
            ("sayHello(String)", self.test_say_hello_with_string),
            ("sayHello(HelloRequest)", self.test_say_hello_with_object),
            ("sayHelloList(List<String>)", self.test_say_hello_list),
            ("sayHelloMap(Map<String,Object>)", self.test_say_hello_map),
            ("sayHelloListObject(List<HelloRequest>)", self.test_say_hello_list_object),
            ("sayHello(String,Integer,String)", self.test_say_hello_multiple_params)
        ]
        
        results = {}
        for test_name, test_method in test_methods:
            try:
                results[test_name] = test_method()
            except Exception as e:
                print(f"❌ {test_name} 测试执行异常: {str(e)}")
                results[test_name] = False
        
        # 打印汇总结果
        self._print_summary(results)
    
    def _print_summary(self, results: dict):
        """打印测试结果汇总"""
        print("\n" + "=" * 80)
        print("🏁 测试结果汇总")
        print("=" * 80)
        
        total_tests = len(results)
        passed_tests = sum(1 for success in results.values() if success)
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"成功: {passed_tests}")
        print(f"失败: {failed_tests}")
        print()
        
        for test_name, success in results.items():
            status = "✅ 通过" if success else "❌ 失败"
            print(f"  {status} - {test_name}")
        
        if passed_tests == total_tests:
            print("\n🎉 所有测试都通过了！HelloFacade服务调用正常")
        else:
            print(f"\n⚠️  有 {failed_tests} 个测试失败，请检查:")
            print("   1. Nacos注册中心是否正常运行")
            print("   2. HelloFacade服务是否已正确注册")
            print("   3. 网络连接是否正常")
            print("   4. 方法签名是否匹配")
        
        print(f"\n📝 详细日志已保存到: test_real_nacos.log")


def main():
    """主函数"""
    print("🚀 HelloFacade真实Nacos连接测试")
    print("⚡ 这将执行真实的Dubbo服务调用")
    
    # # 提示用户确认
    # response = input("\n是否继续执行真实调用测试？(y/N): ").strip().lower()
    # if response not in ['y', 'yes']:
    #     print("取消测试")
    #     return
    
    # 运行测试
    test = RealNacosTest()
    test.run_all_tests()


if __name__ == "__main__":
    main() 