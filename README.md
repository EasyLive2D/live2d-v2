# Live2D Cubism Python SDK

[中文](./README.cn.md)

This is a translation project from **Cubism 2.1** Web SDK (JavaScript) to pure Python, without using any Javascript runtime or c++ bindings.

Just a few dependencies are needed:

```
PyOpenGL # rendering
numpy # data transmission from Python to OpenGL
pygame # rendering
pillow # loading textures
```

## Performance

At least, it works.

A lot of work needs to be done for performance improvements, such as replacing pure python calculation with numpy.

Since the core code is translated from the obfuscated `live2d.min.js`, the code may not be tidy and understandable.

## Project Structure

```

|-- core       # Python implementation of live2d.min.js (Cubism 2.1)
|-- framework  # Python implementation of Cubism 2.1 Web Framework
|-- references # References for the translation work
|-- requirements.txt
|-- resources  # Models for app.py
|-- sample     # Usage examples
|-- test-data  # Models for simple.py
```

## Quick Start

Install dependencies in `requirements.txt` and run either of the following:

A simple example: [simple.py](main/simple.py)

A more comprehensive example: [app.py](main/app.py)

## Special Thanks

- JavaScript to Python translation is primarily done by [JSConvert](https://github.com/JonBoynton/JSConvert).
- MOC data exploration is facilitated by [FreeLive](https://github.com/NiaBie/FreeLive).
- Most deobfuscation work is done by [de4js](https://github.com/lelinhtinh/de4js).
- Cubism: For their incredible work in developing a robust framework for interactive 2D character animations, which
  inspired and enabled this project.

## Disclaimer

The models in this project are sourced from the official Cubism dataset, BanG Dream!, and custom creations.

This project is not intended for commercial or other purposes.



