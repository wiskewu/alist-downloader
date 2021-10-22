def size_format(size, is_disk = False, precision = 2):
  '''
    size format for human:
    size: number  默认Byte
    kilobyte ---- (KB)
    megabyte ---- (MB)
    gigabyte ---- (GB)
    terabyte ---- (TB)
    petabyte ---- (PB)
    exabyte  ---- (EB)
    zettabyte---- (ZB)
    yottabyte---- (YB)
    参考自网上资源。
  '''
  formats = ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  unit = 1000.0 if is_disk else 1024.0;
  if not(isinstance(size, float) or isinstance(size, int)):
    raise TypeError('a float number or int number is required.');
  if size < 0:
    raise ValueError('number must be non-negative');
  for u in formats:
    size = size / unit;
    if size < unit:
      return f'{round(size, precision)}{u}';
  return f'{round(size, precision)}{u}';


if __name__ == '__main__':
  print('test: {}', size_format(10245, True));