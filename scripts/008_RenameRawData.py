import os
import shutil

# local origin
path = "/var/mri/raw/"
filenames = os.listdir(path)

# separate filenames in basename
basenames = [item.split(".")[0] for item in filenames]
# extension
endings = [".".join(item.split(".")[1:]) for item in filenames]
# date
dates = [item[:8] for item in filenames]
# earmarks
earmarks = [item[-6:-3] for item in basenames]

# lisf of names that have to be deleted from filename
names = [
         "Charlotte", "Diana", "Kate", "Lukrezia", "Lucrezia", "Lucrez", "Mary", "Stuart", "Wu", "Zetian",
         "Ada", "Beatrix", "Katharina", "Katarina", "Letizia", "Leticia", "Maxima",
         "Camilla", "Kamilla", "Fergie", "Grace", "Kelly", "Hedwig", "Silvia", "Victoria", "Viktoria",
         "Charlene", "Charlenne", "Cleopatra", "Elli", "Else", "Luise",
         "Adelheid", "Marie", "Nitokris", "Pippa", "Sissi", "Sophie",
         "Agrippina", "Juliana", "Leopoldine", "Mette", "Marit", "Theo", "Nofretete",
         "-", "CLEAR", "CLEA", "LEAR", "LEA", "CLE"] 

# clumsy approach to delete unwanted strings from filename
basenames2 = []
for base in basenames:
    for name in names:
        base = base.replace(name, "")
    basenames2 += [base]

# extract sequence names
methods = [item[15:-6] for item in basenames2]
# put every part of the new file name in a tuple list
variables = zip(earmarks, dates, methods, endings)

# create new filenames
newnames = ["M{0}P100_{1}_{2}.{3}".format(a, b, c, d) for a, b, c, d in variables]
# create new path
newFullPath = [os.path.join("/home/hans/MINIPIG_HD_100/M{0}P100/M{0}P100_{1}/M{0}P100_{1}_{2}.{3}".format(a, b, c, d)) for a, b, c, d in variables]


bothnames = zip(filenames, newFullPath)
newpath = "/home/hans/MINIPIG_HD_100"
newFullPath

# do the renaming
for src, dst in bothnames:
    try:
        os.mkdirs(os.path.dirname(dst))
        print('created directory {0}'.format(os.path.dirname(dst)))
    except:
        print('directory {0} already existed'.format(os.path.dirname(dst)))
        pass
    shutil.copy2(os.path.join(path, src), dst)
    
#[shutil.copy2(os.path.join(path, src), os.path.join(newpath, dst)) for src, dst in bothnames]

