import sys, os;

# src目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)));

print(BASE_DIR);

# 外部模块注入
sys.path.append(BASE_DIR);

from core import core;

if __name__ == '__main__':
  core.main();