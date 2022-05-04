# -*- coding: windows-1250 -*-
import redis

class TOsztaly():
        
    def __init__(self):
        redis_host='172.22.223.200'
        redis_port=6379
               
        self.r=redis.Redis(host=redis_host, 
                           port=redis_port, 
                           decode_responses=True)
        
    #1. autó és sofőr felvétele (rendszám, sofőrnév, szállítható utasok száma, autó_évjárata, autótípusa, telefonszám) (egy rendszám csak egyszer szerepelhet)
    def uj_auto(self, rendszam, sofor, utas_db, 
                auto_evj, auto_tipus, tel):
        if self.r.sismember('autok', rendszam):
            print('mar van ilyen rendszam')
            return
            
        self.r.hmset('auto_'+rendszam,
                     {'rendszam':rendszam, 
                      'sofor':sofor, 
                      'utas_db':utas_db, 
                      'auto_evj':auto_evj, 
                      'auto_tipus':auto_tipus, 
                      'tel':tel})
        self.r.sadd('autok', rendszam)
        
    def auto_lista(self):
        for i in self.r.smembers('autok'):
            print(self.r.hgetall('auto_'+i))
            
    #2. az autó és a sofőr  szolgálatba áll (mikortól)
    def szolgalatba_all(self, rendszam, idopont):
        if not(self.r.sismember('autok', rendszam)):
            print('nincs ilyen rendszam')
            return
             
        self.r.zadd('szolgalat', rendszam, idopont)
        
    #3. az autó és a sofőr  befejezi szolgálatot (időpont)
    def befejezi_a_szolgalatot(self, rendszam, idopont):
        if not(self.r.sismember('autok', rendszam)):
            print('nincs ilyen rendszam')
            return
        
        if self.r.zscore('szolgalat', rendszam)>float(idopont):
            print('hibas idopont')
            return
        
        self.r.zrem('szolgalat', rendszam)
        self.r.zrem('osszar', rendszam)
        
    #4. A szolgálatban lévő autók kezdési időpont szerint csökkenően rendezve
    def szolgalat_lista(self):
        print(self.r.zrevrange('szolgalat',0,-1, 
                               withscores=True))
        
    #5. ut_rendelés (cím, időpont, létszám) (jó, ha lesz azonosítója)
    def ut_rendeles(self, cim, idopont, letszam):
        
        if letszam>4:
            print('sokan vannak')
            return 
        utid=str(self.r.incr('utid'))
        self.r.hmset('ut_'+utid,
                     {'cim':cim, 
                      'idopont':idopont, 
                      'letszam':letszam})
        self.r.sadd('utak', utid)
        return utid
        
    #6. az úthoz sofőr és autó rendelése
    def auto_uthoz_rendel(self, utid, rendszam):
        if not(self.r.sismember('autok', rendszam)):
            print('nincs auto')
            return
        if not(self.r.sismember('utak', utid)):
            print('nincs ut')
            return 
        
        if self.r.hget('ut_'+utid, 'ar')!=None:
            print('mar ez az ut teljesitva van')
            return 
        
        self.r.hset('ut_'+utid, 'rendszam', rendszam)
        
    #7. az út_teljesítése, ár, km rögzítése
    def teljesit(self, utid, ar, km):
        
        rendszam=self.r.hget('ut_'+utid, 'rendszam')
        
        if rendszam==None:
            print('nincs auto vagy nincs ut')
            return 
        
        self.r.hmset('ut_'+utid,
                     {'ar':ar,
                      'km':km})
        self.r.zincrby('osszar', rendszam, ar)
        self.r.zincrby('osszkm', rendszam, km)
        
    #8. az autók és sofőrök listája összkm alapján rendezve
    def osszkm_lista(self):
        print('osszkm')
        print(self.r.zrange('osszkm', 0, -1, withscores=True))
        
    #9. az autó és a sofőr adatainak a lekérdezése (rendszam)
    def auto_adat(self, rendszam):
        print('autoadat')
        print(self.r.hgetall('auto_'+rendszam))
        
    #10. a megrendelt, de még le nem zárt utak listája
    def megrendelt_lenemzart_utak(self):   
        print('lenemzatutak') 
        for i in self.r.smembers('utak'):
            if self.r.hget('ut_'+i, 'ar')==None:
                print(i)
                print(self.r.hgetall('ut_'+i))
            
    #11. a szolgálatban lévő autók listája a szolgálat időtartamára vonatkozó összár alapján növekvően rendezve
    def osszar_lista(self):
        print('osszar') 
        for i in self.r.zrange('osszar', 0, -1, 
                               withscores=False):
            print(i)
            print(self.r.zscore('osszar', i))
            print(self.r.hgetall('auto_'+i))
    
    def utlista(self):
        print('utlista')
        for i in self.r.smembers('utak'):
            print(self.r.hgetall('ut_'+i))    
        
        
        
        from TOsztaly import TOsztaly
rf=TOsztaly()


rf.uj_auto('aaa111', 'anna', 4, '2017', 'Opel', '1223')
rf.uj_auto('bbb222', 'bela', 3, '2019', 'Ford', '222')
rf.uj_auto('ccc333', 'cili', 3, '2018', 'VW', '555')
rf.uj_auto('ddd444', 'denes', 4, '2016', 'Skoda', '567')
rf.uj_auto('eee555', 'elek', 4, '2017', 'Smart', '8987')

rf.auto_lista()

rf.szolgalatba_all('aaa111', '202204140600')
rf.szolgalatba_all('aaa222', '202204140600')
rf.szolgalatba_all('bbb222', '202204140700')
rf.szolgalatba_all('ccc333', '202204141000')

rf.szolgalat_lista()

rf.ut_rendeles('Db Kassai u 26', '202204141520', 20)
utid1=rf.ut_rendeles('Db Kassai u 26', '202204141520', 4)
utid2=rf.ut_rendeles('Db Kassai u 26', '202204141521', 3)
utid3=rf.ut_rendeles('Db Forum', '202204141320', 2)
utid4=rf.ut_rendeles('Db Egyetem ter 1', '202204141010', 1)
utid5=rf.ut_rendeles('Db Interspar', '202204141110', 2)

rf.utlista()

rf.auto_uthoz_rendel('0', 'aaa111')
rf.auto_uthoz_rendel(utid1, 'aaa222')
rf.auto_uthoz_rendel(utid1, 'aaa111')
rf.auto_uthoz_rendel(utid2, 'aaa111')
rf.auto_uthoz_rendel(utid3, 'bbb222')
rf.auto_uthoz_rendel(utid4, 'ccc333')


rf.teljesit(utid5, 3000, 5)
rf.teljesit(utid1, 4000, 7)
rf.teljesit(utid2, 2000, 3)
rf.teljesit(utid3, 1000, 1)

rf.megrendelt_lenemzart_utak()

rf.osszkm_lista()

rf.osszar_lista()

rf.auto_adat('aaa111')


rf.befejezi_a_szolgalatot('aaa111', '202204141600')















        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
         
    
    
    
    
    
    
    
    
    
    
    
    
    
        












                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
                     
        
