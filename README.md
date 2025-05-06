# Dubbo调用器 (Dubbo Invoker)

这是一个用于调用Dubbo服务的Dify插件。通过该插件，您可以直接连接Dubbo服务或通过ZooKeeper等注册中心发现并调用服务。

## 功能

- 支持通过ZooKeeper注册中心发现服务
- 支持直连方式调用Dubbo服务
- 每次使用时配置连接信息，无需预先授权
- 支持自定义参数传递
- 使用dubbo-python官方SDK调用服务，同时支持telnet方式作为备选

## 使用方法

### 配置参数

每次调用时需要提供以下配置信息：

1. **注册中心地址或服务地址**（二选一）
   - 注册中心地址格式：`zookeeper://host:port`（目前仅支持ZooKeeper）
   - 服务地址格式：`host:port`

2. **接口名称**（必填）
   - Dubbo服务接口的完整名称，例如：`com.example.DemoService`

3. **方法名称**（必填）
   - 要调用的服务方法名

4. **参数**（可选）
   - 方法调用的参数，以JSON字符串形式提供

### 使用示例

```python
# 通过ZooKeeper调用
result = dubbo_invoke(
    registry_address="zookeeper://127.0.0.1:2181",
    interface="com.example.DemoService",
    method="sayHello",
    params='{"message": "Hello, Dubbo!"}'
)

# 直连方式调用
result = dubbo_invoke(
    service_address="127.0.0.1:20880",
    interface="com.example.DemoService",
    method="sayHello",
    params='{"message": "Hello, Dubbo!"}'
)
```

## 底层实现

本插件使用了两种方式调用Dubbo服务：

1. **dubbo-python官方SDK**：默认使用官方SDK进行调用，支持Triple协议
2. **telnet命令行模式**：作为备选方案，当SDK调用失败时自动切换

## 注意事项

- 确保您有权限访问所配置的注册中心或服务地址
- 参数格式必须是有效的JSON字符串
- 目前仅支持ZooKeeper作为注册中心
- 服务调用使用Triple协议（基于gRPC的HTTP/2协议）

## 许可证

[Apache License 2.0](LICENSE) 