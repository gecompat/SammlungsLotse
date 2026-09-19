from __future__ import annotations
import importlib.util, unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
s=importlib.util.spec_from_file_location("p",ROOT/"tools"/"experiments"/"provision_exp_0021_docker_image.py");m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_profile_image_verifies(self):
  p=m.load(); d=p["docker_image"]
  m.verify({"Id":d["id"],"Os":"linux","Architecture":"amd64","Config":{"Entrypoint":d["entrypoint"]}},p)
 def test_profile_image_rejects_drift(self):
  p=m.load()
  with self.assertRaises(m.ProvisionError): m.verify({"Id":"sha256:no","Os":"linux","Architecture":"amd64","Config":{"Entrypoint":[]}},p)
 def test_transfer_tags_loaded_image_for_expected_docker_tag(self):
  p=m.load(); d=p["docker_image"]
  source={"Id":p["source_podman_image"]["id"],"Os":"linux","Architecture":"amd64","Config":{"Entrypoint":d["entrypoint"]}}
  run=MagicMock(side_effect=[MagicMock(returncode=0,stdout=__import__('json').dumps([source])),MagicMock(returncode=0),MagicMock(returncode=0)])
  save=MagicMock(stdout=MagicMock(),returncode=0); save.stdout.close=MagicMock(); save.wait=MagicMock()
  with patch.object(m.subprocess,"run",run),patch.object(m.subprocess,"Popen",return_value=save): m.transfer(p)
  self.assertIn((['docker','tag',p['source_podman_image']['id'],d['tag']],),[call.args for call in run.call_args_list])
if __name__=="__main__": unittest.main()
