"""Render only the bundled synthetic demo output into a fresh local GIF."""
import argparse
import io
import os
from pathlib import Path
import subprocess
import sys
import textwrap

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mindtunnel.files import write_private


def make_gif(destination):
    from PIL import Image, ImageDraw, ImageFont

    completed = subprocess.run([sys.executable, str(ROOT/'scripts/demo.py')], cwd=ROOT,
                               env={'PATH':os.defpath, 'PYTHONIOENCODING':'utf-8', 'PYTHONDONTWRITEBYTECODE':'1'},
                               capture_output=True, timeout=30)
    if completed.returncode:
        raise ValueError('synthetic_demo_failed')
    text = completed.stdout.decode('utf-8')
    if 'PUBLIC REQUEST (synthetic):' not in text or 'Malicious plan rejected; synthetic demo passed.' not in text:
        raise ValueError('unexpected_demo_output')
    lines = []
    for line in text.splitlines():
        lines.extend(textwrap.wrap(line, width=86, replace_whitespace=False,
                                   drop_whitespace=False, break_on_hyphens=False) or [''])
    pages = [lines[index:index+25] for index in range(0,len(lines),25)]
    font = ImageFont.load_default(size=23)
    frames = []
    for number, page in enumerate(pages,1):
        image = Image.new('RGB',(1280,900),'white')
        draw = ImageDraw.Draw(image)
        draw.text((36,24),'MindTunnel synthetic demo  '+str(number)+'/'+str(len(pages)),font=font,fill='black')
        for row, line in enumerate(page):
            draw.text((36,76+row*31),line,font=font,fill='black')
        frames.append(image)
    output = io.BytesIO()
    frames[0].save(output,format='GIF',save_all=True,append_images=frames[1:],
                   duration=7000,loop=0,disposal=2,optimize=False)
    write_private(destination,output.getvalue())
    return len(frames)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True)
    args = parser.parse_args()
    try:
        count = make_gif(args.out)
    except (ImportError,OSError,ValueError,UnicodeError,subprocess.SubprocessError):
        print('Rejected: local_demo_render_failed',file=sys.stderr)
        return 2
    print('Synthetic local GIF written with '+str(count)+' frames.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
