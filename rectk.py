import os
import subprocess
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
		self.update_idletasks()
		self.update()
		self.label.config(text=text,bg=bg)
		self.update_idletasks()
		self.update()

	def clear(self):
		self.label.config(text='', bg='gray')
	def error(self, text: str):
		self.set(text=text, bg='coral')
	def sucess(self, text: str):
		self.set(text=text, bg='chartreuse4')
	def warn(self, text: str):
		self.set(text=text, bg='yellow')

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
		self.fr2=tkinter.Frame(self)
		self.fr2.pack(expand=0,fill='x')

		self.codec = MediaSelect(self.fr,lang.get('lb_codec'))
		self.codec.pack(side='left',expand=1,fill='x')
		self.encoder = MediaSelect(self.fr,lang.get('lb_encoder'))
		self.encoder.pack(side='left',expand=1,fill='x')
		self.source = MediaSelect(self.fr2,lang.get('lb_source'))
		self.source.pack(side='left',expand=1,fill='x')
		self.ident = MediaSelect(self.fr2,lang.get('lb_item'))
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
		self.ch_video_var = tkinter.BooleanVar()
		self.ch_video_var.set(True)
		self.ch_audio_var = tkinter.BooleanVar()
		self.ch_audio_var.set(True)
		self.bv_video_playback = tkinter.BooleanVar()
		self.bv_video_playback.set(False)
		self.bv_audio_playback = tkinter.BooleanVar()
		self.bv_audio_playback.set(True)
		self.bv_control = tkinter.BooleanVar()
		self.bv_control.set(False)

		self.ch_video = tkinter.Checkbutton(self.fr_options,text=lang.get('ch_video'), variable=self.ch_video_var)
		self.ch_video.pack(side='left',expand=1,fill='x',anchor='n')
		self.ch_audio = tkinter.Checkbutton(self.fr_options,text=lang.get('ch_audio'), variable=self.ch_audio_var)
		self.ch_audio.pack(side='left',expand=1,fill='x',anchor='n')
		self.ch_video_playback = tkinter.Checkbutton(self.fr_options, text=lang.get('ch_video_playback'), variable=self.bv_video_playback)
		self.ch_video_playback.pack(side='left',expand=1,fill='x',anchor='n')
		self.ch_audio_playback = tkinter.Checkbutton(self.fr_options, text=lang.get('ch_audio_playback'), variable=self.bv_audio_playback)
		self.ch_audio_playback.pack(side='left',expand=1,fill='x',anchor='n')

		border_colors=('green','blue')
		# video options
		self.fr_record = tkinter.Frame(self.fr_home)
		self.fr_record.pack(expand=0,fill='x')
		self.video_media = MediaType(self.fr_record, 'video','green')

		self.video_media.codec.var.trace('w',self.on_video_codec_changer)
		self.video_media.source.combobox.config(values=['display','camera'])
		self.video_media.source.combobox.set('display')
		self.video_media.source.var.trace('w',self.on_video_source_changer)
		self.video_media.pack(expand=0,fill='x')

		self.audio_media = MediaType(self.fr_record, 'audio','blue')
		self.audio_media.codec.var.trace('w',self.on_audio_codec_changer)
		self.audio_media.source.combobox.config(values=['output','mic'])
		self.audio_media.source.combobox.set('output')
		self.audio_media.pack(expand=0,fill='x')

		self.status_bar = Statusbar(self.master)
		self.status_bar.set('status bar')
		self.status_bar.pack(side='bottom',fill='x',expand=0)
		
		self.bt_record = tkinter.Button(self.master, text=lang.get('lb.record.start'))
		self.bt_record.pack(side='bottom',fill='x', expand=0)
		self.bt_record['command']=self._start_record
		
	def _update_info(self):
		self.status_bar.set(lang.get('status_updating_info'))
		try:
			new_info=libscrrec.get_encoder_list()
			# displays and cameras
			new_info['displays']=libscrrec.get_displays()
			new_info['cameras']=libscrrec.get_cameras()
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
		self.on_video_source_changer()
	def on_video_source_changer(self,*w,**kw):
		media_source = self.video_media.source.var.get()
		if media_source =='display':
			values=self._encoder_list['displays']
		elif media_source =='camera':
			values=self._encoder_list['cameras']
		self.video_media.ident.combobox.config(values=values)
		self.video_media.ident.combobox.set(values[0])
	def on_audio_codec_changer(self, *w, **kw):
		encoders=tuple(self._encoder_list['audio'][self.audio_media.codec.var.get()])
		self.audio_media.encoder.combobox.config(values=encoders)
		self.audio_media.encoder.combobox.set(encoders[0])

	def on_change_codec(self, new):
		print(new)
	def _update_home(self):
		self.fr_home.destroy()
		self._build_home()

	def _start_record(self):
		# video
		video_source = self.video_media.source.var.get()
		video_codec = self.video_media.codec.var.get()
		video_encoder = self.video_media.encoder.var.get()
		video_ident =self.video_media.ident.var.get()
		# audio
		audio_source = self.audio_media.source.var.get()
		audio_codec = self.audio_media.codec.var.get()
		audio_encoder = self.audio_media.encoder.var.get()
		audio_ident =self.audio_media.ident.var.get()
		# record options
		record_video = self.ch_video_var.get()
		record_audio = self.ch_audio_var.get()
		playback_audio = self.bv_audio_playback.get()
		playback_video = self.bv_video_playback.get()
		control = self.bv_control.get()
		rcmd=self.craft_record_command(video_source, video_codec, video_encoder, video_ident, audio_source, audio_codec, audio_encoder, audio_ident, record_video, record_audio, playback_audio, playback_video, control)
		self._run_record(rcmd)

	def craft_record_command(self, video_source, video_codec, video_encoder, video_ident, 
		audio_source, audio_codec, audio_encoder, audio_ident, record_video, record_audio, 
		playback_audio, playback_video, control):
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
		else:
			cmd+=f'--no-audio '
		if not control:
			cmd+=f'--no-control '
		# record
		if record_video or record_audio:
			pkg = libscrrec.get_current_activity_package_name()
			folder=os.path.expanduser("~/Videos")
			filename=libscrrec.get_record_filename(pkg,folder)
			cmd+=f'--record="{folder}/{filename}" '
		return cmd
	def _run_record(self, cmd):
		self.status_bar.set(lang.get('lb.status_bar.recording'))
		self.bt_record['text']=lang.get('bt_record.stop')
		self.bt_record['command']=self._stop_record
		print(cmd)
		self.record_process = subprocess.Popen((cmd,),shell=True)
		self.fr_home.pack_forget()
		
	def _stop_record(self):
		self.fr_home.pack(expand=1,fill='both')
		self.bt_record['text']=lang.get('bt_record.start')
		self.bt_record['command']=self._start_record
		self.record_process.terminate()
		self.record_process.wait()
		rcode=self.record_process.returncode
		if rcode == 0:
			# sucess
			self.status_bar.sucess(lang.get('lb.scrcpy.sucess_record'))
		elif rcode == 1:
			# start error
			self.status_bar.error(lang.get('lb.scrcpy.start.failure'))
		elif rcode == 2:
			# device disconnect while running
			self.status_bar.warn(lang.get('lb.scrcpy.device_disconnected_while_running'))
		else:
			self.status_bar.set(f'unknow exit: {rcode}')
root = tkinter.Tk()
window=Window(root)
root.mainloop()