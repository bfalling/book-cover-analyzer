# Takes a list of Archive identifiers via stdin, outputs an HTML page
# containing a table listing cover images and calculated "usefulness".
# Also writes a text file containing the identifiers of items with
# less useful covers and which should probably use their title page as
# the thumbnail.
#
# Requirements:
# - `pip install opencv-python`
#
# Thanks to Peter De Wachter for the algorithm!

# TODO: Examine the actual cover images, instead of the existing thumb
#       cuz the existing thumb could already be the title page.

import cv2
from urllib.request import urlopen
import numpy
import sys

# Configurable parameters
file_of_ids_to_use_title_page = 'title_page_ids.txt'

def log_now(text):
    sys.stderr.write(text)
    sys.stderr.flush()

def convert_to_cv_image(data):
    numpy_array = numpy.fromstring(data, numpy.uint8)
    return cv2.imdecode(numpy_array, cv2.IMREAD_UNCHANGED)

def is_useful_cover(image):
    # intended for thumbnail images, e.g. width = 180 pixels
    converted_image = cv2.Canny(image, 100, 200)
    edginess = numpy.mean(converted_image, axis=1)
    edge_level = numpy.std(edginess)
    return edge_level >= 13

log_now('Starting')

title_page_ids_file = open(file_of_ids_to_use_title_page, 'w')

item_outputs = []
for line in sys.stdin:
    item_output = []

    log_now('.')

    identifier = line.rstrip('\n')
    url = 'https://archive.org/services/img/{}'.format(identifier)
    item_output.append('<img src={} alt="">'.format(url))

    try:
        with urlopen(url) as response:

            # Handle placeholder images
            if response.geturl() == 'https://archive.org/images/notfound.png':
                item_output.append('<span class="not-useful">not useful</span>')
                item_output.append('<a href="https://archive.org/details/{0}">{0}</a>'.format(identifier))
                item_outputs.append(item_output)
                continue

            cv_image = convert_to_cv_image(response.read())
            if is_useful_cover(cv_image):
                item_output.append('<span class="useful">USEFUL</span>')
            else:
                item_output.append('<span class="not-useful">not useful</span>')
                title_page_ids_file.write(identifier + '\n')

            # Output identifier third in row (giving priority to cover image and status)
            item_output.append('<a href="https://archive.org/details/{0}">{0}</a>'.format(identifier))

    except Exception as e:
        item_output.append('<span class="error">error reading</span>')
        item_output.append('<a href="https://archive.org/details/{0}">{0}</a>'.format(identifier))
        log_now('\nERROR with image for {identifier}: {error}\n'.format(identifier=identifier, error=str(e)))

    item_outputs.append(item_output)

title_page_ids_file.close()

# Output HTML
print("""
<!DOCTYPE html>
<html>
    <head>
        <title>Cover Analyzer</title>
        <style>
            body { font-family: sans-serif; }
            th { text-align: left; }
            td { padding: 4px; }
            .useful { font-weight: bold; }
            .not-useful { color: gray }
            .error { color: red }
        </style>
    </head>
    <body>
        <table>
            <tr>
                <th>Cover Image</th>
                <th>Useful?</th>
                <th>Identifier</th>
            </tr>
""")

for item_output in item_outputs:
    print('<tr>')
    for value in item_output:
        print('<td>{}</td>'.format(value))
    print('</tr>')

print("""
        </table>
    </body>
</html>
""")

sys.stderr.write('done\n')
