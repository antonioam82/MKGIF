from setuptools import setup

setup(
    name="mkgif",
    version="1.0.0",
    description="Convierte videos y WebP animados en GIFs optimizados desde la linea de comandos",
    py_modules=["mkgif"],
    install_requires=[
        "opencv-python",
        "pillow",
        "numpy",
        "tqdm",
        "colorama",
        "pynput",
        "pyfiglet",
        "pyglet",
    ],
    entry_points={
        "console_scripts": [
            "mkgif=mkgif:main",
        ],
    },
    python_requires=">=3.9",
)
