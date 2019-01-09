# Takes a list of Archive identifiers via stdin, outputs an HTML page
# containing a table listing cover images and calculated "usefulness"

from wand.image import Image
from urllib.request import urlopen
import numpy
import sys

# Configurable parameters
grid_width = 16 # Width of grid to shrink to for color checking
grid_height = 16 # Height of grid to shrink to for color checking
side_length_fraction_to_keep = 0.6 # What fraction of each dimension to keep (rest is cropped)
human_scale_factor = 255 # Desired scale of RGB values, e.g. 0-255, for readability
threshold_deviation = 15.0 # Max standard deviation for indicating cloth cover

item_outputs = []
for line in sys.stdin:
    item_output = []
    sys.stderr.write('.')
    sys.stderr.flush()

    identifier = line.rstrip('\n')
    url = 'https://archive.org/services/img/{}'.format(identifier)
    item_output.append('<img src={} alt="">'.format(url))

    try:
        with urlopen(url) as response:
            with Image(file=response) as image:
                (image_width, image_height) = image.size

                # Use the center section to avoid barcodes etc. placed close to edges
                image.crop(
                    width=int(round(side_length_fraction_to_keep * image_width)),
                    height=int(round(side_length_fraction_to_keep * image_height)),
                    gravity='center'
                )

                # Switch to coarse grid, allowing ImageMagick to average pixels
                image.resize(grid_width, grid_height)

                # Gather all pixel color values
                reds = []
                greens = []
                blues = []
                for image_row in image:
                    for pixel in image_row:
                        reds.append(pixel.red * human_scale_factor)
                        greens.append(pixel.green * human_scale_factor)
                        blues.append(pixel.blue * human_scale_factor)

                # Call it not useful (i.e. cloth cover) if all channels show little variation
                deviations = (numpy.std(reds), numpy.std(greens), numpy.std(blues))
                if all([deviations[i] < threshold_deviation for i in [0, 1, 2]]):
                    item_output.append('<span class="not-useful">not useful</span>')
                else:
                    item_output.append('<span class="useful">USEFUL</span>')

                # Output identifier third in row (giving priority to cover image and status)
                item_output.append('<a href="https://archive.org/details/{0}">{0}</a>'.format(identifier))

                # Show standard deviation for each channel (for diagnostics)
                item_output.append('({:.2f}, {:.2f}, {:.2f})'.format(deviations[0], deviations[1], deviations[2]))

    except Exception as e:
        item_output.append('<span class="error">error reading</span>')
        item_output.append(identifier)
        item_output.append('') # Needed to keep number of output cells constant
        sys.stderr.write('\nERROR with image for {identifier}: {error}\n'.format(identifier=identifier, error=str(e)))

    item_outputs.append(item_output)

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
                <th>Std Deviation (R, G, B)</th>
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

sys.stderr.write('done.\n')
