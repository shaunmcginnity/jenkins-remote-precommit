#!/usr/bin/env python
import subprocess

class P4Change:
    def __init__(self, changenum):
        self.changenum = changenum

        proc = subprocess.Popen(['p4', 'change', '-o', str(changenum)], 
                                stdout=subprocess.PIPE,
                                )
        self.p4change = proc.communicate()[0]

    def AddToDescription(self, text):
        number = 1
        newChange = ""
        currentChange = self.p4change.splitlines()
        for line in currentChange:
            nextLine = currentChange[number]
            if '#' not in nextLine and 'Configuration' not in nextLine and 'Files:' in nextLine:
                newChange += "\t" + text + "\n"

            if number < len(currentChange) - 1 :
                number += 1

            newChange += line + "\n"

        self.p4change = newChange

    def Save(self):
        proc = subprocess.Popen(['p4', 'change', '-i'], 
                        stdin=subprocess.PIPE,
                        )
        proc.communicate(self.p4change)



