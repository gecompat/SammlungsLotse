#!/usr/bin/env python3
"""Explicit offline Podman-to-Docker image transfer for EXP-0021 only."""
from __future__ import annotations
import argparse,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PROFILE=ROOT/"experiments"/"ebook"/"exp-0021"/"profile.json"
class ProvisionError(RuntimeError): pass
def load(): return json.loads(PROFILE.read_text(encoding="utf-8"))
def inspect(tag):
 r=subprocess.run(["docker","image","inspect",tag],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,encoding="utf-8",check=False)
 return json.loads(r.stdout)[0] if r.returncode==0 else None
def verify(value,p):
 d=p["docker_image"]; actual=str(value.get("Id", "")); actual=actual if actual.startswith("sha256:") else "sha256:"+actual
 if actual!=d["id"] or value.get("Os")!=d["os"] or value.get("Architecture")!=d["architecture"] or value.get("Config",{}).get("Entrypoint")!=d["entrypoint"]: raise ProvisionError("docker_image_contract_differs")
def transfer(p):
 src=p["source_podman_image"]
 check=subprocess.run(["podman","image","inspect",src["tag"]],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,encoding="utf-8",check=False)
 if check.returncode: raise ProvisionError("podman_source_unavailable")
 if not check.stdout: raise ProvisionError("podman_source_contract_differs")
 source=json.loads(check.stdout)[0]; d=p["docker_image"]
 if source.get("Id")!=src["id"] or source.get("Os")!=d["os"] or source.get("Architecture")!=d["architecture"] or source.get("Config",{}).get("Entrypoint")!=d["entrypoint"]: raise ProvisionError("podman_source_contract_differs")
 save=subprocess.Popen(["podman","save",src["tag"]],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
 load=subprocess.run(["docker","load"],stdin=save.stdout,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=False)
 save.stdout.close(); save.wait()
 if save.returncode or load.returncode: raise ProvisionError("offline_transfer_failed")
 tag=subprocess.run(["docker","tag",src["id"],d["tag"]],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=False)
 if tag.returncode: raise ProvisionError("docker_tag_failed")
def main():
 a=argparse.ArgumentParser();a.add_argument("--from-podman",action="store_true");x=a.parse_args();p=load();v=inspect(p["docker_image"]["tag"])
 if v is None:
  if not x.from_podman: raise ProvisionError("docker_image_unavailable")
  transfer(p);v=inspect(p["docker_image"]["tag"])
 if v is None: raise ProvisionError("docker_image_unavailable")
 verify(v,p);print("[OK] EXP-0021 Docker image")
if __name__=="__main__":
 try: main()
 except Exception as e: print(type(e).__name__);raise SystemExit(3)
