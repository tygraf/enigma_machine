#!/usr/bin/env python3
import sys # needed for inputs
import random
import math
import os
import json
import pickle

rotor_file=os.getcwd() + '/settings/rotor_configs/'

class rotor:
    def __init__(self):
        # create a dictionary mapping of "index" to "letter" and vice versa
        self._alphabetLetters=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',]
        self._alphabetKeys=list(range(0,len(self._alphabetLetters)))
        self._index_to_letter_mapping=dict(zip(self._alphabetKeys,self._alphabetLetters))
        self._letter_to_index_mapping=dict(zip(self._alphabetLetters,self._alphabetKeys))
        self.num_increments=0 # the number of increments that this rotor has gone through
        # initialize rotor
        self._create_random_rotor()

    def _create_random_rotor(self):
        self._rotor_index=list(range(0,len(self._alphabetLetters)))
        self._rotor_values=list(range(0,len(self._alphabetLetters)))
        random.shuffle(self._rotor_values)
        self.rotor_vals = dict(zip(self._rotor_index,self._rotor_values))
        self.rev_rotor_vals = dict(zip(self._rotor_values,self._rotor_index))
   
    def shift_rotor(self,by_count=1,enable=True):
        if enable:
            self._shifted_rotor = {}
            for i in sorted(self.rotor_vals.keys()):
                self._shifted_rotor[(i+by_count)%26] = self.rotor_vals[i]
            self.rotor_vals = self._shifted_rotor
            self.rev_rotor_vals = dict(zip(self.rotor_vals.values(),self.rotor_vals.keys()))

    def calc_output(self,rotor_input,direction):
        if direction == "fwd":
            return(self._index_to_letter_mapping[self.rotor_vals[self._letter_to_index_mapping[rotor_input]]])
        elif direction == "bwd":
            return(self._index_to_letter_mapping[self.rev_rotor_vals[self._letter_to_index_mapping[rotor_input]]])
        else:
            raise ValueError("Rotor Direction Not Specified")

class reflector:
    def __init__(self):
        self._alphabetLetters=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',]
        self._create_reflector()
    def _create_reflector(self):
        letters=self._alphabetLetters
        random.shuffle(letters)
        temp_reflector={}
        self.reflector={}
        # take the first 13 letters and pair them with the second thirteen
        for i in range(0,13):
            temp_reflector[self._alphabetLetters[i]] = self._alphabetLetters[i+13]
            self.reflector[self._alphabetLetters[i+13]] = self._alphabetLetters[i]
        self.reflector.update(temp_reflector)
    def calc_output(self,reflector_input):
        return(self.reflector[reflector_input])

class enigma_machine:
    def __init__(self,serial_num):
        self.serial_number=serial_num
        self.rotor_dir = rotor_file + self.serial_number
        self.rotor1_file = self.rotor_dir + '/rotor1.pkl'
        self.rotor2_file = self.rotor_dir + '/rotor2.pkl'
        self.rotor3_file = self.rotor_dir + '/rotor3.pkl'
        self.reflector_file = self.rotor_dir + '/reflector.pkl'
        self._char_counter = 0
        if not os.path.exists(self.rotor_dir):
            print("Creating Enigma Machine, Serial Number: " + self.serial_number)
            self.rotor1 = rotor()
            self.rotor2 = rotor()
            self.rotor3 = rotor()
            self.reflector = reflector()
            self._save_rotors()
        else:
            print("Found Enigma Machine, Serial Number: " + self.serial_number)
            with open(self.rotor1_file,'rb') as rotor1_input:
                self.rotor1 = pickle.load(rotor1_input)
            
            with open(self.rotor2_file,'rb') as rotor2_input:
                self.rotor2 = pickle.load(rotor2_input)
        
            with open(self.rotor3_file,'rb') as rotor3_input:
                self.rotor3 = pickle.load(rotor3_input)
    
            with open(self.reflector_file,'rb') as reflector_input:
                self.reflector = pickle.load(reflector_input)
    
    def _calc_rotor_increments(self,rotor_num):
        return(math.floor(self._char_counter/26**(rotor_num-1)) % 26)

    def _update_rotor_increments(self):
        new_rotor1_inc = self._calc_rotor_increments(rotor_num=1)
        new_rotor2_inc = self._calc_rotor_increments(rotor_num=2)
        new_rotor3_inc = self._calc_rotor_increments(rotor_num=3)
        
        if new_rotor1_inc != self.rotor1.num_increments:
            self.rotor1.num_increments = new_rotor1_inc
            self.rotor1.shift_rotor()
        
        if new_rotor2_inc != self.rotor2.num_increments:
            self.rotor2.num_increments = new_rotor2_inc
            self.rotor2.shift_rotor()
    
        if new_rotor3_inc != self.rotor3.num_increments:
            self.rotor3.num_increments = new_rotor3_inc
            self.rotor3.shift_rotor()
    
    def _calc_output_char(self,input_char):
        output_rotor1 = self.rotor1.calc_output(input_char,'fwd')
        output_rotor2 = self.rotor2.calc_output(output_rotor1,'fwd')
        output_rotor3 = self.rotor3.calc_output(output_rotor2,'fwd')
        output_reflector = self.reflector.calc_output(output_rotor3)
        output_rotor3 = self.rotor3.calc_output(output_reflector,'bwd')
        output_rotor2 = self.rotor2.calc_output(output_rotor3,'bwd')
        output_rotor1 = self.rotor1.calc_output(output_rotor2,'bwd')
        return(output_rotor1)

    def parse_input(self,input_phrase):
        output_phrase = ""
        for i in input_phrase:
            output_phrase += self._calc_output_char(input_char=i)
            # update counters and shift rotors
            self._char_counter += 1
            self._update_rotor_increments()
        print(output_phrase)
    
    def _save_rotors(self):
        if not os.path.exists(self.rotor_dir):
            os.makedirs(self.rotor_dir)
        rotor1_file = self.rotor_dir + '/rotor1.pkl'
        rotor2_file = self.rotor_dir + '/rotor2.pkl'
        rotor3_file = self.rotor_dir + '/rotor3.pkl'
        reflector_file = self.rotor_dir + '/reflector.pkl'
            
        with open(rotor1_file,'wb') as output1:
            pickle.dump(self.rotor1, output1, pickle.HIGHEST_PROTOCOL)
        with open(rotor2_file,'wb') as output2:
            pickle.dump(self.rotor2, output2, pickle.HIGHEST_PROTOCOL)
        with open(rotor3_file,'wb') as output3:
            pickle.dump(self.rotor3, output3, pickle.HIGHEST_PROTOCOL)
        with open(reflector_file,'wb') as output4:
            pickle.dump(self.reflector, output4, pickle.HIGHEST_PROTOCOL)
        output1.close()
        output2.close()
        output3.close()
        output4.close()

# Next steps: make rotors move, confirm both decrypt and encrypt (this will require static rotor settings)
