import datetime
import re

import click

from lxml import etree, html

from settings import (
    LINE_FORMAT,
    CREDITS_DATETIME_FORMAT,
    CREDITS_SRC_PROGRAM,
    BODY_TAG,
    SUMMARY_TAG
)

# Matches lines that fit the pattern of [digits].[digits]|[digits].[digits]|CC[O, 0, or 1]|[anything]
cc_line_pattern = re.compile("^(\d*.\d*)\|(\d*.\d*)\|CC[O01]\|(.*)")
# Matches lines that fit the pattern of [digits].[digits]|[digits].[digits]|[anything]
timestamped_line_pattern = re.compile("^(\d*.\d*)\|(\d*.\d*)\|(.*)")

def read_seg_file(in_file: click.File) -> list:
    """
    Reads an annotated text file and returns a list of lines.
    The first element in each list is the raw string,
    the second is the list of tags in that string.
    """
    line_list = []

    # Reading the file/stream is handled by click.

    # For each line in the input file/stream,
    for line in in_file:
        # remove trailing newline character, if any,
        line = re.sub("\n$", "", line)
        # and append the processed line to the list of lines.
        line_list.append([line, line.split("|")])
    return line_list


def add_credits(line_list: list) -> list:
    """
    Adds credits section to the end of the header section,
    as per https://www.redhenlab.org/home/the-cognitive-core-research-topics-in-red-hen/red-hen-data-format
    """
    # TODO: Figure out why the ", FFS" bit is there
    template = "{tag_code}|{date_and_time}|Source_Program={source_program}|Source_Person=Ömer Boratav, FFS|Codebook={codebook}"

    for line, index in zip(line_list, range(len(line_list))):
        # Header sections always end with an LBT tag, as per https://www.redhenlab.org/home/the-cognitive-core-research-topics-in-red-hen/red-hen-data-format
        if line[1][0] == "LBT":
            # Insert credits section immediately after the LBT tag.
            dt = datetime.datetime.now().strftime(CREDITS_DATETIME_FORMAT)
            credits_line = template.format(
                tag_code=BODY_TAG,
                date_and_time=dt,
                source_program=CREDITS_SRC_PROGRAM,
                codebook=LINE_FORMAT.format(
                    # Generate a codebook using dummy parameters.
                    color="Color",
                    text="Text",
                ),
            )
            """
            TODO: Implement summary tags
            credits_summary = template.format(
                tag_code=SUMMARY_TAG,
                date_and_time=dt,
                source_program=CREDITS_SRC_PROGRAM,
                codebook="Colors/Tags/Lines",
            )
            line_list.insert(index + 1, [credits_summary, credits_summary.split("|")])
            """
            line_list.insert(index + 1, [credits_line, credits_line.split("|")])
            return line_list


def find_color_tags_in_line(line: list) -> list:
    """
    Given a CC line, looks for XML color tags.
    If color tags are present, returns a CTG_0 line.

    As seen in 2020-02-02_2100_ES_24h_Telediario_1a_Edición.txt,
    the color tags are preserved as XML tags in the form of <font color="[hex]">[text]</font>.

    Many channels separate a single line into multiple color tags, even though
    there is no change in color within that line. If 
    """
    # If the line matches the regex pattern for a CC line,
    if cc_line_pattern.fullmatch(line[0]) is not None:
        # parse xml tags if any, and get font tags, if any.
        font_tags = html.fragment_fromstring(line[1][3], create_parent="line").xpath("font")
        # If any font tags are present,
        if font_tags:
            # return a list of them with their colors and text.
            return [{"color": tag.attrib.get("color").lower(), "text": tag.text} for tag in font_tags if tag.attrib.get("color")]

    # If either of these conditions isn't satisfied, return None.
    return None

"""
if font_tags:
    return "{start}|{end}|{tag}|{content}".format(
        start=line[1][0],
        end=line[1][1],
        tag=TAG_CODE,
        content="|".join([
            LINE_FORMAT.format(
                color=tag.attrib.get("color").lower(),
                text=tag.text
            ) for tag in font_tags if tag.attrib.get("color")
        ])
    )
"""

def annotate_line_list(lines: list, add_summary: bool = False) -> list:
    """
    Runs find_color_tags_in_line over a number of lines and annotates the line list.

    Places a CTG_0 tag immediately before each line containing color tags,
    and, if add_summary is set to True, places one CTG_1 tag just below the 
    header that summarizes overall color/tag content in the file.
    """
    # Set counters to zero to begin with.
    number_of_lines = 0
    number_of_tags = 0
    number_of_colors = 0
    colors = set()
    lines_out = []
    # For each line provided,
    for line, index in zip(lines, range(len(lines))):
        # look for color tags.
        found = find_color_tags_in_line(line)
        # If any are there,
        if found is not None:
            # increment the line counter by one,
            number_of_lines += 1
            # increment the tags counter by the number of tags in this line,
            number_of_tags += len(found)
            # add the colors found to the set of colors,
            colors.update([ tag["color"] for tag in found ])
            # form a tag to insert right before the CC tag itself,
            ctg0_line = "{start}|{end}|{tag}|{content}".format(
                start=line[1][0],
                end=line[1][1],
                tag=BODY_TAG,
                content="|".join([
                    LINE_FORMAT.format(
                        color=tag.get("color").lower(),
                        text=tag.get("text"),
                    ) for tag in found if tag["color"]
                ])
            )
            # and insert the body tag right before the CC tag.
            lines_out.append([ctg0_line, ctg0_line.split("|")])
        # Finally, insert the CC tag itself.
        lines_out.append(line)
        # If a summary tag is requested in the header of the file,
        if add_summary:
            # TODO: Implement summary tags
            pass
    return lines_out

def flatten_line_list(lines: list) -> list:
    """
    Flattens the line list into a single string.
    """
    return "\n".join([line[0] for line in lines])
                

