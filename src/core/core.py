import os, requests, time, json;
from pyaria2 import Aria2RPC;
from tqdm import tqdm;
from lib.load_config import load_cfg, load_undone_path_down, load_undone_paths;
from lib.size_format import size_format;
from lib.logger import get_logger;

# 当前目录
cur_dir = os.path.dirname(__file__);
# 获取配置文件
config_file = load_cfg();
# 下载的根路径
root_dst = config_file['root_out_dir'];
# alist网站地址，也为接口请求域
req_host = config_file['api_host'];
api_list = config_file['api_list'];
api_load_path = api_list['load_path'];
# 资源目录路径
source_paths = config_file['source_paths'];
# 是否继续上一次未完成的下载
continue_previous_task = config_file['continue_previous_task'];

# 所有待下载路径 List<string>
path_list = [];
# 所有下载出错的路径 List<string>
path_fail_list = [];

# 所有待下载对象信息List<Object>
path_info_list = [];
# 所有下载出错的文件/文件夹列表 List<Object>
path_down_fail_list = [];

# logger
logger = get_logger('AlistDownloader', 'log');

def init_tasks():
  global path_list, path_info_list, path_fail_list, path_down_fail_list;
  if not continue_previous_task:
    path_list = source_paths[:];
    path_info_list = [];
    path_fail_list = [];
    path_down_fail_list = [];
  else:
    last_paths = load_undone_paths();
    last_paths_info = load_undone_path_down();
    path_list = [x for l1 in (last_paths, source_paths) for x in l1]; # 即[...last_paths, ...source_paths]
    path_info_list = last_paths_info[:];
    path_fail_list = [];
    path_down_fail_list = [];

def load_path_info(url, data):
  '''
    获取路径基本信息
    url: string   请求接口地址
    data: object  请求参数
  '''
  headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/json;charset=UTF-8",
    "Pragma": "no-cache",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
  };
  res = requests.post(url, data = json.dumps(data), headers = headers);
  msg = '';
  try:
    res_json = res.json();
    if res_json and res.status_code == 200:
      if res_json["code"] == 200:
        result_list = res_json["data"];
        for info in reversed(result_list):
          path_info_list.insert(0, info);
        return True;
    elif res_json and res_json["message"]:
      msg = '请求【{}】失败：{}'.format(url, res_json["message"]);
      logger.error(msg);
    else:
      msg = '请求【{}】失败。'.format(url);
      logger.error(msg);
    return False;
  except Exception:
    msg = '!!请求【{}】失败。'.format(url);
    logger.error(msg);
    return False;

def handleNextPath():
  '''
    处理路径数组中的首项
  '''
  if len(path_list) == 0:
    return;
  next_path = path_list[0];
  # next_path = next_path.rstrip('/');
  del path_list[:1];
  req_data = {
    "password": "",
    "path": next_path
  };
  req_url = req_host + api_load_path;
  req_ok = load_path_info(req_url, req_data);
  if req_ok:
    # next_path默认为顶层文件夹
    # dir_path = get_closest_dir(next_path);
    # dst_path = root_dst + '//' + dir_path;
    # make_sure_dir_exist(dst_path);
    handleNextPathInfo();
  else:
    # 将请求失败的项放到失败集合中
    path_fail_list.append(next_path);

def handleNextPathInfo():
  '''
    处理路径信息数组中的首项
  '''
  if len(path_info_list) == 0:
    return;
  info_obj = path_info_list[0];
  del path_info_list[:1];
  file_type = info_obj["type"];
  file_dir = info_obj["dir"];
  file_name = info_obj["name"];
  print(file_name);
  file_category = info_obj["category"];
  file_size = info_obj["size"];
  file_password = info_obj["password"];
  
  if file_type == 'file':
    # 默认d为下载地址
    tmp_url = '/d/' + file_dir + file_name;
    file_down_url = req_host + tmp_url.replace(r'//', '/'); # 去除多余/
    # 组成最终目录
    file_dst_dir = root_dst;
    if not file_dir == '':
      file_dst_dir = root_dst + '//' + file_dir.replace(r'/', '//'); # 转换win盘符
    make_sure_dir_exist(file_dst_dir);
    down_ok = False;
    try:
      down_ok = down_file_from_url(file_down_url, file_name, file_dst_dir);
    except RecursionError:
      logger.error(f'文件【{file_name}】由于内部无限递归意外退出下载错误。');
      down_ok = False;
    if not down_ok:
      path_down_fail_list.append(info_obj);
    else:
      handleNextPathInfo();
  elif file_type == 'folder':
    print("准备读取文件夹信息");
    file_path = file_dir + file_name;
    req_data = {
      "password": file_password,
      "path": file_path
    };
    req_url = req_host + api_load_path;
    req_ok = load_path_info(req_url, req_data);
    if req_ok:
      # 开始下载
      handleNextPathInfo();
    else:
      # 失败记录
      path_down_fail_list.append(info_obj);

def make_sure_dir_exist(dir_name):
  '''
    确保文件夹存在
    dir_name: string  文件夹路径

    return: boolean 创建文件夹，则返回true，否则返回false
  '''
  dst_path = dir_name.strip(); # 去除首位空格
  dst_path = dst_path.rstrip("\\"); # 去除尾部 \ 符号
  exists = os.path.exists(dst_path);
  # 判断结果
  if not exists:
    # 如果不存在则创建目录 创建目录操作函数
    os.makedirs(dst_path);
    logger.info(f'创建文件夹【{dst_path}】');
    return True;
  else:
    # 如果目录存在则不创建
    # print('文件夹【】已存在。'.format(dst_path));
    return False;

def get_closest_dir(path_str):
  '''
    获取最近的上层文件夹
    path_str: string 路径字符串

    return: 返回文件夹名
  '''
  dir_path = path_str.split(".")[0]; # 去除文件路径（xxx/zzz.jpg）干扰
  dirs = dir_path.split("/");
  dst = '';
  while (dst == ''):
    dst = dirs.pop();
  return dst;

def print_downloading_status(gid, jsonrpc, filename, outdir):
  '''
    输出下载进度信息
    gid: string       aria2返回的任务id
    jsonrpc: object   aria2 jsonRpc实例
    filename: string  文件名，带格式后缀
    outdir: string    输出路径

    return: 返回是否下载成功标识
  '''
  # 计时
  start_time = time.time();
  # 是否下载成功
  download_sucessfully = False;
  # 实时状态
  status_in_time = jsonrpc.tellStatus(gid);
  # 进度条
  pbar = None;
  completedLength = 0;
  lastCompletedLength = 0;
  totalLength = 0;
  status = status_in_time['status'];
  onceFlag = False;
  msg = f"===================新任务-开始下载文件【{filename}】===================";
  print(msg);
  logger.info(msg);

  while status in ['active', 'paused', 'waiting']:
    completedLength = int(status_in_time['completedLength']);
    totalLength = int(status_in_time['totalLength']);
    if totalLength == 0 and status == 'active' and not onceFlag:
      onceFlag = True;
      msg = '正在开始下载【{}】，当前进度: 0%'.format(filename);
      print(msg);
    else:
      pbar = pbar if pbar else tqdm(totalLength);
      rate = 0 if totalLength == 0 else completedLength / totalLength;
      rate = rate * 100;
      if rate != 0:
        pbar.set_description_str('正在下载【{}】，任务状态【{}】，当前进度【{}/{}】，已完成：{:.2f}%'.format(filename, status, size_format(completedLength, True), size_format(totalLength, True), rate));
        pbar.update(completedLength - lastCompletedLength);

    lastCompletedLength = completedLength;
    time.sleep(0.1);
    # 读取最新状态
    status_in_time = jsonrpc.tellStatus(gid);
    status = status_in_time['status'];

  completedLength = int(status_in_time['completedLength']);
  totalLength = int(status_in_time['totalLength']);
  print('\n');
  if status == 'complete':
    # complete包含完成或停止
    if completedLength == totalLength and totalLength == 0:
      rate = 0 if totalLength == 0 else completedLength / totalLength;
      rate = rate * 100;
      msg = '文件【{}】下载已停止，当前已完成进度{:.2f}%'.format(filename, rate);
      logger.error(msg);
    else:
      msg = '文件【{}】下载（总大小：{}）完成，已保存至目录【{}】'.format(filename, size_format(totalLength, True), outdir);
      print(msg);
      logger.info(msg);
      download_sucessfully = True;
  elif status == 'removed':
    msg = '文件【{}】下载任务已被移除。'.format(filename);
    logger.error(msg);
  elif status == 'error':
    msg = '文件【{}】下载错误。'.format(filename);
    logger.error(msg);
  else:
    msg = '文件【{}】下载任务已结束，结束时信息为：【状态:{}，已下载：{}，总大小：{}】。'.format(filename, status, size_format(completedLength, True), size_format(totalLength, True));
    print(msg);
    logger.warning(msg);

  if pbar:
    pbar.set_description_str('\n文件【{}】下载任务已结束：【状态:{}，已下载：{}，总大小：{}】。'.format(filename, status, size_format(completedLength, True), size_format(totalLength, True)));
  
  end_time = time.time();
  ok_msg = "成功" if download_sucessfully else "失败/重复";
  msg = "下载任务【{}】执行{},共计耗时{:.2f}s,储存位置：【{}】".format(filename, ok_msg, end_time - start_time, outdir);
  logger.info(msg);
  msg = f"===================下载文件【{filename}】任务结束===================";
  logger.info(msg);
  return download_sucessfully;

def down_file_from_url(url, filename, outdir):
  '''
    下载资源
    url: string       下载地址
    filename: string  文件名，带格式后缀
    outdir: string    输出路径，绝对
  '''
  jsonrpc = Aria2RPC();
  req_options = { "dir": outdir, "out": filename };
  res_of_gid = jsonrpc.addUri([url], options = req_options);
  return print_downloading_status(res_of_gid, jsonrpc, filename, outdir);

def main():
  init_tasks();
  start_time = time.time();
  msg = "####################程序启动，开始下载资源####################";
  print(msg);
  logger.info(msg);

  while len(path_list) > 0:
    handleNextPath();

  while len(path_info_list) > 0:
    handleNextPathInfo();

  if len(path_fail_list):
    try:
      with open(os.path.join(cur_dir, '../log/path_fail.json'), 'w') as f:
        logger.info('保存失败资源路径至☞【log/path_fail.json】成功。');
        f.write(json.dumps(path_fail_list));
    except Exception:
      logger.error('保存失败资源路径至☞【log/path_fail.json】失败。');

  if len(path_down_fail_list):
    try:
      logger.info('保存失败资源信息至☞【log/path_down_fail.json】成功。');
      with open(os.path.join(cur_dir, '../log/path_down_fail.json'), 'w') as f:
        f.write(json.dumps(path_down_fail_list));
    except Exception:
      logger.error('保存失败资源信息至☞【log/path_down_fail.json】失败。');

  end_time = time.time();
  msg = '####################资源下载结束, 总共耗时：{:.2f}s.####################'.format(end_time - start_time);
  print(msg);
  logger.info(msg);