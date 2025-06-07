# Privacy Policy

## Data Collection

The Dubbo Invoker plugin ("this plugin") does not collect or store any personal data. All configuration information is:

1. **Not permanently stored** - No configuration data is saved by the plugin
2. **Runtime only** - Connection details are only kept in memory during execution
3. **Automatically cleared** - All data is removed after each request completes

## Data Transmission

When you use this plugin, your provided information is transmitted only to:

1. **Your specified registry** (e.g., Nacos, ZooKeeper) for service discovery
2. **Your target Dubbo service** for method invocation

The plugin acts as a bridge - it forwards your requests to your services but does not store, log, or send data elsewhere.

## Data Security

- **No data storage**: We don't save any of your configuration or parameters
- **No external transmission**: Data only goes to the services you specify
- **Memory-only processing**: All operations happen in temporary memory
- **Your responsibility**: Please ensure your target services handle data securely

## What We Don't Do

- ❌ Store your service URLs or credentials
- ❌ Log your method calls or parameters  
- ❌ Send data to third-party services
- ❌ Retain any information after execution

## Contact

If you have questions about this privacy policy, please open an issue on our GitHub repository. 