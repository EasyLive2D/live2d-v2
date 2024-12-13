# Live2D Cubism Python SDK

[English](./README.md)

这是一个将 **Cubism 2.1** Web SDK（JavaScript）完全翻译为纯 Python 的项目。这意味着使用 Live2D 将变得更加简单，无需烦人的环境配置或处理依赖缺失问题。

只需要安装以下依赖即可：

```
PyOpenGL  # 渲染 
numpy # 从 Python 到 OpenGL 的数据传输 
pygame # 渲染 
pillow # 加载纹理
```

## 性能

目前，这个项目“至少能跑起来”。  

仍有许多性能优化工作需要完成，例如用 numpy 替换纯 Python 的计算逻辑。  

由于核心代码是从混淆过的 `live2d.min.js` 翻译而来，代码可能不够整洁和易于理解。

## 项目结构
```
|-- core # live2d.min.js（Cubism 2.1）的 Python 实现 
|-- framework # Cubism 2.1 Web Framework 的 Python 实现 
|-- references # 翻译工作所用的参考资料
|-- requirements.txt 
|-- resources # app.py 使用的模型 
|-- sample # 使用示例 
|-- test-data # simple.py 使用的模型

```

## 使用方法

简单示例：[simple.py](./sample/simple.py)

更复杂的示例：[app.py](./sample/app.py)

## 特别感谢

- [JSConvert](https://github.com/JonBoynton/JSConvert)：主要用于将 JavaScript 翻译为 Python。
- [FreeLive](https://github.com/NiaBie/FreeLive)：提供了 MOC 数据的探索工具。
- [de4js](https://github.com/lelinhtinh/de4js)：完成了大部分反混淆工作。
- **Cubism**：感谢其为交互式 2D 角色动画开发了一个强大的框架，为本项目提供了灵感和支持。

## 免责声明

本项目中的模型来源于官方 Cubism 数据集、《BanG Dream!》。

本项目不用于任何商业或其他目的。
