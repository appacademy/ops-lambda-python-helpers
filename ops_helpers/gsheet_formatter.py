from collections import OrderedDict, namedtuple
from typing import Dict, NamedTuple
import pandas as pd


def get_values_from_sheets(service, spreadsheet_id: str, range_name: str):
    "Requires a validated service resource"
    result = (
        service.spreadsheets().values()
        .get(spreadsheetId=spreadsheet_id, range=range_name)
        .execute()
    )
    values = result.get('values', [])
    df = pd.DataFrame(values)
    df.columns = df.iloc[0]
    df = df.reindex(df.index.drop(0))
    return df


# [START read functions]
def get_spreadsheet_info(service, spreadsheet_id: str) -> dict:
    return service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()


def get_sheet_info_by_title(spreadsheet_id: str) -> Dict[str, int]:
    sheets = get_spreadsheet_info(spreadsheet_id)
    title_to_id_map = {}
    for item in sheets['sheets']:
        sheet_title = item['properties']['title']
        title_to_id_map[sheet_title] = item['properties']['sheetId']
    return title_to_id_map


def get_sheet_info_by_id(spreadsheet_id: str) -> Dict[int, NamedTuple]:
    sheets = get_spreadsheet_info(spreadsheet_id)
    sheet_dims = OrderedDict()
    Info = namedtuple('Info', ['n_rows', 'n_columns', 'title'])
    for item in sheets['sheets']:
        sheet_id = item['properties']['sheetId']
        n_rows = item['properties']['gridProperties']['rowCount']
        n_columns = item['properties']['gridProperties']['columnCount']
        sheet_title = item['properties']['title']
        sheet_dims[sheet_id] = Info(n_rows, n_columns, sheet_title)
    return sheet_dims


def get_conditional_format_rule_count(spreadsheet_id: str) -> Dict[int, int]:
    """
    Count the number of conditional formatting rules currently in each sheet
    Returns:
       {sheet_id: count_of_preexisting_conditional_format_rules}
    """
    sheets = get_spreadsheet_info(spreadsheet_id)
    rule_count = OrderedDict()
    for item in sheets['sheets']:
        sheet_id = item['properties']['sheetId']
        n_conditional_format_rules = len(item.get('conditionalFormats', []))
        rule_count[sheet_id] = n_conditional_format_rules
    return rule_count
# [END read functions]


# [START reset formatting rules]
def reset_basic_formatting(sheet_id: int) -> dict:
    request = {
        'repeatCell': {
            'range': {
                'sheetId': sheet_id
            },
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': {
                        'red': 1.0,
                        'green': 1.0,
                        'blue': 1.0
                    },
                    'horizontalAlignment': 'LEFT',
                    'textFormat': {
                        'foregroundColor': {
                            'red': 0.0,
                            'green': 0.0,
                            'blue': 0.0
                        },
                        'fontSize': 10,
                        'bold': False
                        }
                }
            },
            'fields': (
                'userEnteredFormat'
                '(backgroundColor, textFormat, horizontalAlignment)'
                )
            }
    }
    return request


def reset_conditional_formatting(sheet_id: int, current_rules: dict={}):
    requests = []
    if current_rules:
        rule_count = current_rules[sheet_id]
        for rule_num in reversed(range(rule_count)):
            request = {
                'deleteConditionalFormatRule': {
                    'sheetId': sheet_id,
                    'index': rule_num
                }
            }
            requests.append(request)
    else:
        requests = {
            'deleteConditionalFormatRule': {
                'sheetId': sheet_id,
                'index': 0
            }
        }
    return requests
# [END reset formatting rules]


# [START new formatting rules]
def create_type_casting_rule(
    sheet_id: int, column_start: int, column_end: int, new_type: str
) -> dict:

    cast_to_numeric = {
        'type': 'NUMBER',
        'pattern': '0'
    }

    cast_to_percent = {
        'type': 'PERCENT',
        'pattern': '0%'
    }

    cast_to_date = {
        'type': 'DATE',
        'pattern': 'mm/dd/yyyy'
    }

    TYPE_MAP = {
        'numeric': cast_to_numeric,
        'percentage': cast_to_percent,
        'date': cast_to_date
    }

    request = {
        'repeatCell': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': 1,
                'startColumnIndex': column_start,
                'endColumnIndex': column_end,
            },
            'cell': {
                'userEnteredFormat': {
                    'numberFormat': TYPE_MAP[new_type]
                }
            },
            'fields': 'userEnteredFormat.numberFormat'
        }
    }
    return request


def create_frozen_area_rule(sheet_id: int, row_count: int, column_count: int) -> Dict:

    request = {
        'updateSheetProperties': {
            'properties': {
                'sheetId': sheet_id,
                'gridProperties': {
                    'frozenRowCount': row_count,
                    'frozenColumnCount': column_count
                }
            },
            'fields': 'gridProperties.frozenRowCount, gridProperties.frozenColumnCount'
        }
    }
    return request


def create_header_row_rule(sheet_id: int) -> Dict:

    request = {
        'repeatCell': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': 0,
                'endRowIndex': 1
            },
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': {
                        'red': 0.0,
                        'green': 0.0,
                        'blue': 0.0
                    },
                    'horizontalAlignment': 'LEFT',
                    'textFormat': {
                        'foregroundColor': {
                            'red': 1.0,
                            'green': 1.0,
                            'blue': 1.0
                        },
                        'fontSize': 8,
                        'bold': True
                    }
                }
            },
            'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
        }
    }
    return request


def create_hidden_column_rule(sheet_id: int, column_start: int, column_end: int) -> Dict:

    request = {
        'updateDimensionProperties': {
            'range': {
                'sheetId': sheet_id,
                'dimension': 'COLUMNS',
                'startIndex': column_start,
                'endIndex': column_end
            },
            'properties': {
                'hiddenByUser': True,
            },
            'fields': 'hiddenByUser'
        }
    }
    return request


def create_conditional_format_rule(
    sheet_id: int, column_start: int, column_end: int,
    rule: Dict, insert_position: int=0
) -> Dict:

    request = {
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{
                    'sheetId': sheet_id,
                    'startRowIndex': 1,
                    'startColumnIndex': column_start,
                    'endColumnIndex': column_end
                }],
                **rule
            },
            'index': insert_position
        }
    }
    return request
# [END new formatting rules]


# [START apply formatting rules]
def format_cells(service, spreadsheet_id: str, rules: list) -> None:
    (
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body={'requests': rules})
        .execute()
    )
# [END apply formatting rules]


# [START sheet operations]
def add_sheet(service, spreadsheet_id: str, sheet_name: str, color_labels: dict={}) -> None:
    """
    Add a new sheet/tab to a spreadsheet
    Args:
        spreadsheet_id: unique id, as visible in URL (spreadsheets/d/[id]/edit)
        sheet_name: new sheet name, to become visible on new tab
        color_labels (optional): rgb settings (0 to 1) for new tab color
            Keys:
                'red', 'blue', 'green'
    """
    if not color_labels:
        color_labels = {
            'red': 0,
            'green': 0,
            'blue': 0
        }

    body = {
        'requests': [{
            'addSheet': {
                'properties': {
                    'title': sheet_name,
                    'tabColor': color_labels
                }
            }
        }]
    }
    (
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body)
        .execute()
    )


def delete_rows(service, spreadsheet_id: int, sheet_id: int, row_start: int) -> None:
    body = {
        'requests': [{
            'deleteDimension': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'ROWS',
                    'startIndex': row_start,
                }
            }
        }]
    }
    (
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body)
        .execute()
    )


def delete_columns(service, spreadsheet_id: int, sheet_id: int, column_start: int) -> None:
    """
    Remove a specified row and all subsequent rows from an individual sheet
    Args:
        spreadsheet_id: unique id, as visible in URL (spreadsheets/d/[id]/edit)
        sheet_id: unique id, as visible in URL (...#gid=[id])
        column_start: 0-based index of first row to delete
    """
    body = {
        'requests': [{
            'deleteDimension': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': column_start,
                }
            }
        }]
    }
    (
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body)
        .execute()
    )


def delete_excess_cells(spreadsheet_id: int, sheet_id: int) -> None:
    """
    Inspect contents of a sheet, delete empty rows and columns
    Args:
        spreadsheet_id: unique id, as visible in URL (spreadsheets/d/[id]/edit)
        sheet_id: unique id, as visible in URL (...#gid=[id])
    """
    info_by_id = get_sheet_info_by_id(spreadsheet_id)[sheet_id]
    range_name = info_by_id.title
    df = get_values_from_sheets(spreadsheet_id, range_name)
    rows_in_df, cols_in_df = df.shape
    # Adjust for header row
    rows_in_df += 1
    if info_by_id.n_rows > rows_in_df:
        print(f'{info_by_id.n_rows} is greater than {rows_in_df}, deleting rows')
        delete_rows(spreadsheet_id, sheet_id, rows_in_df)

    if info_by_id.n_columns > cols_in_df:
        print(f'{info_by_id.n_columns} is greater than {cols_in_df}, deleting columns')
        delete_columns(spreadsheet_id, sheet_id, cols_in_df)
# [END sheet operations]
