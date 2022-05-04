# -*- coding: windows-1250 -*-
import redis
import uuid
from _datetime import datetime

class UNOsztaly():
        
    def __init__(self):
        redis_host='172.22.223.181'
        redis_port=6379
               
        self.r=redis.Redis(host=redis_host, 
                           port=redis_port, 
                           decode_responses=True)

    #Felhasználó regisztrációja: 
    #Felhasználók tárolása (név, jelszó, email, valódi név, születési dátum) 
    #(ne írjuk felül a létező felhasználói nevet, jelezzük, ha már van)
    def uj_felh(self, nev, jelszo):
        if self.r.hexists('felhasznalok', nev):
            print('foglalt nev')
            return 
        self.r.hset('felhasznalok', nev, jelszo)
        
    def felhasznalo_lista(self):
        print(self.r.hkeys('felhasznalok'))
        
    def elfelejtett_jelszo(self, nev):
        print(self.r.hget('felhasznalok', nev))

    #A felhasználó bejelentkezik 
    #Token generálás (kódolt karaktersorozat, melyet a rendszer autentitikációra használ) 
    #felhasználói név és token tárolása (egy felhasználónak lehet több tokenje)
    def bejelentkezes(self, nev, jelszo):
        if self.r.hget('felhasznalok', nev)!=jelszo:
            print('hibas jelszo')
            return 
        
        tok=self.generate_token()
        
        self.r.hset('tokenek', tok, nev)
        self.kattint(tok)
        return tok
        
    def generate_token(self):
        return str(uuid.uuid4())
    
    def erv_tok(self, tok):
        return self.r.hexists('tokenek', tok)
    
    def token_lista(self):
        print(self.r.hkeys('tokenek'))
        
    def kijelentkezik(self, tok):
        self.r.hdel('tokenek', tok)
        
    def utasitas(self, tok, ut):
        felh=self.r.hget('tokenek', tok)
        if felh!=None:
            self.r.lrem(felh+'_utasitasai', ut, 5)
            self.r.lpush(felh+'_utasitasai', ut)
            self.r.ltrim(felh+'_utasitasai', 0, 4)
            self.kattint(tok)
            
    def utasitas_lista(self, tok):
        felh=self.r.hget('tokenek', tok)
        if felh!=None:
            print(self.r.lrange(felh+'_utasitasai', 0, -1))
            self.kattint(tok)
            
    def kattint(self, tok):
        if self.erv_tok(tok):
            ido=datetime.now().strftime("%Y%m%d%H%M%S") 
            self.r.zadd('aktiv_tokenek', tok, ido)
            
    def ut_ajanl(self, tok, kb):
        felh=self.r.hget('tokenek', tok)
        if felh!=None:
            for i in self.r.lrange(felh+'_utasitasai', 0, -1):
                if kb[0]==i[0]:
                    print(i)
            
            
#TOKEN TOKEN TOKEN TOKEN TOKEN TOKEN TOKEN 
import redis
from _datetime import datetime
from time import sleep
from datetime import timedelta

redis_host='172.22.223.200'
redis_port=6379
               
r=redis.Redis(host=redis_host, port=redis_port,
              decode_responses=True)

while(True):
    sleep(10)
    ido=(datetime.now()-timedelta(minutes=1)).strftime("%Y%m%d%H%M%S")
    
    for i in r.zrangebyscore('aktiv_tokenek', 0, ido, 
                             withscores=False):
        r.hdel('tokenek', i)
        r.zrem('aktiv_tokenek', i)
#TOKEN TOKEN TOKEN TOKEN TOKEN TOKEN TOKEN        ,



#TESZTELES TESZTELES TESZTELES TESZTELES TESZTELES TESZTELES        
from UNOsztaly import UNOsztaly


rf=UNOsztaly()

# rf.uj_felh('anna', 'anna')
# rf.uj_felh('anna', 'geza')
# rf.uj_felh('bela', 'bela')
# rf.uj_felh('cili', 'cili')

rf.felhasznalo_lista()

tok_a1=rf.bejelentkezes('anna', 'anna')
tok_a2=rf.bejelentkezes('anna', 'anna')
# rf.bejelentkezes('anna', 'geza')
# rf.bejelentkezes('gabor', 'geza')
#tok_b=rf.bejelentkezes('bela', 'bela')

rf.token_lista()
#print(rf.erv_tok(tok_b))
#print(rf.erv_tok('abc'))

rf.utasitas(tok_a1, 'alma')
rf.utasitas(tok_a2, 'dio')
rf.utasitas(tok_a1, 'elefant')
rf.utasitas(tok_a2, 'alma')
rf.utasitas(tok_a2, 'eper')
rf.utasitas(tok_a1, 'elefant')
rf.utasitas(tok_a1, 'alma')
rf.utasitas(tok_a1, 'dio')
rf.utasitas(tok_a1, 'elefant')
rf.utasitas(tok_a1, 'malna')

rf.utasitas_lista(tok_a1)

rf.ut_ajanl(tok_a1, 'e')

#
# rf.utasitas(tok_b, 'delfin')
# rf.utasitas(tok_b, 'balna')
# rf.utasitas(tok_b, 'bigyo')
# rf.utasitas(tok_b, 'banan')
# rf.utasitas(tok_b, 'alma')
# rf.utasitas(tok_b, 'eper')

# rf.utasitas_lista(tok_a1)
# rf.utasitas_lista(tok_a2)
# rf.utasitas_lista(tok_b)
#
#
# rf.kijelentkezik(tok_b)
# rf.kijelentkezik(tok_a1)
# rf.kijelentkezik(tok_a2)

rf.token_lista()      
        
            
        
    