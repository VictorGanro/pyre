###    pyre document

Fast pyre 一个简单的python反编译封装，快速反编译。喜欢的话给个Star💖吧😘

###### 1.反编译

```shell
./pyre xxxx.exe    #pyinstall程序
or
./pyre xxxx.pyc
```

Notice: 生成汇编码需要将项目的编译环境 与 pyc 的环境一致 （可选）  【无法生成反编译也会尝试用cdc进行反编译尝试】

tip:汇编码用于 当 cdc 无法反编译时，审计，去除花指令等查看使用

pyinstaller程序反编译存放于 {{FileName}}_extracted 中的  {{FileName}}_py 中

pyc当前目录下放于当前

```shell
#直接调用python文件反编译
pyre.py 
调用runner()函数
runner({{FileName}})
```

tip. 尽量将程序放在该项目下进行反编译哦

###### 2.指令查找 

```shell
 ./pyre --search JUMP_FORWARD
 ./pyre --search {{Command}}
```

#### 3.具体使用案例参考 Example 文件夹下的 Writeup 😍
