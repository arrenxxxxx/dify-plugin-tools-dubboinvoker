#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
线程状态查看工具

用法:
    python thread_status.py              # 查看并打印所有线程状态
    python thread_status.py --dump file  # 将线程状态导出到指定文件
"""

import sys
import os
import argparse
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("thread_status")

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入线程工具
from utils.thread_utils import print_thread_status, dump_thread_status_to_file, get_thread_status

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="线程状态查看工具")
    parser.add_argument("--dump", metavar="FILE", help="将线程状态导出到文件")
    parser.add_argument("--json", action="store_true", help="以JSON格式输出")
    parser.add_argument("--id", metavar="ID", help="查看指定线程ID的状态")
    parser.add_argument("--name", metavar="NAME", help="查看指定名称的线程状态")
    
    args = parser.parse_args()
    
    # 获取所有线程的状态
    thread_info = get_thread_status()
    
    # 处理不同的命令行参数
    if args.id:
        # 查找指定ID的线程
        target_thread = None
        for name, info in thread_info.items():
            if str(info['id']) == args.id:
                target_thread = (name, info)
                break
        
        if target_thread:
            name, info = target_thread
            logger.info(f"线程ID {args.id} 的信息:")
            logger.info(f"线程名称: {name}")
            logger.info(f"存活状态: {'是' if info['alive'] else '否'}")
            logger.info(f"运行状态: {info['state']}")
            logger.info(f"堆栈信息:\n{info['stack_trace']}")
        else:
            logger.error(f"找不到ID为 {args.id} 的线程")
    elif args.name:
        # 查找指定名称的线程
        if args.name in thread_info:
            info = thread_info[args.name]
            logger.info(f"线程 {args.name} 的信息:")
            logger.info(f"线程ID: {info['id']}")
            logger.info(f"存活状态: {'是' if info['alive'] else '否'}")
            logger.info(f"运行状态: {info['state']}")
            logger.info(f"堆栈信息:\n{info['stack_trace']}")
        else:
            logger.error(f"找不到名称为 {args.name} 的线程")
    elif args.dump:
        # 导出到文件
        filename = dump_thread_status_to_file(args.dump)
        logger.info(f"线程状态已导出到: {filename}")
    elif args.json:
        # 以JSON格式输出
        import json
        # 将堆栈跟踪字符串化处理，确保可以序列化为JSON
        json_friendly_info = {}
        for name, info in thread_info.items():
            json_friendly_info[name] = {
                "id": info["id"],
                "alive": info["alive"],
                "daemon": info["daemon"],
                "state": info["state"],
                "stack_trace": str(info["stack_trace"])
            }
        print(json.dumps(json_friendly_info, ensure_ascii=False, indent=2))
    else:
        # 默认打印所有线程状态
        print_thread_status()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 