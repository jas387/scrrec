#language

import os

# DEFAULT
LANG='en' # english
DIR='./lang' # directory
DICT=dict({'en':dict({})}) # empyt dict

def _load(code:str):
	path=f'./lang/{code}.txt'
	if os.path.isfile(path):
		_dict=dict({})
		with open(path,'r') as file:
			for line in file.readlines():
				line=line.strip()
				key,value = line.split('=')
				_dict[key]=value
		return _dict
	raise FileNotFoundError(f'invalid lang file: {path}')

def set(code:str):
	lang_list=get_languages()
	if code not in lang_list:
		raise ValueError(f'invalid language, choose one of: {lang_list}')
	lang=_load(code)
	global LANG, DICT
	LANG=code
	DICT=lang

def get_current():
	global LANG
	return LANG

def get_languages():
	return [lang.rsplit('.')[0] for lang in os.listdir(DIR)]

def get(string: str):
	global LANG, DICT
	return DICT.get(string,None)

set(LANG)
