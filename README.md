##### 简介（INTRO）
一款简单的使用aria2下载alist项目云盘文件夹内所有文件的爬虫工具。

##### 功能设计（DESIGN）
- 输入待下载的所有文件/文件夹请求path
- 遍历列表，根据接口返回的数据判断是文件夹还是文件，若为文件，则下载；若为文件夹，则逐一遍历内部的文件，重复上述操作。

##### 运行与使用（HOW TO USE）
- 安装所需py依赖
- 外部启动aria2应用并后台运行
- 执行src/bin/start.py

##### 参考文档（References）
- https://aria2.github.io/manual/en/html/aria2c.html
- https://github.com/zhenlohuang/pyaria2
- https://tqdm.github.io/docs/tqdm/

##### 如何解决文件夹跳级问题？
直接使用文件所在的dir属性

##### 可优化的点（TODOS）
- 根据文件大小进行归类排序
- 开启多线程并行多文件下载
- 密码限制？？？？

##### Licenses
`None. TOTALLY FREE AND OPEN.`