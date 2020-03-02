# logparserX
WIP log parsing code for research project. Objective was to resolve some workflow issues with offloading data from our subs.
Decoupling the parsing code from Matlab also helps to make the log parser more portable.

Compartmentalizing the parsing of different log files into different tasks let me run them in parallel in separate threads which sped up the start-to-finish parsing time dramatically over the existing Matlab parser.


Log files and executable file omitted.
