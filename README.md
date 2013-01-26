ab
==

模拟apache benchmark的一个简单的网站压力测试程序，用python编写，可以自由选择发送请求数以及并发的线程数

使用示例：

$ python problem2.py -n 100 -c 10 -u http://www.163.com
===============================================
URL:  http://www.163.com
Total Requests Number:  100
Concurrent Requests Number:  10
Total Time Cost(seconds):  21.3480730057
Average Time Per Request:  0.213480730057
Average Requests Number Per Second:  4.68426353861
Total Error Number:  0
