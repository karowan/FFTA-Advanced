"""Classify ARM ELF data without mistaking instruction words for ROM pointers."""
import bisect
import subprocess

class ELFData:
    def __init__(self, elf, prefix):
        # nm omits ARM mapping symbols even with -a unless --special-syms is set.
        rows=subprocess.check_output([prefix+'nm.exe','-a','-n','--special-syms',str(elf)],text=True)
        mapping={}
        for row in rows.splitlines():
            fields=row.split()
            if len(fields)==3 and fields[2].split('.')[0] in ('$a','$t','$d'):
                address=int(fields[0],16);kind=fields[2][1]
                assert address not in mapping or mapping[address]==kind,('ambiguous ELF mapping',elf,address)
                mapping[address]=kind
        assert mapping,('missing ARM mapping symbols',elf)
        self.addresses=sorted(mapping);self.kinds=[mapping[a] for a in self.addresses]
        # A C constant object can occupy a merged read-only section without a
        # fresh mapping symbol. Its ELF OBJECT extent is also explicit data.
        self.objects=[]
        rows=subprocess.check_output([prefix+'readelf.exe','-sW',str(elf)],text=True)
        for row in rows.splitlines():
            fields=row.split()
            if len(fields)>=8 and fields[3]=='OBJECT' and fields[6]!='UND':
                address=int(fields[1],16);size=int(fields[2],0)
                if size:self.objects.append((address,address+size))

    def contains_word(self, address):
        if any(a<=address and address+4<=b for a,b in self.objects):return True
        index=bisect.bisect_right(self.addresses,address)-1
        return (index>=0 and self.kinds[index]=='d' and
                (index+1==len(self.addresses) or address+4<=self.addresses[index+1]))
