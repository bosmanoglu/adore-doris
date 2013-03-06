#!/bin/bash

OIFS=${IFS}
IFS=$'\n'
for p in `cat ${1}`
do
  obj=${p%%.*}
  prp=${p##*.}
  
  echo "@property"
  echo "def ${prp}(self):"
  echo "    return self.${obj}.${prp}"
  echo "@${prp}.setter"
  echo "def ${prp}(self, value):"
  echo "    self.${obj}.${prp}= value"
  echo ""
done
IFS=${OIFS}

#    @property
#    def nlines(self):
#        return self.nlines
#    @nlines.setter
#    def nlines(self, value):
#        self.nlines=<np.long> value
