Naming Scheme
=====================

The constraints are:

* Naming should be stable: it should never change. This implies that enough room should be given to account for many years of future samples
* Name should be informative: one should get an idea of where the gene/SAG comes from from its name.
* Name should be concise: ideally, a gene name (which is the end product in a way) should be kept under 20 characters

Quick guide::

    sample well asbly reserved
    _____  ___  _     _
    O331AC_C09A_A002340
         –    –  –––––
     plate    run gene

Complete description
-------------------------

* *Sample*: 
    * Five characters, alphanumeric, letter in capitals
    * Should be as informative as possible (e.g. O331A for Ocean Drilling program exp. 331, sample A)
* *Plates*:
    * Start with sample ID
    * One extra character (A-Z) to indicate the nth plate from this sample (e.g. O331AC for the third plate sorted from sample O331A)
    * The same extra character (a-z and 0-9) for plate dilutions (e.g. O331Ab for the second plate dilution from sample O331A)
    * For metagenomes, this should indicate different extractions from the same sample.
* *Well/Metagenome/Pure culture/Amplicons*:
    * Starts with plate ID, then an underscore
    * Three characters in addition: one letter (A-L) and two digits (00-16) to describe the well.
    * Metagenomes are labeled with X, then 01. Further digits are reserved for later use.
    * Pure cultures are labeled with Z, then 01. Further digits are reserved for later use.
    * Amplicons are labeled with Y, then 01. Further digits are reserved for later use.
    * A1 should be always written A01
    * E.g. O331AC_C09
* *DNA library*
    * Describes many DNA libraries from the same source: can be different dilution plates, different sequencing runs, different preparations, for example.
    * Starts with the well ID
    * One character (A-Z; 0-9), in order
    * E.g. O331AC_C09A
* *Assembly*
    * Describes one assembly performed on one dataset from one run (SAG)
    * Starts with run ID, then an underscore
    * One character (A-Z; 0-9), in order
    * E.g. O331AC_C09A_B
* *Genes*:
    * Starts with assembly ID
    * 6 digits, with a 10 increment to allow adding genes in the middle
    * tRNAs have t prefix, rRNAs a r instead of the first digit
    * E.g. O331AC_C09A_B002340, O331AC_C09A_Bt05610
