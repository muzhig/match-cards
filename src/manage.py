import glob
import json
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
@click.option('--dry-run', is_flag=True, default=False)
def sort_pictures(dir, dry_run):
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

        'ars_brush_with_black_paint_an_illustration_for_a_book_white_bac_63d37d5c-f8c9-44dc-865a-aa52765dac59.png': ('black', 'colors', 'mj'),
        'ars_brush_with_blue_paint_an_illustration_for_a_book_white_back_2e762666-4735-477f-85fe-bec5fd64c45e.png': ('blue', 'colors', 'mj'),
        'ars_brush_with_brown_paint_an_illustration_for_a_book_white_bac_4b312c16-a973-4ab1-97b8-01b059092af1.png': ('brown', 'colors', 'mj'),
        'ars_brush_with_gray_paint_an_illustration_for_a_book_white_back_f18aeea9-9d00-4ae1-b545-d1d0856f489d.png': ('gray', 'colors', 'mj'),
        'ars_brush_with_green_paint_an_illustration_for_a_book_white_bac_e88583cd-67be-4a00-90cc-e9addaad0c1a.png': ('green', 'colors', 'mj'),
        'ars_brush_with_orange_paint_an_illustration_for_a_book_white_ba_e5bd38bb-d22c-462a-915b-038f6d287d17.png': ('orange', 'colors', 'mj'),
        'ars_brush_with_pink_paint_an_illustration_for_a_book_white_back_ee7f3063-3523-4b29-ace4-ac0760cb0894.png': ('pink', 'colors', 'mj'),
        'ars_brush_with_purple_paint_an_illustration_for_a_book_white_ba_5d729d08-d59d-40a0-9b60-4e36ea1ebb44.png': ('purple', 'colors', 'mj'),
        'ars_brush_with_red_paint_an_illustration_for_a_book_white_backg_907ce82e-fde2-495e-b34c-92b59baa2f9a.png': ('red', 'colors', 'mj'),
        'ars_brush_with_white_paint_an_illustration_for_a_book_white_bac_13f7e614-f14b-4f66-a053-871b0a0e6a33.png': ('white', 'colors', 'mj'),
        'ars_brush_with_white_paint_an_illustration_for_a_book_white_bac_4096abbd-2807-4479-a5f0-0d81141fe723.png': ('white', 'colors', 'mj'),
        'ars_brush_with_white_paint_an_illustration_for_a_book_white_bac_e264ad44-e664-45bd-9267-80ea28ce440e.png': ('white', 'colors', 'mj'),
        'ars_brush_with_white_paint_an_illustration_for_a_book_white_bac_fe885a77-5a9d-46b2-b892-039bcc6839e8.png': ('white', 'colors', 'mj'),
        'ars_brush_with_yellow_paint_an_illustration_for_a_book_white_ba_d14133d0-ce60-49a3-988c-bfb0693e7576.png': ('yellow', 'colors', 'mj'),
        'ars_red_bucket_of_paint_an_illustration_for_a_book_white_backgr_31cf9928-3b8c-45af-aafc-7b9e66a3606c.png': ('red', 'colors', 'mj'),
        'ars_red_marker_an_illustration_for_a_book_white_background_colo_4d88b281-f04e-47ec-b8f7-ab6f7cd1588e.png': ('red', 'colors', 'mj'),

        'ars_thunderstorm_weather_nature_an_illustration_for_a_book_whit_4c46ddec-4262-41fb-96bf-bbf0ade3479c.png': ('storm', 'weather', 'mj'),
        'ars_birds_habitat_an_illustration_for_a_book_white_background_c_524a5301-013d-41d0-b22a-7f22a0d2663c.png': ('bird', 'animals', 'mj'),
        'ars_lake_without_island_an_illustration_for_a_book_white_backgr_91335892-1fed-4eac-ae16-1857f4998800.png': ('lake', 'nature', 'mj'),
        'ars_grass_hills_habitat_an_illustration_for_a_book_white_backgr_2bdf9c7c-a6b6-4235-924e-0f45e9891103.png': ('hill', 'nature', 'mj'),
        'ars_sand_desert_an_illustration_for_a_book_white_background_col_5445041b-3992-4608-a995-58ddc3056331.png': ('desert', 'nature', 'mj'),
        'ars_tv_in_a_living_room_an_illustration_for_a_book_white_backgr_f2e8e346-ad22-45a4-bec6-b0d2280ced39.png': ('tv', 'house', 'mj'),
        'ars_tv_in_a_living_room_an_illustration_for_a_book_white_backgr_43295b1a-8411-437a-b2ce-cf76abee4f35.png': ('tv', 'house', 'mj'),
        'ars_giraffes_in_the_savannah_an_illustration_for_a_book_white_b_114206e9-7af0-4348-9d9c-b3f5fd484179.png': ('giraffe', 'animals', 'mj'),
        'ars_north_forest_an_illustration_for_a_book_white_background_co_cac47bd5-fe49-4aee-b28c-956b44514fc7.png': ('forest', 'nature', 'mj'),
        'ars_island_in_ocean_landscape_an_illustration_for_a_book_white__b202a76a-64bb-4502-b2a7-287a98f94b04.png': ('island', 'nature', 'mj'),
        'ars_lightbulb_an_illustration_for_a_book_white_background_color_82ab0698-29ba-43ec-891f-202cc9f42bfd.png': ('lamp', 'house', 'mj'),
        'ars_tv_in_a_living_room_an_illustration_for_a_book_white_backgr_19b29c15-3f07-4230-b170-2b6631d9d121.png': ('tv', 'house', 'mj'),
        'ars_tropical_beach_nature_an_illustration_for_a_book_white_back_d7d9cd0b-6484-48a8-9f63-530dfa32084b.png': ('beach', 'nature', 'mj'),
        'ars_animals_of_antarctica_an_illustration_for_a_book_white_back_a3421cda-0b41-4f94-aa83-d7300428877d.png': ('penguin', 'animals', 'mj'),
        'ars_meadow_landscape_nature_an_illustration_for_a_book_white_ba_5cdab318-9c51-401c-89ce-b7ce8f9dca92.png': ('meadow', 'nature', 'mj'),
        'ars_sand_beach_an_illustration_for_a_book_white_background_colo_47daa6ad-0331-412a-9110-93e12f32317a.png': ('beach', 'nature', 'mj'),
        'ars_animals_in_habitat_an_illustration_for_a_book_white_backgro_d74d2b45-8af9-436d-8940-bab6292a2380.png': ('bird', 'animals', 'mj'),
        'ars_deers_on_a_grassfield_an_illustration_for_a_book_white_back_41a85196-4367-4757-9609-725dcfe2fecb.png': ('deer', 'animals', 'mj'),
        'ars_bears_on_a_river_an_illustration_for_a_book_white_backgroun_e9cf2b3d-da8e-4b9a-9069-be194e5b62f3.png': ('bear', 'animals', 'mj'),
        'ars_island_in_ocean_an_illustration_for_a_book_white_background_e8d8b3ea-0d19-4298-ba66-266500327afd.png': ('island', 'nature', 'mj'),
        'ars_mirror_hanging_on_a_wall_in_the_bathroom_an_illustration_fo_3327258b-10b0-4608-a2ac-124507103b06.png': ('mirror', 'house', 'mj'),
        'ars_tornado_weather_realistic_an_illustration_for_a_book_white__2d2f186b-cd4e-4ba4-b3ee-0ec8209c977f.png': ('tornado', 'nature', 'mj'),
        'ars_mirror_wall_fittings_an_illustration_for_a_book_white_backg_11c6968f-8e35-430b-86c6-744009628021.png': ('mirror', 'house', 'mj'),
        'ars_lamp_house_furniture_an_illustration_for_a_book_white_backg_c98de15c-671e-4174-841c-114c4d740eca.png': ('lamp', 'house', 'mj'),
    }
    with open('rename.log', 'a') as flog:
        for f in os.listdir(dir):
            if os.path.isdir(os.path.join(dir, f)):
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
            dst_fname = f'{word}__{label}__mj{word_counters[word]}.png'
            dst = os.path.join(word_dir, dst_fname)
            if os.path.exists(dst):
                print(f'❌ {f} {word}/{dst_fname} (already exists)')
                continue
            if not dry_run:
                flog.write(f'"{src}" "{dst}"\n')
                os.makedirs(word_dir, exist_ok=True)
                shutil.move(src, dst)
            print(f'✅ {f} {word} {label} {dst_fname}')

@cli.command()
@click.option('--dir', default='public/pictures')
def cut_squares(dir):
    """Clip pictures into 4 squares"""
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
@click.option('--category', default=None)
def fill_pictures(dir, category=None):
    """Fill pictures column in spreadsheet"""

    all_words = defaultdict(list)
    for f in glob.glob(f'{dir}/**/*_?.png', recursive=True):
        if os.path.isdir(f):
            continue
        fdir, fname = os.path.split(f)
        word = fdir.rsplit('/', 1)[-1]
        all_words[word].append(fname)
    all_categories = list_existing_categories()
    categories = all_categories.items() if category is None else [(category, all_categories[category])]
    for category, ws in categories:
        for i, rec in enumerate(ws.get_all_records()):
            word = rec['word']
            if word not in all_words:
                print(f'❌ {word} {category}')
                continue
            ws.update_cell(i + 2, 4, ';'.join(all_words[word]))
            print(f'✅ updated {category}/{word} (row {i + 1})')


@cli.command()
@click.option('--only-with-pictures/--all', default=True)
def words_json(only_with_pictures=True):
    res= []
    for category, ws in list_existing_categories().items():
        if category in ['TEMPLATE', 'META']:
            continue
        records = ws.get_all_records()
        for i, rec in enumerate(records):
            if only_with_pictures and not rec['pictures']:
                continue
            word = {
                "category": category,
                "words": [rec['word']],
                "pictures": rec['pictures'].split(';') if rec['pictures'] else [],
                "audio": rec['audio'].split(';') if rec['audio'] else [],
                "suppress_pairs_with": rec['suppress_pairs_with'].split(';') if rec['suppress_pairs_with'] else [],
                "weight": float(rec['weight']) if rec['weight'] else 1.0,
                **({"glyph": rec['label']} if rec['label'] else {}),
            }
            res.append(json.dumps(word))
    print("[\n  ", end="")
    print(",\n  ".join(res))
    print("]")

if __name__ == '__main__':
    cli()
