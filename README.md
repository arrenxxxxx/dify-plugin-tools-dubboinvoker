# Dubbo Invoker - Dify Plugin

A powerful Dify plugin for invoking Dubbo services. Supports direct connection to Dubbo services or service discovery through registries (such as ZooKeeper, Nacos). Fully supports complex parameter types, including nested objects, collections, Maps, and multi-parameter method invocations.

[![English](https://img.shields.io/badge/Language-English-blue)](README.md)
[![中文简体](https://img.shields.io/badge/Language-简体中文-red)](README_zh.md)

🚀 Dubbo Invoker — Providing powerful Dubbo service invocation capabilities for AI applications!

Dubbo Invoker is specifically designed for the Dify platform, providing a complete Dubbo service integration solution that enables your AI applications to seamlessly invoke enterprise-level microservices.

## 🌟 Key Features

* **Registry Support** - Supports Nacos registry service discovery
* **Direct Connection Mode** - Direct invocation of Dubbo services without registry
* **Complex Parameter Types** - Supports all Java types including primitives, objects, generic collections, arrays
* **Multi-Parameter Invocation** - Supports multi-parameter method calls with precise type specification
* **Native Protocol Compatibility** - Uses Dubbo native protocol (Hessian serialization) for service invocation
* **Multi-Protocol Framework** - Extensible multi-protocol support framework (currently implements Dubbo native protocol)

## 📦 Installation

### Prerequisites
- Dify v1.0.0 or higher
- Network environment with access to your Dubbo services or registry

### Installation Methods

#### Method 1: Install from Dify Marketplace
```bash
# In Dify workspace
Plugins → Marketplace → Search "Dubbo Invoker" → Install
```

#### Method 2: Local Package Installation
```bash
# After downloading .difypkg file
Plugins → Local Installation → Upload package file → Install
```

#### Method 3: Install from GitHub (Development Version)
```bash
# Clone repository
git clone https://github.com/your-repo/dify-plugin-dubbo-invoker.git
cd dify-plugin-dubbo-invoker

# Package plugin
dify plugin package ./

# Install generated .difypkg file
```

## 🚀 Quick Start

### Pre-authorization Configuration

Before using the tool, it's recommended to configure pre-authorization parameters to optimize Dubbo invocations:

1. **Enter Tool Configuration**
   - In your Dify workspace, go to **Plugins → Installed Plugins**
   - Find the **Dubbo Invoker** plugin
   - Click the **Configure** button

2. **Configure Pre-authorization Parameters**

| Configuration | Default | Description | Example |
|---------------|---------|-------------|---------|
| **Dubbo Version** | 2.4.10 | Specify Dubbo protocol version, affects serialization compatibility | `2.4.10`, `2.6.x`, `2.7.15`, `3.0.1` |
| **Call Timeout** | 60000ms | Timeout for Dubbo service calls (milliseconds) | `30000` (30 seconds), `120000` (2 minutes) |

**Configuration Notes:**
- **Dubbo Version**: Choose a version compatible with your server, ensuring serialization protocol matching
- **Timeout**: Set reasonable timeout values based on service response time, range: 1ms - 300000ms (5 minutes)

### Configure Tool in Dify Interface

1. **Add Tool to Workflow**
   - Go to your Dify workspace
   - Create a new workflow or edit an existing workflow
   - Add a **Tool** node to the workflow

2. **Select Dubbo Invoker Tool**
   - In the tool selection panel, find **Dubbo Invoker** (调用Dubbo服务)
   - Click to add to workflow

3. **Configure Tool Parameters**
   - Configuration panel will open, displaying input fields
   - Pre-authorization configured Dubbo version and timeout will be automatically applied

### Basic Configuration Examples

```yaml
# Simple string list method call
Registry Address: nacos://192.168.3.111:8848
Interface Name: io.example.api.HelloService
Method Name: sayHelloList
Parameter Types: java.util.List<java.lang.String>
Parameter Values: ["Zhang San", "Li Si", "Wang Wu"]
```

### Complex Object List Method Call

```yaml
# Complex object list method
Registry Address: nacos://192.168.3.111:8848
Interface Name: io.example.api.UserService
Method Name: batchCreateUsers
Parameter Types: java.util.List<io.example.dto.UserRequest>
Parameter Values: >
  [
    {"name":"Zhang San","age":25,"email":"zhangsan@example.com"},
    {"name":"Li Si","age":30,"email":"lisi@example.com"}
  ]
```

### Multi-Parameter Method Call

```yaml
# Multi-parameter mixed type call
Registry Address: nacos://192.168.3.111:8848
Interface Name: io.example.api.UserService
Method Name: updateUser
Parameter Types: java.lang.Long,io.example.dto.UserRequest,java.lang.Boolean
Parameter Values: >
  [
    123, 
    {"name":"Zhang San","age":26,"email":"zhangsan@example.com"}, 
    true
  ]
```

### Direct Connection Call

```yaml
# Direct connection call without registry
Service URI: dubbo://192.168.3.55:20880
Interface Name: io.example.api.UserService
Method Name: getUserById
Parameter Types: java.lang.Long
Parameter Values: 123
```

## 📋 Supported Parameter Types

### Basic Types and Wrapper Classes
- `int`, `long`, `float`, `double`, `boolean`, `byte`, `short`, `char`
- `java.lang.Integer`, `java.lang.String`, `java.lang.Boolean`, etc.

### Complex Types
- **Custom Objects**: Any Java POJO class
- **Collection Types**: `java.util.List<T>`, `java.util.Map<K,V>`, `java.util.Set<T>`
- **Array Types**: `int[]`, `String[]`, `CustomObject[]`
- **Nested Objects**: Support for arbitrarily deep object nesting

## 🔧 Configuration Field Details

### Pre-authorization Configuration Fields

These configurations are set at the plugin level and apply to all calls:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| **Dubbo Version** | String | 2.4.10 | Dubbo protocol version, affects serialization compatibility |
| **Call Timeout** | String | 60000 | Timeout for all Dubbo calls |

**Version Compatibility Guide:**
- `2.4.x` - Classic version, compatible with most legacy systems
- `2.6.x` - Stable version, recommended for production environments
- `2.7.x` - Feature version, supports more protocols
- `3.0.x` - Latest version, cloud-native features

### Required Fields (marked as "Required" in interface)

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| **Interface Name** | String | Yes | Complete Dubbo interface class name | `io.example.api.UserService` |
| **Method Name** | String | Yes | Method name to invoke | `getUserById` |

### Connection Configuration (Choose One)

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| **Registry Address** | String | Optional* | Registry server address | `nacos://192.168.3.111:8848` |
| **Service URI** | String | Optional* | Direct connection service URI address | `dubbo://127.0.0.1:20880` |

*Note: Registry Address and Service URI must provide one (cannot provide both)

### Parameter Configuration (Optional)

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| **Parameter Types** | String | Optional | Java parameter types, comma-separated for multiple | `java.lang.String,java.lang.Integer` |
| **Parameter Values** | String | Optional | JSON format parameter values | `["Zhang San", 25]` |

## 🔧 Configuration Tips

### Pre-authorization Configuration Best Practices

#### 🎯 Dubbo Version Selection Recommendations

**Check Server Version:**
```bash
# Check server Dubbo version
grep dubbo pom.xml
# Or check service startup logs
```

**Version Matching Strategy:**
- Prioritize choosing a version completely consistent with the server
- If uncertain, use the default version

#### ⏱️ Timeout Setting Recommendations

**Adjust based on service type:**
- Query services: `30000ms` (30 seconds)
- Computation services: `60000ms` (60 seconds) - Default
- Complex business services: `120000ms` (2 minutes)
- Batch processing services: `300000ms` (5 minutes)

### Field Validation Rules

1. **Registry Address or Service URI**: Must fill exactly one, when both are filled, direct connection is used
2. **Complete Interface Name**: Must use complete Java class name including package path
3. **Exact Method Name**: Method name must match exactly with Dubbo service method name
4. **Complete Generic Types**: For collection types, must specify complete generic types
5. **Valid JSON Format**: Parameter values must be valid JSON format
6. **Dubbo Version Format**: Must comply with `major.minor.patch` or `major.minor.x` format
7. **Timeout Range**: Must be within 1-300000 milliseconds range

### Using Variables in Configuration

You can use Dify workflow variables in any field:

```yaml
Registry Address: {{registry_url}}
Interface Name: {{service_interface}}
Method Name: getUserById
Parameter Types: java.lang.Long
Parameter Values: {{user_id}}
```

**Quick Variable Insertion:**
- Type `/` in any field to see available variables
- Select from dropdown list
- Variables formatted as `{{variable_name}}`

### Common Configuration Errors

#### ❌ Incorrect Examples
```yaml
# Pre-authorization configuration errors
Dubbo Version: 2.4                             # Incomplete version format
Call Timeout: 0                                # Invalid timeout
Call Timeout: 500000                           # Exceeds maximum limit

# Tool parameter configuration errors
Parameter Types: java.util.List                # Missing generic type
Parameter Values: "param1", 123, "param2"     # Multi-param not using array format
```

#### ✅ Correct Examples
```yaml
# Pre-authorization configuration correct
Dubbo Version: 2.6.x                          # Correct version format
Call Timeout: 60000                           # Reasonable timeout (milliseconds)

# Tool parameter configuration correct
Parameter Types: java.util.List<java.lang.String>  # Complete generic type
Parameter Values: ["param1", 123, "param2"]       # Multi-param using JSON array
Registry Address: nacos://192.168.3.111:8848      # Use only one connection method
Service URI: [empty]                              # Keep other blank
```

## 🏗️ Architecture Design

This plugin is built on an extensible protocol framework design:

### 1. Dubbo Native Protocol
- Uses Hessian serialization format, fully compatible with Java Dubbo services
- Supports automatic serialization and deserialization of complex objects

### 2. Intelligent Type Conversion System
- Automatically recognizes and converts JSON to Java objects
- Supports recursive conversion of nested objects and collections
- Preserves generic type information, ensuring type safety
- Specially optimized for List, Map and other collection types

### 3. Multi-Protocol Support Framework
- Extensible protocol processing architecture
- Currently implemented: Dubbo native protocol
- Planned support: Triple protocol, REST protocol

## 🗺️ Development Roadmap

### Current Version (v1.0.0)
- ✅ Dubbo native protocol support
- ✅ Nacos registry integration
- ✅ Complex parameter type handling
- ✅ Intelligent type conversion
- ✅ Multi-parameter invocation

### Upcoming Release (v1.1.0)
- 🔄 **ZooKeeper Registry Support**: Complete ZooKeeper integration for service discovery
- 🔄 **Triple Protocol Support**: gRPC-based Triple protocol implementation

## ⚠️ Important Notes

### Configuration Considerations
- **Pre-authorization Configuration**: It's recommended to configure Dubbo version and timeout before first use to avoid subsequent call issues
- **Version Compatibility**: Ensure the configured Dubbo version is compatible with the server, version mismatch may cause serialization errors
- **Network Access**: Ensure you have permission to access the configured registry or service address
- **Timeout Settings**: Service call timeout defaults to 60 seconds, adjustable through pre-authorization configuration (1ms-300000ms)
- **Performance Optimization**: Set reasonable timeout values to avoid excessive waiting affecting workflow performance

### Troubleshooting
- **Call Timeout**: Check network connection and service response time, appropriately increase timeout configuration
- **Serialization Error**: Check if Dubbo version configuration matches the server
- **Connection Failure**: Verify the correctness of registry address or direct connection URI

## 🤝 Contributing

We welcome code contributions, issue reports, and feature requests!

### How to Contribute

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the [Apache License 2.0](LICENSE).

## About

Providing Dubbo service invocation capabilities for the Dify platform.

### Topics

 dify-plugin  dubbo  rpc  microservices  nacos  zookeeper  java  service-discovery 

### Resources

 📄 Documentation 