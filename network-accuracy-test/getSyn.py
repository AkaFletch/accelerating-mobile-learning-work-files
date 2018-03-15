



def findSyn(label):
    f = open('map', 'r')
    p = 0
    for i in f.readlines():
        if(p==0):
            l = i.replace(',','').split(' ')
            if(l[0] == label):
            	return(l[1].rsplit()[0])
            p=1
        else:
            p=0
findSyn("n01443537")
