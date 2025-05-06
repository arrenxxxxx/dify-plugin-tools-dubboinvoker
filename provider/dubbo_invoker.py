from typing import Any

from dify_plugin import ToolProvider


class DubboInvokerProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        无需预先授权，使用时配置
        """
        pass 