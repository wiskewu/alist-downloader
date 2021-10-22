import json
from os import path;

my_path = path.abspath(path.dirname(__file__));

def read_file(rel_file_path, default_value):
  '''
    读取文件并返回内容
    rel_file_path: string  相对路径文件地址
    default_value: any 读取错误时返回的默认值
  '''
  try:
    with open(path.join(my_path, rel_file_path), 'r', encoding = 'UTF-8') as f:
      return json.load(f);
  except IOError:
    print(f'读取【{rel_file_path}】文件错误');
  except UnicodeDecodeError:
    print(f'【{rel_file_path}】文件解析错误');
  except Exception:
    print(f'【{rel_file_path}】文件解析出错');
  return default_value;

def load_cfg():
  '''
    加载配置
  '''
  return read_file('../conf/config.json', json.loads("{}"));

def load_undone_path_down():
  '''
    加载上次下载失败的资源路径信息集合
  '''
  return read_file('../log/path_down_fail.json', json.loads("[]"));

def load_undone_paths():
  '''
    加载上次下载失败的资源路径集合
  '''
  return read_file('../log/path_fail.json', json.loads("[]"));

if __name__ == '__main__':
  f = load_cfg();
  print(f);