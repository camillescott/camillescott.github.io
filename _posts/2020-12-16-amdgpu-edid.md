---
layout: post
title: "The Tale of the Fuzzy Text"
subtitle: "Manually overriding the EDID data on GNU/Linux with the amdgpu driver"
mathjax: true
---

Or: how Camille ended up learning more than she probably needed about EDID, Linux's `amdgpu` driver, and even the boot process. This will be relevant to you if you own a recent AMD GPU (one that uses `amdgpu` instead of the old `radeon` driver) and have a monitor displaying inexplicable fuzzy and pixelated text.

## Preamble

So you just got yourself a fancy new AMD graphics card. Maybe you dual boot Windows and GNU/Linux, the former for gaming and the latter for work. You've already booted into Windows and flexed your F250-sized GPU's muscles on some games, so now it's time to make sure things work correctly on your Linux install. You boot that sucker up, log in without issue, and are about to declare victory -- when you squint a tad. Are your glasses out of focus? Maybe you don't even wear glasses, but your text is kind of fuzzy and pixelated. Oh no. Something is wrong with the graphics driver. You pray to the Machine Spirits that it's a simple resolution or refresh rate issue, and start poking at your display settings. Nothing works. Your resolution is correct, your refresh rate is fine, and the card has correctly detected your monitor. If you've been using Linux for a while, you sigh deeply, for you know what's coming: This Is Going To Suck.

To save you some suspense, dear reader, I'll tell you now what the problem is: your GPU has decided that your monitor is a TV, and is feeding it YCbCr colors. With less color space to work with, and slightly different rendering, the edges of things like text get funky, and everything feels slightly out of focus. Your monitor would rather be fed full RGB, but it will settle for YCbCr. And unfortunately, because your monitor was trusting enough to tell `amdgpu` that it's capable of both, the driver decided [it would be having YCbCr, whether it wants it or not](https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/tree/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.c?h=linux-5.6.y&id=63c3d497410788af1804579f0cded007318c5991#n3849).

Well then! --

![that's easy](https://thumbs.gfycat.com/SeriousFloweryDipper-small.gif)

-- you just have to switch your output to RGB mode, after which you can happily skip along to whatever grail you're implementing. Alas, It Is Not That Easy.

## Initial Thought: Poke X11

Neither the display manager or shell gives you options to change the color signal format. X11, however, is aware, and makes the decision based on the graphics driver. If you're on an old card, and are thus on the `radeon` driver, the property will probably show up in the output from `xrandr`; but if that's the case, you won't be having this problem in the first place, as it only shows up with the newer `amdgpu` driver. If you look at the `X11` log (on newish Ubuntu it will live at `~/.local/share/xorg/Xorg.0.log`), you'll find a line somewhat like:

```bash
AMDGPU(0): Supported color encodings: RGB 4:4:4 YCrCb 4:4:4
```

One would think you could use `xrandr` to tell X11 to prefer RGB. One would be wrong. The [relevant entries](https://askubuntu.com/questions/883988/xrandr-how-to-find-the-correct-rgb-full-spectrum-output-command-for-my-system) don't exist for `amdgpu` -- no `output_csc`, no `Broadcast RGB`. Which make sense, when you think about it, because of that nice little comment in the linked `amdgpu` source above: `/* TODO: un-hardcode */`. Well then.

## Next Thought: Spoof the EDID

### The EDID Binary

I remembered that I had a similar issue a few years back when using this monitor with my MacBook, and that the solution was to give it a custom EDID file to override what the monitor provides. EDID, or [Extended Display Identification Data](https://en.wikipedia.org/wiki/Extended_Display_Identification_Data), is the format your monitor uses to tell your video hardware about its capabilities. EDID as a 128 byte binary format (with support for extension blocks); X11 will report it like so:

```bash
	EDID:
		00ffffffffffff0004728700b21e4084
		2c12010380301b78caee95a3544c9926
		0f5054bfef80714f8180b300d1c09500
		a940814081c01a3680a070381e403020
		3500132b21000018000000fd00384c1f
		5311000a202020202020000000fc0048
		323133480a20202020202020000000ff
		004c46383044303032383530300a0148
		02031df14a9005040302011112131423
		09070765030c00100083010000023a80
		1871382d40582c450007442100001f01
		1d8018711c1620582c25000744210000
		9f011d007251d01e206e285500c48e21
		00001e8c0ad08a20e02d10103e960007
		44210000180000000000000000000000
		0000000000000000000000000000000d
```

The linked Wiki article gives a detailed explanation of how the various fields are encoded; for our purposes, we care about bits 3 and 4 of byte 24, which encode the display type. My monitor happily reports `01` for these bits, which tells the GPU it can handle `RGB 4:4:4` and `YCrCb 4:4:4`, after which `amdgpu` says "thanks, I hereby dub you a TV, now fuck off."

On MacOS, I was able to use this [handy script](https://gist.github.com/adaugherity/7435890), which snarfs your monitor's EDID, munges the correct bits, and sticks the resulting EDID binary in a place the kernel cares about. On linux, the commands are different.

#### Acquiring the EDID Binary

You might get lucky and find an existing modified EDID binary for your specific monitor, perhaps in [this thread](https://embdev.net/topic/284710). Mine is an Acer K272HUL, so I had to do it myself.

You'll need an EDID file for you monitor to modify. There are couple ways to do this. The first is the classic unixy "everything is a file" approach; you can run:

```bash
╭─ ‹base› camille@galactica ~ ‹main›
╰─$ find /sys/devices/pci*/ -name edid
/sys/devices/pci0000:00/0000:00:02.0/0000:01:00.0/0000:02:00.0/0000:03:00.0/drm/card0/card0-HDMI-A-1/edid
/sys/devices/pci0000:00/0000:00:02.0/0000:01:00.0/0000:02:00.0/0000:03:00.0/drm/card0/card0-DP-2/edid
/sys/devices/pci0000:00/0000:00:02.0/0000:01:00.0/0000:02:00.0/0000:03:00.0/drm/card0/card0-DP-3/edid
/sys/devices/pci0000:00/0000:00:02.0/0000:01:00.0/0000:02:00.0/0000:03:00.0/drm/card0/card0-DP-1/edid
```
These files get the EDID for the monitor connected to the corresponding port. Your directory structure will be different, depending on how your PCI slots and lanes are laid out. If you cat one, you get a bunch of binary in your terminal. There happens to be a Debian package called `read-edid` that contains a program that will parse this for you (`apt install read-edid`); for me, for example, I get:

```bash
╭─ ‹base› camille@galactica ~ ‹main›
╰─$ cat /sys/devices/pci0000:00/0000:00:02.0/0000:01:00.0/0000:02:00.0/0000:03:00.0/drm/card0/card0-DP-2/edid | parse-edid
Checksum Correct

Section "Monitor"
	Identifier "Acer K272HUL"
	ModelName "Acer K272HUL"
	VendorName "ACR"
	# Monitor Manufactured week 4 of 2014
	# EDID version 1.3
	# Digital Display
```

And so forth (there will be much more output). Note that this is in X11 config format. So let's copy it...

```bash
cat /sys/devices/pci0000:00/0000:00:02.0/0000:01:00.0/0000:02:00.0/0000:03:00.0/drm/card0/card0-DP-2/edid > K272HUL.original.bin
```

That `read-edid` package also comes with a utility called `get-edid` that you can use to extract the
EDID file. I suspect it basically does the same thing as above, but try it out if you'd like.

#### Modifying the EDID Binary

There are a couple ways to do this. This user-friend GUI way of doing it is to use a program like [wxedid](https://sourceforge.net/projects/wxedid/); I had to compile it from source, which was a standard `./configure; make` deal. There is also a package in AUR if you're on Arch. You can set the appropriate bits to `0` down in the `CHD` section.

You could also do it manually; for example, you might modify that [Ruby script](https://gist.github.com/adaugherity/7435890) from earlier, or use it as a guide to write you own. For example, here's some stripped down Python:

```python
#!/usr/bin/env python

import argparse
from functools import reduce
import sys

def printerr(*args):
    print(*args, file=sys.stderr)

def print_edid_as_hex(edid_bytes):
    edid_hex = ['{:02x}'.format(c) for c in edid_bytes]

    for idx in range(0, len(edid_hex), 16):
        printerr(''.join(edid_hex[idx:idx+16]))


parser = argparse.ArgumentParser()
parser.add_argument('edid_file')
args = parser.parse_args()

edid_string = ''
with open(args.edid_file, 'rb') as fp:
    edid_string = bytearray(fp.read())

printerr('Source EDID (Hex)')
printerr('-' * 64)
printerr()
print_edid_as_hex(edid_string)
printerr()

printerr('Color modes:')
if edid_string[24] & 0b11000 == 0b0:
    printerr('RGB 4:4:4 only')
elif edid_string[24] & 0b11000 == 0b01000:
    printerr('RGB 4:4:4 and YCrCb 4:4:4')
elif edid_string[24] & 0b11000 == 0b10000:
    printerr('RGB 4:4:4 and YCrCb 4:2:2')
else:
    printerr('RGB 4:4:4, YCrCb 4:4:4, and YCrCb 4:2:2')

printerr('Begin modifying EDID...')
printerr('Setting color mode to RGB 4:4:4 only...')

edid_string[24] &= ~(0b11000)
printerr()

printerr('Removing extension blocks...')
printerr(f'Number of extension blocks: {edid_string[126]}')
printerr('Removing extension blocks...')

edid_string = edid_string[:128]
edid_string[126] = 0
edid_string[127] = (0x100 - (reduce(lambda a, b: a + b, edid_string[0:127]) % 256)) % 256
printerr()

printerr('Final EDID (Hex)')
printerr('-' * 64)
print_edid_as_hex(edid_string)
printerr()

sys.stdout.buffer.write(edid_string)
```

Which will give you something like this:

```sh
╭─ ‹base› camille@galactica ~ ‹main›
╰─$ python patch-edid-minimal.py .config/K272HUL.original.bin > K272HUL.modified.bin
Source EDID (Hex)
----------------------------------------------------------------

00ffffffffffff000472dd035d5a4040
04180103803c22782a4b75a7564ba325
0a5054bd4b00d100d1c08180950f9500
b30081c0a940565e00a0a0a029503020
350055502100001e000000fd00174c0f
4b1e000a202020202020000000ff0054
30534141303031343230300a000000fc
0041636572204b32373248554c0a0198
020324744f0102030506071011121314
15161f04230907078301000067030c00
2000b83c023a80d072382d40102c9680
565021000018011d8018711c1620582c
250056502100009e011d80d0721c1620
102c258056502100009e011d00bc52d0
1e20b828554056502100001e8c0ad090
204031200c405500565021000018007e

Color modes:
RGB 4:4:4 and YCrCb 4:4:4
Begin modifying EDID...
Setting color mode to RGB 4:4:4 only...

Removing extension blocks...
Number of extension blocks: 1
Removing extension blocks...

Final EDID (Hex)
----------------------------------------------------------------
00ffffffffffff000472dd035d5a4040
04180103803c2278224b75a7564ba325
0a5054bd4b00d100d1c08180950f9500
b30081c0a940565e00a0a0a029503020
350055502100001e000000fd00174c0f
4b1e000a202020202020000000ff0054
30534141303031343230300a000000fc
0041636572204b32373248554c0a00a1
```

Regardless of your method, you've now got an EDID binary matching your monitor without the YCbCr support. Now, we simply tell X11 about it and we're good to go!

### Informing X11

Welp, you can't.

I tried [many](https://unix.stackexchange.com/questions/496553/second-monitor-not-recognized-xorg-conf-file-resolved). [different](https://unix.stackexchange.com/questions/295784/how-to-tell-intel-graphics-to-use-my-custom-edid-file). [variants](https://unix.stackexchange.com/questions/377781/how-to-set-custom-edid-manually) of X11 configuration options; I tried telling it it in a `Device` block, a `Screen` block, a `Monitor` block, to no avail. In fact, it appears once again that the existence of the `CustomEDID` option is driver-dependent, as it doesn't even exist in the [current version's manual](https://www.x.org/releases/current/doc/man/man5/xorg.conf.5.xhtml).

Apparently, we'll have to go to a lower level.

### Informing the Kernel

A [number](https://forum.libreelec.tv/thread/14940-bug-how-to-get-full-rgb-hdmi-output-on-amd-videocards-with-le/) of [guides](https://blog.tingping.se/2018/12/01/amdgpu-fullrgb.html) describe the need to load the customized EDID into the kernel as a firmware at boot. The all-powerful Arch wiki itself has a [section](https://wiki.archlinux.org/index.php/kernel_mode_setting#Forcing_modes_and_EDID) on this, where it provides several solutions. There even is a convenient way to do this after boot, according to the Wiki, using kernel debugging features. As root:

```bash
cat K272HUL.modified.bin > /sys/kernel/debug/dri/0/DP-2/edid_override
```

Well, this did nothing for me. I didn't spend too much time playing with it, so maybe some reader will have better luck. Instead, I moved on to boot-time loading.

I based my initial attempts off [this helpful guide by someone called TingPing](https://blog.tingping.se/2018/12/01/amdgpu-fullrgb.html), the aforementioned Arch wiki article, and Canonical's [documentation for adding kernel boot parameters](https://wiki.ubuntu.com/Kernel/KernelBootParameters). I have multiple monitors, so I needed to load the EDID for a specific port; note the `DP-2:` before the file path (the `firmware` directory gets prefixed automatically). So I stick the modified binary in `/usr/lib/firmware/edid/` and put the parameters in `/etc/default/grub`:

```bash
GRUB_CMDLINE_LINUX_DEFAULT="splash drm.edid_firmware=DP-2:edid/K272HUL.modified.bin"
```

Then you just run `update-grub`, reboot, and! --

nothing changes! Shit.

### A Helpful Bug Report

Naturally, I looked at `dmesg` to see if the damn kernel would explain itself, and it did! A grep for `EDID` turned up:

```bash
[    1.874241] kernel: [drm:edid_load [drm]] *ERROR* Requesting EDID firmware "edid/K272HUL.modified.bin" failed (err=-2)
```

Well, it kind of explained itself. Googling for this error turns up a fair number of results, most of which are for corrupted EDID files, but in that case the kernel does more specific complaining -- my binary is just fine thankyouverymuch. I finally stumbled upon [this bug report](https://bugs.launchpad.net/ubuntu/+source/initramfs-tools/+bug/1814938), however, which was the last piece of the puzzle. Somewhere along the line, Ubuntu (or the kernel itself?) got more secure, and started requiring the firmware be in the initramfs image. So, you have to add a helper to your initramfs creation: you create a new file at `/etc/initramfs-tools/hooks/edid`, which contains:

```
#!/bin/sh
PREREQ=""
prereqs()
{
    echo "$PREREQ"
}

case $1 in
prereqs)
    prereqs
    exit 0
    ;;
esac

. /usr/share/initramfs-tools/hook-functions
# Begin real processing below this line
mkdir -p "${DESTDIR}/lib/firmware/edid"
cp -a /usr/lib/firmware/edid/K272HUL.modified.bin "${DESTDIR}/lib/firmware/edid/K272HUL.modified.bin"
exit 0
```

Make it executable with `chmod +x /etc/initramfs-tools/hooks/edid`, and then rebuild the image with `update-initramfs -u`. If all goes well, you'll have a new set of images spit out with no error codes. You'll reboot, furtively peak at your monitor, and!...

![success gif](https://media1.tenor.com/images/5958957a8b5ad55c8874eeafcc60829a/tenor.gif?itemid=5101957)

SUCCESS! Your text is nice and crisp, and now if you grep your dmesg, it will say:

```bash
[    1.930533] kernel: [drm] Got external EDID base block and 1 extension from "edid/K272HUL.modified.bin" for connector "DP-2"
```

And the X11 log, when loading up your monitor, should now have:

```bash
[   118.655] (II) AMDGPU(0): Supported color encodings: RGB 4:4:4
```

Sweet, sweet victory.


