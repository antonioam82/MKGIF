#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyfiglet
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
 
bright = {0:Style.BRIGHT,1:Style.NORMAL}#2:Style.DIM}
 
c_index = color[random.randint(0,6)]
b_index = bright[random.randint(0,1)]
stop = False
done = True
frame_list = []
 
def check_result_ext(file):
    name, ex = os.path.splitext(file)
    if ex != '.gif':
        raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"result file must be '.gif' ('{ex}' is not valid)."+Fore.RESET+Style.RESET_ALL)
    return file
 
def check_source_ext(file):
    supported_formats = ['.mp4','.avi','.mov','.wmv','.rm','.webp']
    name, ex = os.path.splitext(file)
    if os.path.exists(file):
        if ex not in supported_formats:
            raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"Source file must be '.mp4', '.avi', '.mov', '.wmv', '.rm' or '.webp' ('{ex}' is not valid)."+Fore.RESET+Style.RESET_ALL)
    else:
        raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"FILE NOT FOUND: File '{file}' not found."+Fore.RESET+Style.RESET_ALL)
    return file
 
def create_gif(args,frame_list,w,h,num_frames,video_fps):
    global done
    output_frames = []
    listener = None
    pbar = None

    try:
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
 
        print("\nCREATING YOUR GIF...(PRESS SPACE BAR TO CANCEL)")
 
        pbar = tqdm(total=total_frames, unit='frames', ncols=100) ##############
        factor = args.size/100
 
        for frame in frame_list:
            img = Image.fromarray(frame)
            img = img.resize((int(w * factor), int(h * factor)), Image.LANCZOS)
            output_frames.append(img)
            pbar.update(1)
 
            if stop:
                print(Fore.YELLOW + Style.NORMAL + "\nGif creation interrupted by user." + Fore.RESET + Style.RESET_ALL)
                pbar.disable = True
                done = False
                break
 
        pbar.close()
        listener.stop() ############
        
        if done == True:
            print("\nSAVING YOUR GIF...")
            #print("DURATION: ",1000 // video_fps)
            if args.speed:
                duration = 1000 / (video_fps * (args.speed / 100))
            else:
                duration = 1000 / video_fps
 
            output_frames[0].save(args.destination,save_all=True,append_images=output_frames[1:],
                              optimize=False, duration = duration, loop=0)
 
            size = get_size_format(os.stat(args.destination).st_size)
            print(f"Created gif '{args.destination}' with size '{size}' from '{args.source}'.")

    except Exception as e:
        if pbar:
            pbar.close()
        if listener and listener.is_alive():
            listener.stop()
        done = False
        error = str(e)
        print(Fore.RED + Style.BRIGHT + f"\nUNEXPECTED ERROR: {error}" + Fore.RESET + Style.RESET_ALL)
    #print("ALL DONE!")
    '''if listener and not listener.is_alive():
        print("Listener has been successfully closed.")'''
 
def read_video(args):
    global done, frame_list, width, height, num_frames, video_fps, total_frames
    pbar = None
    listener = None
    try:
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        print(c_index+b_index+pyfiglet.figlet_format('MKGIF',font='graffiti')+Fore.RESET+Style.RESET_ALL)
        cap = cv2.VideoCapture(args.source)

        num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video_fps = cap.get(cv2.CAP_PROP_FPS)#
        duration = num_frames / video_fps #################################

        initial_frame = args.from_frame
        if args.to_frame:
            final_frame = int(args.to_frame)
        else:
            final_frame = int(num_frames)

        
        if (initial_frame >= 0 and initial_frame <= num_frames) and (final_frame > 0 and final_frame <= num_frames) and (initial_frame < final_frame):
            cap.set(cv2.CAP_PROP_POS_FRAMES,initial_frame)###########################
            total_frames = abs(num_frames - initial_frame) - abs(final_frame - num_frames)#########
            print("SOURCE VIDEO DATA:")
            print(f'NUMBER OF FRAMES: {num_frames} | WIDTH: {width} | HEIGHT: {height} | FRAME RATE: {video_fps} | DURATION: {duration}\n')
 
            print("PROCESSING...(PRESS SPACE BAR TO CANCEL)")
 
            pbar = tqdm(total=int(total_frames), unit='frames', ncols=100)
            ret = True
 
            while ret:
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_list.append(frame)
                    pbar.update(1)
                
                if args.to_frame:
                    current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                    if current_frame >= final_frame:
                        break
 
                if stop:
                    print(Fore.YELLOW + Style.NORMAL + "\nFrame processing interrupted by user." + Fore.RESET + Style.RESET_ALL)
                    pbar.disable = True
                    done = False
                    break
                
            cap.release()
            pbar.close()
            listener.stop()
        else:
            print(Fore.RED+Style.BRIGHT+"Invalid index for initial or final frame."+Fore.RESET+Style.RESET_ALL)
            #stop = True
            done = False
 
    except Exception as e:
        if pbar:
            pbar.close()
        if listener:
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
    print("GENERATING VIEW -PRESS 'ESC' TO CLOSE THE WINDOW-")
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

        #CERRAR VENTANA AL PRESIONAR 'ESC'
        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.ESCAPE:
                window.close()
 
        pyglet.app.run()
        print(f"Successfully generated view from '{f}'.")
    except Exception as e:
        error = str(e)
        print(Fore.RED+Style.BRIGHT+f"UNEXPECTED ERROR: {error}"+Fore.RESET+Style.RESET_ALL)
 
def check_positive(v):
    ivalue = float(v)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"speed and size values must be positive ('{v}' is not valid)."+Fore.RESET+Style.RESET_ALL)
    return ivalue

def check_initial(v):
    ivalue = int(v)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(Fore.RED+Style.BRIGHT+f"initial frame position must be greater or equal to 0 ('{v}' is not valid)."+Fore.RESET+Style.RESET_ALL)
    return ivalue
 
def get_size_format(b, factor=1024, suffix="B"):
    for unit in ["","K","M","G","T","P","E","Z"]:
        if b < factor:
            return f"{b:.4f}{unit}{suffix}"
        b /= factor
    return f"{b:.4f}Y{suffix}"
 
def main():
    parser = argparse.ArgumentParser(prog="MKGIF 3.2", conflict_handler='resolve',
                                     description="Create gifs from videos in command line or convert '.webp' files into '.gif'.",
                                     epilog = "REPO: https://github.com/antonioam82/MKGIF",allow_abbrev=False)
 
    parser.add_argument('-src','--source',required=True,type=check_source_ext,help='Source file name')
    parser.add_argument('-dest','--destination',type=check_result_ext,default=None,help="Destination file name")
    parser.add_argument('-sz','--size',default=100,type=check_positive,help='Relative size of the gif (100 by default)')
    parser.add_argument('-delsrc','--delete_source',action='store_true',help='Generate gif and remove source file')
    parser.add_argument('-fps','--frames_per_second',default=None,type=check_positive,help='Duration of the gif')
    parser.add_argument('-spd', '--speed', default=100, type=check_positive, help='Speed of the gif as a percentage of the original (100 by default)')
    parser.add_argument('-shw','--show',action='store_true',help='Show result file')
    parser.add_argument('-from','--from_frame',default=0,type=check_initial, help='Starting frame')
    parser.add_argument('-to','--to_frame',default=None,type=check_positive,help='Ending frame')
 
    args = parser.parse_args()
    name, file_extension = os.path.splitext(args.source)
 
    if args.destination is None:
            hash_name = calculate_sha1(args.source)
            if file_extension == '.webp':
                args.destination = f"{hash_name}.gif"
            else:
                if args.speed:
                    speed = int(args.speed)
                else:
                    speed = 0
                size = int(args.size)
                args.destination = f"{hash_name}{speed}{size}.gif"
 
    if file_extension == '.webp':
        if args.size != 100 or args.speed != 100 or args.frames_per_second or args.to_frame or args.from_frame != 0:
            parser.error(Fore.RED+Style.BRIGHT+"size, speed, fps and from/to frames specs is not allowed for '.webp' to '.gif' conversion."+Fore.RESET+Style.RESET_ALL)
        else:
            convert_to_gif(args)
    else:
        read_video(args)
        #print("STOPPED: ",stop)
        #print("NUMBER OF FRAMES: ",len(frame_list))
        if not stop and done:
            create_gif(args,frame_list,width,height,num_frames,video_fps)
            #print("ok")
 
    if args.delete_source:
        os.remove(args.source)
        print(f"Removed file '{args.source}'.")
 
    if args.show and done == True:
        show(args.destination)
 
if __name__=='__main__':
    main()
