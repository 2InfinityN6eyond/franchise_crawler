from tqdm import tqdm
import time


ll = list(range(100))

with tqdm(total = -1) as bar :
    for i in ll :
        time.sleep(0.2)
        bar.update(1)
        bar.set_description(str(i))

        if i % 2 == 0 :
            ll.append(len(ll))
            bar.total = len(ll)
