# -*- coding: windows-1250 -*-
import redis

class POsztaly():
        
    def __init__(self):
        redis_host='172.22.223.200'
        redis_port=6379
               
        self.r=redis.Redis(host=redis_host, 
                           port=redis_port, 
                           decode_responses=True)
    
    #1 Fel tudunk venni pizzát az adatbázisba (név, ár)       
    def uj_pizza(self, nev, ar):
        self.r.hset('pizzak', nev, ar)

    #2 a pizzához feltétet vehetünk fel (pizza_azon, feltét). Egy pizzához több feltétünk is lehet. Ezekkel lehet alapvetően megrendelni a pizzát.
    def uj_feltet(self, pizza, feltet):
        if not(self.r.hexists('pizzak', pizza)):
            print('nincs ilyen pizza')
            return 
        
        self.r.sadd('feltet_'+pizza, feltet)
        
    #4 a pizzák listája feltéttel
    def pizza_lista(self):
        #for i in self.r.hgetall('pizzak')
        for i in self.r.hkeys('pizzak'):
            print(i)
            print(self.r.hget('pizzak', i))
            print(self.r.smembers('feltet_'+i))
            
    #5 megrendelést felvétele (idő, amikor bejön; szállítási cím megadása; azonosító)
    def megrendeles(self, ido, cim):
        mra=str(self.r.incr('mra'))
        
        self.r.hmset('mr_'+mra,
                     {'ido':ido,
                      'cim':cim})
        self.r.sadd('megrendelesek', mra)
        return mra
        
    #6 a megrendeléshez pizza rendelése (megrendelés_azon, pizza_azon, db_szam)
    def megrendeles_pizza(self, mra, pizza, db):
        if not(self.r.sismember('megrendelesek', mra)):
            print('nincs ilyen megrendeles')
            return 
        
        for i in range(db):
            mrr=str(self.r.incr('mrr'))
            self.r.hmset('mrr_'+mrr,
                         {'mra':mra,
                          'pizza':pizza})
            
            self.r.sadd('mrreszletek_'+mra, mrr)
            
            self.r.rpush('sutnivalo', mrr)
    
    #7 lista arról, hogy a szakácsnak melyik soron következő pizzát kell sütnie: megrendelés_azon, pizza_azon, pizza_név, feltétlista, db
    def sutnivalo_lista(self):
        for i in self.r.lrange('sutnivalo', 0, -1):
            print('mrr:'+i)
            print(self.r.hget('mrr_'+i, 'mra'))
            pizza=self.r.hget('mrr_'+i, 'pizza')
            print(pizza)
            print(self.r.smembers('feltet_'+pizza))

    #8 a szakács elkezdi sütni a pizzát (megrendelés_azon, pizza_azon, db) 
    def sutobe(self, mrr):
        if self.r.lrem('sutnivalo', mrr)==0:
            print('nincs mrr')
            return 
        self.r.rpush('suto', mrr)
    
    #9 a sütőben lévő pizzák listája
    def suto_lista(self):
        for i in self.r.lrange('suto', 0, -1):
            print('mrr:'+i)
            print(self.r.hget('mrr_'+i, 'mra'))
            print(self.r.hget('mrr_'+i, 'pizza'))

    #10 a pizza kész (megrendelés_azon, pizza_azon, db)  
    def kesz(self, mrr):
        if self.r.lrem('suto', mrr)==0:
            print('nincs mrr')
            return 
        self.r.rpush('kesz_pizzak', mrr)
        
        mra=self.r.hget('mrr_'+mrr, 'mra')
        
        kesz=True
        for i in self.r.lrange('sutnivalo', 0,-1):
            if mra==self.r.hget('mrr_'+i, 'mra'):
                kesz=False
                break
            
        for i in self.r.lrange('suto', 0,-1):
            if mra==self.r.hget('mrr_'+i, 'mra'):
                kesz=False
                break
            
        if kesz:
            self.r.rpush('kesz_megrendeles', mra)
            for i in self.r.smembers('mrreszletek_'+mra):
                self.r.lrem('kesz_pizzak', i)

    #11 a kész, de még nem kiszállított pizzák listája 
    def kesz_megrendeles_lista(self):
        for i in self.r.lrange('kesz_megrendeles', 0, -1):
            print(i)
            print(self.r.hget('mr_'+i, 'cim'))
            for j in self.r.smembers('mrreszletek_'+i):
                print(self.r.hget('mrr_'+j, 'pizza'))
                
    #12 a pizza kiszállítása (megrendelés_azon, pizza_azon, db) (nem tároljuk tovább a rendszerben)
    def kiszallit(self, mra):
        if self.r.lrem('kesz_megrendeles', mra)==0:
            print('nincs ilyen mra')
            return
        
        for i in self.r.smembers('mrreszletek_'+mra):
            self.r.delete('mrr_'+i)
            
        self.r.delete('mrreszletek_'+mra)
        self.r.srem('megrendelesek', mra)
        self.r.delete('mr_'+mra)
    
        
# -*- coding: windows-1250 -*-
from POsztaly import POsztaly
rf=POsztaly()

# rf.uj_pizza('songoku', 1800)
# rf.uj_pizza('hawaii', 2300)
# rf.uj_pizza('magyaros', 2800)
#
# rf.uj_feltet('songoku', 'sonka')
# rf.uj_feltet('songoku', 'gomba')
# rf.uj_feltet('songoku', 'kukorica')
#
# rf.uj_feltet('hawaii', 'ananasz')
# rf.uj_feltet('hawaii', 'sonka')
#
# rf.uj_feltet('magyaros', 'kolbasz')
# rf.uj_feltet('magyaros', 'szalonna')
# rf.uj_feltet('magyaros', 'hagyma')

rf.pizza_lista()

# mra1=rf.megrendeles('202204071430', 'Db Kassai 26 TEOKJ')
# rf.megrendeles_pizza(mra1, 'magyaros', 2)
# rf.megrendeles_pizza(mra1, 'songoku', 1)
#
# mra2=rf.megrendeles('202204071435', 'Laktanya u. 23')
# rf.megrendeles_pizza(mra2, 'hawaii', 1)
# rf.megrendeles_pizza(mra2, 'songoku', 1)

print('sutnivalo')
rf.sutnivalo_lista()

rf.sutobe('6')
rf.sutobe('7')
rf.sutobe('8')
rf.sutobe('9')


print('suto')
rf.suto_lista()

print('sutnivalo')
rf.sutnivalo_lista()


rf.kesz('6')
rf.kesz('7')
rf.kesz('8')
rf.kesz('9')

print('suto')
rf.suto_lista()

print('kesz')
rf.kesz_megrendeles_lista()

rf.kiszallit('3')



        
        
        
        
        
        
            
            
            
    
        
        
        
        
        
        
        
        
        
            
            
            
            
            
            
            
        
        
        
        
        
        
            
    
    
    
    
    
        
        
        
        
        
        
