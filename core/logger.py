"""
Logger - 日志系统
"""

import os
from datetime import datetime

class Logger:
    """简单日志系统"""
    
    def __init__(self, name: str, log_dir: str = "logs"):
        self.name = name
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        self.log_file = os.path.join(
            log_dir, 
            f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
    def log(self, level: str, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] [{level}] {message}\n"
        
        # 输出到控制台
        print(line.strip())
        
        # 写入文件
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(line)
            
    def info(self, message: str):
        self.log("INFO", message)
        
    def warning(self, message: str):
        self.log("WARN", message)
        
    def error(self, message: str):
        self.log("ERROR", message)
