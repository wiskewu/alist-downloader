import logging;
import os;

cur_path = os.path.abspath(os.path.dirname(__file__));

def get_logger(name, log_file_name):
  logger = logging.getLogger(name);
  logger.setLevel(level = logging.INFO);
  # 写入日志
  handler = logging.FileHandler(os.path.join(cur_path, '../log/{}.txt'.format(log_file_name)), encoding = 'utf-8');
  handler.setLevel(logging.INFO);
  formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s');
  handler.setFormatter(formatter);

  logger.addHandler(handler);
  return logger;
