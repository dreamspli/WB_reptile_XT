#!/usr/bin/env python3
"""
简化的Web服务启动脚本
"""
import os
import sys
import time
import signal
import threading
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from integration.spider_integration import SpiderIntegration


class WebSystemManager:
    def __init__(self):
        """初始化Web系统管理器"""
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
            return True
        except Exception as e:
            print(f"启动数据集成服务失败: {e}")
            return False
    
    def start_web_app(self):
        """启动Web应用"""
        print("启动Web应用...")
        try:
            # 直接导入并运行Flask应用
            from app import app, socketio
            
            # 在新线程中启动Flask应用
            def run_app():
                socketio.run(app, debug=False, host='0.0.0.0', port=5000, use_reloader=False)
            
            app_thread = threading.Thread(target=run_app)
            app_thread.daemon = True
            app_thread.start()
            
            print("Web应用已启动")
            print("Web界面地址: http://localhost:5000")
            return True
            
        except Exception as e:
            print(f"启动Web应用失败: {e}")
            return False
    
    def start_all(self):
        """启动所有服务"""
        print("=" * 50)
        print("微博舆情监测系统 (Web版) 启动中...")
        print("=" * 50)
        
        self.is_running = True
        
        # 检查依赖
        if not self._check_dependencies():
            print("依赖检查失败，请安装所需的Python包")
            return False
        
        # 启动数据集成服务
        if not self.start_integration():
            return False
        
        time.sleep(2)
        
        # 启动Web应用
        if not self.start_web_app():
            return False
        
        time.sleep(3)
        
        print("\n" + "=" * 50)
        print("系统启动完成！")
        print("=" * 50)
        print("服务状态:")
        print("  数据集成服务: 运行中")
        print("  Web应用: 运行中")
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
        
        self.is_running = False
        print("所有服务已停止")
    
    def _check_dependencies(self):
        """检查依赖包"""
        required_packages = [
            'flask',
            'flask_socketio',
            'jieba',
            'requests'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"缺少以下依赖包: {', '.join(missing_packages)}")
            print("请运行以下命令安装:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
        
        return True
    
    def monitor_services(self):
        """监控服务状态"""
        while self.is_running:
            try:
                # 检查集成服务状态
                if self.integration:
                    status = self.integration.get_processing_status()
                    if not status['is_running']:
                        print("警告: 数据集成服务已停止")
                
                time.sleep(30)  # 每30秒检查一次
                
            except Exception as e:
                print(f"监控服务时出错: {e}")
                time.sleep(60)


def main():
    """主函数"""
    manager = WebSystemManager()
    
    try:
        if manager.start_all():
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
