#!/usr/bin/env python3
"""Restore the Amaravati plot-map working kit from this repository.

    python3 kit/bootstrap.py <repo_dir> <password> [kit_dir]      (kit_dir default /home/claude/kit)

Decrypts kit_state.enc (needs the site password), unpacks it into kit_dir, and copies the master-plan
map tiles (kit/map_tiles) and the website tiles (tiles/) next to it. Then read kit_dir/HANDOFF_NOTE.md.
Needs: pip install cryptography (usually preinstalled).
"""
import sys, os, json, base64, io, tarfile, shutil
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_der_private_key
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

repo, pw = sys.argv[1], sys.argv[2]
kit = sys.argv[3] if len(sys.argv) > 3 else '/home/claude/kit'
b = base64.b64decode
key = json.load(open(os.path.join(repo, 'key.json')))
kek = PBKDF2HMAC(hashes.SHA256(), 32, b(key['salt']), key['iter']).derive(pw.encode())
try: priv = load_der_private_key(AESGCM(kek).decrypt(b(key['iv']), b(key['wrapped']), None), None)
except Exception: sys.exit('Wrong password.')

def opened(path):
    d = json.load(open(path))
    epk = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), b(d['epk']))
    k = HKDF(hashes.SHA256(), 32, b(d['salt']), b'amaravati-plots-v1').derive(priv.exchange(ec.ECDH(), epk))
    return AESGCM(k).decrypt(b(d['iv']), b(d['ct']), None)

os.makedirs(kit, exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(opened(os.path.join(repo, 'kit_state.enc'))), mode='r:gz') as tf: tf.extractall(kit)
shutil.copytree(os.path.join(repo, 'kit', 'map_tiles'), os.path.join(kit, 'map_tiles'), dirs_exist_ok=True)
os.makedirs(os.path.join(kit, 'work'), exist_ok=True)
shutil.copytree(os.path.join(repo, 'tiles'), os.path.join(kit, 'work', 'tiles'), dirs_exist_ok=True)
live = json.loads(opened(os.path.join(repo, 'data.json')))          # sanity check: live site data matches the state
n = len(json.load(open(os.path.join(kit, 'plots_data.json'))))
print(f'kit restored to {kit}: {n} plot records; live site shows {len(live["plots"])} plots')
print(f'Next: read {kit}/HANDOFF_NOTE.md')
