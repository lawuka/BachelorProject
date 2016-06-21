----------------------------------------------------------------------------------
*                                                                                *
*                                                                                *
*   FABRICATION CAD-TOOL FOR THE PRODUCTION OF MICROFLUIDIC FLOW-BASED BIOCHIPS  *
*                                                                                *
*                                                                                *
----------------------------------------------------------------------------------

Note: The CAD-tool is developed under Python 3.5.1, the tool may not work with
      other versions.

----------------------------------------------------------------------------------

To use the Fabrication CAD-tool, run main.py with Python either from console or
through a Python IDE like PyCharm.

The Fabrication CAD-tool only works with the attached GUI, though the model can
be separated and used elsewhere.

----------------------------------------------------------------------------------

Files:

README.txt - this file.
Logfile.txt - A log file, cleared at each startup, which holds log for when the
              CAD-tool comes with an error message.

Folders:

chip_examples / - include examples of biochip architectures, to use inside the
                  GUI.
config / - includes the config file for the GUI.
controller / - includes the controller and the writing G-code to files.
library / - includes different libraries, designed with the origin of the
            CAD-tool.
model / - includes the model and different math and helper functions to assist the
          model.
parsers / - includes each parser used within the model.
view / - includes the view for the GUI.

----------------------------------------------------------------------------------