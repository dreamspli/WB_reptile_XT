#!/usr/bin/env python3
"""
修复导入问题的脚本
"""
import os
import sys
from pathlib import Path

def fix_spider_imports():
    """修复爬虫模块的导入问题"""
    project_root = Path(__file__).parent
    
    # 修复文章爬虫的导入
    article_spider_path = project_root / 'spider' / 'article_data' / 'article_spider.py'
    if article_spider_path.exists():
        print(f"修复 {article_spider_path}")
        
        with open(article_spider_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经修复
        if 'sys.path.append' not in content:
            # 在导入部分添加路径
            lines = content.split('\n')
            new_lines = []
            import_added = False
            
            for i, line in enumerate(lines):
                if line.startswith('from util import stringUtil') and not import_added:
                    # 替换这一行
                    new_lines.extend([
                        '# 添加项目根目录到Python路径',
                        'sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))',
                        'from util import stringUtil'
                    ])
                    import_added = True
                else:
                    new_lines.append(line)
            
            if import_added:
                with open(article_spider_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))
                print("✓ 文章爬虫导入已修复")
            else:
                print("- 文章爬虫导入已经正确")
    
    # 修复评论爬虫的导入（已经修复过了）
    comment_spider_path = project_root / 'spider' / 'comment_spider' / 'comment_spider.py'
    if comment_spider_path.exists():
        print("✓ 评论爬虫导入已经正确")

def create_spider_launcher():
    """创建爬虫启动器脚本"""
    project_root = Path(__file__).parent
    
    launcher_content = '''#!/usr/bin/env python3
"""
爬虫启动器 - 解决路径问题
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def start_article_spider():
    """启动文章爬虫"""
    try:
        # 切换到爬虫目录
        spider_dir = project_root / 'spider' / 'article_data'
        os.chdir(str(spider_dir))
        
        # 导入并启动爬虫
        from spider.article_data.article_spider import start
        start()
    except Exception as e:
        print(f"启动文章爬虫失败: {e}")

def start_comment_spider():
    """启动评论爬虫"""
    try:
        # 切换到爬虫目录
        spider_dir = project_root / 'spider' / 'comment_spider'
        os.chdir(str(spider_dir))
        
        # 导入并启动爬虫
        from spider.comment_spider.comment_spider import main
        main()
    except Exception as e:
        print(f"启动评论爬虫失败: {e}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='爬虫启动器')
    parser.add_argument('--type', choices=['article', 'comment'], required=True, help='爬虫类型')
    
    args = parser.parse_args()
    
    if args.type == 'article':
        start_article_spider()
    elif args.type == 'comment':
        start_comment_spider()
'''
    
    launcher_path = project_root / 'spider_launcher.py'
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print(f"✓ 创建爬虫启动器: {launcher_path}")

def main():
    """主函数"""
    print("修复导入问题...")
    print("=" * 40)
    
    fix_spider_imports()
    create_spider_launcher()
    
    print("=" * 40)
    print("修复完成！")
    print("\n现在可以重新启动系统:")
    print("python start_system.py")

if __name__ == '__main__':
    main()
