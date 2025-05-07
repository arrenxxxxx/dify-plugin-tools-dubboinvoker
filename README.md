# Dubbo调用器 (Dubbo Invoker)

这是一个用于调用Dubbo服务的Dify插件。通过该插件，您可以直接连接Dubbo服务或通过ZooKeeper等注册中心发现并调用服务。

## 功能

- 支持通过ZooKeeper和Nacos注册中心发现服务
- 支持直连方式调用Dubbo服务
- 每次使用时配置连接信息，无需预先授权
- 支持自定义参数传递
- 支持参数类型精确指定（适用于复杂类型和多参数调用）
- 使用Dubbo原生协议（Hessian序列化）调用服务
- 支持telnet方式作为备选调用方式
- 可扩展的多协议支持框架（当前实现Dubbo原生协议）

## 使用方法

### 配置参数

每次调用时需要提供以下配置信息：

1. **注册中心地址或服务URI**（二选一）
   - 注册中心地址格式：`zookeeper://host:port`或`nacos://host:port`
   - 服务URI格式：`dubbo://host:port`（未来将支持更多协议）

2. **接口名称**（必填）
   - Dubbo服务接口的完整名称，例如：`com.example.DemoService`

3. **方法名称**（必填）
   - 要调用的服务方法名

4. **参数传递**（可选，两种方式二选一）
   - **传统方式**：使用`params`参数提供JSON字符串
   - **类型明确方式**：使用`parameter_types`和`parameter_values`参数明确指定类型和值

### 参数传递示例

#### 传统方式

```python
# 传统的参数传递方式
result = dubbo_invoke(
    service_uri="dubbo://127.0.0.1:20880",
    interface="com.example.DemoService",
    method="sayHello",
    params='{"message": "Hello, Dubbo!"}'
)
```

#### 类型明确方式

```python
# 基础类型参数
result = dubbo_invoke(
    service_uri="dubbo://127.0.0.1:20880",
    interface="com.example.DemoService",
    method="findUser",
    parameter_types="int,java.lang.String",
    parameter_values="[123, \"张三\"]"
)

# 复杂对象参数
result = dubbo_invoke(
    service_uri="dubbo://127.0.0.1:20880",
    interface="com.example.DemoService",
    method="saveUser",
    parameter_types="com.example.UserDTO",
    parameter_values="{\"name\":\"张三\", \"age\":25, \"address\":{\"city\":\"上海\"}}"
)

# 数组参数
result = dubbo_invoke(
    service_uri="dubbo://127.0.0.1:20880",
    interface="com.example.DemoService",
    method="batchDelete",
    parameter_types="java.lang.Integer[]",
    parameter_values="[1, 2, 3, 4, 5]"
)
```

## 底层实现

本插件基于协议扩展框架设计，目前支持：

1. **Dubbo原生协议**：默认使用Dubbo原生协议进行调用
   - 使用Hessian序列化格式
   - 基于TCP长连接通信
   - 支持心跳检测机制
   - 支持的数据类型：bool、int、long、float、double、String、Object等

2. **Telnet命令行模式**：当原生协议调用失败时，插件会自动切换到telnet方式作为备选
   - 使用Dubbo内置的telnet命令行接口
   - 通过TCP连接直接发送命令
   - 不依赖额外协议库

## 注意事项

- 确保您有权限访问所配置的注册中心或服务地址
- 参数格式必须是有效的JSON字符串
- 支持ZooKeeper和Nacos作为注册中心
- 当前实现仅支持Dubbo原生协议（Hessian序列化），未来将支持更多协议
- 服务调用超时默认为10秒，如需更长时间请提前考虑

## 许可证

[Apache License 2.0](LICENSE) 