import glob
import pathlib
import re
import shutil
import os
from collections import defaultdict

import click
import requests

from wiktionary import get_wiktionary, parse_audio_urls, download_file
from spreadsheet import list_existing_categories, get_category_worksheet, get_category_words

root_dir = pathlib.Path(__file__).parent

@click.group()
def cli():
    pass

@cli.command()
def ls():
    for category in list_existing_categories():
        print(category)

@cli.command()
@click.option('--name', prompt='Category name', help='The word category to print')
def category(name):
    ws = get_category_worksheet(name)
    for rec in ws.get_all_records():
        print(rec)


@cli.command()
@click.option('--dir', default='public/audio/{word}')
@click.option('--word', default=None, required=False)
@click.option('--category', default=None, required=False)
def download_audio(dir, word=None, category=None):
    ses = requests.Session()
    ses.headers['User-Agent'] = 'PotapovBot/0.0 (https://potapov.dev; arseniy@potapov.dev) python-requests/0.0'
    if word and not category:
        categories = [None]
    elif category:
        categories = [category]
    else:
        categories = list(list_existing_categories())
    only_words = [word] if word else None
    for category in categories:
        if category:
            print(f'\n\nCategory: {category}')
            ws = get_category_worksheet(category)
        else:
            ws = None
        if only_words:
            words = only_words
        elif category:
            words = [
                rec['word'] for rec in ws.get_all_records()
                if not rec.get('audio') and not rec['word'].startswith('#')
            ]
        else:
            raise ValueError('Either word or category should be specified')

        for word in words:
            print(f'\n{word}...')
            try:
                content = get_wiktionary(word, ses=ses)
            except IOError as ex:
                print(f'  {ex}')
                continue
            urls = parse_audio_urls(content)
            print(urls)
            filenames = [
                download_file(url, dir.format(word=word), ses=ses)
                for url in urls
            ]
            print(filenames)
            if filenames and category:
                if existing_cell := ws.find(word, in_column=1):
                    ws.update_cell(existing_cell.row, 5, ';'.join(filenames))
                    print(f'  Updated row {existing_cell.row}')
                else:
                    # word, source_category, label, pictures, audio, weight, suppress_pairs_with
                    ws.append_row([word, '', '', '', ';'.join(filenames), 1, ''])
                    print('  Added row')


@cli.command()
@click.option('--dir', default='public/pictures')
def sort_pictures(dir):
    word_counters = defaultdict(int)
    all_categories = list_existing_categories()
    all_words = defaultdict(list)
    for category in all_categories:
        for word in get_category_words(category):
            all_words[word].append(category)
    exemptions = {
        'chicken-food-mj1.png': ('chicken', 'food', 'mj'),
        'chicken-mj1.png': ('chicken', 'animals', 'mj'),
        'chicken-mj2.png': ('chicken', 'animals', 'mj'),
        'crocodile_mj1.png': ('crocodile', 'animals', 'mj'),
        'giraffe_mj1.png': ('giraffe', 'animals', 'mj'),
        'horse_mj1.png': ('horse', 'animals', 'mj'),
        'horse_mj2.png': ('horse', 'animals', 'mj'),
        'horse_mj3.png': ('horse', 'animals', 'mj'),
        'king_mj1.png': ('king', 'fantasy', 'mj'),
        'mother_family_mj1.png': ('mother', 'family', 'mj'),
        'prince_mj1.png': ('prince', 'fantasy', 'mj'),
        'princess_mj1.png': ('prince', 'fantasy', 'mj'),
        'princess_mj2.png': ('prince', 'fantasy', 'mj'),
        'queen_mj1.png': ('queen', 'fantasy', 'mj'),
        'queen_mj2.png': ('queen', 'fantasy', 'mj'),
        'tomato_food_mj1.png': ('tomato', 'food', 'mj'),
        'witch_mj1.png': ('witch', 'fantasy', 'mj'),
        'witch_mj2.png': ('witch', 'fantasy', 'mj'),
        'wizard_mj1.png': ('wizard', 'fantasy', 'mj'),
        'ars_sugar_crystals_macro_an_illustration_for_a_book_white_backg_a88c8ef3-e1f9-4424-8b9a-80a6258ca876.png': ('sugar', 'food', 'mj'),
        'ars_spoon_with_sugar_sand__an_illustration_for_a_book_white_bac_41079b43-092f-4798-b0f5-34f0175b8068.png': ('sugar', 'food', 'mj'),
        'ars_chilli_pepper_food_an_illustration_for_a_book_white_backgro_b618ab73-ff5b-43da-ac4a-f4245eddb5a8.png': ('pepper', 'food', 'mj'),
        'ars_glass_of_milk_an_illustration_for_a_book_white_background_c_ded288d8-2dbe-4d86-877d-1729b18e31fc.png': ('milk', 'food', 'mj'),
        'ars_ants_insects_an_illustration_for_a_book_white_background_co_7e07bf75-b5d7-49ad-abe9-98e820326b0a.png': ('ant', 'animals', 'mj'),
        'ars_green_apple_fruit_an_illustration_for_a_book_white_backgrou_b61d7974-1c01-407b-a905-9e4d4ccf60b9.png': ('apple', 'food', 'mj'),
        'ars_jelly_on_a_plate__an_illustration_for_a_book_white_backgrou_516dbfb6-ebf0-4bb7-944b-1e5b3f07e6a9.png': ('jelly', 'food', 'mj'),
        'ars_one_banana_fruit_an_illustration_for_a_book_white_backgroun_46db5c36-adf5-4a24-b652-c079b3b98f4d.png': ('banana', 'food', 'mj'),
        'ars_diplodocus_dinosaur_an_illustration_for_a_book_white_backgr_d3c8d826-b5ab-45ad-b383-29d971757709.png': ('dinosaur', 'animals', 'mj'),
        'ars_boiled_egg_an_illustration_for_a_book_white_background_colo_9f9bcfea-5ef6-4cf7-9766-1eb2ef4b4c64.png': ('egg', 'food', 'mj'),
        'ars_black_horse_galloping_animals_an_illustration_for_a_book_wh_e171c624-4c8a-4b06-aeb5-d0d8d828f7a6.png': ('horse', 'animals', 'mj'),
        'ars_icecream_food_an_illustration_for_a_book_white_background_c_0ca8eb1e-68bf-4e42-94b6-d59fa9e4f088.png': ('ice_cream', 'food', 'mj'),
        'ars_glass_of_juice__an_illustration_for_a_book_white_background_ae85510f-fae8-461d-9e17-4f7f073cac1c.png': ('juice', 'food', 'mj'),
        'ars_boiled_edd_an_illustration_for_a_book_white_background_colo_6744ec9d-06b3-49ef-9043-aa67fb0a0038.png': ('egg', 'food', 'mj'),
        'ars_sugar_cube_food_an_illustration_for_a_book_white_background_294144e6-3417-45e1-8615-96e66ce3e796.png': ('sugar', 'food', 'mj'),
        'ars_subway_sandwich__an_illustration_for_a_book_white_backgroun_3de802f4-fb9d-48f6-9c90-fe6bc4bc2ed1.png': ('sandwich', 'food', 'mj'),
        'ars_white_pigeon_birds_an_illustration_for_a_book_white_backgro_b50a4d10-e971-4c0c-bfc0-a4f2695dbbc0.png': ('pigeon', 'animals', 'mj'),
        'ars_glass_of_water_an_illustration_for_a_book_white_background__873adf21-01d4-4cd6-86b7-0a08925b8120.png': ('water', 'food', 'mj'),
        'ars_Jello_dessert_on_a_plate__an_illustration_for_a_book_white__75ffaefd-ba44-405c-b58e-1872579d2e18.png': ('jelly', 'food', 'mj'),
        'ars_magpie_birds_an_illustration_for_a_book_white_background_co_dbba40d1-1ad7-495a-9477-2b822b33dbc6.png': ('magpie', 'animals', 'mj'),
        'ars_jelly_with_strawberries_food__an_illustration_for_a_book_wh_497e151f-c135-4581-b55d-ec9f0ce9d937.png': ('jelly', 'food', 'mj'),
        'ars_mug_of_coffee__an_illustration_for_a_book_white_background__d338b656-93ae-4ef3-a437-7da43d9246fc.png': ('coffee', 'food', 'mj'),
        'ars_baked_salmon_food_an_illustration_for_a_book_white_backgrou_e6e5c67f-f6e4-43bc-8323-eec6736159da.png': ('fish', 'food', 'mj'),
        'ars_fries_food_an_illustration_for_a_book_white_background_colo_cd5afd0a-4586-40a9-8bc8-749a5503c3dd.png': ('fries', 'food', 'mj'),
        'ars_chocolate_bar_food_an_illustration_for_a_book_white_backgro_8bb8ab03-27ea-4bae-acb4-6ffa02f7ac33.png': ('chocolate', 'food', 'mj'),
        'ars_Christmas_candy_an_illustration_for_a_book_white_background_7ce87b07-cd54-406e-9231-9a8f2001c457.png': ('candy', 'food', 'mj'),
        'ars_beef_steak_food_an_illustration_for_a_book_white_background_fccb6f22-e602-45db-919a-67f78a8a1813.png': ('steak', 'food', 'mj'),
        'ars_caramel_candy_on_a_plate_an_illustration_for_a_book_white_b_b866fed6-1b15-449e-8dcc-97075f2e689e.png': ('candy', 'food', 'mj'),
        'ars_one_cane_candy_on_a_plate_an_illustration_for_a_book_white__972e8a1c-7888-4716-9e63-88adcc39fc6e.png': ('candy', 'food', 'mj'),
        'ars_piece_of_sugar_an_illustration_for_a_book_white_background__75003aab-6344-4c6a-8c67-045593f35e2b.png': ('sugar', 'food', 'mj'),
        'ars_single_Christmas_cane_candy_an_illustration_for_a_book_whit_7269044b-2da8-47a9-8750-7397d9a9705c.png': ('candy', 'food', 'mj'),
        'ars_fried_egg_an_illustration_for_a_book_white_background_color_d8c6b1de-d166-42d1-bfb5-d2102744c896.png': ('egg', 'food', 'mj'),
        'ars_golden_fish_animals_an_illustration_for_a_book_white_backgr_078861d4-8196-4079-87e7-d204ef4d6a27.png': ('fish', 'animals', 'mj'),
        'ars_pickled_cucumbers_food__an_illustration_for_a_book_white_ba_c1fc2631-2cde-4d7b-99d6-9af518548226.png': ('cucumber', 'food', 'mj'),
        'ars_cooked_chicken_meal_an_illustration_for_a_child_book_white__b5a3786f-e425-4456-a6a3-f630ef9f2cb3.png': ('chicken', 'food', 'mj'),
        'ars_spoon_of_sugar_an_illustration_for_a_book_white_background__1d182742-1be0-4a38-b9ab-d96dbc56cd1b.png': ('sugar', 'food', 'mj'),
        'ars_piece_of_butter_on_a_plate_an_illustration_for_a_book_white_3e37352a-a4bc-475c-b529-5159438c57c3.png': ('butter', 'food', 'mj'),
        'ars_baked_chicken_on_a_plate_an_illustration_for_a_child_book_w_58eac72f-0c31-4636-a502-aa80e2d3f0c4.png': ('chicken', 'food', 'mj'),
        'ars_brown_sugar_piece__an_illustration_for_a_book_white_backgro_2413c77b-eb7d-47c3-bdfc-61c35c45397d.png': ('sugar', 'food', 'mj'),
        'ars_tuna_steak_food_an_illustration_for_a_book_white_background_aa8c4894-e14c-4bc5-a52a-9d65d888ca85.png': ('fish', 'food', 'mj'),
        'ars_sugar_sand_in_a_small_bowl__an_illustration_for_a_book_whit_cd1c4bbe-79d9-4341-a289-2f97e21fa0c9.png': ('sugar', 'food', 'mj'),
        'ars_cup_of_tea__an_illustration_for_a_book_white_background_col_1e762bde-6ddc-4338-9328-29747fceb5e4.png': ('tea', 'food', 'mj'),
        'ars_blueberry_berries_on_a_plate_an_illustration_for_a_book_whi_1bffe1e1-6072-479c-aad5-c4a9aae39213.png': ('blueberry', 'food', 'mj'),
        'ars_two_cherries_on_a_plate_an_illustration_for_a_book_white_ba_ed93d41f-b3cd-423a-9ffa-71a6a6d80454.png': ('cherry', 'food', 'mj'),
    }
    with open('rename.log', 'w') as flog:
        for f in os.listdir(dir):
            if os.path.isdir(f):
                continue
            if f in exemptions:
                word, label, src_suffix = exemptions[f]
            elif m := re.fullmatch(r'ars_(.+?)_+([^_]*)_*an_illustration.*([a-z0-9\-]{36})\.png', f):
                word, label, uuid = m.groups()
            else:
                print(f'❌ {f}')
                continue
            if word not in all_words:
                print(f'❌ {f} (unknown word: {word} {label} {uuid})')
                continue
            word_counters[word] += 1
            word_dir = os.path.join(dir, word)
            src = os.path.join(dir, f)
            dst = os.path.join(word_dir, f'{word}__{label}__mj{word_counters[word]}.png')
            flog.write(f'"{src}" "{dst}"\n')
            os.makedirs(word_dir, exist_ok=True)
            shutil.move(src, dst)
            print(f'✅ {f} {word} {label} {uuid} {word_counters[word]}')

@cli.command()
@click.option('--dir', default='public/pictures')
def cut_squares(dir):
    """Split all pictures into quarters"""
    from PIL import Image

    for f in glob.glob(f'{dir}/**/*_mj?.png', recursive=True):
        if os.path.isdir(f):
            continue
        print(f'Processing {f}..', end='')
        fdir, fname = os.path.split(f)
        fname, ext = os.path.splitext(fname)
        img = Image.open(f)
        width, height = img.size
        assert width == height
        assert width % 2 == 0

        for i in range(4):
            x = (i % 2) * width // 2
            y = (i // 2) * height // 2
            img.crop(
                (x, y,
                 x + width // 2, y + height // 2)
            ).save(f'{fdir}/{fname}_{i}{ext}')
        os.remove(f)
        print('✅')


@cli.command()
@click.option('--dir', default='public/pictures')
def fill_pictures(dir):
    """Fill pictures column in spreadsheet"""

    all_words = defaultdict(list)
    for f in glob.glob(f'{dir}/**/*_?.png', recursive=True):
        if os.path.isdir(f):
            continue
        fdir, fname = os.path.split(f)
        word = fdir.rsplit('/', 1)[-1]
        all_words[word].append(fname)
    all_categories = list_existing_categories()
    for category, ws in all_categories.items():
        for i, rec in enumerate(ws.get_all_records()):
            word = rec['word']
            if word not in all_words:
                print(f'❌ {word} {category}')
                continue
            ws.update_cell(i + 2, 4, ';'.join(all_words[word]))
            print(f'✅ updated {category}/{word} (row {i + 1})')



if __name__ == '__main__':
    cli()
