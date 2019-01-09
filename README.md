Explorations of book cover analysis, e.g. detecting when a book has a useful cover image.

## cover-analyzer.py

Takes a list of Internet Archive (Archive.org) item identifiers via stdin, outputs an HTML page containing a table
that shows cover images and calculated "usefulness". Some books have colorful covers; others were scanned with
just their bare cloth covers. A cover is determined to be "not useful" if it shows too little color variation
in its main section.

### Requirements
- Python 3
- ImageMagick
- wand (`pip install wand`)

### Example
```
  cat cover_sources/y2k-useful-covers-100.txt | python cover-analyzer.py > output/results-y2k-useful-covers-100.html
```

### Details

Images undergo the following process:
1) Chop off the top, bottom, and sides, because that's where library stickers usually go.
2) Shrink the remaining image to 16 by 16 pixels, to average out textural differences.
3) Take a standard deviation of the red, green, and blue channels, across all pixels.
3) If *all* of the standard deviations are below a threshold value, then designate it as a not useful cloth cover.

The `cover_sources` directory contains files of sample image identifiers:
- `not-useful-covers.txt`: Books from 1923 with mostly useless covers
- `useful-covers.txt`: Books from 1923 with a mix of useful and useless covers
- `y2k-useful-covers.txt`: Modern books with mostly useful covers

The files containing "100" in their filenames are the first 100 identifiers of the corresponding source files.
The results of processing these files are in the `output` directory.

The `sample_images` directory contains a few sample book cover images.

## Contact

Brenton Cheng (brenton at archive dot org)
