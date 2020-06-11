import os

import argparse
from fpdf import FPDF

import pprint

A4_WIDTH = 210
A4_HEIGHT = 297

MARGIN = 4
IMAGE_WIDTH = 100
INTER_IMAGE_GAP = 2

NADE_GROUPS = [
    ['lineup_crosshair.jpg', 'lineup.jpg'],
    ['pos_shot.jpg', 'pos_bot.jpg'],
    ['effect.jpg', 'last.jpg']
]


def get_structure(map, side, allowed_nades):
    nades = {}
    structure = {}

    for root, dirs, files in os.walk(os.path.curdir + '/maps/' + map + '/' + side):
        if not nades:
            nades = dict.fromkeys(dirs)
            continue

        nade = root.split('/')[-1]

        if nade in nades:
            nades[nade] = [root + '/' + file for file in files]

    structure_smokes = {}
    structure_mollies = {}
    structure_flashes = {}
    structure_hes = {}
    for nade_name in nades:
        if 'smokes' in allowed_nades and 'smoke' in nade_name:
            structure_smokes[nade_name] = nades[nade_name]
        if 'mollies' in allowed_nades and 'molly' in nade_name:
            structure_mollies[nade_name] = nades[nade_name]
        if 'flashes' in allowed_nades and 'flash' in nade_name:
            structure_flashes[nade_name] = nades[nade_name]
        if 'hes' in allowed_nades and 'hes' in nade_name:
            structure_hes[nade_name] = nades[nade_name]

    return {**structure_smokes, **structure_mollies, **structure_flashes, **structure_hes}


def create_front_page(pdf, map, nades):
    pdf.add_page()
    pdf.set_font('Open Sans Bold')
    pdf.cell(0, 10, txt=f'{map.capitalize()} Smokes', ln=1, align='C')

    pdf.set_font('Open Sans')

    counter = 1
    for name, nade in nades.items():
        text = str(counter) + '. ' + name.replace('_', ' ')
        pdf.cell(0, 10, txt=text, ln=1)
        counter += 1


def create_pdf(map, side, nades=['smokes', 'mollies', 'flashes', 'hes']):
    if not os.path.exists(os.path.curdir + '/maps/' + map + '/' + side):
        return

    print(f'Creating pdf for {map} on {side} side with {", ".join(nades)} ....')

    nade_string = '' if nades == ['smokes', 'mollies', 'flashes', 'hes'] else '_' + '_'.join(nades)
    nades = get_structure(map, side, nades)

    pdf = FPDF()
    pdf.add_font('Open Sans', '', os.path.curdir + '/fonts/Open_Sans/OpenSans-Regular.ttf', uni=True)
    pdf.add_font('Open Sans Bold', '', os.path.curdir + '/fonts/Open_Sans/OpenSans-Bold.ttf', uni=True)

    create_front_page(pdf, map, nades)

    nade_counter = 1
    pdf.set_font('Open Sans Bold')

    for dir_name, nade in nades.items():
        name = str(nade_counter) + '. ' + dir_name.replace('_', ' ').upper()
        pdf.add_page()
        pdf.cell(0, txt=name, ln=1, align='C')

        nade_path = '/'.join([os.path.curdir, 'maps', map, side, dir_name])
        fname_txt = nade_path + '/text.txt'
        if os.path.isfile(fname_txt):
            with open(fname_txt) as f:
                nade_text = f.read()
            pdf.set_font('Open Sans')
            pdf.y += pdf.l_margin + 2
            pdf.multi_cell(0, 5, txt=nade_text)
            pdf.set_font('Open Sans Bold')

        fname_throw = nade_path + '/throw.txt'
        if os.path.isfile(fname_throw):
            with open(fname_throw) as f:
                throw = f.read()
            old_y = pdf.y
            pdf.y = 10.5
            pdf.cell(50, txt=throw, ln=1)
            pdf.y = old_y

        row_counter = 0
        for nade_group in NADE_GROUPS:
            indent_y = 8 + 77 * row_counter + pdf.y
            height = IMAGE_WIDTH * 3 / 4  # assumes all images are 4:3

            if indent_y + height > pdf.page_break_trigger:
                pdf.add_page()
                pdf.cell(0, txt=name, ln=1, align='C')
                row_counter = 0
                indent_y = 8 + 77 * row_counter + pdf.y

            prev_image = False
            for image in nade_group:
                image = [nade_image for nade_image in nade if image in nade_image]
                if image:
                    image = image[0]
                    indent_x = MARGIN + IMAGE_WIDTH + INTER_IMAGE_GAP if prev_image else MARGIN
                    pdf.image(image, x=indent_x, y=indent_y, w=IMAGE_WIDTH)
                    prev_image = True
            row_counter += 1

        nade_counter += 1

    pdf.output(f'maps/{map}/{map}_nades_{side}{nade_string}.pdf')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create pdf for a given map')
    parser.add_argument('map', type=str, nargs=1,
                        help='a map for which the pdf should be created')
    parser.add_argument('--side', dest='side', type=str,
                        help='a side for which the pdf should be created')
    parser.add_argument('--nades', dest='nades', type=str, nargs='*',
                        help='nades for which the pdf should be created. Enter multiple nades separated with spaces. '
                             'Should be one or all of smokes, mollies, flashes, hes')
    args = parser.parse_args()

    nades = ['smokes', 'mollies', 'flashes', 'hes']
    if args.nades and all(i in ['smokes', 'mollies', 'flashes', 'hes'] for i in args.nades):
        nades = args.nades

    if args.map[0] == 'all':
        maps = [map for map in os.listdir(os.path.curdir + '/maps/') if not map.startswith('.')]
    else:
        maps = [args.map[0]]

    for map in maps:
        if args.side and args.side in ['t', 'ct']:
            create_pdf(map, side=args.side, nades=nades)
        else:
            create_pdf(map, side='t', nades=nades)
            create_pdf(map, side='ct', nades=nades)
