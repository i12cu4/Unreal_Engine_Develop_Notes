pydub 音频处理库 可对wav使用

pip install pydub

若要使用mp3 则需要下载ffmpeg

Static里面只有3个应用程序：ffmpeg.exe，ffplay.exe，ffprobe.exe，每个exe的体积都很大，相关的Dll已经被编译到exe里面去了。

Shared里面除了3个应用程序之外，还有一些Dll，比如说avcodec-54.dll之类的。Shared里面的exe体积很小，他们在运行的时候，到相应的Dll中调用功能。

Dev版本是用于开发的，里面包含了库文件xxx.lib以及头文件xxx.h，这个版本不包含exe文件。

下载路径
https://ffmpeg.org/download.html
https://github.com/BtbN/FFmpeg-Builds/releases

参考资料
https://zhuanlan.zhihu.com/p/118362010