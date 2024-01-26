import argparse
import os
import sys

import libscrrec
import debug
debug.set_mode(True)

def validate_folder(*w,**kw):
	for _dir in w:
		_dir=os.path.expanduser(_dir)
		if not os.path.isdir(_dir):
			return None
		else:
			return _dir



parser = argparse.ArgumentParser()
parser.add_argument('-D','--debug',action='store_true',help='enable debug messages')

parser.add_argument('--path',type=validate_folder, default='~/Videos',help='folder to save video (default: ~/Videos)')
parser.add_argument('--filename',default=None,help='record filename (default: com.package.name_yyyyddmm_hhmmss.mkv)')

parser.add_argument('--wait-for-package',default=None,type=str,help='wait package activity start')
parser.add_argument('--wait-for-device',action='store_true',help='wait for device connect')

parser.add_argument('--list-encoders',action='store_true',help='list encoders you can use')

parser.add_argument('--video-codec',default='',help='video codec')
parser.add_argument('--video-encoder', default='',help='video encoder')
parser.add_argument('--video-playback',action='store_false',help='enable video on pc screen')
parser.add_argument('--video-source',default='display',choices=['display','camera'],help='video source')


parser.add_argument('--audio-codec',default='',help='audio codec')
parser.add_argument('--audio-encoder', default='',help='audio encoder')
parser.add_argument('--audio-source', default='output',choices=['output','mic'],help='audio source')
parser.add_argument('--require-audio',action='store_false',help='requires audio to work')
parser.add_argument('--no-audio-playback',action='store_true',help='disable audio on pc')

parser.add_argument('--control',action='store_false',help='disable control')


args=parser.parse_args()

if args.list_encoders:
	encoders=libscrrec.get_encoder_list()
	for _type in encoders:
		print(f"{_type}:")
		codecs=encoders[_type]
		for k,v in codecs.items():
			print(f"{k}:",' '.join(v))
		print('')

	exit()

wait_for_device=args.wait_for_device
wait_for_package=args.wait_for_package
path=args.path
filename=args.filename
video_codec=args.video_codec
video_encoder=args.video_encoder
audio_codec=args.audio_codec
audio_encoder=args.audio_encoder
require_audio=args.require_audio
no_audio_playback=args.no_audio_playback
no_video_playback=args.video_playback
control=args.control

debug.debug('debug mode:',debug.get_mode())
debug.debug('wait_for_device:',wait_for_device)
debug.debug('wait_for_package:',wait_for_package)
debug.debug('path:',path)
debug.debug('filename:',filename)
debug.debug('video_codec:',video_codec)
debug.debug('video_encoder:',video_encoder)
debug.debug('no_video_playback:',no_video_playback)
debug.debug('audio_codec:',audio_codec)
debug.debug('audio_encoder:',audio_encoder)
debug.debug('require_audio:',require_audio)
debug.debug('no_audio_playback:',no_audio_playback)
debug.debug('no_control:',control)



if wait_for_device:
	debug.debug('waiting for device connect...')
	libscrrec.wait_for_device()
if wait_for_package:
	debug.debug('waiting for package:',wait_for_package)
	libscrrec.wait_for_package_activity(wait_for_package)

debug.debug('getting activity package name')
pkg_name=libscrrec.get_current_activity_package_name()
debug.debug('activity package name:',pkg_name)

if filename is None:
	debug.debug('generating filename for record')
	filename=libscrrec.get_record_filename(pkg_name,path)
debug.debug('record filename:',filename)

debug.debug('creating record command...')
record_command=libscrrec.set_record(path,filename,require_audio=require_audio,no_audio_playback=no_audio_playback,no_video_playback=no_video_playback,no_control=control,
	video_codec=video_codec,video_encoder=video_encoder,audio_codec=audio_codec,audio_encoder=audio_encoder)

debug.debug(record_command)
debug.debug('starting record...')

exit_code=libscrrec.start_record(record_command)
if exit_code==0:
	debug.debug('exit code:',exit_code)
elif exit_code==1:
	debug.error('exit code:',exit_code)
else:
	debug.warn('exit code:',exit_code)