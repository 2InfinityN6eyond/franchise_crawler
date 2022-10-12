from tqdm import tqdm
from time import sleep

for a in tqdm(range(10), desc='foo', leave=None):

    for b in tqdm(range(10), desc='bar', leave=None):
        sleep(.1)

    for b in tqdm(range(10), desc='baz', leave=None):
        sleep(.1)