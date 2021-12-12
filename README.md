
# Red Hen Teletext Color Annotator
[A Red Hen Lab project.](https://www.redhenlab.org/home/the-cognitive-core-research-topics-in-red-hen/the-barnyard/convert-teletext-colors-to-speaker-tags)

## Introduction
Some providers in certain countries use styling features available in DVB Teletext to color-code their closed captioning. These color codes can potentially be used to detect turn-taking between interlocutors.

This program takes a `.seg` file, reads color tags inside it (if any), and outputs an annotated version of the same file.

The tags it adds are in the form of:

    [start]|[end]|CTG_0|[hex]/[text]

| Field | Description |
|--|--|
| [start] | Starting timestamp of the annotation |
| [end] | Ending timestamp of the annotation |
| [hex] | Hex color of the tag |
| [text] | Contents of the tag |

For instance:

    20200202214233.960|20200202214234.760|CTG_0|#ffff00/y nuevas pistas.
    20200202214233.960|20200202214234.760|CC1|<font color="#ffff00">y nuevas pistas.</font>

The `hex/text` pairs may repeat if more than one color tag exists in a single CC line, with each pair being separated by `|` like so:

    20200202214242.840|20200202214245.360|CTG_0|#ffff00/en busca de respuestas|#ffff00/a las nuevas tendencias.
    20200202214242.840|20200202214245.360|CC1|<font color="#ffff00">en busca de respuestas</font> <font color="#ffff00">a las nuevas tendencias.</font>

## How to Install and Use
### via Docker
Installing and using the tool as a Docker container is by far the easiest way. Simply run:

    docker pull oboratav/speaker-tagging
And Docker will take care of the rest. To annotate a file, simply pipe it into the container, and capture its output:

    cat input_file.txt | docker run -i -a stdin -a stdout oboratav/speaker-tagging > output_file.txt

You can also use the `-v` flag to mount files from the local filesystem:

    docker run -i -v /some/input/file.seg:/usr/data/input_file.seg -a stdout oboratav/speaker-tagging > output_file.txt

### Directly
You can also skip Docker altogether and just clone this git repo, create a virtual environment, and install the requirements listed in `requirements.txt`

## Example Use Cases

- Find occurrences of two different colors in the same line:
    `CTG_0\|.*([a-f0-9]{6}).*\|(?!\1)(?:[a-f0-9]{6})`
