######################################################################
# Author: David Newswanger
# username: newswangerd
#
# Assignment: Final Project
# Purpose: Encrypts information using a slightly modified enigma algorith.
#
# The Scherbius Enigma machine was a german cryptography device that was used during World War II.
# It used three rotors which contained a series of scrambled wires that lead from one input to another
# output. In order to encrypt a message, the rotors were set in a certain position, then a key would
# be pressed on the keyboard. This would send an electrical pulse through all three rotors, lighting up
# one of the output lights. The rotors would then rotate. The first one would rotate every time a key was
# pressed, the second every full rotation of the first and the third once every full rotation of the
# second. This program simulates this algorithm digitally.
#
# Acknowledgements: The Code Book: The Science of Secrecy from Ancient Egypt to Quantum Cryptography
#                   by Simon Singh
#
######################################################################

import random
import sys

class Rotor():
    ''' A rotor is simply a list with the numbers 0 through 94 which represent the various letters and punctuation in
    english. The rotor can shift the the values of the list over by one, which represents a rotation of the disk in the
    enigma machine. '''
    def __init__(self, offset):
        self.offset = offset
        self.set_rotor()

    def rotate(self):
        ''' Appends the first value of the list to the top of the list, sliding all the values over by one. '''
        self.rotor.append(self.rotor.pop(0))

    def set_rotor(self):
        ''' Sets the value of the rotors. Each rotor has to be build exactly the same each time. We do this by
         using a random number generator that is seeded with the same value, in this case 42, before each series
         of rotors is generated. This ensures that we always get the same set of rotors regardless of whether we
         are generating 3 or 300. '''
        characters = [x - 32 for x in range(32, 127)]
        self.rotor = []

        for x in range(len(characters)):
            index = random.randint(0, len(characters) - 1)
            self.rotor.append(characters[index])
            del(characters[index])

        for x in range(ord(self.offset)):
            self.rotate()

    def to_number(self, character):
        ''' Converts a character to its numerical representation by converting it into the decimal ASCII equivalent and
        subtracting 32. This ensures that we aren't using the first 32 ASCII characters, which are weird. '''
        return ord(character) - 32

    def to_character(self, number):
        ''' Converts a number to a character by adding 32 to it and transforming it using ASCII '''
        return chr(number + 32)

    def next_index(self, index):
        ''' Takes in a character, converts it to decimal, inserts it into a rotor and retrieving the output. '''
        #Enters as character
        index = self.to_number(index)
        #Transformed to number and looked up
        index = self.rotor[index]
        #Returned as character
        return self.to_character(index)

    def prev_index(self, index):
        ''' Performs the reverse operation of next_index by searching the values in the list and returning the
        corresponding index. '''
        #Enters as character
        index = self.to_number(index)
        #Transformed to number and looked up
        index = self.rotor.index(index)
        #Returned as character
        return self.to_character(index)

class Enigma():
    ''' Creates an Enigma object which initializes all the necessary rotors based on the key that's given and either
    encrypts or decrypts the message based on the desired outcome. '''
    def __init__(self, message, key, encrypt):
        self.message = message
        self.key = key
        if encrypt:
            self.plain_text = message
            self.cipher_text = ""
            self.encrypt()
        else:
            self.cipher_text = message
            self.plain_text = ""
            self.decrypt()

    def set_rotors(self):
        random.seed(42)
        rotors = []
        for x in self.key:
            rotors.append(Rotor(x))
        self.rotors = rotors[:]

    def clean(self):
        good_chars = [x for x in range(32, 127)]
        cleaned = ""
        for x in self.plain_text:
            if ord(x) in good_chars:
                cleaned += x
        self.plain_text = cleaned

        cleaned = ""
        for x in self.cipher_text:
            if ord(x) in good_chars:
                cleaned += x
        self.cipher_text = cleaned

    def encrypt(self):
        ''' Encrypts the message by inserting the first character into the first rotor, the output of the first
         rotor into the second, the output of the second into the third etc. Each rotor is rotated every 1, 95, 190
         characters, depending on the rotor order. '''
        self.set_rotors() # The rotors must be reset each time
        self.clean()
        output = ""
        for (i, val) in enumerate(self.plain_text):
            for (j, x) in enumerate(self.rotors):
                val = x.next_index(val)
                if i % (95 ** j) == 0:
                    x.rotate()
            output += val
        self.cipher_text = output

    def decrypt(self):
        ''' Decrypts by reversing the process in the encrypt function. The character starts at the last rotor and
         makes it's way to teh first. '''
        self.set_rotors()
        self.clean()
        output = ""
        for (i, val) in enumerate(self.cipher_text):
            for x in self.rotors[::-1]:
                val = x.prev_index(val)
            for (j, x) in enumerate(self.rotors):
                if i % (95 ** j) == 0:
                    x.rotate()
            output += val
        self.plain_text = output


def main():
    message = raw_input("Message: ")

    key = raw_input("Key: ")

    encrypt = ""
    options = {"encrypt": True, "decrypt": False, "e": True, "d": False}
    while encrypt.lower() not in options.keys():
        encrypt = raw_input("Encrypt(e) or decrypt(d): ")

    encrypt = options[encrypt]
    enigma = Enigma(message, key, encrypt)
    print "+---------- Cipher Text ----------+ \n" + enigma.cipher_text + "\n"
    print "+---------- Plain  Text ----------+ \n" + enigma.plain_text + "\n"

def testit(did_pass):
    """ Print the result of a unit test. """
    # This function works correctly--it is verbatim from the text
    linenum = sys._getframe(1).f_lineno # Get the caller's line number.
    if did_pass:
        msg = "Test at line {0} ok.".format(linenum)
    else:
        msg = ("Test at line {0} FAILED.".format(linenum))
    print(msg)

def test():
    cipher1 = Enigma("Hello World!", 'secret key', True)
    cipher2 = Enigma(cipher1.cipher_text, 'secret key', False)

    testit(cipher1.plain_text == cipher2.plain_text)

    cipher1.key = "key2"
    cipher2.key = "key2"

    cipher1.encrypt()
    cipher2.encrypt()

    testit(cipher1.cipher_text == cipher2.cipher_text)

    cipher1.decrypt()
    cipher2.decrypt()

    testit(cipher1.plain_text == cipher2.plain_text)



    '''car = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
    for x in car:
        print x, ord(x), cipher1.rotors[0].to_number(x)
    cipher1.key = car
    for x in car:
        print x
        cipher1.plain_text = x
        cipher1.encrypt()'''


if __name__ == '__main__':
    main()