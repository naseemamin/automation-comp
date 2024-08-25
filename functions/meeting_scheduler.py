import pyautogui as pyag
import time
import win32api
import win32con
import win32gui

def open_teams(): 
    pyag.press('win', interval=0.1)
    pyag.write('teams', interval=0.1)
    pyag.press('enter')


def return_main_monitor_coords():
    monitor_handles = win32api.EnumDisplayMonitors(None, None)
    for monitor in monitor_handles:
        monitor_info = win32api.GetMonitorInfo(monitor[0])
        if monitor_info['Flags'] == win32con.MONITORINFOF_PRIMARY:
            print(f"Your main monitor is: {monitor_info['Monitor']}")
            return monitor_info['Monitor']
        
def return_application_monitor(window_handle):
    monitor_handle = win32api.MonitorFromWindow(window_handle, win32con.MONITOR_DEFAULTTONEAREST)
    monitor_info = win32api.GetMonitorInfo(monitor_handle)
    print(f"Teams is open on this monitor: {monitor_info['Monitor']}")
    return monitor_info['Monitor'] 

def find_window_by_title(title):
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and title in win32gui.GetWindowText(hwnd):
            hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds

def compare_teams_monitor_vs_main_monitor():
    window_title = "Microsoft Teams"
    window_handles = find_window_by_title(window_title)

    if window_handles:
        window_handle = window_handles[0]
        teams_monitor = return_application_monitor(window_handle)

    main_monitor = return_main_monitor_coords()

    if teams_monitor == main_monitor:
        print("teams is open on the main monitor")
        return True
    elif teams_monitor[0] < main_monitor[0]:
        print("teams monitor is on the left")
        move_teams_right()
        return True
    else:
        print("teams monitor is on the right")
        move_teams_left()
        return True
    
def move_teams_left():
    time.sleep(5)
    with pyag.hold('win'):
            with pyag.hold('shift'):
                pyag.press('left')

def move_teams_right():
    time.sleep(5)
    with pyag.hold('win'):
            with pyag.hold('shift'):
                pyag.press('right')

def click_calendar():
    attempts = 0
    while attempts < 10:
        calendar_location_D = pyag.locateOnScreen('images/calendar_D.png', grayscale=True, confidence=0.8)
        calendar_location_L = pyag.locateOnScreen('images/calendar_L.png', grayscale=True, confidence=0.8)
        calendar_open_L = pyag.locateOnScreen('images/calendar_open_D.png', confidence=0.8)
        calendar_open_D = pyag.locateOnScreen('images/calendar_open_L.png', confidence=0.8)
        if calendar_location_D or calendar_location_L:
            if calendar_location_D:
                print("dark theme")
                pyag.click(calendar_location_D)
            else:
                print("light theme")
                pyag.click(calendar_location_L)
            return True
        elif calendar_open_D or calendar_open_L:
            print("calendar already open")
            return True
        else:
            attempts += 1
            time.sleep(1)
    else:
        return False
   
def click_new_meeting():
    attempts = 0
    while attempts < 10:
        new_meeting_D = pyag.locateOnScreen('images/new_meeting_D.png', confidence=0.8)
        new_meeting_L = pyag.locateOnScreen('images/new_meeting_L.png', confidence=0.8)
        if new_meeting_D or new_meeting_L:
            print("found new meeting button, clicking")
            if new_meeting_D:
                pyag.click(new_meeting_D)
            else:
                pyag.click(new_meeting_L)
            return True
        else:
            attempts += 1
            time.sleep(1)
    else:
        return False
    
def input_meeting_details(title, attendees, date, start_time, end_time):
    attempts = 0
    while attempts < 10:
        meeting_open_D = pyag.locateOnScreen('images/meeting_open_D.png', confidence=0.8)
        meeting_open_L = pyag.locateOnScreen('images/meeting_open_L.png', confidence=0.8)
        if meeting_open_D or meeting_open_L:
            pyag.write(title.title(), interval=0.05)
            pyag.press('tab')
            for attendee in attendees:
                pyag.write(attendee.title(), interval=0.13)
                time.sleep(1.5)
                pyag.press('enter')
            pyag.press(['tab', 'tab'], interval=0.2)
            pyag.write(date, interval=0.05)
            pyag.press('tab')
            pyag.write(start_time, interval=0.05)
            pyag.press(['tab', 'tab'])
            pyag.write(end_time, interval=0.05)
            return True
        else:
            print("meeting not open yet")
            attempts += 1
            time.sleep(1)
    else:
        return False
