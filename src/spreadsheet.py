import os

import gspread

gc = gspread.service_account('src/service_account.json')
sheet_id = os.environ['SHEET_ID']
sheet = gc.open_by_key(sheet_id)
default_columns = [
    'word',
    'source_category',
    'label',  # text representation of the word, for example '10' for 'ten', or emoji '🤣' for 'joy'
    'pictures',  # list filenames of pictures separated by semicolon
    'audio',  # list of audio files separated by semicolon
    'weight',  # float, default 1. relative weight of the word in the category. Multiplied by category weight later.
    'suppress_pairs_with',  # list of words separated by semicolon. These words will not be paired with this word. Useful for synonyms.
    # can also ban combinations with specific "category/word/picture"
    # just in case specific picture contains a word that should not be paired with this word.
]


def list_existing_categories():
    return {
        ws.title: ws
        for ws in sheet.worksheets()
        if ws.title not in ['TEMPLATE', 'META']
    }


def get_category_worksheet(category):
    return sheet.worksheet(category)


def get_category_words(category):
    ws = get_category_worksheet(category)
    return [rec['word'] for rec in ws.get_all_records()]


"""
Sharing a Spreadsheet

sh.share('otto@example.com', perm_type='user', role='writer')
Selecting a Worksheet

# Select worksheet by index. Worksheet indexes start from zero
worksheet = sh.get_worksheet(0)

# By title
worksheet = sh.worksheet("January")

# Most common case: Sheet1
worksheet = sh.sheet1

# Get a list of all worksheets
worksheet_list = sh.worksheets()
Creating a Worksheet

worksheet = sh.add_worksheet(title="A worksheet", rows="100", cols="20")
Deleting a Worksheet

sh.del_worksheet(worksheet)
Getting a Cell Value

# With label
val = worksheet.get('B1').first()

# With coords
val = worksheet.cell(1, 2).value
Getting All Values From a Row or a Column

# Get all values from the first row
values_list = worksheet.row_values(1)

# Get all values from the first column
values_list = worksheet.col_values(1)
Getting All Values From a Worksheet as a List of Lists

list_of_lists = worksheet.get_values()
Finding a Cell

# Find a cell with exact string value
cell = worksheet.find("Dough")

print("Found something at R%sC%s" % (cell.row, cell.col))

# Find a cell matching a regular expression
amount_re = re.compile(r'(Big|Enormous) dough')
cell = worksheet.find(amount_re)
Finding All Matched Cells

# Find all cells with string value
cell_list = worksheet.findall("Rug store")

# Find all cells with regexp
criteria_re = re.compile(r'(Small|Room-tiering) rug')
cell_list = worksheet.findall(criteria_re)
Updating Cells

# Update a single cell
worksheet.update('B1', 'Bingo!')

# Update a range
worksheet.update('A1:B2', [[1, 2], [3, 4]])

# Update multiple ranges at once
worksheet.batch_update([{
    'range': 'A1:B2',
    'values': [['A1', 'B1'], ['A2', 'B2']],
}, {
    'range': 'J42:K43',
    'values': [[1, 2], [3, 4]],
}])
"""

# https://github.com/burnash/gspread

# we store word lists in worksheets
