import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.registry_strategy import RegistryFactory, ZookeeperRegistryStrategy, NacosRegistryStrategy

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("registry_test")

def test_zookeeper_registry():
    """测试ZooKeeper注册中心"""
    logger.info("=== 测试ZooKeeper注册中心 ===")
    
    # 使用工厂创建ZooKeeper注册中心策略
    registry_type = "zookeeper"
    registry = RegistryFactory.create_registry(registry_type)
    
    assert isinstance(registry, ZookeeperRegistryStrategy)
    logger.info(f"创建{registry_type}注册中心策略成功")
    
    # 测试连接和获取提供者
    try:
        zk_address = "localhost:2181"  # 请修改为实际的ZooKeeper地址
        interface = "com.example.DemoService"  # 请修改为实际的接口名称
        
        logger.info(f"尝试从ZooKeeper({zk_address})获取接口{interface}的提供者")
        provider = registry.get_provider(zk_address, interface)
        logger.info(f"成功获取到提供者: {provider}")
    except Exception as e:
        logger.error(f"测试ZooKeeper注册中心失败: {str(e)}")

def test_nacos_registry():
    """测试Nacos注册中心"""
    logger.info("=== 测试Nacos注册中心 ===")
    
    # 使用工厂创建Nacos注册中心策略
    registry_type = "nacos"
    try:
        registry = RegistryFactory.create_registry(registry_type)
        
        assert isinstance(registry, NacosRegistryStrategy)
        logger.info(f"创建{registry_type}注册中心策略成功")
        
        # 测试连接和获取提供者
        try:
            nacos_address = "localhost:8848"  # 请修改为实际的Nacos地址
            interface = "com.example.DemoService"  # 请修改为实际的接口名称
            
            logger.info(f"尝试从Nacos({nacos_address})获取接口{interface}的提供者")
            provider = registry.get_provider(nacos_address, interface)
            logger.info(f"成功获取到提供者: {provider}")
        except Exception as e:
            logger.error(f"测试Nacos注册中心失败: {str(e)}")
    except ImportError as e:
        logger.error(f"Nacos依赖未安装，测试跳过: {str(e)}")

def test_invalid_registry():
    """测试无效的注册中心类型"""
    logger.info("=== 测试无效的注册中心类型 ===")
    
    registry_type = "invalid"
    try:
        registry = RegistryFactory.create_registry(registry_type)
        logger.error("应该抛出异常，但没有")
    except ValueError as e:
        logger.info(f"预期的异常: {str(e)}")

if __name__ == "__main__":
    logger.info("开始测试注册中心策略")
    
    # 测试ZooKeeper注册中心
    test_zookeeper_registry()
    
    # 测试Nacos注册中心
    test_nacos_registry()
    
    # 测试无效的注册中心类型
    test_invalid_registry()
    
    logger.info("注册中心策略测试完成") 