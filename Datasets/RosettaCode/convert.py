import sys, os

def convert(infile, outfile):
  for line in infile:
    print line
    (task, type, link) = line.split('\t')
    tokens = [task, link, 'y' if link == 'True' else 'n']
    outfile.write('\t'.join(tokens) + '\n')

def main():
  infile = open(sys.argv[1])
  outfile = open(sys.argv[2], 'w')
  print "From %s to %s" %(infile, outfile)
  convert(infile, outfile)

if __name__ == '__main__':
  main()
