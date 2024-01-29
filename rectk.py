import tkinter
import tkinter.ttk
import lang
import libscrrec

class Statusbar(tkinter.Frame):
	def __init__(self,master, *w,**kw):
		super(Statusbar, self).__init__(master,*w,**kw)
		self.label = tkinter.Label(self,bg='gray')
		self.label.pack(expand=1,fill='x')

	def set(self, text: str,bg='grey'):
		self.label.config(text=text,bg=bg)

	def clear(self):
		self.label.config(text='', bg='gray')
	def error(self, text: str):
		self.set(text=text, bg='coral')
	def sucess(self, text: str):
		self.set(text=text, bg='chartreuse4')

class MediaSelect(tkinter.Frame):
	def __init__(self, master, name, *w, **kw):
		super(MediaSelect, self).__init__(master,*w,**kw)
		self.label=tkinter.Label(self,text=name+':')
		self.label.pack(side='left', expand=0,fill='x')
		self.var = tkinter.StringVar()
		self.combobox = tkinter.ttk.Combobox(self, textvariable=self.var, state='readonly')
		self.combobox.pack(expand=1,fill='x',side='left')
		#self.var.trace('w', self.on_change)
		self.combobox.bind('<<ComboboxSelected>>', self.on_change)

	def on_change(self, *w, **kw):
		pass

class MediaType(tkinter.Frame):
	# create a frame with codec/encoder label and combolist to select
	def __init__(self, master, title: str, color: str ,*w ,**kw):
		super(MediaType, self).__init__(master, *w, **kw)
		self.config(highlightbackground=color,highlightcolor=color,highlightthickness=3)
		# title label
		self.label=tkinter.Label(self, text=title,fg=color)
		self.label.pack(expand=0,fill='x')
		# selecter
		self.fr=tkinter.Frame(self)
		self.fr.pack(expand=0,fill='x')
		self.codec = MediaSelect(self.fr,lang.get('lb_codec'))
		self.codec.pack(side='left',expand=1,fill='x')
		self.encoder = MediaSelect(self.fr,lang.get('lb_encoder'))
		self.encoder.pack(side='left',expand=1,fill='x')
		self.source = MediaSelect(self.fr,lang.get('lb_source'))
		self.source.pack(side='left',expand=1,fill='x')
		self.ident = MediaSelect(self.fr,lang.get('lb_item'))
		self.ident.pack(side='left',expand=1,fill='x')



		

class Window:
	def __init__(self, master: tkinter.Tk, *w, width: int= 800, height: int=600, x: int=0, y: int=0, **kw):
		self.master = master
		self.master.title('rectk')
		self.master.geometry(f'{width}x{height}+{x}+{y}')
		self.master.protocol('WM_DELETE_WINDOW',self.close)
		self._encoder_list={} # get info
		self._build_home()

	def close(self):
		self.master.destroy()

	def _build_home(self):
		self.fr_home=tkinter.Frame(self.master)
		self.fr_home.pack(expand=1,fill='both')
		# get phone data and update informations on home screen
		self.bt_update_info=tkinter.Button(self.fr_home, text=lang.get('bt_update_info'),command=self._update_info)
		self.bt_update_info.pack(fill='x', expand=0,anchor='n')


		# record options
		self.fr_options=tkinter.Frame(self.fr_home)
		self.fr_options.pack(expand=0,fill='x')
		self.ch_video = tkinter.Checkbutton(self.fr_options,text=lang.get('ch_video'))
		self.ch_video.pack(side='left',expand=1,fill='x',anchor='n')
		self.ch_audio = tkinter.Checkbutton(self.fr_options,text=lang.get('ch_audio'))
		self.ch_audio.pack(side='left',expand=1,fill='x',anchor='n')

		border_colors=('green','blue')
		# video options
		self.fr_record = tkinter.Frame(self.fr_home)
		self.fr_record.pack(expand=0,fill='x')
		self.video_media = MediaType(self.fr_record, 'video','green')

		self.video_media.codec.var.trace('w',self.on_video_codec_changer)
		self.video_media.source.combobox.config(values=['display','camera'])
		self.video_media.source.combobox.set('display')
		self.video_media.pack(expand=0,fill='x')

		self.audio_media = MediaType(self.fr_record, 'audio','blue')
		self.audio_media.codec.var.trace('w',self.on_audio_codec_changer)
		self.audio_media.source.combobox.config(values=['playback','mic'])
		self.audio_media.source.combobox.set('playback')
		self.audio_media.pack(expand=0,fill='x')


		self.status_bar = Statusbar(self.master)
		self.status_bar.set('status bar')
		self.status_bar.pack(side='bottom',fill='x',expand=0)
		
		
	def _update_info(self):
		self.status_bar.set(lang.get('status_updating_info'))
		try:
			new_info=libscrrec.get_encoder_list()
		except ValueError as e:
			self.status_bar.error(str(e))
		else:
			self._encoder_list = new_info
			self.status_bar.set(lang.get('status_updated_info'))
			# update comboboxes
			# video
			vcodecs=tuple(self._encoder_list['video'].keys())
			self.video_media.codec.combobox.config(values=vcodecs)
			self.video_media.codec.combobox.set(vcodecs[0])
			# audio
			acodecs=tuple(self._encoder_list['audio'].keys())
			self.audio_media.codec.combobox.config(values=acodecs)
			self.audio_media.codec.combobox.set(acodecs[0])
	
	def on_video_codec_changer(self, *w, **kw):
		encoders=tuple(self._encoder_list['video'][self.video_media.codec.var.get()])
		self.video_media.encoder.combobox.config(values=encoders)
		self.video_media.encoder.combobox.set(encoders[0])
		if self.video_media.source.var.get()=='display':
			displays=libscrrec.get_displays()
			self.video_media.ident.combobox.config(values=displays)
			self.video_media.ident.combobox.set(displays[0])
	def on_audio_codec_changer(self, *w, **kw):
		encoders=tuple(self._encoder_list['audio'][self.audio_media.codec.var.get()])
		self.audio_media.encoder.combobox.config(values=encoders)
		self.audio_media.encoder.combobox.set(encoders[0])

	



	def on_change_codec(self, new):
		print(new)
	def _update_home(self):
		self.fr_home.destroy()
		self._build_home()

root = tkinter.Tk()
window=Window(root,x=800)
root.mainloop()