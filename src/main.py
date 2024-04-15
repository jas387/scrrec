import os
import signal
import threading
import subprocess
import asyncio
import flet
import libscrrec


class App:
	def __init__(self, *w, width:int=None, height:int=None, **kw):
		self._width = width
		self._height = height
		self._dict = None
		self._displays = []
		self._cameras = []
		self._playbacks = ('output',)
		self._mics = ('mic',)
		self._video_sources = ('display','camera')
		self._audio_sources = ('output','mic')
		self._record_process = None # subprocessing.Popen - None if not recording
		self._is_recording = False

	def target(self, page: flet.Page):
		self.page = page
		page.window_max_width = self._width
		page.window_max_height = self._height
		# top
		self.get_device_info = flet.ElevatedButton('get device info', on_click=self._get_device_info, expand=True)
		self.video = flet.Checkbox(label='video', value=True)
		self.video_playback = flet.Checkbox(label='video playback', value=False)
		self.audio = flet.Checkbox(label='audio', value=True)
		self.audio_playback = flet.Checkbox(label='audio playback', value=True)
		self.control = flet.Checkbox(label='control', value=False)

		# sessions
		self.video_callback = SessionCallback(self.on_video_source,self.on_video_source_id,self.on_video_codec,self.on_video_encoder,self.on_video_codec_options)
		self.audio_callback = SessionCallback(self.on_audio_source,self.on_audio_source_id,self.on_audio_codec,self.on_audio_encoder,self.on_audio_codec_options)

		self.video_session = Session(self.video_callback,'video','red',)
		self.audio_session = Session(self.audio_callback,'audio','green')

		# start record
		self.start_record = flet.ElevatedButton(text='start',disabled=True,on_click=self._start_record,expand=True)

		#
		numeric_filter=flet.InputFilter('^[0-9]*')
		self.max_resolution_size=flet.TextField(label='--max-size',value='',expand=False,input_filter=numeric_filter)
		self.home_view = flet.Column(alignment=flet.MainAxisAlignment.START,horizontal_alignment=flet.CrossAxisAlignment.CENTER,controls=[
			flet.Row(controls=[self.get_device_info]),
			flet.Row(controls=[self.video,self.video_playback,self.audio,self.audio_playback,self.control],alignment=flet.MainAxisAlignment.CENTER),
			self.video_session,
			self.max_resolution_size
		])
		page.add(self.home_view)
		page.add(self.audio_session,flet.Row([self.start_record]))
		self.status_bar = flet.TextField(read_only=True,expand=True,disabled=False,autofocus=True,multiline=True,min_lines=20)
		page.add(flet.SafeArea(expand=True,content=self.status_bar))

	def _get_device_info(self, event):
		self.get_device_info.disabled = True
		self.get_device_info.update()
		_dict = libscrrec.get_encoder_list()
		self._dict = _dict  # never get this button 
		self._displays = tuple(map(lambda x: ' '.join(x),libscrrec.get_displays()))
		self._cameras = tuple(map(lambda x: ' '.join(x),libscrrec.get_cameras()))
		self._playbacks = ('playback',)
		self._mics = ('mic',)
		self._update_info()
		self.get_device_info.disabled = False
		self.get_device_info.update()
	
	def _update_info(self):
		self._update_video_session()
		self._update_audio_session()	
		self.page.update()
		self.start_record.disabled = False
		self.start_record.update()	

	def _update_video_session(self):
		self.video_session.clear()
		# video
		self.video_session.add_source(self._video_sources)
		self.video_session.set_option(self.video_session.source,0)
		self.video_session.add_source_id(self._displays)
		self.video_session.set_option(self.video_session.source_id,0)
		codecs = libscrrec.get_codecs(self._dict, 'video')
		self.video_session.add_codec(codecs)
		self.video_session.set_option(self.video_session.codec,0)
		encoders = libscrrec.get_encoder(self._dict, 'video',self.video_session.get_current(self.video_session.codec))
		self.video_session.add_encoder(encoders)
		self.video_session.set_option(self.video_session.encoder,0)
		self.video_session.update()

	def _update_audio_session(self):
		self.audio_session.clear()
		# audio
		self.audio_session.add_source(self._audio_sources)
		self.audio_session.set_option(self.audio_session.source,0)
		# displays = map(lambda x: ' '.join(x),libscrrec.get_displays())
		playbacks = self._playbacks
		self.audio_session.add_source_id(playbacks)
		self.audio_session.set_option(self.audio_session.source_id,0)
		codecs = libscrrec.get_codecs(self._dict, 'audio')
		self.audio_session.add_codec(codecs)
		self.audio_session.set_option(self.audio_session.codec,0)
		encoders = libscrrec.get_encoder(self._dict, 'audio',self.audio_session.get_current(self.audio_session.codec))
		self.audio_session.add_encoder(encoders)
		self.audio_session.set_option(self.audio_session.encoder,0)
		self.audio_session.update()	

	def on_video_source(self, *w, **kw):
		source = self.video_session.source
		source_id = self.video_session.source_id
		self.video_session.clear_source_id()
		func = None
		if source.value == 'display':
			func = self._displays
			self.video_session.add_codec(libscrrec.get_codecs(self._dict, 'video'))
			self.video_session.add_encoder(libscrrec.get_encoders(self._dict, 'video'))
		elif source.value == 'camera':
			func = self._cameras
			self.video_session.clear_codec()
			self.video_session.clear_encoder()
		
		ids = func
		self.video_session.add_source_id(ids)
		self.video_session.set_option(source_id,0)
		self.video_session.update()

	def on_video_source_id(self, *w, **kw):
		pass
	
	def on_video_codec(self, *w, **kw):
		codec = self.video_session.codec
		encoder = self.video_session.encoder
		self.video_session.clear_encoder()
		current_codec = self.video_session.get_current(codec)
		self.video_session.add_encoder(libscrrec.get_encoder(self._dict, 'video', current_codec))
		self.video_session.set_option(encoder,0)
		self.video_session.update()
	
	def on_video_encoder(self, *w, **kw):
		pass
	def on_video_codec_options(self, *w, **kw):
		pass

	# audio
	def on_audio_source(self, *w, **kw):
		source = self.audio_session.source
		source_id = self.audio_session.source_id
		self.audio_session.clear_source_id()
		func = None
		if source.value == 'output':
			func = self._playbacks
			self.audio_session.add_codec(libscrrec.get_codecs(self._dict, 'audio'))
			self.audio_session.add_encoder(libscrrec.get_encoders(self._dict, 'audio'))
		elif source.value == 'mic':
			func = self._mics
			self.audio_session.clear_codec()
			self.audio_session.clear_encoder()
		
		ids = func
		self.audio_session.add_source_id(ids)
		self.audio_session.set_option(source_id,0)
		self.audio_session.update()
	
	def on_audio_source_id(self, *w, **kw):
		pass
	
	def on_audio_codec(self, *w, **kw):
		codec = self.audio_session.codec
		encoder = self.audio_session.encoder
		self.audio_session.clear_encoder()
		current_codec = self.audio_session.get_current(codec)
		self.audio_session.add_encoder(libscrrec.get_encoder(self._dict, 'audio', current_codec))
		self.audio_session.set_option(encoder,0)
		self.audio_session.update()
	
	def on_audio_encoder(self, *w, **kw):
		pass

	def on_audio_codec_options(self, *w, **kw):
		pass
	

	def _start_record(self, event):
		print('process:',self._record_process)
		if not self._is_recording:
			self.start_record.text = 'stop'
			self.start_record.update()
			self.home_view.disabled = True
			self.home_view.update()

			video_source = self.video_session.source.value
			video_ident = self.video_session.source_id.value
			video_codec = self.video_session.codec.value
			video_encoder = self.video_session.encoder.value
			video_codec_options = self.video_session.codec_options.value
			max_resolution_size = self.max_resolution_size.value

			audio_source = self.audio_session.source.value
			audio_ident = self.audio_session.source_id.value
			audio_codec = self.audio_session.codec.value
			audio_encoder = self.audio_session.encoder.value
			audio_codec_options = self.audio_session.codec_options.value
			

			record_video = self.video.value
			record_audio = self.audio.value
			playback_video = self.video_playback.value
			playback_audio = self.audio_playback.value
			control = self.control.value

			def on_record_start(*w, **kw):	
				while self._record_process!=None:
					stdout, stderr = self._record_process.stdout, self._record_process.stderr
					stdout = stdout.read()
					stderr = stderr.read()
					self.status_bar.value += f'DEBUG: {stdout}\n'
					self.status_bar.value += f'ERROR: {stderr}\n\n'
					self.status_bar.update()
					self.page.update()
					if isinstance(self._record_process,subprocess.CompletedProcess) or self._record_process is None:
						self._record_process = None
						self.start_record.text = 'start'
						self.start_record.update()
						self.home_view.disabled = False
						self.home_view.update()
						break
					else:
						self._record_process.communicate()
			self._is_recording = True
			cmd = self.craft_record_command(video_source, video_codec, video_encoder, video_ident, video_codec_options, max_resolution_size, audio_source, audio_codec, audio_encoder, audio_ident, audio_codec_options, record_video, record_audio, playback_audio, playback_video, control)
			print('cmd:',cmd)
			self._record_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE,preexec_fn=os.setsid)
			td = threading.Thread(target=on_record_start)
			td.start()


		else:
			print('killing process')
			self._is_recording = False
			self.start_record.text = 'start'
			self.start_record.update()
			self.home_view.disabled = False
			self.home_view.update()
			#os.killpg(os.getpgid(self._record_process.pid), signal.SIGTERM)
			self._record_process.kill()
			self._record_process = None
			os.system('killall scrcpy')		


	def craft_record_command(self, video_source, video_codec, video_encoder, video_ident, video_codec_options, max_resolution_size,
		audio_source, audio_codec, audio_encoder, audio_ident, audio_codec_options,
		record_video, record_audio, playback_audio, playback_video, control):
		cmd='scrcpy '
		# source video
		if record_video:
			if video_source!='':
				cmd+=f'--video-source="{video_source}" '
				if video_source=='display':
					if video_ident!='':
						_id,res=video_ident.split()
						cmd+=f'--display-id="{_id}" '
				elif video_source=='camera':
					if video_ident!='':
						_id,name,res,fps=video_ident.split()
						cmd+=f'--camera-id="{_id}" --camera-fps="{fps}" --camera-size="{res}" '
				if video_codec_options!='':
					cmd+=f'--video-codec-options="{video_codec_options}" '
				if max_resolution_size!='':
					cmd+=f'--max-size={max_resolution_size} '
			else:
				cmd+='--video-source="display" '
			if video_codec!='':
				cmd+=f'--video-codec="{video_codec}" '
			if video_encoder!='':
				cmd+=f'--video-encoder="{video_encoder}" '
			if not playback_video:
				cmd+=f'--no-video-playback '
		else:
			cmd+=f'--no-video '
		# audio
		if record_audio:
			cmd+=f'--require-audio '
			if audio_source!='':
				cmd+=f'--audio-source="{audio_source}" '
			else:
				cmd+=f'--audio-source="output" '
			# codec
			if audio_codec!='':
				cmd+=f'--audio-codec="{audio_codec}" '
			# encoder
			if audio_encoder!='':
				cmd+=f'--audio-encoder="{audio_encoder}" '
			if not playback_audio:
				cmd+=f'--no-audio-playback '

			if audio_codec_options!='':
				cmd+=f'--audio-codec-options="{audio_codec_options}" '
		else:
			cmd+=f'--no-audio '
		if not control:
			cmd+=f'--no-control '
		# record
		if record_video or record_audio:
			pkg = libscrrec.get_current_activity_package_name()
			folder=os.path.expanduser("~/Videos")
			if not os.path.isdir(folder):
				os.mkdir(folder)
			filename=libscrrec.get_record_filename(pkg,folder)
			file_ext=libscrrec.get_record_file_ext(video_codec,audio_codec)
			cmd+=f'--record="{folder}/{filename}.{file_ext}" '
		return cmd

class SessionCallback:
	def __init__(self, source, source_id, codec, encoder,codec_options):
		self.source = source
		self.source_id = source_id
		self.codec = codec
		self.encoder = encoder
		self.codec_options = codec_options

	def _source(self, *w, **kw):
		self.source(*w, **kw)
	
	def _source_id(self, *w, **kw):
		self.source_id(*w, **kw)
	
	def _codec(self, *w, **kw):
		self.codec(*w, **kw)
	
	def _encoder(self, *w, **kw):
		self.encoder(*w, **kw)

	def _codec_options(self, *w, **kw):
		self.codec_options(*w, **kw)


class Session(flet.UserControl):
	def __init__(self, callback: SessionCallback, title:str, color: str, *w, sources=[], sources_ids=[],
		codecs=[], encoders=[], **kw):
		super(Session, self).__init__(*w, **kw)
		self._title = title
		self._color = color
		self.source = flet.Dropdown(label='source',expand=True,on_change=callback.source)
		self.source_id = flet.Dropdown(label='id',expand=True,on_change=callback.source_id)
		self.codec = flet.Dropdown(label='codec', expand=True,on_change=callback.codec)
		self.encoder = flet.Dropdown(label='encoder',expand=True,on_change=callback.encoder)
		self.codec_options = flet.TextField(label=f'{title} codec options (key:type=value),... type=int|long|float|string',on_change=callback.codec_options)

		if len(sources)>0:
			self.add_source(sources)
		if len(sources_ids)>0:
			self.add_source_id(sources_ids)

		if len(codecs)>0:
			self.add_codec(codecs)
		if len(encoders)>0:
			self.add_encoder(encoders)

	def add_codec(self, _list: list):
		self.codec.options.extend([flet.dropdown.Option(item) for item in _list])
	
	def add_encoder(self, _list: list):
		self.encoder.options.extend([flet.dropdown.Option(item) for item in _list])

	def add_source(self, _list: list):
		self.source.options.extend([flet.dropdown.Option(item) for item in _list])
	
	def add_source_id(self, _list: list):
		self.source_id.options.extend([flet.dropdown.Option(item) for item in _list])

	def clear(self):
		self.codec.options.clear()
		self.encoder.options.clear()
		self.source.options.clear()
		self.source_id.options.clear()
		self.update()

	def clear_codec(self):
		self.codec.options.clear()
		self.update()
	
	def clear_encoder(self):
		self.encoder.options.clear()
		self.update()
	
	def clear_source(self):
		self.source.options.clear()
		self.update()
	
	def clear_source_id(self):
		self.source_id.options.clear()
		self.update()

	def set_option(self, dropdown, index: int=0):
		dropdown.value = dropdown.options[index].key
		dropdown.update()

	def get_option(self, dropdown, index: int=0):
		return dropdown.options[index].key

	def get_current(self, dropdown):
		return dropdown.value

	def build(self):
		return flet.Column(controls=[
			flet.Text(self._title,color=self._color),
			flet.Row(controls=[self.source, self.source_id, self.codec,self.encoder],alignment=flet.MainAxisAlignment.CENTER,vertical_alignment=flet.CrossAxisAlignment.START),
			self.codec_options
		], horizontal_alignment=flet.CrossAxisAlignment.CENTER,alignment=flet.MainAxisAlignment.START)


if __name__=='__main__':
	app = App()#width=1280,height=480)
	flet.app(app.target)
