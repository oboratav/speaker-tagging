import sys

import click

from utilities import read_seg_file, add_credits, annotate_line_list, flatten_line_list


@click.command()
@click.argument(
    "input_file",
    type=click.File("r"),
    default="-",
    required=False,
)
@click.argument(
    "output_file",
    type=click.File("w"),
    default="-",
    required=False,
)
def tag_red_hen_file(input_file, output_file):
    """
    Reads a Red Hen .seg file or from file-in (or stdin),
    and writes an annotated version to file-out (or stdout).
    """
    # Parse the input .seg file
    working_file = read_seg_file(input_file)
    # Add credits to the file
    working_file = add_credits(working_file)
    # Annotate the file
    working_file = flatten_line_list(annotate_line_list(working_file))
    # Write the annotated file to file-out
    output_file.write(working_file)


if __name__ == "__main__":
    tag_red_hen_file()

#
