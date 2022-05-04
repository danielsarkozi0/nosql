# -*- coding: windows-1250 -*-
import redis

class SZJOsztaly():
        
    def __init__(self):
        redis_host='172.22.223.181'
        redis_port=6379
               
        self.r=redis.Redis(host=redis_host, 
                           port=redis_port, 
                           decode_responses=True)
    #ez semmi
    def get_alma(self):
        print(self.r.get('alma'))

    #Új játék indítása
    def uj_jatek(self, betu):
        for i in self.r.zrange('zutrang',0,-1, 
                               withscores=False):
            self.r.delete('s_'+i)
        
        self.r.delete('zutrang')
        self.r.setex('jatek',betu[0],60)

    #Játékos beküld egy szót, sikeres: pontot kap érte, 
    #sikertelen: lejárt játék, rossz betűvel kezdődik
    #sikertelen: már volt
    def bekuld(self, jatekos, szo):
        if not(self.r.exists('jatek')):
            print('lejart')
            return
        if self.r.get('jatek')!=szo[0]:
            print('hibas kezdobetu')
            return 
        if self.r.sismember('s_'+jatekos, szo):
            print('mar volt')
            return 
        
        self.r.sadd('s_'+jatekos, szo)
        self.r.zincrby('zutrang', jatekos, 1)
        self.r.zincrby('zosszrang', jatekos, 1)

    #A játék végén kiírjuk a ranglistát, 
    #a legtöbb pontot kapó kerül a legelejére  
    def utolso_rangsor(self):
        print(self.r.zrevrange('zutrang',0,-1
                               , withscores=True))

    #Több játék során kapott pontszámokat összegezzük, 
    #és készítünk egy rangsort a felhasználók között.       
    def ossz_rangsor(self):
        print(self.r.zrevrange('zosszrang',0,-1
                               , withscores=True))
       
#TESZTELES
from SZJOsztaly import SZJOsztaly

rf=SZJOsztaly()

#rf.get_alma()
rf.uj_jatek('b')

rf.bekuld('anna', 'beka')
rf.bekuld('anna', 'beka')
rf.bekuld('anna', 'alma')
rf.bekuld('anna', 'banan')
rf.bekuld('anna', 'baarack')

rf.bekuld('geza', 'bar')
rf.bekuld('geza', 'banan')

rf.utolso_rangsor()
rf.ossz_rangsor()
       
            
        
        