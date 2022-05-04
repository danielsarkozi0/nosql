# -*- coding: windows-1250 -*-
import redis

class Osztaly():
        
    def __init__(self):
        redis_host='172.22.223.200'
        redis_port=6379
               
        self.r=redis.Redis(host=redis_host, 
                           port=redis_port, 
                           decode_responses=True)
    #1.új dolgozó felvétele: 
    #paramétere: email, név. A dolgozót azonosíthatjuk az email címével.   
    def uj_dolgozo(self, email, nev):
        if self.r.hexists('dolgozok', email):
            print('mar van ilyen')
            return 
        
        self.r.hset('dolgozok', email, nev)

    #2.dolgozók emailjéhez a név kiírása
    def dolgozo_nev(self, email):
        print(self.r.hget('dolgozok', email))

    #3.dolgozók nevéhez az emailjének a kiírása
    def dolgozo_email(self, nev):
        for i in self.r.hkeys('dolgozok'):
            if self.r.hget('dolgozok', i)==nev:
                print(i)
    
    #4.új feladatot kiírása: paraméterei: kiírja ki (email), leírás, prioritás. A feladatokhoz generáljunk azonosítót, 
    #a metódus adja az azonosítót vissza.           
    def uj_feladat(self, kiiro_email, leiras, prioritas):
        if not(self.r.hexists('dolgozok', kiiro_email)):
            print('nincs ilyen dolgozo')
            return
        
        f_azon=str(self.r.incr('f_azon'))
        
        self.r.hmset('feladat_'+f_azon, 
                     {'kiiro_email':kiiro_email, 
                      'leiras':leiras})
        self.r.zadd('feladatok', f_azon, prioritas)
        return f_azon


    #5.feladathoz munkavégző (dolgozó) rendelése: paraméterei: feladat, 
    #munkavégző email. Egy feladatot több munkavégző is el tud végezni 
    #(azt adjuk itt meg), de majd csak egy munkavégző végzi el a valóságban. 
    #A feladat elvégzőjét előzetesen hozzá kell rendelni a feladathoz.       
    def feladathoz_dolgozo_rendeles(self, f_azon, email):
        if not(self.r.hexists('dolgozok', email)):
            print('nincs ilyen dolgozo')
            return
        
        #if not(self.r.exists('feladat_'+f_azon)):
        if self.r.zscore('feladatok', f_azon)==None:
            print('nincs feladat')
            return 
        
        self.r.sadd('lmunkavegzok_'+f_azon, email)
    

    #6.feladat lehetséges munkavégzőinek a leírása
    def feladat_leiras(self, f_azon):
        print(self.r.hget('feladat_'+f_azon, 'leiras'))
        
        print(self.r.hgetall('feladat_'+f_azon))
        print(self.r.zscore('feladatok', f_azon))

    #9.munka elvégzése (ki, mit): a feladatok közül töröljük 
    #az adott munkát, amit elvégeztek.
    def feladat_elvegzes(self, f_azon, email):
        if not(self.r.sismember('lmunkavegzok_'+f_azon, email)):
            print('a feladat es a dolgozo nincs ooszerendelve')
            return
        
        self.r.delete('feladat_'+f_azon)
        self.r.delete('lmunkavegzok_'+f_azon)
        self.r.zrem('feladatok', f_azon)
        
        self.r.zincrby('elvegzett_feladatok', email, 1)
    
    #10.dolgozók emailjének listázása az elvégzett feladatok darabszáma szerinti sorrendben.
    def dolgozok_lista_db(self):
        print(self.r.zrevrange('elvegzett_feladatok', 0, -1,
                               withscores=True))
        
        for i in self.r.zrevrange('elvegzett_feladatok', 0, -1,
                               withscores=False):
            print(i)
            print(self.r.zscore('elvegzett_feladatok', i))
            print(self.r.hget('dolgozok', i))
        
    #7. feladatok listázása prioritás szerint 
    #(elég az azonosítót és a prioritást visszaadni)

    #8. feladatazonosítóhoz adjuk vissza a leírását
    #Ez a ketto nemtom melyikhez menne
    def munkavegzo_lista(self, f_azon):
        print(self.r.smembers('lmunkavegzok_'+f_azon))
            
    def feladat_lista(self):
        print(self.r.zrevrange('feladatok', 0, -1, 
                               withscores=True))
        
    def dolgozo_lista(self):
        print(self.r.hgetall('dolgozok'))        
        
#TESZTELES
from Osztaly import Osztaly
rf=Osztaly()

rf.uj_dolgozo('a@g.c', 'anna')
rf.uj_dolgozo('a@g.c', 'bela')

rf.uj_dolgozo('b@g.c', 'bela')
rf.uj_dolgozo('c@g.c', 'cili')
rf.uj_dolgozo('d@g.c', 'denes')
rf.uj_dolgozo('e@g.c', 'elek')
rf.uj_dolgozo('f@g.c', 'elek')

rf.dolgozo_lista()

rf.dolgozo_nev('a@g.c')

rf.dolgozo_email('elek')

rf.uj_feladat('w@g.c', 'takaritas', 3)
f1=rf.uj_feladat('a@g.c', 'takaritas', 5)
f2=rf.uj_feladat('b@g.c', 'mosogatas', 4)
f3=rf.uj_feladat('b@g.c', 'szemetlevitel', 5)
f4=rf.uj_feladat('b@g.c', 'mosas', 3)
f5=rf.uj_feladat('b@g.c', 'cipopucolas', 1)

rf.feladat_lista()

rf.feladat_leiras(f5)

rf.feladathoz_dolgozo_rendeles(f1, 'a@g.c')
rf.feladathoz_dolgozo_rendeles(f1, 'b@g.c')
rf.feladathoz_dolgozo_rendeles(f1, 'c@g.c')

rf.feladathoz_dolgozo_rendeles(f2, 'a@g.c')
rf.feladathoz_dolgozo_rendeles(f2, 'd@g.c')

rf.feladathoz_dolgozo_rendeles(f3, 'e@g.c')
rf.feladathoz_dolgozo_rendeles(f3, 'd@g.c')

rf.feladathoz_dolgozo_rendeles(f4, 'd@g.c')
rf.feladathoz_dolgozo_rendeles(f5, 'd@g.c')

rf.munkavegzo_lista(f1)

rf.feladat_elvegzes(f1, 'w@g.c')
rf.feladat_elvegzes('-1', 'a@g.c')
rf.feladat_elvegzes(f1, 'd@g.c')

rf.feladat_elvegzes(f1, 'a@g.c')
rf.feladat_elvegzes(f2, 'a@g.c')
rf.feladat_elvegzes(f3, 'd@g.c')
rf.feladat_elvegzes(f4, 'd@g.c')
rf.feladat_elvegzes(f5, 'd@g.c')

rf.dolgozok_lista_db() 