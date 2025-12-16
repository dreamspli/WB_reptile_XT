#!/usr/bin/env python3
"""
重启系统脚本
"""
import os
import sys
import time
import psutil
import signal
from pathlib import Path

def kill_existing_processes():
    """杀死现有的相关进程"""
    print("正在停止现有进程...")
    
    # 查找并杀死相关进程
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any('start_web.py' in cmd or 'app.py' in cmd or 'spider' in cmd for cmd in cmdline):
                print(f"停止进程: {proc.info['pid']} - {' '.join(cmdline)}")
                proc.terminate()
                
                # 等待进程结束
                try:
                    proc.wait(timeout=5)
                except psutil.TimeoutExpired:
                    proc.kill()
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    time.sleep(2)
    print("现有进程已停止")

def start_new_system():
    """启动新系统"""
    print("启动新系统...")
    
    # 启动Web系统
    os.system("python start_web.py")

def main():
    """主函数"""
    print("=" * 50)
    print("重启微博舆情监测系统")
    print("=" * 50)
    
    try:
        kill_existing_processes()
        start_new_system()
    except KeyboardInterrupt:
        print("\n重启被取消")
    except Exception as e:
        print(f"重启过程中出错: {e}")

if __name__ == '__main__':
    main()
