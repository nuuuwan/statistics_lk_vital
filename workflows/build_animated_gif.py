import os

import imageio
from utils import Log

dir_images = os.path.abspath('images')
log = Log('build_animated_gif')


def main():
    images = []
    for file_name in os.listdir(dir_images):
        if not file_name.endswith('.png'):
            continue
        if '2006' in file_name:
            continue
        if '199' in file_name:
            continue
        png_path = os.path.join(dir_images, file_name)
        images.append(imageio.imread(png_path))
    gif_path = os.path.join(dir_images, 'cause-of-death-ALL.gif')
    imageio.mimsave(gif_path, images, duration=2_000)
    log.info(f'Animated GIF saved to {gif_path}')


if __name__ == '__main__':
    main()
