import flet
import libscrrec


class App:
	def __init__(self, *w, width:int=None, height:int=None, **kw):
		self._width = width
		self._height = height
		self._dict = None
		self._displays = []
		self._cameras = []
		self._playbacks = ('playback',)
		self._mics = ('mic',)
		self._video_sources = ('display','camera')
		self._audio_sources = ('playback','mic')

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

		# sessions
		self.video_callback = SessionCallback(self.on_video_source,self.on_video_source_id,self.on_video_codec,self.on_video_encoder)
		self.audio_callback = SessionCallback(self.on_audio_source,self.on_audio_source_id,self.on_audio_codec,self.on_audio_encoder)

		self.video_session = Session(self.video_callback,'video','red',)
		self.audio_session = Session(self.audio_callback,'audio','green')

		# start record
		self.start_record = flet.ElevatedButton(text='start',disabled=True,on_click=self._start_record,expand=True)

		#
		home_view = flet.Column(alignment=flet.MainAxisAlignment.START,horizontal_alignment=flet.CrossAxisAlignment.CENTER,controls=[
			flet.Row(controls=[self.get_device_info]),
			flet.Row(controls=[self.video,self.video_playback,self.audio,self.audio_playback],alignment=flet.MainAxisAlignment.CENTER),
			self.video_session, self.audio_session,flet.Row([self.start_record])

		])
		page.add(home_view)

	def _get_device_info(self, event):
		_dict = libscrrec.get_encoder_list()
		self._dict = _dict  # never get this button 
		self._displays = tuple(map(lambda x: ' '.join(x),libscrrec.get_displays()))
		self._cameras = tuple(map(lambda x: ' '.join(x),libscrrec.get_cameras()))
		self._playbacks = ('playback',)
		self._mics = ('mic',)
		self._update_info()
	
	def _update_info(self):
		self._update_video_session()
		self._update_audio_session()		
		self.page.update()

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
	
	# audio
	def on_audio_source(self, *w, **kw):
		source = self.audio_session.source
		source_id = self.audio_session.source_id
		self.audio_session.clear_source_id()
		func = None
		if source.value == 'playback':
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

	def _start_record(self, event):
		pass
	

class SessionCallback:
	def __init__(self, source, source_id, codec, encoder):
		self.source = source
		self.source_id = source_id
		self.codec = codec
		self.encoder = encoder

	def _source(self, *w, **kw):
		self.source(*w, **kw)
	
	def _source_id(self, *w, **kw):
		self.source_id(*w, **kw)
	
	def _codec(self, *w, **kw):
		self.codec(*w, **kw)
	
	def _encoder(self, *w, **kw):
		self.encoder(*w, **kw)


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
			flet.Row(controls=[self.source, self.source_id, self.codec,self.encoder],alignment=flet.MainAxisAlignment.CENTER,vertical_alignment=flet.CrossAxisAlignment.START)
		], horizontal_alignment=flet.CrossAxisAlignment.CENTER,alignment=flet.MainAxisAlignment.START)


if __name__=='__main__':
	app = App(width=1024,height=600)
	flet.app(app.target)
