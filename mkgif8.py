import pyfiglet
import ffmpeg
import pyglet
from pyglet.window import key
import argparse
from PIL import Image
import random
#import subprocess
from colorama import Fore, init, Style
import os
from tqdm import tqdm


init()
color = {0:Fore.RED,1:Fore.GREEN,2:Fore.YELLOW,
         3:Fore.BLUE,4:Fore.CYAN,5:Fore.MAGENTA,6:Fore.WHITE}
 
bright = {0:Style.DIM,1:Style.NORMAL,2:Style.BRIGHT}
 
c_index = color[random.randint(0,6)]
b_index = bright[random.randint(0,2)]
