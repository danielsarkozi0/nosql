# -*- coding: windows-1250 -*-
import redis

class COsztaly():
        
    def __init__(self):
        redis_host='172.22.223.200'
        redis_port=6379
               
        self.r=redis.Redis(host=redis_host, 
                           port=redis_port, 
                           decode_responses=True)
        
    #1. helyszínek felvétele
    def uj_helyszin(self, helyszin):
        self.r.sadd('s_helyszinek',helyszin)
    
    #2. helyszínek listája
    def helyszin_lista(self):
        print(self.r.smembers('s_helyszinek'))
        
    #3. esemény felvétele (helyszín, esemény_kezdete, esemény_vége, megnevezés, felelős: név, telefon) (egy helyszínen egyszerre csak egy esemény lehet, a helyszínnek léteznie kell)
    def uj_esemeny(self, helyszin, kezdet, veg, megnevezes, 
                   felelos_nev, felelos_tel):
        if not(self.r.sismember('s_helyszinek', helyszin)):
            print('Nincs ilyen helyszin')
            return
        if kezdet>=veg:
            print('Hibas idointervallum')
            return 
    
    #4. adott időpontban folyó események listája (időpont): A lista tartalmazza a helyszínt, megnevezést, kezdetet, véget, felelős nevét, telefonszámát
        for i in self.r.zrange('z_esemenyek', 0,-1,
                               withscores=False):
            if helyszin==self.r.hget(i, 'helyszin'):
                if not(self.r.hget(i, 'veg')<kezdet or 
                       veg<=self.r.hget(i, 'kezdet')):
                    print('Mar vannak a szinpadon')
                    return 
        
    #5. az összes esemény listája helyszínnel, kezdés és befejezési idővel, megnevezéssel, felelőssel, kezdési idő szerint, azon belül a megnevezés szerint növekvően rendezve
        a=str(self.r.incr('esemeny_azon'))
        self.r.hmset('h_esemeny_'+a, 
                     {'helyszin':helyszin,
                      'kezdet':kezdet,
                      'veg':veg,
                      'megnevezes':megnevezes,
                      'felelos_nev':felelos_nev, 
                      'felelos_tel':felelos_tel})
        self.r.zadd('z_esemenyek','h_esemeny_'+a, kezdet)
        
        
    def esemeny_lista(self):
        for i in self.r.zrange('z_esemenyek',0,-1, 
                               withscores=False):
            print(i)
            print(self.r.hgetall(i))
            
    def esemeny_lista_idopont(self, idopont):
        for i in self.r.zrange('z_esemenyek',0,-1, 
                               withscores=False):
            if (self.r.hget(i,'kezdet')<=idopont
                and idopont<=self.r.hget(i,'veg')):
                print(self.r.hgetall(i))
    
    #6. jegytípus felvitele (név, ár, érvényesség kezdete, érvényesség vége)
    def uj_jegytipus(self, nev, ar, kezdet, veg):
        self.r.sadd('s_jegytipusok', nev)
        self.r.hmset('h_jegytipus_'+nev, 
                     {'nev':nev,
                      'ar':ar,
                      'ervenyesseg_kezdete':kezdet,
                      'ervenyesseg_vege':veg})
    
    def jegytipus_lista(self):
        for i in self.r.smembers('s_jegytipusok'):
            print(self.r.hgetall('h_jegytipus_'+i))
            
    #8. új vendég (email, név, szül_dat, nem)
    def uj_vendeg(self, nev, email, szul_dat):
        self.r.sadd('s_vendegek', email)
        self.r.hmset('h_vendeg_'+email, 
                     {'nev':nev,
                      'email':email,
                      'szul_dat':szul_dat})
    
    #10. a vendégek listája
    def vendeg_lista(self):
        for i in self.r.smembers('s_vendegek'):
            print(self.r.hgetall('h_vendeg_'+i)) 
            
    #9. a vendég jegyet vásárol (email, jegytípus) (egy vendég több jegyet vehet)
    def vendeg_jegyet_vesz(self, email, jegytipus_nev):
        if not(self.r.sismember('s_vendegek', email)):
            print('Nincs ilyen vendeg')
            return 
        if not(self.r.sismember('s_jegytipusok', jegytipus_nev)):
            print('Nincs ilyen jegytipus')
            return 
        self.r.sadd('s_vendeg_jegyei_'+email, jegytipus_nev)           
        
    def vendeg_jegyei(self, email):
        print(self.r.smembers('s_vendeg_jegyei_'+email))
        
    def jegyvasarlasok(self):
        for i in self.r.smembers('s_vendegek'):
            print(i)
            print(self.r.hget('h_vendeg_'+i, 'nev'))
            self.vendeg_jegyei(i)
    
    #11. azon vendégek listája, akik adott időpontban jogosultak a rendezvényt látogatni (idopont)
    def vendeg_idopont(self, idopont):
        for i in self.r.smembers('s_vendegek'):
            for j in self.r.smembers('s_vendeg_jegyei_'+i):
                if (self.r.hget('h_jegytipus_'+j,'ervenyesseg_kezdete')<=idopont
                    and idopont<=self.r.hget('h_jegytipus_'+j,'ervenyesseg_vege')):
                    print(i)
                    print(self.r.hget('h_vendeg_'+i, 'nev'))
    
    #12. a vendég az eseményt like-olja (email, esemeny) (egy eseményt csak egyszer like-olhat)
    def like(self, email, esemeny):
        if not(self.r.sismember('s_vendegek', email)):
            print('nincs ilyen vendeg')
            return 
        
        if self.r.zscore('z_esemenyek', esemeny)==None:
            print('nincs ilyen esemeny')
            return 
        
        if not(self.r.sismember('s_'+email+'_lajkjai', esemeny)):
            self.r.sadd('s_'+email+'_lajkjai', esemeny)
            self.r.zincrby('z_lajkok', esemeny,1)
            
    #13. az események listája a like darabszámok szerint csökkenően rendezve
    def esemeny_lista_lajkkal(self):
        print(self.r.zrevrange('z_lajkok', 0, -1, withscores=True))
    
    #14. a vendég által like-olt események listája (email)
    def vendeg_lajkjai(self, email):
        print(self.r.smembers('s_'+email+'_lajkjai'))
                
        
        
        
        # -*- coding: windows-1250 -*-
from CFOsztaly import COsztaly

rf=COsztaly()

# rf.uj_helyszin('Nagyerdo')
# rf.uj_helyszin('Viztorony')
# rf.uj_helyszin('Stadion')
# rf.uj_helyszin('DEIK sator')

rf.helyszin_lista()

#rf.uj_esemeny('Kassai', '202203171400', '202203171500', 
#              'Tankcsapda', 'Geza', '123')

# rf.uj_esemeny('Nagyerdo', '202203171400', '202203171500', 
#               'Tankcsapda', 'Geza', '123')
# rf.uj_esemeny('Nagyerdo', '202203171530', '202203171700', 
#               'Shakira', 'Anna', '124')
# rf.uj_esemeny('Nagyerdo', '202203171430', '202203171700', 
#               'HoneyBeast', 'Peti', '125')
# rf.uj_esemeny('Viztorony', '202203171430', '202203171520', 
#               'HoneyBeast', 'Peti', '125')

rf.esemeny_lista()
print()

#rf.esemeny_lista_idopont('202203171440')

# rf.uj_jegytipus('felnott', 20000, '202203140000', '202203210000')
# rf.uj_jegytipus('felnott_csutortok', 5000, '202203170000', 
#                 '202203180000')
# rf.uj_jegytipus('felnott_pentek', 5000, '202203180000', 
#                 '202203190000')
# rf.uj_jegytipus('gyerek_pentek', 2000, '202203180000', 
#                 '202203190000')
# rf.uj_jegytipus('gyerek_csutortok', 2000, '202203170000', 
#                 '202203180000')



rf.jegytipus_lista()

# rf.uj_vendeg('Anna', 'a@g.c', '20000101')
# rf.uj_vendeg('Cili', 'c@g.c', '20100101')
# rf.uj_vendeg('Bela', 'b@g.c', '20010101')
# rf.uj_vendeg('Denes', 'd@g.c', '20010101')

rf.vendeg_lista()
print()

# rf.vendeg_jegyet_vesz('c@g.c', 'gyerek_csutortok')
# rf.vendeg_jegyet_vesz('c@g.c', 'gyerek_pentek')
# rf.vendeg_jegyet_vesz('b@g.c', 'felnott_csutortok')
# rf.vendeg_jegyet_vesz('d@g.c', 'felnott')

rf.jegyvasarlasok()
print()

#rf.vendeg_idopont('202203171410')

rf.like('c@g.c', 'h_esemeny_1')
rf.like('c@g.c', 'h_esemeny_x')
rf.like('x@g.c', 'h_esemeny_1')
rf.like('c@g.c', 'h_esemeny_1')
rf.like('c@g.c', 'h_esemeny_2')
rf.like('c@g.c', 'h_esemeny_3')

rf.like('d@g.c', 'h_esemeny_2')


rf.vendeg_lajkjai('c@g.c')

rf.esemeny_lista_lajkkal()






        
        
        
            
        
        
        
        
        
        
        
        