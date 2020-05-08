
import core.gui as gui
from core.gui import HOR_SEP
from core.on_off import on_off_left_upper, OnOffPatch, OnOffWorld
from core.sim_engine import SimEngine
from core.utils import bin_str

from copy import copy

# from random import choice, random, randint
import random

from typing import List


class CA_World(OnOffWorld):

    ca_display_size = 151

    # bin_0_to_7 is ['000' .. '111']
    bin_0_to_7 = [bin_str(n, 3) for n in range(8)]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.pos_to_switch is a dictionary that maps position values in a binary number to range(8) represented
        # as 3-digit binary strings:
        #     {1: '000', 2: '001', 4: '010', 8: '011', 16: '100', 32: '101', 64: '110', 128: '111'}
        # The three digits are the rule components and the keys to the switches.
        # To see it, try: print(self.pos_to_switch) after executing the next line.
        # The function bin_str() is defined in utils.py

        self.pos_to_switch = dict(zip([2**i for i in range(8)], CA_World.bin_0_to_7))
        # print(self.pos_to_switch)

        # The rule number used for this run, initially set to 110 as the default rule.
        # (You might also try rule 165.)
        # The following sets the local variable self.rule_nbr. It doesn't change the 'Rule_nbr' slider widget.
        self.rule_nbr = 110
        # Set the switches and the binary representation of self.rule_nbr.
        self.set_switches_from_rule_nbr()
        self.set_binary_nbr_from_rule_nbr()
        self.make_switches_and_rule_nbr_consistent()
        self.init = None

        # self.ca_lines is a list of lines, each of which is a list of 0/1. Each line represents
        # a state of the CA, i.e., all the cells in the line. self.ca_list contains the entire
        # history of the CA.
        self.ca_lines: List[List[int]] = [[]]
        # gui.WINDOW['rows'].update(value=len(self.ca_lines))
        SimEngine.gui_set('rows', value=len(self.ca_lines))

    def build_initial_line(self):
        """
        Construct the initial CA line
        """
        self.init = SimEngine.gui_get('justification')
        if SimEngine.gui_get('Random?'):
            # Set the initial row to random 1/0.
            # You complete this line.
            line = [0,0]
            for _ in range(self.ca_display_size):
                line.append(random.randint(0,1))
            line += [0,0]
        else:
            if SimEngine.gui_get('init_line') == '':
                line = [0] * self.ca_display_size
            elif SimEngine.gui_get('init_line'):
                line_0 = SimEngine.gui_get('init_line')
                # Convert line_0 to 0's and 1's
                # line = [0,0] + [c for c in line_0] + [0,0]        # pad with proper zeros. Then clean up later
                line = [0,0] + [0 if c == ' ' or c == '0' else 1 for c in line_0] + [0,0]
            else:
                line = [0] * self.ca_display_size
                col = 2 if self.init == 'Left' else \
                      CA_World.ca_display_size // 2 if self.init == 'Center' else \
                      CA_World.ca_display_size - 3   # self.init == 'Right'
                line[col] = 1
        return line

    def drop_extraneous_0s_from_ends_of_new_line(self, line): # direction is left or right
        if 1 not in line:
            return line
        print(f'line in drop:{line}')

        line = line[line.index(1) - 2:]         # leave 2 zeros trailing first 1
        line.reverse()                          # flip and do the same to the other side
        line = line[line.index(1) - 2:]
        line.reverse()                          # flip it back now that your done

        return line


    def extend_ca_lines_if_needed(self):
        # This function checks the top line and extends all lines if needed
        if not self.ca_lines:                   # Edge case if ca_lines is empty
            return

        top = self.ca_lines[-1]                 # Get the top element of ca_lines. This is the newest added line
        if len(top) < 5:                        # ca_lines should be at minimum of 5. eg 00100
            return

        if 1 in top[0:2]:                       # Only case is 0,1,....  rest doesn't matter. Should never be 1,1
            for line in self.ca_lines:          # add a 0 to the beginning of each line
                line.insert(0,0)

        if 1 in top[-2:]:                       # does the same but for last 2 elements instead
            for line in self.ca_lines:
                line.append(0)


    # @staticmethod
    def generate_new_line_from_current_line(self):
        new_line = [0]                                              # Start with 0
        current_line = self.ca_lines[-1]
        for i in range(len(current_line) - 2):                      # look through entire line but last element (offset)
            pattern = "".join(map(str, current_line[i:i+3]))
            new_line.append(gui.WINDOW[pattern].get())              # 0 if switch off else 1

        new_line.append(0)                                          # add a 0 to end it
        return new_line

    def get_rule_nbr_from_switches(self):
        """
        Translate the on/off of the switches to a rule number.
        This is the inverse of set_switches_from_rule_nbr(), but it doesn't set the 'Rule_nbr' Slider.
        """
        bin_string = ''
        for bin in self.bin_0_to_7:
            bin_string += str(gui.WINDOW[bin].get())

        bin_string = bin_string[::-1]
        return int(bin_string, 2)

    def handle_event(self, event):
        """
        This is called when a GUI widget is changed and isn't handled by the system.
        The key of the widget that changed is the event.
        If the changed widget has to do with the rule number or switches, make them all consistent.

        This is the function that will trigger all the code you write this week
        """
        # Handle color change requests.
        super().handle_event(event)

        event = SimEngine.event
        if event in ['Rule_nbr'] + CA_World.bin_0_to_7:
            if event in ['Rule_nbr']:
                self.rule_nbr = SimEngine.gui_get('Rule_nbr')
            else:
                self.rule_nbr = self.get_rule_nbr_from_switches()
            self.make_switches_and_rule_nbr_consistent()

    def make_switches_and_rule_nbr_consistent(self):
        """
        Make the Slider, the switches, and the bin number consistent: all should equal self.rule_nbr.
        """
        gui.WINDOW['Rule_nbr'].update(value=self.rule_nbr)          # Slider
        self.set_binary_nbr_from_rule_nbr()                         # Binary Number
        self.set_switches_from_rule_nbr()

    def set_binary_nbr_from_rule_nbr(self):
        """
        Translate self.rule_nbr into a binary string and put it into the
        gui.WINDOW['bin_string'] widget. For example, if self.rule_nbr is 110,
        the string '(01101110)' is stored in gui.WINDOW['bin_string']. Include
        the parentheses around the binary number.

        Use gui.WINDOW['bin_string'].update(value=new_value) to update the value of the widget.
        Use SimEngine.gui_set('bin_string', value=new_value) to update the value of the widget.
        """
        binaryNum = [0] * 8
        binaryStr = ""
        i = 0
        rule_nbr_copy = self.rule_nbr
        while rule_nbr_copy > 0:
            binaryNum[i] = rule_nbr_copy % 2
            rule_nbr_copy = int(rule_nbr_copy / 2)
            i += 1

        while len(binaryNum) > 0:
            binaryStr += str(binaryNum.pop())

        gui.WINDOW['bin_string'].update(value=binaryStr)

    def set_display_from_lines(self):
        """
        Copy values from self.ca_lines to the patches. One issue is dealing with
        cases in which there are more or fewer lines than Patch row.
        """
        self.init = SimEngine.gui_get('justification')

        col_offset = len(self.ca_lines[-1]) - self.ca_display_size

        for row in range(self.ca_display_size):
            for col in range(self.ca_display_size):
                if row < self.ca_display_size - len(self.ca_lines):                       # blank top if small ca_lines
                    self.patches_array[row, col].set_on_off(False)
                else:
                    ca_lines_row = row - self.ca_display_size + len(self.ca_lines)      # calc row + offset

                    if self.init == 'Left':
                        if col > len(self.ca_lines[-1]) - 1:
                            self.patches_array[row,col].set_on_off(False)
                        else:
                            self.patches_array[row,col].set_on_off(self.ca_lines[ca_lines_row][col])
                    elif self.init == 'Right':
                        ca_lines_col = col + col_offset
                        if ca_lines_col < 0:
                            self.patches_array[row,col].set_on_off(False)
                        else:
                            self.patches_array[row, col].set_on_off(self.ca_lines[ca_lines_row][ca_lines_col])
                    elif self.init == 'Center' or self.init == 'Random':
                        ca_lines_col = col + col_offset // 2 + 1
                        if ca_lines_col < 0:
                            self.patches_array[row, col].set_on_off(False)
                        elif ca_lines_col > len(self.ca_lines[-1]) - 1:
                            self.patches_array[row, col].set_on_off(False)
                        else:
                            self.patches_array[row, col].set_on_off(self.ca_lines[ca_lines_row][ca_lines_col])


    # Self added. Probably inconvenient
    def rule_nbr_to_pos(self):
        pos_val = dict(zip([2**i for i in range(8)], [False]*8))

        rule_num_copy = int(self.rule_nbr)
        for exponent in reversed(range(8)):
            big = 2**exponent
            if rule_num_copy >= big:
                pos_val[big] = True
                rule_num_copy -= big

            exponent -= 1
        return pos_val

    def set_switches_from_rule_nbr(self):
        """
        Update the settings of the switches based on self.rule_nbr.
        Note that the 2^i position of self.rule_nbr corresponds to self.pos_to_switch[i]. That is,
        self.pos_to_switch[i] returns the key for the switch representing position  2^i.

        Set that switch as follows: gui.WINDOW[self.pos_to_switch[pos]].update(value=new_value).
        Set that switch as follows: SimEngine.gui_set(self.pos_to_switch[pos], value=new_value).
        (new_value will be either True or False, i.e., 1 or 0.)

        This is the inverse of get_rule_nbr_from_switches().
        """
        pos_vals = self.rule_nbr_to_pos()
        for pos in pos_vals.keys():
            gui.WINDOW[self.pos_to_switch[pos]].update(pos_vals[pos])

    def setup(self):
        """
        Make the slider, the switches, and the bin_string of the rule number consistent with each other.
        Give the switches priority.
        That is, if the slider and the switches are both different from self.rule_nbr,
        use the value derived from the switches as the new value of self.rule_nbr.

        Once the slider, the switches, and the bin_string of the rule number are consistent,
        set self.ca_lines[0] as directed by SimEngine.gui_get('init').

        Copy (the settings on) that line to the bottom row of patches.
        Note that the lists in self.ca_lines are lists of 0/1. They are not lists of Patches.
        """
        for patch in self.patches:
            patch.set_on_off(False)

        self.ca_lines = [[]] # Resets the ca_lines between resets

        new_line = self.build_initial_line()
        if self.init == 'Left' or self.init == 'Right' or self.init == 'Center':
            new_line = self.drop_extraneous_0s_from_ends_of_new_line(new_line)
        self.ca_lines[0] = new_line
        self.set_display_from_lines()

    def step(self):
        """
        Take one step in the simulation.
        o Generate an additional line in self.ca_lines.
        o Copy self.ca_lines to the display
        """
        # self.patches_array[80][50].set_on_off(True)
        SimEngine.gui_set('rows', value=len(self.ca_lines))
        new_line = self.generate_new_line_from_current_line()
        self.ca_lines.append(new_line)
        self.extend_ca_lines_if_needed()
        self.set_display_from_lines()

# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

""" 
The following appears at the top-left of the window. 
It puts a row consisting of a Text widgit and a ComboBox above the widgets from on_off.py
"""
ca_left_upper = \
    [[sg.Text('Row justification'),
      sg.Combo(values=['Left', 'Center', 'Right'], key='justification', default_value='Right')],
     HOR_SEP(30),
     [sg.Text('Initial row:', pad=((0, 10), (20, 10)),
              tooltip="0's and 1's for the initial row. An empty \n" +
                      "string will set the initial row to all 0's."),
      sg.Input(default_text="1", key='init_line', size=(20, None), text_color='white',
               background_color='steelblue4', justification='center')],

     [sg.CB('Random?', key='Random?', enable_events=True, pad=((75, 0), None),
            tooltip="Set the initial row to random 0's and 1's.")],
     HOR_SEP(30, pad=(None, None)),
     [sg.Text('Rows:', pad=(None, (10, 0))), sg.Text('     0', key='rows', pad=(None, (10, 0)))],
     HOR_SEP(30, pad=(None, (0, 10)))
     ] + on_off_left_upper

# The switches are CheckBoxes with keys from CA_World.bin_0_to_7 (in reverse).
# These are the actual GUI widgets, which we access via their keys.
# The pos_to_switch dictionary maps position values in the rule number as a binary number
# to these widgets. Each widget corresponds to a position in the rule number.
# Note how we generate the text for the chechboxes.
switches = [sg.CB(n + '\n 1', key=n, pad=((30, 0), (0, 0)), enable_events=True)
                                             for n in reversed(CA_World.bin_0_to_7)]

""" 
This  material appears above the screen: 
the rule number slider, its binary representation, and the switches.
"""
ca_right_upper = [[sg.Text('Rule number', pad=((100, 0), (20, 10))),
                   sg.Slider(key='Rule_nbr', range=(0, 255), orientation='horizontal',
                             enable_events=True, pad=((10, 20), (0, 10))),
                   sg.Text('00000000 (binary)', key='bin_string', enable_events=True, pad=((0, 0), (10, 0)))],

                  switches
                  ]


if __name__ == "__main__":
    """
    Run the CA program. PyLogo is defined at the bottom of core.agent.py.
    """
    from core.agent import PyLogo

    # Note that we are using OnOffPatch as the Patch class. We could define CA_Patch(OnOffPatch),
    # but since it doesn't add anything to OnOffPatch, there is no need for it.
    PyLogo(CA_World, '1D CA', patch_class=OnOffPatch,
           gui_left_upper=ca_left_upper, gui_right_upper=ca_right_upper,
           fps=10, patch_size=3, board_rows_cols=(CA_World.ca_display_size, CA_World.ca_display_size))
