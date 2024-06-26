#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyfiglet
import ffmpeg
import pyglet
from pyglet.window import key
import argparse
from PIL import Image
import random
import subprocess
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
    parser = argparse.ArgumentParser(prog="MKGIF 3.0",conflict_handler='resolve',
                                     description="Create gifs from videos in command line or convert '.webp' files into '.gif'.",
                                     epilog = "REPO: https://github.com/antonioam82/MKGIF")
    parser.add_argument('-src','--source',required=True,type=check_source_ext,help='Source file name')
    parser.add_argument('-dest','--destination',default='my_gif.gif',type=check_result_ext,help="Destination file name ('my_gif.gif' by default)")
    parser.add_argument('-st','--start',default=0.0,type=check_time,help='Initial second of the gif')
    parser.add_argument('-shw','--show',help='Generate gif and display the result',action='store_true')
    parser.add_argument('-sz','--size',default=100,type=check_positive,help='Relative size of the gif (100 by default)')
    #parser.add_argument('-fps','--fraps',default=None,type=check_positive,help='Frames per second')
    parser.add_argument('-delsrc','--delete_source',action='store_true',help='Generate gif and remove source file')########
    parser.add_argument('-dur','--duration',default=None,type=float,help='Result file duration')
    
    args=parser.parse_args()
    name, file_extension = os.path.splitext(args.source)
 
    if file_extension == '.webp':
        if args.start != 0.0 or args.duration is not None or args.size != 100:
            parser.error(Fore.RED+Style.BRIGHT+"-st/--start, -sz/--size and -dur/--duration specs not allowed for '.webp' to '.gif' conversion."+Fore.RESET+Style.RESET_ALL)
    else:
        probe = ffmpeg.probe(args.source)
        video_streams = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]
 
        #if args.start > args.duration:
            #parser.error(Fore.RED+Style.BRIGHT+"start value must be smaller than end value."+Fore.RESET+Style.RESET_ALL)
 
    gm(args)
 
 
def check_time(val):
    time = float(val)
    if time < 0.0:
        raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"time values must be equal or bigger than 0.00 ('{val}' is not valid)."+Fore.RESET+Style.RESET_ALL)
    return time
 
def check_positive(val):
    ivalue = float(val)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"speed and size values must be positive ('{val}' is not valid)."+Fore.RESET+Style.RESET_ALL)
    return ivalue
 
def check_source_ext(file):
    supported_formats = ['.mp4','.avi','.mov','.wmv','.rm','.webp']
    #file_extension = pathlib.Path(file).suffix#
    name, file_extension = os.path.splitext(file)
    if file in os.listdir():
        if file_extension not in supported_formats:
            raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"Source file must be '.mp4', '.avi', '.mov', '.wmv', '.rm' or '.webp' ('{file_extension}' is not valid)."+Fore.RESET+Style.RESET_ALL)
    else:
        raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"FILE NOT FOUND: File '{file}' not found."+Fore.RESET+Style.RESET_ALL)
    return file
 
def check_result_ext(file):
    #file_extension = pathlib.Path(file).suffix
    name, ex = os.path.splitext(file)
    c = 0
    if ex != '.gif':
        raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"result file must be '.gif' ('{ex}' is not valid)."+Fore.RESET+Style.RESET_ALL)
    ###########################
    else:
        for i in os.listdir():
            if i == file:
                c+=1
        if c > 0:
            return name + str(c) + ex
        else:
            return name + ex
    ###########################
 
def show(f,w,h):
    print("GENERATING VIEW...")
    try:
        animation = pyglet.image.load_animation(f)
        binm = pyglet.image.atlas.TextureBin()
        animation.add_to_texture_bin(binm)
        window = pyglet.window.Window(int(w),int(h),'GIF VIEW')
        sprite = pyglet.sprite.Sprite(animation)

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

def generate_gif(video_input, gif_output, start_time, duration, width, height, frame_rate):

    comand = ['ffmpeg', '-y', '-i', video_input]
    
    if start_time:
        comand.extend(['-ss', str(start_time)])
    if duration:
        comand.extend(['-t', str(duration)])
    
    opciones_vf = ['fps={}'.format(frame_rate)]
    opciones_vf.append('scale={}:{}'.format(width, height))
    
    comand.extend(['-r', str(frame_rate), '-vf', ','.join(opciones_vf)])
    comand.append(gif_output)
    subprocess.call(comand)
    

def gm(args):
    try:
        if file_extension != '.webp':

            ###########################################################
            probe = ffmpeg.probe(args.source)
            video_streams = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]

            width = video_streams[0]['width'] * args.size / 100
            height = video_streams[0]['height'] * args.size / 100
            if args.duration:
                duration = args.duration
            else:
                duration = video_streams[0]['duration'] 

            '''if args.fraps:
                frame_rate = args.fraps
            else:'''
            
            frame_rate = video_streams[0]['avg_frame_rate']
            print(Fore.YELLOW + ("WIDTH: {} | HEIGHT: {} | FRAME RATE: {} | DURATION: {}"  + Fore.RESET).format(width, height, frame_rate, duration))
            #############################################################
            
            generate_gif(args.source,args.destination,args.start,duration,width,height,frame_rate)##########
            print(c_index+b_index+pyfiglet.figlet_format('MKGIF',font='graffiti')+Fore.RESET+Style.RESET_ALL)
            size = get_size_format(os.stat(args.destination).st_size)
            print(f"Created gif '{args.destination}' with size {size}.")
 
        else:
            print("CONVERTING...")
            file = Image.open(args.source)
            width, height = file.size
            file.save(args.destination,'gif',save_all=True,background=0)
            
            file.close()
            size = get_size_format(os.stat(args.destination).st_size)
            print(c_index+b_index+pyfiglet.figlet_format('MKGIF',font='graffiti')+Fore.RESET+Style.RESET_ALL)
            print(f"Created '{args.destination}' with size {size} from '{args.source}'.")
 
        if args.delete_source:
            os.remove(args.source)
            print(f"Removed file '{args.source}'.")
 
        if args.show:
            show(args.destination,width,height)
 
    except Exception as e:
        print("UNEXPECTED ERROR: "+str(e))
 
if __name__=='__main__':
    main()
