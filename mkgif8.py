#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyfiglet
import ffmpeg
import pyglet
import argparse
from PIL import Image
import random
from colorama import Fore, init, Style
import os
import cv2
from tqdm import tqdm
import hashlib
from pynput import keyboard

init()
color = {0:Fore.RED,1:Fore.GREEN,2:Fore.YELLOW,
         3:Fore.BLUE,4:Fore.CYAN,5:Fore.MAGENTA,6:Fore.WHITE}
 
bright = {0:Style.DIM,1:Style.NORMAL,2:Style.BRIGHT}
 
c_index = color[random.randint(0,6)]
b_index = bright[random.randint(0,2)]
stop = False
done = True

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

def read_video(args):
    global done
    try:
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        print(c_index+b_index+pyfiglet.figlet_format('MKGIF',font='graffiti')+Fore.RESET+Style.RESET_ALL)
        probe = ffmpeg.probe(args.source)
        video_streams = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]
        num_frames = video_streams[0]['nb_frames']

        print("PROCESSING...(PRESS SPACE BAR TO CANCEL)")
        frame_list = []

        cap = cv2.VideoCapture(args.source)
        pbar = tqdm(total=int(num_frames), unit='frames', ncols=100)
        ret = True

        while ret:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_list.append(frame)
                pbar.update(1)

            if stop:
                print(Fore.YELLOW + Style.DIM + "\nFrame processing interrupted by user." + Fore.RESET + Style.RESET_ALL)
                pbar.disable = True
                done = False
                break
        
        cap.release()
        pbar.close()
        listener.stop()
        print('Frames: ', len(frame_list))
        print(stop)
        print(done)
        
    except Exception as e:
        pbar.close()
        listener.stop()
        done = False
        error = str(e)
        print(Fore.RED + Style.DIM + f"\nUNEXPECTED ERROR: {error}" + Fore.RESET + Style.RESET_ALL)
        
def on_press(key):
    global stop
    if key == keyboard.Key.space:
        stop = True
        return False

def calculate_sha1(file_path):
    sha1_hash = hashlib.sha1()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha1_hash.update(byte_block)
    return sha1_hash.hexdigest()
    
def convert_to_gif(args):
    global done
    try:
        print(c_index+b_index+pyfiglet.figlet_format('MKGIF',font='graffiti')+Fore.RESET+Style.RESET_ALL)
        print("CONVERTING WEBP TO GIF...")
        file = Image.open(args.source)
        file.save(args.destination,'gif',save_all=True,background=0)
        file.close()
        size = get_size_format(os.stat(args.destination).st_size)
        print(f"Created '{args.destination}' with size {size} from '{args.source}'.")
    except Exception as e:
        done = False
        error = str(e)
        print(Fore.RED + Style.DIM + f"\nUNEXPECTED ERROR: {error}" + Fore.RESET + Style.RESET_ALL)

def show(f):
    print("GENERATING VIEW...")
    try:
        from pyglet.window import key ######################################################################################
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
    parser = argparse.ArgumentParser(prog="MKGIF 3.1", conflict_handler='resolve',
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
            if file_extension == '.webp':
                args.destination = f"{hash_name}.gif"
            else:
                args.destination = f"{hash_name}{args.speed}{args.size}.gif"

    if file_extension == '.webp':
        if args.size != 100:
            parser.error(Fore.RED+Style.BRIGHT+"-sz/--size spec is not allowed for '.webp' to '.gif' conversion."+Fore.RESET+Style.RESET_ALL)
        else:
            convert_to_gif(args)
    else:
        read_video(args)
        print("STOPPED: ",stop)
        
    if args.delete_source:
        os.remove(args.source)
        print(f"Removed file '{args.source}'.")

    if args.show and done == True:
        show(args.destination)
        #print("TIME TO SHOW")
    
if __name__=='__main__':
    main()

