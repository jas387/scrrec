#!/usr/bin/env python3

import os
import sys
from datetime import datetime
import time
import subprocess

SCRCPY_VERSION='2.3.1' # work with this version of scrcpy
ADB_VERSION='1.0.41' # work with this version of adb

def get_adb_version():
    return os.popen('adb --version').read().splitlines()[0].split(' ')[-1]
def get_scrcpy_version():
    return os.popen('scrcpy --version').read().splitlines()[0].split(' ')[1]

def check_versions():
    # check if executable are in correct format
    return get_adb_version()==ADB_VERSION and get_scrcpy_version()==SCRCPY_VERSION

def get_current_activity_package_name():
    recents_activity = os.popen('adb shell "dumpsys activity recents"').read().splitlines()
    for line_index in range(len(recents_activity)):
        line_text=recents_activity[line_index]
        if line_text.find("Recent #0")!=-1:
            name="".join([i.split(":")[1] for i in line_text.split(" ") if i.startswith("A=")])
            return name
    return None
def get_record_filename(package_name:str, path: str='~/Videos'):
    sufix_datetime =datetime.now().strftime("_%Y%d%m_%H%M%S.mkv")
    name = package_name+sufix_datetime
    return f'{name}'

def set_record(path:str,filename:str, require_audio=True,no_audio_playback=False,no_video_playback=True,no_control=True,
    video_codec='h264',video_encoder='OMX.MTK.VIDEO.ENCODER.AVC',
    audio_codec='aac',audio_encoder='OMX.google.aac.encoder',*w):
    require_audio='' if not require_audio else '--require-audio'
    no_audio_playback='' if not no_audio_playback else '--no-audio-playback'
    no_video_playback='' if not no_video_playback else '--no-video-playback'
    no_control='' if not no_control else '--no-control'

    return f"scrcpy {require_audio} {no_audio_playback} {no_video_playback} {no_control} \
    --video-codec={video_codec} --video-encoder='{video_encoder}' \
    --audio-codec={audio_codec} --audio-encoder='{audio_encoder}' --record=\"{path}/{filename}\" "+' '.join(w)

def start_record(command: str):
    try:
        process=subprocess.run([command],shell=True)
        return process.returncode
    except KeyboardInterrupt:
        return 2
    return 3

def get_encoder_list():
    data=[i.strip() for i in os.popen('scrcpy --list-encoders').read().splitlines()]
    vidx=data.index('[server] INFO: List of video encoders:')
    aidx=data.index('[server] INFO: List of audio encoders:')
    video_codecs=data[vidx+1:aidx]
    audio_codecs=data[aidx+1:]
    aidx=[audio_codecs.index(i) for i in audio_codecs if i.startswith('scrcpy')][0]
    audio_codecs=audio_codecs[:aidx]
    codecs={'video':dict({}),'audio':dict({})} # dict as {audio:{codec:set(encoders)},video:{codec:set(encoders)}}
    
    for video_codec in video_codecs:
        codec,encoder=[line.split('=')[1] for line in video_codec.split()]
        encoder=encoder[1:-1] # remove '' from string
        if codec not in codecs['video'].keys():
            codecs['video'][codec]=set({})
        codecs['video'][codec].add(encoder)
    for audio_codec in audio_codecs:
        codec,encoder=[line.split('=')[1] for line in audio_codec.split()]
        encoder=encoder[1:-1] # remove '' from string
        if codec not in codecs['audio'].keys():
            codecs['audio'][codec]=set({})
        codecs['audio'][codec].add(encoder)
    return codecs

def get_codecs(_dict,mode):
    return tuple(_dict[mode].keys())

def get_encoders(_dict,mode):
    encoders=set({})
    for codec in _dict[mode].keys():
        for encoder in _dict[mode][codec]:
            encoders.add(encoder)
    return tuple(encoders)

def get_encoder(_dict,mode,codec):
    return _dict[mode][codec]
   
def wait_for_package_activity(package: str):
    current=None
    while current!=package:
        try:
            time.sleep(0.2)
            current=get_current_activity_package_name()
        except KeyboardInterrupt:
            return False
    return True