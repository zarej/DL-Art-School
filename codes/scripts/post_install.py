import filecmp
import os
import shutil
import sys
import sysconfig
import subprocess
from pathlib import Path
import requests
import zipfile
if sys.version_info < (3, 8):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata

req_file = os.path.join(os.getcwd(), "requirements.txt")

def run(command, desc=None, errdesc=None, custom_env=None):
    if desc is not None:
        print(desc)

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=os.environ if custom_env is None else custom_env)

    if result.returncode != 0:

        message = f"""{errdesc or 'Error running command'}.
Command: {command}
Error code: {result.returncode}
stdout: {result.stdout.decode(encoding="utf8", errors="ignore") if len(result.stdout)>0 else '<empty>'}
stderr: {result.stderr.decode(encoding="utf8", errors="ignore") if len(result.stderr)>0 else '<empty>'}
"""
        raise RuntimeError(message)

    return result.stdout.decode(encoding="utf8", errors="ignore")

def check_versions():
    global req_file
    reqs = open(req_file, 'r')
    lines = reqs.readlines()
    reqs_dict = {}
    for line in lines:
        splits = line.split("==")
        if len(splits) == 2:
            key = splits[0]
            if "torch" not in key:
                if "diffusers" in key:
                    key = "diffusers"
                reqs_dict[key] = splits[1].replace("\n", "").strip()
    

#uninstall tensorboard so it works
#download dvae https://huggingface.co/jbetker/tortoise-tts-v2/resolve/3704aea61678e7e468a06d8eea121dba368a798e/.models/dvae.pth
print("Downloading DVAE...")
r = requests.get("https://huggingface.co/jbetker/tortoise-tts-v2/resolve/3704aea61678e7e468a06d8eea121dba368a798e/.models/dvae.pth", allow_redirects=True)
#save to experiments
open('experiments/dvae.pth', 'wb').write(r.content)

print("Downloading Autoregressive Model...")
r = requests.get("https://huggingface.co/jbetker/tortoise-tts-v2/resolve/main/.models/autoregressive.pth", allow_redirects=True)
#save to experiments
open('experiments/autoregressive.pth', 'wb').write(r.content)

run("pip uninstall tensorboard -y", "Uninstalling Tensorboard")

base_dir = os.path.dirname(os.getcwd())
#repo = git.Repo(base_dir)
#revision = repo.rev_parse("HEAD")
#print(f"Dreambooth revision is {revision}")
#check_versions()
# Check for "different" B&B Files and copy only if necessary
if os.name == "nt":
    '''
    python = sys.executable
    bnb_src = os.path.join(os.getcwd(), "resources/bitsandbytes_windows")
    bnb_dest = os.path.join(sysconfig.get_paths()["purelib"], "bitsandbytes")
    '''
    cudnn_src = os.path.join(os.getcwd(), "resources/cudnn_windows")
    #check if chudnn is in cwd
    if not os.path.exists(cudnn_src):
        print("Can't find CUDNN in resources, trying main folder...")
        cudnn_src = os.path.join(os.getcwd(), "cudnn_windows")
        if not os.path.exists(cudnn_src):
            cudnn_url = "https://developer.download.nvidia.com/compute/redist/cudnn/v8.6.0/local_installers/11.8/cudnn-windows-x86_64-8.6.0.163_cuda11-archive.zip"
            print(f"Downloading CUDNN 8.6")
            #download with requests
            r = requests.get(cudnn_url, allow_redirects=True)
            #save to cwd
            open('cudnn_windows.zip', 'wb').write(r.content)
            #unzip
            with zipfile.ZipFile('cudnn_windows.zip','r') as zip_ref:
                zip_ref.extractall(os.path.join(os.getcwd(),"resources/"))
            #remove zip
            os.remove('cudnn_windows.zip')
            cudnn_src = os.path.join(os.getcwd(), "resources/cudnn-windows-x86_64-8.6.0.163_cuda11-archive/bin")
            print(cudnn_src)
    cudnn_dest = os.path.join(sysconfig.get_paths()["purelib"], "torch", "lib")
    print(f"Checking for CUDNN files in {cudnn_dest}")
    if os.path.exists(cudnn_src):
        if os.path.exists(cudnn_dest):
            # check for different files
            filecmp.clear_cache()
            for file in os.listdir(cudnn_src):
                src_file = os.path.join(cudnn_src, file)
                dest_file = os.path.join(cudnn_dest, file)
                #if dest file exists, check if it's different
                if os.path.exists(dest_file):
                    status = shutil.copy2(src_file, cudnn_dest)
            if status:
                print("Copied CUDNN 8.6 files to destination")
    '''
    print(f"Checking for B&B files in {bnb_dest}")
    if not os.path.exists(bnb_dest):
        # make destination directory
        os.makedirs(bnb_dest, exist_ok=True)
    printed = False
    filecmp.clear_cache()
    for file in os.listdir(bnb_src):
        src_file = os.path.join(bnb_src, file)
        if file == "main.py":
            dest = os.path.join(bnb_dest, "cuda_setup")
            if not os.path.exists(dest):
                os.mkdir(dest)
        else:
            dest = bnb_dest
            if not os.path.exists(dest):
                os.mkdir(dest)
        dest_file = os.path.join(dest, file)
        status = shutil.copy2(src_file, dest)
    if status:
        print("Copied B&B files to destination")
    
    d_commit = 'f7bb9ca'
    diffusers_cmd = f"git+https://github.com/huggingface/diffusers.git@{d_commit}#egg=diffusers --force-reinstall"
    run(f'"{python}" -m pip install {diffusers_cmd}', f"Installing Diffusers {d_commit} commit", "Couldn't install diffusers")
    #install requirements file
    t_commit = '491a33d'
    trasn_cmd = f"git+https://github.com/huggingface/transformers.git@{t_commit}#egg=transformers --force-reinstall"
    run(f'"{python}" -m pip install {trasn_cmd}', f"Installing Transformers {t_commit} commit", "Couldn't install transformers")

    req_file = os.path.join(os.getcwd(), "requirements.txt")
    run(f'"{python}" -m pip install -r "{req_file}"', "Updating requirements", "Couldn't install requirements")
    '''