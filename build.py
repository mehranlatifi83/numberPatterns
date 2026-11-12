"""Build numberPatterns-<version>.nvda-addon: compiles .po files to .mo and zips the addon folder."""

import ast
import os
import re
import struct
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ADDON = os.path.join(HERE, "addon")


def parsePo(path):
	entries, key, cur, field = {}, None, [], None
	def flush():
		if field == "msgstr" and key is not None:
			entries[key] = "".join(cur)
	for line in open(path, encoding="utf-8"):
		line = line.strip()
		if line.startswith("msgid "):
			flush()
			field, cur = "msgid", [ast.literal_eval(line[6:])]
		elif line.startswith("msgstr "):
			key = "".join(cur)
			field, cur = "msgstr", [ast.literal_eval(line[7:])]
		elif line.startswith('"'):
			cur.append(ast.literal_eval(line))
	flush()
	return entries


def writeMo(entries, path):
	keys = sorted(entries)
	ids = b"".join(k.encode() + b"\0" for k in keys)
	strs = b"".join(entries[k].encode() + b"\0" for k in keys)
	n = len(keys)
	keyStart = 28 + 16 * n
	valStart = keyStart + len(ids)
	koffs, voffs, o = [], [], 0
	for k in keys:
		b = k.encode()
		koffs += [len(b), keyStart + o]
		o += len(b) + 1
	o = 0
	for k in keys:
		b = entries[k].encode()
		voffs += [len(b), valStart + o]
		o += len(b) + 1
	with open(path, "wb") as f:
		f.write(struct.pack("Iiiiiii", 0x950412DE, 0, n, 28, 28 + 8 * n, 0, 0))
		f.write(struct.pack(f"{2 * n}i", *koffs))
		f.write(struct.pack(f"{2 * n}i", *voffs))
		f.write(ids)
		f.write(strs)


def main():
	for root, _dirs, files in os.walk(os.path.join(ADDON, "locale")):
		for name in files:
			if name.endswith(".po"):
				po = os.path.join(root, name)
				writeMo(parsePo(po), po[:-3] + ".mo")
	version = re.search(r"^version\s*=\s*(\S+)", open(os.path.join(ADDON, "manifest.ini"), encoding="utf-8").read(), re.M).group(1)
	out = os.path.join(HERE, f"numberPatterns-{version}.nvda-addon")
	with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
		for root, _dirs, files in os.walk(ADDON):
			for name in files:
				if name.endswith((".po", ".pyc")):
					continue
				full = os.path.join(root, name)
				z.write(full, os.path.relpath(full, ADDON))
	print(out)


if __name__ == "__main__":
	main()
