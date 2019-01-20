# -*- coding: utf-8 -*-

"""Helper script to query parameters."""

import json
import os
from collections import OrderedDict
from typing import Iterable, List, Tuple

import click

from pykeen.constants import (
    CONFIG_FILE_ERROR_MSG, CONFIG_FILE_PROMPT_MSG, CPU, GPU, HPO_MODE, ID_TO_KG_MODEL_MAPPING,
    ID_TO_OPTIMIZER_MAPPING, IMPORTERS, KG_MODEL_TO_ID_MAPPING, OPTIMIZER_TO_ID_MAPPING, PYKEEN, TRAINING_MODE,
)


def _is_correct_format(path: str):
    return (
            any(
                path.startswith(prefix)
                for prefix in IMPORTERS
            )
            or path.endswith('.tsv')
            or path.endswith('.nt')
    )


def get_input_path(prompt_msg, error_msg, is_dataset=False):
    while True:
        user_input = click.prompt(prompt_msg).strip('"').strip("'")

        if not os.path.exists(os.path.dirname(user_input)):
            click.echo(error_msg)
            continue
        if is_dataset:
            if not _is_correct_format(path=user_input):
                click.echo()
                click.echo('Invalid data source, following data sources are supported:\n'
                           'A string path to a .tsv file containing 3 columns corresponding to subject, predicate, and object.\n'
                           'A string path to a .nt RDF file serialized in N-Triples format.\n'
                           'A string NDEx network UUID prefixed by "ndex:" like in ndex:f93f402c-86d4-11e7-a10d-0ac135e8bacf')
                click.echo()
                continue

        return user_input


def select_keen_execution_mode(lib_name=PYKEEN):
    r = click.confirm(
        f'Do you have hyper-parameters? If not, {lib_name} will be configured for hyper-parameter search.',
        default=False,
    )
    return TRAINING_MODE if r else HPO_MODE


def select_embedding_model():
    click.echo('Please select the embedding model you want to train:')
    number_width = 1 + round(len(KG_MODEL_TO_ID_MAPPING) / 10)
    for model, model_id in KG_MODEL_TO_ID_MAPPING.items():
        click.echo(f'{model_id: >{number_width}}: {model}')

    ids = list(KG_MODEL_TO_ID_MAPPING.values())
    available_models = list(KG_MODEL_TO_ID_MAPPING.keys())

    while True:
        user_input = click.prompt('> Please select one of the options')

        if user_input in ids:
            return ID_TO_KG_MODEL_MAPPING[user_input]
        click.echo(
            f"Invalid input, please type in a number between {available_models[0]} and {ids[0]} indicating the "
            f"model id.\n For example, type {ids[0]} to select the model {available_models[0]} and press enter."
        )


def select_integer_value(print_msg, prompt_msg, error_msg):
    click.echo(print_msg)
    return click.prompt(prompt_msg, type=int)


def select_float_value(print_msg, prompt_msg, error_msg):
    click.echo(print_msg)
    return click.prompt(prompt_msg, type=float)


def select_zero_one_float_value(print_msg, prompt_msg, error_msg):
    click.echo(print_msg)

    while True:
        float_value = click.prompt(prompt_msg, type=float)
        try:
            if not (0 <= float_value <= 1):
                continue
            return float_value
        except ValueError:
            click.echo(error_msg)


def ask_for_evaluation():
    return click.confirm('Do you want to evaluate your model?')


def ask_for_test_set():
    return click.confirm('Do you provide a test set yourself?')


def select_ratio_for_test_set():
    while True:
        user_input = click.prompt('> Please select the ratio', type=float)

        try:
            ratio = float(user_input)
            if 0. < ratio < 1.:
                return ratio
        except ValueError:
            pass

        click.echo('Invalid input, the ratio should be 0.< ratio < 1. (e.g. 0.2).\n'
                   'Please try again.')


def select_preferred_device():
    click.secho(click.style("Current Step: Please specify the preferred device (GPU or CPU).", fg='blue'))

    while True:
        user_input = click.prompt('> Please type \'GPU\' or \'CPU\'').lower()
        if user_input == GPU or user_input == CPU:
            return user_input
        else:
            click.echo('Invalid input, please type in \'GPU\' or \'CPU\' and press enter.')


def ask_for_filtering_of_negatives():
    return click.confirm('Do you want to filter out negative triples during evaluation of your model?')


def load_config_file():
    path_to_config_file = get_input_path(prompt_msg=CONFIG_FILE_PROMPT_MSG, error_msg=CONFIG_FILE_ERROR_MSG)
    while True:
        with open(path_to_config_file, 'rb') as f:
            try:
                config = json.load(f)
                assert type(config) == dict or type(config) == OrderedDict
                return config
            except:
                click.echo('Invalid file, the configuration must be a JSON file.\n'
                           'Please try again.')
                path_to_config_file = get_input_path(prompt_msg=CONFIG_FILE_PROMPT_MSG, error_msg=CONFIG_FILE_ERROR_MSG)


def ask_for_existing_config_file():
    click.confirm('Do you provide an existing configuration file?')


def query_output_directory():
    click.echo('Please provide the path to your output directory.\n')
    click.echo()

    while True:
        user_input = click.prompt('> Path to output directory:')
        if os.path.exists(os.path.dirname(user_input)):
            return user_input
        else:
            click.echo('Invalid input, please make sure that the path to the directory exists.\n'
                       'Please try again.')


def query_height_and_width_for_conv_e(embedding_dim):
    click.echo("Note: Height and width must be positive positive integers.\n"
               "Besides, height * width must equal to  embedding dimension \'%d\'" % embedding_dim)
    click.echo()

    while True:
        height = click.prompt('> Height:', type=int)
        width = click.prompt('> Width:', type=int)
        if height * width == embedding_dim:
            return height, width

        click.echo("Invalid input, height * width are not equal to \'%d\' (your specified embedding dimension).\n"
                   "Please try again, and fulfill the constraint)" % embedding_dim)


def query_kernel_param(depending_param, print_msg, prompt_msg, error_msg):
    click.echo(print_msg % depending_param)

    while True:
        kernel_param = click.prompt(prompt_msg, type=int)
        if kernel_param <= depending_param:
            return kernel_param
        click.echo(error_msg % depending_param)


def select_float_values(print_msg, prompt_msg, error_msg):
    click.echo(print_msg)
    float_values = []
    is_valid_input = False

    while not is_valid_input:
        user_input = click.prompt(prompt_msg)
        user_input = user_input.split(',')
        is_valid_input = True

        for float_value in user_input:
            try:
                float_value = float(float_value)
                float_values.append(float_value)
            except ValueError:
                click.echo(error_msg)
                is_valid_input = False
                break

    return float_values


def select_zero_one_range_float_values(print_msg, prompt_msg, error_msg):
    click.echo(print_msg)
    float_values = []
    is_valid_input = False

    while not is_valid_input:
        user_input = click.prompt(prompt_msg)
        user_input = user_input.split(',')
        is_valid_input = True

        for float_value in user_input:
            try:
                float_value = float(float_value)
            except ValueError:
                click.echo(error_msg)
                is_valid_input = False
                break

            if 0. <= float_value <= 1.:
                click.echo("hey")
                float_values.append(float_value)
            else:
                click.echo(error_msg)
                is_valid_input = False
                break

    return float_values


def select_positive_integer_values(print_msg, prompt_msg, error_msg):
    click.echo(print_msg)
    integers = []
    is_valid_input = False

    while not is_valid_input:
        user_input = click.prompt(prompt_msg)
        user_input = user_input.split(',')
        is_valid_input = True

        for integer in user_input:
            try:
                integer = int(integer)
            except ValueError:
                click.echo(error_msg)
                is_valid_input = False
                break
            else:
                integers.append(integer)

    return integers


def select_optimizer():
    click.echo('Please select the optimizer you want to train your model with:')
    for optimizer, id in OPTIMIZER_TO_ID_MAPPING.items():
        click.echo("%s: %s" % (optimizer, id))

    ids = list(OPTIMIZER_TO_ID_MAPPING.values())
    available_optimizers = list(OPTIMIZER_TO_ID_MAPPING.keys())

    while True:
        user_input = click.prompt('> Please select one of the options')

        if user_input not in ids:
            click.echo(
                "Invalid input, please type in a number between %s and %s indicating the optimizer id.\n"
                "For example type %s to select the model %s and press enter" % (
                    available_optimizers[0], ids[0], ids[0], available_optimizers[0]))
            click.echo()
        else:
            return ID_TO_OPTIMIZER_MAPPING[user_input]


def select_heights_and_widths(embedding_dimensions: Iterable[str]) -> Tuple[List[int], List[int]]:
    heights = []
    widths = []

    for embedding_dim in embedding_dimensions:
        while True:
            click.echo(f'Specify the height for specified embedding dimension {embedding_dim}.')
            height = click.prompt('> Height:', type=int)

            click.echo(f'Specify the width for specified embedding dimension {embedding_dim}.')
            width = click.prompt('> Width:', type=int)

            if int(height) * int(width) == embedding_dim:
                heights.append(height)
                widths.append(width)
                break

            click.secho(
                f"Invalid input, height and width must be positive integers, and height * width must equal the "
                f" specified embedding dimension of {embedding_dim}.",
                fg='red',
            )
        click.echo()

    return heights, widths


def select_kernel_sizes(depending_params, print_msg, prompt_msg, error_msg) -> List[int]:
    kernel_params = []
    click.echo(print_msg)

    for dep_param in depending_params:
        while True:
            kernel_param = click.prompt(prompt_msg % dep_param, type=int)

            if kernel_param <= dep_param:
                kernel_params.append(int(kernel_param))
                break

            click.secho(error_msg % dep_param, fg='red')
        click.echo()

    return kernel_params
