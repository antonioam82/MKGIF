#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import hashlib

init()
color = {0:Fore.RED,1:Fore.GREEN,2:Fore.YELLOW,
         3:Fore.BLUE,4:Fore.CYAN,5:Fore.MAGENTA,6:Fore.WHITE}
 
bright = {0:Style.DIM,1:Style.NORMAL,2:Style.BRIGHT}
 
c_index = color[random.randint(0,6)]
b_index = bright[random.randint(0,2)]

def check_result_ext(file):
    name, ex = os.path.splitext(file)
    if ex != '.gif':
        raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"result file must be '.gif' ('{ex}' is not valid)."+Fore.RESET+Style.RESET_ALL)
    return file

def check_source_ext(file):
    supported_formats = ['.mp4','.avi','.mov','.wmv','.rm','.webp']
    name, ex = os.path.splitext(file)
    if file in os.listdir():
        if ex not in supported_formats:
            raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"Source file must be '.mp4', '.avi', '.mov', '.wmv', '.rm' or '.webp' ('{ex}' is not valid)."+Fore.RESET+Style.RESET_ALL)
    else:
        raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"FILE NOT FOUND: File '{file}' not found."+Fore.RESET+Style.RESET_ALL)
    return file

def make_gif(args):
    print(c_index+b_index+pyfiglet.figlet_format('MKGIF',font='graffiti')+Fore.RESET+Style.RESET_ALL)
    probe = ffmpeg.probe(args.source)
    video_streams = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]
    #width = video_streams[0]['width'] * args.size / 100
    #height = video_streams[0]['height'] * args.size / 100
    num_frames = video_streams[0]['nb_frames']
    print("FRAMES: ",num_frames)
    
'''def calculate_hash(filepath):
    sha256 = hashlib.sha256()
    with open(str(filepath), "rb") as file:
        while True:
            block = file.read(65536)
            if not block:
                break
            sha256.update(block)
    return sha256.hexdigest()'''

def calculate_sha1(file_path):
    sha1_hash = hashlib.sha1()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha1_hash.update(byte_block)
    return sha1_hash.hexdigest()
    
def convert_to_gif(args):
    print(c_index+b_index+pyfiglet.figlet_format('MKGIF',font='graffiti')+Fore.RESET+Style.RESET_ALL)
    file = Image.open(args.source)
    file.save(args.destination,'gif',save_all=True,background=0)
    file.close()
    size = get_size_format(os.stat(args.destination).st_size)
    print(f"Created '{args.destination}' with size {size} from '{args.source}'.")

def show(f):
    print("GENERATING VIEW...")
    try:
        with Image.open(f) as img:
            w, h = img.size

        animation = pyglet.image.load_animation(f)
        binm = pyglet.image.atlas.TextureBin()
        animation.add_to_texture_bin(binm)
        window = pyglet.window.Window(w,h,'GIF VIEW')
        sprite = pyglet.sprite.Sprite(animation)

        @window.event
        def on_draw():
            sprite.draw()

        pyglet.app.run()
        print(f"Successfully generated view from '{f}'.")
    except Exception as e:
        print("UNEXPECTED ERROR: ",str(e))
    
def check_positive(v):
    ivalue = float(v)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"speed and size values must be positive ('{v}' is not valid)."+Fore.RESET+Style.RESET_ALL)
    return ivalue

def get_size_format(b, factor=1024, suffix="B"):
	for unit in ["","K","M","G","T","P","E","Z"]:
	    if b < factor:
	        return f"{b:.4f}{unit}{suffix}"
	    b /= factor
	return f"{b:.4f}Y{suffix}"
    
def main():
    parser = argparse.ArgumentParser(prog="MKGIG 3.1",conflict_handler='resolve',
                                     description="Create gifs from videos in command line or convert '.webp' files into '.gif'.",
                                     epilog = "REPO: https://github.com/antonioam82/MKGIF")
    
    parser.add_argument('-src','--source',required=True,type=check_source_ext,help='Source file name')
    parser.add_argument('-dest','--destination',type=check_result_ext,default=None,help="Destination file name")
    parser.add_argument('-sz','--size',default=100,type=check_positive,help='Relative size of the gif (100 by default)')
    parser.add_argument('-delsrc','--delete_source',action='store_true',help='Generate gif and remove source file')
    parser.add_argument('-spd','--speed',default=100,type=check_positive,help='Relative speed of the gif (100 by default)')
    parser.add_argument('-shw','--show',action='store_true',help='Show result file')

    args = parser.parse_args()
    name, file_extension = os.path.splitext(args.source)

    if args.destination is None:
            hash_name = calculate_sha1(args.source)
            args.destination = f"{hash_name}.gif"    
    
    if file_extension == '.webp':
        if args.size != 100:
            parser.error(Fore.RED+Style.BRIGHT+"-sz/--size spec is not allowed for '.webp' to '.gif' conversion."+Fore.RESET+Style.RESET_ALL)
        else:
            convert_to_gif(args)
    else:
        make_gif(args)
        print("OK")

    if args.delete_source:
        os.remove(args.source)
        print(f"Removed file '{args.source}'.")

    if args.show:
        show(args.destination)
    
if __name__=='__main__':
    main()

