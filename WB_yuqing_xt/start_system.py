#!/usr/bin/env python3
"""
系统启动脚本 - 协调启动爬虫、分析和Web服务
"""
import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from integration.spider_integration import SpiderIntegration


class SystemManager:
    def __init__(self):
        """初始化系统管理器"""
        self.processes = {}
        self.integration = None
        self.is_running = False
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n收到信号 {signum}，正在关闭系统...")
        self.stop_all()
        sys.exit(0)
    
    def start_spider(self):
        """启动爬虫进程"""
        print("启动文章爬虫...")
        try:
            # 使用爬虫启动器启动文章爬虫
            launcher_path = project_root / 'spider_launcher.py'
            if launcher_path.exists():
                process = subprocess.Popen([
                    sys.executable, str(launcher_path), '--type', 'article'
                ], cwd=str(project_root))
                self.processes['article_spider'] = process
                print(f"文章爬虫已启动，PID: {process.pid}")
            else:
                print(f"爬虫启动器不存在: {launcher_path}")
        except Exception as e:
            print(f"启动文章爬虫失败: {e}")
    
    def start_comment_spider(self):
        """启动评论爬虫进程"""
        print("启动评论爬虫...")
        try:
            # 使用爬虫启动器启动评论爬虫
            launcher_path = project_root / 'spider_launcher.py'
            if launcher_path.exists():
                process = subprocess.Popen([
                    sys.executable, str(launcher_path), '--type', 'comment'
                ], cwd=str(project_root))
                self.processes['comment_spider'] = process
                print(f"评论爬虫已启动，PID: {process.pid}")
            else:
                print(f"爬虫启动器不存在: {launcher_path}")
        except Exception as e:
            print(f"启动评论爬虫失败: {e}")
    
    def start_integration(self):
        """启动数据集成服务"""
        print("启动数据集成服务...")
        try:
            self.integration = SpiderIntegration()
            
            # 首先处理现有数据
            print("处理现有数据...")
            self.integration.manual_process_all()
            
            # 开始监控新数据
            self.integration.start_monitoring()
            print("数据集成服务已启动")
        except Exception as e:
            print(f"启动数据集成服务失败: {e}")
    
    def start_web_app(self):
        """启动Web应用"""
        print("启动Web应用...")
        try:
            app_path = project_root / 'app.py'
            if app_path.exists():
                process = subprocess.Popen([
                    sys.executable, str(app_path)
                ], cwd=str(project_root))
                self.processes['web_app'] = process
                print(f"Web应用已启动，PID: {process.pid}")
                print("Web界面地址: http://localhost:5000")
            else:
                print(f"Web应用文件不存在: {app_path}")
        except Exception as e:
            print(f"启动Web应用失败: {e}")
    
    def start_all(self, include_spiders=True):
        """启动所有服务"""
        print("=" * 50)
        print("微博舆情监测系统启动中...")
        print("=" * 50)
        
        self.is_running = True
        
        # 检查依赖
        if not self._check_dependencies():
            print("依赖检查失败，请安装所需的Python包")
            return False
        
        # 启动数据集成服务
        self.start_integration()
        time.sleep(2)
        
        # 启动爬虫（可选）
        if include_spiders:
            self.start_spider()
            time.sleep(2)
            # 注意：评论爬虫通常不需要持续运行，可以定时执行
            # self.start_comment_spider()
        
        # 启动Web应用
        self.start_web_app()
        time.sleep(3)
        
        print("\n" + "=" * 50)
        print("系统启动完成！")
        print("=" * 50)
        print("服务状态:")
        self._print_status()
        print("\n访问 http://localhost:5000 查看监控面板")
        print("按 Ctrl+C 停止所有服务")
        print("=" * 50)
        
        return True
    
    def stop_all(self):
        """停止所有服务"""
        print("\n正在停止所有服务...")
        
        # 停止数据集成服务
        if self.integration:
            self.integration.stop_monitoring()
            self.integration = None
        
        # 停止所有子进程
        for name, process in self.processes.items():
            try:
                print(f"停止 {name} (PID: {process.pid})")
                process.terminate()
                
                # 等待进程结束
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"强制终止 {name}")
                    process.kill()
                    process.wait()
                    
            except Exception as e:
                print(f"停止 {name} 时出错: {e}")
        
        self.processes.clear()
        self.is_running = False
        print("所有服务已停止")
    
    def _check_dependencies(self):
        """检查依赖包"""
        required_packages = [
            'flask',
            'flask-socketio',
            'jieba',
            'requests',
            'redis'  # 可选
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                if package != 'redis':  # Redis是可选的
                    missing_packages.append(package)
        
        if missing_packages:
            print(f"缺少以下依赖包: {', '.join(missing_packages)}")
            print("请运行以下命令安装:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
        
        return True
    
    def _print_status(self):
        """打印服务状态"""
        for name, process in self.processes.items():
            status = "运行中" if process.poll() is None else "已停止"
            print(f"  {name}: {status} (PID: {process.pid})")
        
        if self.integration:
            integration_status = self.integration.get_processing_status()
            print(f"  数据集成服务: {'运行中' if integration_status['is_running'] else '已停止'}")
    
    def monitor_services(self):
        """监控服务状态"""
        while self.is_running:
            try:
                # 检查进程状态
                for name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        print(f"警告: {name} 进程已退出 (退出码: {process.returncode})")
                        # 可以在这里添加自动重启逻辑
                
                time.sleep(30)  # 每30秒检查一次
                
            except Exception as e:
                print(f"监控服务时出错: {e}")
                time.sleep(60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='微博舆情监测系统')
    parser.add_argument('--no-spider', action='store_true', help='不启动爬虫服务')
    parser.add_argument('--web-only', action='store_true', help='仅启动Web服务')
    
    args = parser.parse_args()
    
    manager = SystemManager()
    
    try:
        if args.web_only:
            # 仅启动Web应用和数据集成
            manager.start_integration()
            time.sleep(2)
            manager.start_web_app()
            print("Web服务已启动: http://localhost:5000")
        else:
            # 启动完整系统
            include_spiders = not args.no_spider
            if manager.start_all(include_spiders=include_spiders):
                # 开始监控服务
                manager.monitor_services()
        
        # 保持程序运行
        while manager.is_running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        pass
    finally:
        manager.stop_all()


if __name__ == '__main__':
    main()
