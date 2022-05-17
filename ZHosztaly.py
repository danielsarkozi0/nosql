# -*- coding: windows-1250 -*-
import redis

class Kosar():
    def __init__(self):
        redis_host='192.168.0.103'
        redis_port=6379
               
        self.r=redis.Redis(host=redis_host, 
                           port=redis_port, 
                           decode_responses=True)

    def uj_jatekos(self, nev, szul_dat):
        azon = self.r.incr('azon')
        jatekos_azon = "jatekos_"+str(azon)
        di = dict()
        di[jatekos_azon] = 0
        self.r.zadd("jatekosok",di)
        self.r.hset(jatekos_azon, nev, szul_dat)

        return jatekos_azon

    def jatekosok_listaja(self):
        for i in self.r.zrange("jatekosok",0,-1,withscores=False):
            print(self.r.hgetall(i))

    def jatekos_csapathoz_igazol(self,jatekos_azon, csapatnev):
        di = dict()
        di[csapatnev] = 0
        self.r.zadd("csapatok",di)
        self.r.sadd(csapatnev,jatekos_azon)

    def jatekos_kilep(self,csapatnev, jatekos_azon):
        self.r.srem(csapatnev,jatekos_azon)
        if len(self.r.smembers(csapatnev)) < 1:
            print(f"{1} megszunt",csapatnev)
            self.r.delete(csapatnev)
            self.r.zrem("csapatok",csapatnev)
    
    def csapat_jatekosai_lista(self,csapatnev):
        for i in self.r.smembers(csapatnev):
            print(self.r.hgetall(i))
    
    def csapatok_listaja(self):
        print(self.r.zrange("csapatok",0,-1,withscores=False))

    def meccs_hirdetes(self,datum,helyszin,Acsapat,Bcsapat):
        azon = self.r.incr("m_azon")
        meccs_azon = "meccs_"+str(azon)
        self.r.sadd("meccsek",meccs_azon)
        self.r.hmset(meccs_azon,
        {
            "datum":datum,
            "helyszin":helyszin,
            "Acsapat":Acsapat,
            "Bcsapat":Bcsapat
        }
        )

        return meccs_azon

    def meccs_lista(self):
        for i in self.r.smembers("meccsek"):
            print(self.r.hgetall(i))

    def dobott_pont_regisztral(self,meccs_azon,jatekos_azon,pont):
        self.r.zincrby(meccs_azon+"_pontjai",pont,jatekos_azon)
        self.r.zincrby("jatekosok",pont,jatekos_azon)

        Acsapat = self.r.hget(meccs_azon,"Acsapat")
        Bcsapat = self.r.hget(meccs_azon,"Bcsapat")

        if jatekos_azon in self.r.smembers(Acsapat):
            self.r.zincrby("Csapatok pontjai",pont,Acsapat)
        if jatekos_azon in self.r.smembers(Bcsapat):
            self.r.zincrby("csapatok_pontjai",pont,Bcsapat)
            

    def jatekos_lekerdezes_meccs_pontjai(self,meccs_azon):
        print(self.r.zrange(meccs_azon+"_pontjai",0,-1,desc=True,withscores=True))

    def jatekosok_pontjai_osszesen(self):
        print(self.r.zrange("jatekosok",0,-1,desc=True,withscores=True))

    def csapat_jatekosai_db(self,csapatnev):
        print(len(self.r.smembers(csapatnev)))

    def ki_gyozott(self,meccs_azon):
        Acsapat = self.r.hget(meccs_azon,"Acsapat")
        Bcsapat = self.r.hget(meccs_azon,"Bcsapat")
        Acsapat_pont = 0
        Bcsapat_pont = 0

        for i in self.r.zrange(meccs_azon+"_pontjai",0,-1,withscores=False):
            if i in self.r.smembers(Acsapat):
                Acsapat_pont += self.r.zscore(meccs_azon+"_pontjai",i)
            if i in self.r.smembers(Bcsapat):
                Acsapat_pont += self.r.zscore(meccs_azon+"_pontjai",i)
        if Acsapat_pont > Bcsapat_pont:
            print("{} Nyert".format(Acsapat))
        else:
             print("{} Nyert".format(Bcsapat))

    def csapatok_pont_szerint(self):
        print(self.r.zrange("csapatok_pontjai",0,-1,desc=True,withscores=True))

rf = Kosar()

j1 = rf.uj_jatekos('Tank Aranka',"20010804")
j2 = rf.uj_jatekos('Beviz Elek',"20020224")
j3 = rf.uj_jatekos('Kasza Blanka',"20020324")
j4 = rf.uj_jatekos('Fekete Peti',"20120324")


rf.jatekosok_listaja()

rf.jatekos_csapathoz_igazol(j1,"Deac")
rf.jatekos_csapathoz_igazol(j4,"Deac")
rf.jatekos_csapathoz_igazol(j3,"Spartacus")

rf.csapat_jatekosai_lista("Deac")

#rf.jatekos_kilep("Spartacus",j3)

rf.csapatok_listaja()

m1 = rf.meccs_hirdetes("20220505","Nagyerdei Stadion","Deac","Spartacus")
m2 = rf.meccs_hirdetes("2022050","Stadion utca","Spartacus","Deac")

rf.meccs_lista()

rf.dobott_pont_regisztral(m1,j1,4)
rf.dobott_pont_regisztral(m1,j3,10)
rf.dobott_pont_regisztral(m1,j3,2)
rf.dobott_pont_regisztral(m2,j4,5)
rf.dobott_pont_regisztral(m2,j3,6)

rf.jatekos_lekerdezes_meccs_pontjai(m1)

rf.jatekosok_pontjai_osszesen()

rf.csapatok_pont_szerint()

rf.ki_gyozott(m1)