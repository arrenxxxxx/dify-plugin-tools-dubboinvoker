# Dubbo调用器使用指南

本插件用于调用Dubbo服务，支持通过注册中心（如ZooKeeper、Nacos）发现服务或直接连接服务。

## 基本概念

[Dubbo](https://dubbo.apache.org/zh-cn/) 是一个高性能、轻量级的开源Java RPC框架，提供了三大核心能力：面向接口的远程方法调用，智能容错和负载均衡，以及服务自动注册和发现。

## 配置选项

使用本插件时，您需要提供以下信息：

1. **注册中心地址或服务URI**（二选一）
   - **注册中心地址**：使用格式 `zookeeper://host:port` 或 `nacos://host:port`，例如 `zookeeper://127.0.0.1:2181` 或 `nacos://127.0.0.1:8848`
   - **服务URI**：直接连接服务的URI，格式为 `dubbo://host:port`，例如 `dubbo://127.0.0.1:20880`

2. **接口名称**（必填）
   - Dubbo接口的完整类名，例如 `com.example.service.UserService`

3. **方法名**（必填）
   - 要调用的方法名，例如 `getUserById`

4. **参数**（可选，两种方式二选一）
   - **传统方式**：使用`params`参数提供JSON字符串，例如 `{"id": 123}`
   - **类型明确方式**：使用`parameter_types`和`parameter_values`参数明确指定类型和值

## 参数类型

### 传统方式（params）

对于简单场景，可以直接使用JSON格式参数：

```json
{
  "service_uri": "dubbo://10.0.0.2:20880",
  "interface": "com.example.UserService",
  "method": "getUserName",
  "params": "{\"userId\": 12345}"
}
```

此方式无需明确指定参数类型，但在处理复杂类型或多参数时可能出现歧义。

### 类型明确方式（parameter_types + parameter_values）

对于复杂参数场景，强烈推荐使用此方式调用：

#### 场景1：基础类型参数

```json
{
  "service_uri": "dubbo://10.0.0.2:20880",
  "interface": "com.example.UserService",
  "method": "findUser",
  "parameter_types": "int,java.lang.String",
  "parameter_values": "[123, \"张三\"]"
}
```

#### 场景2：复杂对象参数

```json
{
  "service_uri": "dubbo://10.0.0.2:20880",
  "interface": "com.example.UserService",
  "method": "saveUser",
  "parameter_types": "com.example.UserDTO",
  "parameter_values": "{\"name\":\"张三\", \"age\":25, \"address\":{\"city\":\"上海\"}}"
}
```

#### 场景3：数组参数

```json
{
  "service_uri": "dubbo://10.0.0.2:20880",
  "interface": "com.example.UserService",
  "method": "batchDelete",
  "parameter_types": "java.lang.Integer[]",
  "parameter_values": "[1, 2, 3, 4, 5]"
}
```

#### 场景4：集合类型参数

```json
{
  "service_uri": "dubbo://10.0.0.2:20880",
  "interface": "com.example.UserService",
  "method": "updateTags",
  "parameter_types": "int,java.util.List",
  "parameter_values": "[123, [\"标签1\", \"标签2\", \"标签3\"]]"
}
```

## 底层实现

本插件基于可扩展的协议框架设计，目前支持：

### 1. Dubbo原生协议

插件默认使用Dubbo原生协议进行服务调用：

- 使用Hessian序列化格式
- 基于TCP长连接通信
- 支持心跳检测机制
- 支持的数据类型：bool、int、long、float、double、String、Object等
- 与Java版Dubbo完全兼容

### 2. Telnet命令行模式

当原生协议调用失败时，插件会自动切换到telnet方式作为备选：

- 使用Dubbo内置的telnet命令行接口
- 通过TCP连接直接发送命令
- 不依赖额外协议库

## 协议扩展

该插件设计为可扩展的协议框架，未来将支持：

- **Triple协议**：基于HTTP/2的gRPC协议
- **REST协议**：基于HTTP的RESTful接口

## 使用场景

本插件适用于以下场景：

1. 需要从AI应用中调用已有的Dubbo服务
2. 与企业内部系统集成，调用基于Dubbo的微服务
3. 测试Dubbo服务的可用性和功能

## 注意事项

- 支持ZooKeeper和Nacos作为注册中心
- 所调用的Dubbo服务需要能够从您的环境访问（网络可达）
- 参数必须是有效的JSON格式
- 当前实现仅支持Dubbo原生协议（Hessian序列化），未来将支持更多协议
- 服务调用超时默认为10秒，如需更长时间请提前考虑
- 对于复杂参数类型，建议使用`parameter_types`和`parameter_values`参数

## 常见问题排查

1. **连接失败**
   - 检查注册中心地址或服务URI是否正确
   - 验证网络连接是否通畅
   - 确认防火墙设置允许相关端口访问

2. **服务未找到**
   - 确认接口名称拼写正确，包括完整的包名
   - 检查服务是否已在注册中心注册
   - 尝试使用直连方式验证服务是否可用

3. **调用异常**
   - 验证方法名是否正确
   - 检查参数格式和类型是否与服务端要求一致
   - 对于复杂类型参数，使用类型明确的调用方式
   - 查看服务端日志以获取更详细的错误信息

## 基本调用示例

### 通过ZooKeeper调用服务

```
{
  "registry_address": "zookeeper://10.0.0.1:2181",
  "interface": "com.example.UserService",
  "method": "getUserName",
  "params": "{\"userId\": 12345}"
}
```

### 通过Nacos调用服务

```
{
  "registry_address": "nacos://10.0.0.1:8848",
  "interface": "com.example.UserService",
  "method": "getUserName",
  "params": "{\"userId\": 12345}"
}
```

### 直连方式调用服务

```
{
  "service_uri": "dubbo://10.0.0.2:20880",
  "interface": "com.example.UserService",
  "method": "getUserName",
  "params": "{\"userId\": 12345}"
}
``` 