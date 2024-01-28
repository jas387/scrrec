import tkinter
import tkinter.ttk
import lang
import libscrrec

class Statusbar(tkinter.Frame):
	def __init__(self,master, *w,**kw):
		super(Statusbar, self).__init__(master,*w,**kw)
		self.label = tkinter.Label(self,bg='gray')
		self.label.pack(expand=1,fill='x')

	def set(self, text: str):
		self.label.config(text=text)
	def clear(self):
		self.label.config(text='')


class MediaSelect(tkinter.Frame):
	def __init__(self, master, name, *w, **kw):
		super(MediaSelect, self).__init__(master,*w,**kw)
		self.label=tkinter.Label(self,text=name+':')
		self.label.pack(side='left', expand=0,fill='x')
		self.var = tkinter.StringVar()
		self.combobox = tkinter.ttk.Combobox(self, textvariable=self.var, state='readonly')
		self.combobox.pack(expand=1,fill='x',side='left')

class MediaType(tkinter.Frame):
	# create a frame with codec/encoder label and combolist to select
	def __init__(self, master, title: str, color: str ,*w ,**kw):
		super(MediaType, self).__init__(*w, **kw)
		self.config(highlightbackground=color,highlightcolor=color,highlightthickness=3)
		# title label
		self.label=tkinter.Label(self, text=title,fg=color)
		self.label.pack(expand=1,fill='x')
		# codec
		self.fr=tkinter.Frame(self)
		self.fr.pack(expand=1,fill='x')
		self.codec = MediaSelect(self.fr,lang.get('lb_codec'))
		self.codec.pack(side='left',expand=1,fill='x')
		self.encoder = MediaSelect(self.fr,lang.get('lb_encoder'))
		self.encoder.pack(side='left',expand=1,fill='x')
		

		

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
		self.ch_playback = tkinter.Checkbutton(self.fr_options,text=lang.get('ch_playback'))
		self.ch_playback.pack(side='left',expand=1,fill='x',anchor='n')
		self.ch_mic = tkinter.Checkbutton(self.fr_options,text=lang.get('ch_mic'))
		self.ch_mic.pack(side='left',expand=1,fill='x',anchor='n')

		border_colors=('green','blue')
		# video options
		self.fr_video = tkinter.Frame(self.fr_home)
		self.fr_video.pack()
		self.video_codec = MediaType(self.fr_video, 'video','green')
		self.video_codec.pack(expand=0,fill='x')

		self.status_bar = Statusbar(self.master)
		self.status_bar.set('status bar')
		self.status_bar.pack(side='bottom',fill='x',expand=0)
		
		
	def _update_info(self):
		self._encoder_list=libscrrec.get_encoder_list()
	def _update_home(self):
		self.fr_home.destroy()
		self._build_home()

root = tkinter.Tk()
window=Window(root)
root.mainloop()