# Basic usage

You can perform annotations directly by calling `annotaty.py`:

`python annotate.py <input file> <output file>`

This script expects input data to be in a tab-separated format(verse id, verse text), one verse per line. The script performs preprocessing (lowercasing, removal of diacritics, and syllabification) on each verse. On the basis of the number of syllables found in each verse, dedicated finite-state machines then handle the hexameter annotation.

# Classes

You can also write your own annotation script using the following classes.

## Preprocessing package

### Selector class

This is mainly custom code that I used for randomly selecting a subset of verses from the corpus. Unlikely to be of interest for you.

### Preprocessor class

#### Method normalise

This method removes diacritics, accents, and lowercases the whole verse.

#### Syllabification
I have experimented with various approaches to syllabification. For example, the method `simple_syllabify` uses James Tauber's library. The method `papakitsos_syllabify`worked best for me and is also used by `annotate.py`.

The method `count_syllables` returns the syllable count.