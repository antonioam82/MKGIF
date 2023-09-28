#!/usr/bin/env python
# -*- coding: utf-8 -*-
from moviepy.editor import VideoFileClip
from PIL import Image
import pyfiglet
import ffmpeg
import pyglet
import pathlib
from pyglet.window import key
import argparse
import random
from colorama import Fore, init, Style
import os
 
init()
color = {0:Fore.RED,1:Fore.GREEN,2:Fore.YELLOW,
         3:Fore.BLUE,4:Fore.CYAN,5:Fore.MAGENTA,6:Fore.WHITE}
 
bright = {0:Style.DIM,1:Style.NORMAL,2:Style.BRIGHT}
 
c_index = color[random.randint(0,6)]
b_index = bright[random.randint(0,2)]
 
def main():
    global file_extension
    parser = argparse.ArgumentParser(prog="MKGIF 2.1.1",conflict_handler='resolve',
                                     description="Create gifs from videos in command line or convert '.webp' files into '.gif'.",
                                     epilog = "REPO: https://github.com/antonioam82/MKGIF")
    parser.add_argument('-src','--source',required=True,type=check_source_ext,help=Fore.YELLOW + Style.DIM + 'Name of source file.' + Fore.RESET + Style.RESET_ALL)
    parser.add_argument('-dest','--destination',default='my_gif.gif',type=check_result_ext,help=Fore.YELLOW + Style.DIM + "Nane of new file ('my_gif.gif' by default')." + Fore.RESET + Style.RESET_ALL)
    parser.add_argument('-st','--start',default=0.0,type=check_time,help=Fore.YELLOW + Style.DIM + 'Initial second of the gif.' + Fore.RESET + Style.RESET_ALL)
    parser.add_argument('-e','--end',default=None,type=check_time,help=Fore.YELLOW + Style.DIM + 'Final second of the gif.' + Fore.RESET + Style.RESET_ALL)
    parser.add_argument('-shw','--show',help=Fore.YELLOW + Style.DIM + 'Show created gif.'+ Fore.RESET + Style.RESET_ALL,action='store_true')
    parser.add_argument('-sz','--size',default=100,type=check_positive,help=Fore.YELLOW + Style.DIM + 'Relative size (100 by default).' + Fore.RESET + Style.RESET_ALL)
    parser.add_argument('-spd','--speed',default=100,type=check_positive,help=Fore.YELLOW + Style.DIM + 'Relative speed (100 by default).' + Fore.RESET + Style.RESET_ALL)
    parser.add_argument('-fps','--fraps',default=None,type=int,help=Fore.YELLOW + Style.DIM + 'Frames per second.' + Fore.RESET + Style.RESET_ALL)
    parser.add_argument('-delsrc','--delete_source',action='store_true',help=Fore.YELLOW + Style.DIM + 'Create gif and remove source file.' + Fore.RESET + Style.RESET_ALL)
 
    args=parser.parse_args()
    file_extension = pathlib.Path(args.source).suffix
 
    if file_extension == '.webp':
        if args.start != 0.0 or args.end is not None or args.speed != 100 or args.size != 100:
            parser.error(Fore.RED+Style.BRIGHT+"-st/--start, -e/--end, -sz/--size and -spd/--speed specs not allowed for '.webp' to '.gif' conversion."+Fore.RESET+Style.RESET_ALL)
    else:
        probe = ffmpeg.probe(args.source)
        video_streams = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]
 
        if args.end:
            args.end = float(args.end)
        else:
            args.end = float(video_streams[0]['duration'])
 
        if args.start > args.end:
            parser.error(Fore.RED+Style.BRIGHT+"start value must be smaller than end value."+Fore.RESET+Style.RESET_ALL)
 
    gm(args)
 
 
def check_time(val):
    time = float(val)
    if time < 0.0:
        raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"time values must be equal or bigger than 0.00 ('{val}' is not valid)."+Fore.RESET+Style.RESET_ALL)
    return time
 
def check_positive(val):
    ivalue = int(val)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"speed and size values must be positive ('{val}' is not valid)."+Fore.RESET+Style.RESET_ALL)
    return ivalue
 
def check_source_ext(file):
    supported_formats = ['.mp4','.avi','.mov','.wmv','.rm','.webp']
    file_extension = pathlib.Path(file).suffix
    if file in os.listdir():
        if file_extension not in supported_formats:
            raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"Source file must be '.mp4', '.avi', '.mov', '.wmv', '.rm' or '.webp' ('{file_extension}' is not valid)."+Fore.RESET+Style.RESET_ALL)
    else:
        raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"FILE NOT FOUND: File '{file}' not found."+Fore.RESET+Style.RESET_ALL)
    return file
 
def check_result_ext(file):
    file_extension = pathlib.Path(file).suffix
    if file_extension != '.gif':
        raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"result file must be '.gif' ('{file_extension}' is not valid)."+Fore.RESET+Style.RESET_ALL)
    return file
 
def show(f):
    print("GENERATING VIEW...")
    try:
        animation = pyglet.image.load_animation(f)
        bin = pyglet.image.atlas.TextureBin()
        animation.add_to_texture_bin(bin)
        sprite = pyglet.sprite.Sprite(animation)
        w = sprite.width
        h = sprite.height
        window = pyglet.window.Window(width=w, height=h)
 
        @window.event
        def on_draw():
            sprite.draw()
        pyglet.app.run()
        print(f"Successfully generated view from '{f}'.")
    except Exception as e:
        print("UNEXPECTED ERROR: ",str(e))
 
def get_size_format(b, factor=1024, suffix="B"):
	for unit in ["","K","M","G","T","P","E","Z"]:
	    if b < factor:
	        return f"{b:.4f}{unit}{suffix}"
	    b /= factor
	return f"{b:.4f}Y{suffix}"
 
def gm(args):
    print(c_index+b_index+pyfiglet.figlet_format('MKGIF',font='graffiti')+Fore.RESET+Style.RESET_ALL)
    try:
        if file_extension != '.webp':
            clip = (VideoFileClip(args.source,audio=False)
            .subclip((0,args.start),
                     (0,args.end))
            .resize(args.size/100)
            .speedx(args.speed/100))
            print('CREATING GIF...')
            clip.write_gif(args.destination,fps=args.fraps)
            clip.close()
            size = get_size_format(os.stat(args.destination).st_size)
            print(f"Created gif '{args.destination}' with size {size}.")
 
        else:
            print("CONVERTING...")
            file = Image.open(args.source)
            file.save(args.destination,'gif',save_all=True,background=0)
            file.close()
            size = get_size_format(os.stat(args.destination).st_size)
            print(f"Created '{args.destination}' with size {size} from '{args.source}'.")

        if args.delete_source:
            os.remove(args.source)
            print(f"Removed file '{args.source}'.")
 
        if args.show:
            show(args.destination)
 
    except Exception as e:
        print("UNEXPECTED ERROR: "+str(e))
 
if __name__=='__main__':
    main()
