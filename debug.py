class ANSI:
	# text colors
	BLACK=30
	RED=31
	GREEN=32
	YELLOW=33
	BLUE=34
	MAGENTA=35
	CYAN=36
	WHITE=37
	# background colors
	BG_BLACK=40
	BG_RED=41
	BG_GREEN=42
	BG_YELLOW=43
	BG_BLUE=44
	BG_MAGENTA=45
	BG_CYAN=46
	BG_WHITE=47
	# DECORATIONS
	RESET=0
	BOLD=1
	ITALIC=3
	UNDERLINE=4

DEBUG_MODE=False
def set_mode(value:bool):
	global DEBUG_MODE
	DEBUG_MODE = value
def get_mode():
	global DEBUG_MODE
	return DEBUG_MODE
def _print(*w, **kw):
	global DEBUG_MODE
	if DEBUG_MODE:
		print(*w,**kw)

def _debug(context,foreground,*w,**kw):
	'''
	context: str messsage to show with colors
	foreground: ANSI COLOR
	background: ANSI BG_COLOR
	r,g,b = 0-255 aditional color pallet if support

	'''
	_print(f'\u001b[{foreground}m[{context}]:',*w,**kw,end='\u001b[0m\n')


def debug(*w, **kw):
	_debug('DEBUG',ANSI.CYAN,*w, **kw)
def warn(*w, **kw):
	_debug('WARN',ANSI.YELLOW,*w, **kw)
def error(*w, **kw):
	_debug('ERROR',ANSI.RED,*w,**kw)
