# Terminal application for managing a SapphireCMS website
# sapphire install <name> [--env <bool> --mod <bool>]: Install a new SapphireCMS website with the specified name, environment (optional) and modifiablitity (optional).
# sapphire config setactive <id>: Set the active configuration for the current SapphireCMS website.
# sapphire config set <id> <data>: Set a value for the specified configuration for the current SapphireCMS website.
# sapphire config get <id>: View the specified configuration for the current SapphireCMS website.
# sapphire config create <id>: Create a new configuration for the current SapphireCMS website.
# sapphire config list: List all available configurations for the current SapphireCMS website.
# sapphire run <dev/prod>: Run the current SapphireCMS website in development or production mode.
# sapphire serve: Serve the current SapphireCMS website (same as run prod).
# sapphire service <bool>: Enable or disable the system service for the current SapphireCMS website.
# sapphire theme install <name>: Install a new theme for the current SapphireCMS website.
# sapphire theme install <url>: Install a new theme from a URL for the current SapphireCMS website.
# sapphire theme remove <name>: Remove a theme from the current SapphireCMS website.
# sapphire theme list: List all installed themes for the current SapphireCMS website.
# sapphire theme get: Get the current theme for the current SapphireCMS website.
# sapphire version: Get the version of the current SapphireCMS website.
# sapphire update: Update the current SapphireCMS environment.
# sapphire help: Get help for the SapphireCMS CLI.

# type: ignore


import os, sys, subprocess
import sys, time
import argparse
from halo import Halo

sys.path.append(os.getcwd())

ver = sys.version_info
# pyexec = f"python{ver.major}.{ver.minor}" if sys.platform in ["linux", "linux2", "darwin"] else "python"
pyexec = sys.executable

def install(name, env, mod):
    global pyexec
    print('\033[92m', 'Creating new SapphireCMS website', '\033[0m', sep='')
    with Halo(text="Checking current Python version", spinner="dots2") as spinner:
        if int("".join(subprocess.run([pyexec, "--version"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode("utf-8").split(" ")[1].split(".")[:2])) < 311:
            spinner.fail("Python version is invalid")
            raise ImportError("Please run this command with Python 3.11 or higher")
        spinner.succeed("Python version is valid")
        
    with Halo(text="Checking current directory", spinner="dots2") as spinner:
        if os.path.exists(name):
            if os.listdir(name) != []:
                spinner.fail(f"Directory '{name}' not empty")
                raise ValueError(f"Directory '{name}' already exists and is not empty")
        else:
            os.mkdir(name)
        os.chdir(name)
        spinner.succeed(f"Using directory '{name}'")
    
    with Halo(text="Checking available storage", spinner="dots2") as spinner:
        import shutil
        if shutil.disk_usage(os.getcwd()).free < 2*(1024**3):
            spinner.fail("Not enough space available: " + str(shutil.disk_usage(os.getcwd()).free))
            raise MemoryError("Not enough space available")
        spinner.succeed("Enough space available")
    
    with Halo(text="Installing basic SapphireCMS project", spinner="dots2") as spinner:
        if subprocess.run(["git", "clone", "https://github.com/SapphireCMS/SapphireBase.git", "."], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
            spinner.fail("Could not clone Base Project")
            raise ImportError("Could not clone Base Project")
        subprocess.run(["git", "remote", "remove", "origin"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        spinner.succeed("Cloned Base Project")
    
    with Halo(text="Installing dependencies", spinner="dots2") as spinner:
        try:
            if env:
                if subprocess.run([pyexec, "-m", "pip", "install", "virtualenv"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
                    spinner.fail("Could not install virtualenv")
                    raise ImportError("Could not install virtualenv")
                subprocess.run([pyexec, "-m", "virtualenv", "env"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                pyexec = os.path.join(os.getcwd(), "env", "bin", "python3") if sys.platform in ["linux", "linux2", "darwin"] else os.path.join(os.getcwd(), "env", "Scripts", "python.exe")
                exec(open("env/Scripts/activate_this.py").read(), {'__file__': "env/Scripts/activate_this.py"})
                if not mod:
                    subprocess.run([pyexec, "-m", "pip", "install", "sapphirecms"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run([pyexec, "-m", "pip", "install", "-r", "requirements.txt"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            spinner.succeed("Installed dependencies")
        except:
            spinner.fail("Could not install dependencies")
            raise ImportError("Could not install dependencies")
    
    if env and mod:
        with Halo(text="Creating dedicated SapphireCMS installation (Modifiable)", spinner="dots2") as spinner:
            if subprocess.run(["git", "clone", "https://github.com/SapphireCMS/SapphireCMS.git"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
                spinner.fail("Could not clone SapphireCMS")
                raise ImportError("Could not clone SapphireCMS")
            subprocess.run(["git", "remote", "remove", "origin"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            spinner.succeed("Cloned SapphireCMS (Modifiable)")
            os.chdir("SapphireCMS")
        with Halo(text="Installing SapphireCMS", spinner="dots2") as spinner:
            if subprocess.run([pyexec, "-m", "pip", "install", "-e", "."], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
                spinner.fail("Could not install SapphireCMS")
                raise ImportError("Could not install SapphireCMS")
            spinner.succeed("Installed SapphireCMS (Modifiable)")
        
    print('\nSapphireCMS website created successfully')
    print('To configure your website, move to the new directory and run:')
    print('sapphire config create Default')
        
def run(mode):
    subprocess.run([pyexec, "-m", "CMS", mode])
    
class theme:
    def add(name):
        if name.startswith("http"):
            subprocess.run(f"git clone {name} themes/{name.split('/')[-1].split('.')[0] if name.endswith('.git') else name.split('/')[-1]}", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(f"git clone https://github.com/SapphireCMS/{name}Theme themes/{name}", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
    def remove(name):
        try:
            subprocess.run(f"rm -rf themes/{name}", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            raise ValueError(f"Theme '{name}' does not exist")
        
    def list():
        for theme in [f for f in os.listdir("themes") if os.path.isdir(f"themes/{f}") and os.path.exists(f"themes/{f}/__init__.py")]:
            print(theme)
            
class config_:
    def setactive(id):
        import config
        if getattr(config, id, None) is not None:
            configfile = open(config.__file__, "r").readlines()
            for i in range(len(configfile)):
                if configfile[i].startswith("active = "):
                    configfile[i] = f"active = {id}()\n"
                    open("config.py", "w").write("".join(configfile))
                    return
            if configfile[-1]!= "\n" or not configfile[-2].endswith("\n"):
                configfile.append("\n\n")
            configfile.append(f"active = {id}()\n")
            open("config.py", "w").write("".join(configfile))
        else:
            print(f"Configuration '{id}' does not exist")
            config_.list()
                
    def set(id, data):
        import config
        if getattr(config, id, None) is not None:
            configfile = open(config.__file__, "r").readlines()
            pos = None
            for i in range(len(configfile)):
                if configfile[i].startswith(f"class {id}:"):
                    break
            for i in range(i, len(configfile)):
                line = configfile[i]
                while line.strip() != "":
                    i += 1
                    line = configfile[i]
                    if "=" in line:
                        v = line.split("=")[0].strip()
                        if v == data.split("=")[0].strip():
                            configfile[i] = f"{ ' ' * (len(line) - len(line.lstrip())) }{data.split('=')[0].strip()} = \"{data.split('=')[1].strip()}\"\n"
                            open("config.py", "w").write("".join(configfile))
                            return
                pos = i
                while line.strip() == "":
                    i += 1
                    line = configfile[i]
                if line.startswith(" ") or line.startswith("\t"):
                    continue
                else:
                    break
            if pos is not None:
                configfile.insert(pos, f"    {data.split('=')[0].strip()} = \"{data.split('=')[1].strip()}\"\n")
                open("config.py", "w").write("".join(configfile))
                        
        else:
            print(f"Configuration '{id}' does not exist")
            config_.list()
                
    def get(id):
        import config
        if getattr(config, id, None) is not None:
            for k, v in [(k, v) for k, v in getattr(config, id).__dict__.items() if not k.startswith("__") and not callable(v)]:
                print(f"{k}: {v}")
        else:
            print(f"Configuration '{id}' does not exist")
            config_.list()
                
    def create(id):
        import config, base64
        if getattr(config, id, None) is None:
            configfile = open(config.__file__, "r").readlines()
            b = {
                "name": "SapphireCMS",
                "description": "This is a SapphireCMS website",
                "logo": "https://via.placeholder.com/256",
                "favicon": "https://via.placeholder.com/32",
                "keywords": "landing, blog",
                "author": "SapphireCMS",
                "theme": "themes.Sapphire",
                "dbplatform": "MongoDB",
                "secret_key": f"{base64.b64encode(os.urandom(32)).decode('utf-8')}"
            }
            
            c = {
                "name": input("Enter the name of the website ['SapphireCMS']: "),
                "description": input("Enter the description of the website ['This is a SapphireCMS website']: "),
                "logo": input("Enter the URL of the website logo ['https://via.placeholder.com/256']: "),
                "favicon": input("Enter the URL of the website favicon ['https://via.placeholder.com/32']: "),
                "keywords": input("Enter the keywords for the website ['landing, blog']: "),
                "author": input("Enter the author of the website ['SapphireCMS']: "),
                "theme": input("Enter the theme for the website ['themes.Sapphire']: "),
                "dbplatform": input("Enter the database platform for the website ['MongoDB'](MongoDB): "),
                "secret_key": input("Enter the secret key for the website [Randomly generated]: ")
            }
            
            c = {k: v if v != "" else b[k] for k, v in c.items()}
            
            if c["keywords"] != "" and "," in c["keywords"]:
                c["keywords"] = [keyword.strip() for keyword in c["keywords"].split(",")]
            elif c["keywords"] != "":
                c["keywords"] = [c["keywords"].strip()]
            else:
                c["keywords"] = b["keywords"]
            
            match c["dbplatform"]:
                case "MongoDB":
                    c["dbname"] = input("Enter the name of the database ['SapphireCMS']: ")
                    c["db_uri"] = input("Enter the URI of the database*: ")
                case _:
                    raise ValueError("Invalid database platform")
            
            
            o = [f"class {id}:\n"] + [f"    {k} = '{v}'\n" for k, v in c.items()] + ["\n"]
            configfile = o + configfile 
            open("config.py", "w").write("".join(configfile))
            print(f"Configuration '{id}' created successfully")
            print(f"Please confirm indentation of the configuration in 'config.py'")
            print(f"To set this configuration as active, run 'sapphire config setactive {id}'")
        else:
            print(f"Configuration '{id}' already exists")
            
    def list():
        import config
        import inspect
        print("Available configurations are:")
        for i, c in enumerate(inspect.getmembers(config, inspect.isclass)):
            print(f"{i+1}. {c[0]}")

def main():
    parser = argparse.ArgumentParser(description="Terminal application for managing a SapphireCMS website")
    subparsers = parser.add_subparsers(dest="command")

    install_parser = subparsers.add_parser("install", help="Install a new SapphireCMS website")
    install_parser.add_argument("name", help="The name of the new SapphireCMS website", default=".", nargs="?")
    install_parser.add_argument("-e", "--env", help="Create a new environment for this SapphireCMS website", action="store_true")
    install_parser.add_argument("-m", "--mod", help="Create a modifiable installation for this SapphireCMS website", action="store_true")
    
    config_parser = subparsers.add_parser("config", help="Configure the current SapphireCMS website")
    config_parser.add_argument("action", help="The action to perform on the current SapphireCMS website", choices=["setactive", "set", "get", "create", "list"], nargs="?")
    config_parser.add_argument("id", help="Identifier of the configuration to perform the action on", nargs="?")
    config_parser.add_argument("data", help="Data to set the configuration to (Only for action 'set')", nargs="?", default="")
    
    run_parser = subparsers.add_parser("run", help="Run the current SapphireCMS website")
    run_parser.add_argument("mode", help="The mode to run the current SapphireCMS website in", choices=["dev", "prod"], default="dev", nargs="?")
    
    serve_parser = subparsers.add_parser("serve", help="Serve the current SapphireCMS website")

    service_parser = subparsers.add_parser("service", help="Enable or disable the system service for the current SapphireCMS website")
    service_parser.add_argument("args", help="Enable or disable the system service for the current SapphireCMS website", choices=["start", "stop", "restart", "false"], nargs="?")
    
    theme_parser = subparsers.add_parser("theme", help="Manage themes for the current SapphireCMS website")
    theme_parser.add_argument("action", help="The action to perform on the current SapphireCMS website", choices=["add", "remove", "list"], nargs="?")
    theme_parser.add_argument("id", help="Identifier of the theme to perform the action on (Can be a name or a URL for adding a theme)", nargs="?")
    
    version_parser = subparsers.add_parser("version", help="Get the version of the current SapphireCMS environment")
    
    update_parser = subparsers.add_parser("update", help="Update the current SapphireCMS environment")    
        
    args = parser.parse_args()


    match args.command:
        case "install":
            install(args.name, args.env, args.mod)
        case "config":
            try:
                import config
            except ImportError:
                raise ImportError("Could not find a valid SapphireCMS environment")
            except:
                pass
            match args.action:
                case "setactive":
                    config_.setactive(args.id)
                case "set":
                    config_.set(args.id, args.data)
                case "get":
                    config_.get(args.id)
                case "create":
                    config_.create(args.id)
                case "list":
                    config_.list()           
        case "run":
            run(args.mode)
        case "serve":
            run("prod")
        case "service":
            try:
                import config
            except:
                raise ImportError("Could not find a valid SapphireCMS environment")
            args.args = [args.args] if args.args is not None else []
            if len(args.args) == 1:
                if sys.platform in ["linux", "linux2"]:
                    if os.getuid() != 0:
                        subprocess.run(["sudo", pyexec, " ".join(sys.argv)])
                    if os.path.exists(f"/etc/systemd/system/{config.active.name}-sapphirecms.service"):
                        if args.args[0] == "start":
                            subprocess.run(["systemctl", "enable", f"{config.active.name}-sapphirecms"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            subprocess.run(["systemctl", "start", f"{config.active.name}-sapphirecms"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        elif args.args[0] == "stop":
                            subprocess.run(["systemctl", "stop", f"{config.active.name}-sapphirecms"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        elif args.args[0] == "restart":
                            subprocess.run(["systemctl", "restart", f"{config.active.name}-sapphirecms"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        else:
                            raise ValueError("Invalid argument for command 'service'")
                    else:
                        if args.args[0] == "false":
                            return
                        execcommand = f"{pyexec} -m CMS prod" if "env" not in os.listdir() else f"{os.getcwd()}/env/bin/activate && {pyexec} -m CMS prod"
                        open(f"{config.active.name.replace(' ', '')}-sapphire.service", "w").write(f"""[Unit]
    Description={config.active.name} SapphireCMS Service
    After=network.target

    [Service]
    Type=simple
    User={os.environ.get('USER', subprocess.run(["whoami"], stdout=subprocess.PIPE).stdout.decode("utf-8").strip())}
    WorkingDirectory={os.getcwd()}
    ExecStart={execcommand}
    Restart=on-failure

    [Install]
    WantedBy=multi-user.target
    """)
                        subprocess.run(["sudo", "ln", "-s", f"{os.getcwd()}/{config.active.name.replace(' ', '')}-sapphire.service", f"/etc/systemd/system/{config.active.name}-sapphirecms.service"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        subprocess.run(["systemctl", "enable", f"{config.active.name}-sapphirecms"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        subprocess.run(["systemctl", "start", f"{config.active.name}-sapphirecms"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif sys.platform in ["darwin"]:
                    raise NotImplementedError("System services are not supported on macOS")
                elif sys.platform in ["win32"]:
                    raise NotImplementedError("System services are not supported on Windows")
                    import ctypes
                    if not ctypes.windll.shell32.IsUserAnAdmin():
                        subprocess.run(["runas", "/user:Administrator", pyexec, " ".join(sys.argv)])
                        return
                    if subprocess.run(f"sc query {config.active.name}-sapphirecms", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
                        open(f"{os.getcwd()}\\{config.active.name}-sapphirecms.bat", "w").write(f"cd {os.getcwd()} && {pyexec} -m CMS prod")
                        subprocess.run(["sc", "create", f"{config.active.name}-sapphirecms", "binPath=", f"\"C:\\Windows\\System32\\cmd.exe /c \"{os.getcwd()}\\{config.active.name}-sapphirecms.bat\"\"", "start=", "auto"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        print(" ".join(["sc", "create", f"{config.active.name}-sapphirecms", "binPath=", f"\"C:\\Windows\\System32\\cmd.exe /c \"{os.getcwd()}\\{config.active.name}-sapphirecms.bat\"\"", "start=", "auto"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
                    if args.args[0] == "start":
                        subprocess.run(["sc", "start", f"{config.active.name}-sapphirecms"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    elif args.args[0] == "stop":
                        subprocess.run(["sc", "stop", f"{config.active.name}-sapphirecms"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    elif args.args[0] == "restart":
                        subprocess.run(["sc", "stop", f"{config.active.name}-sapphirecms"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        subprocess.run(["sc", "start", f"{config.active.name}-sapphirecms"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    raise NotImplementedError("System services are not supported on this platform")
            else:
                raise ValueError("Invalid number of arguments for command 'service'")
        case "theme":
            match args.action:
                case "add":
                    theme.add(args.id)
                case "remove":
                    theme.remove(args.id)
                case "list":
                    theme.list()
                case _:
                    raise ValueError("Invalid action specified for command 'theme'")
        case "version":
            import importlib.metadata
            print(importlib.metadata.version("SapphireCMS"))
        case "update":
            print("Updating SapphireCMS environment")
            with Halo(text="Checking current Python version", spinner="dots2") as spinner:
                if int("".join(subprocess.run([pyexec, "--version"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode("utf-8").split(" ")[1].split(".")[:2])) < 311:
                    spinner.fail("Python version is invalid")
                    raise ImportError("Please run this command with Python 3.11 or higher")
                spinner.succeed("Python version is valid")
            with Halo(text="Updating SapphireCMS", spinner="dots2") as spinner:
                if subprocess.run([pyexec, "-m", "pip", "install", "--upgrade", "sapphirecms"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
                    spinner.fail("Could not update SapphireCMS")
                    raise ImportError("Could not update SapphireCMS")
                spinner.succeed("Updated SapphireCMS")
                    
if __name__ == "__main__":
    main()