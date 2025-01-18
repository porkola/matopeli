import pygame
import random
import os

# Piirretään mato: pää on vihreä, muuten valkoinen
def piirra_mato(mato: list):
    for i in range(len(mato)):
        mato_x, mato_y = mato[i]
        vari = (255, 255, 255)
        if i == 0:
            vari = (0, 255, 0)
        pygame.draw.rect(naytto, vari, pygame.Rect(mato_x,mato_y,palaleveys,palaleveys))

def piirra_ruoka(x_ruoka: int, y_ruoka: int):
    """Piirretään punainen ympyrä, jonka vasen yläkulma on annetuissa koordinaateissa"""
    pygame.draw.circle(naytto, (255, 0, 0), (x_ruoka+palaleveys/2, y_ruoka+palaleveys/2), palaleveys/2)


def ruoka_koordinaatit(mato: list) -> tuple:
    """Arvotaan ruokapalalle uudet koordinaatit (vasen yläkulma), jotka eivät ole madon päällä, ja palautetaan tuple."""
    while True:
        x = random.randrange(0, 640-palaleveys, palaleveys)
        y = random.randrange(0, 480-palaleveys, palaleveys)
        if (x,y) not in mato:
            return (x, y)

# liikutetaan matoa askeleen eteenpäin, tarvittaiessa kasvatetaan yhdessä
# head oltava jo liikkuneen pään koordinaatit
def liikuta_matoa(mato: list, head: tuple, kasvaa: bool):
    if kasvaa:
        mato.append(mato[len(mato) -1])
        for i in  range(len(mato) - 2, 0, -1):
            mato[i] = mato[i - 1]

    else:
        if len(mato) > 1:
            for i in  range(len(mato) - 1, 0, -1):
                mato[i] = mato[i - 1]

    mato[0] = head

    
# Tarkistetaan osuuko mato seinään
def osuu_seinaan(x_head: int, y_head: int) -> bool:
    """Palauttaa arvon True, jos mato osuu seinään, muuten False."""
    if x_head < 0 and vasemmalle:
        # vasemmalle = False
        return True
    if x_head > 640 - palaleveys and oikealle:
        # oikealle = False
        return True
    if y_head < 0 and ylos:
        # ylos = False
        return True
    if y_head > 480 - palaleveys and alas:
        # alas = False
        return True
    return False

# tarkistetaan osuuko mato liikkuessa itseensä
# head oltava liikutetetun pään koordinaatit
def osuu_itseen(mato: list, head: tuple):
    """Palauttaa arvon True, jos mato osuu itseensä, muuten False"""
    if head not in mato[1:]:
        return False
    return True

def tallenna_peli(mato: list, x_ruoka: int, y_ruoka: int, pisteet: int, nopeus: int):
    """Tallentaa pelin tiedostoo 'pelitallenne.txt'"""
    with open("pelitallenne.txt", "w") as tiedosto:
        matostr = "mato;"
        for matopala in mato:
            matostr += f"{matopala[0]},{matopala[1]};"
        matostr = matostr[:-1]
        matostr += "\n"
        tiedosto.write(matostr)
        tiedosto.write(f"ruoka;{x_ruoka},{y_ruoka}\n")
        tiedosto.write(f"pisteet;{pisteet}\n")
        tiedosto.write(f"nopeus;{nopeus}")
        
def lataa_peli():
    """Ladataan peli tiedostosta 'pelitallenne.txt'. Paluuarvot: madon koordinaantit listana, x_ruoka, y_ruoka, pisteet, nopeus"""
    mato = []
    x_ruoka, y_ruoka = ruoka_koordinaatit(mato)
    pisteet = 0
    nopeus = 5

    if os.stat("pelitallenne.txt").st_size == 0:
        mato.append((320,240))
    else:
        with open("pelitallenne.txt") as tiedosto:
            for rivi in tiedosto:
                rivi = rivi.replace("\n", "")
                osat = rivi.split(";")
                if osat[0] == "mato":
                    for i in range(1, len(osat)):
                        xy = osat[i].split(",")
                        mato.append((int(xy[0]),int(xy[1])))
                elif osat[0] == "ruoka":
                    xy = osat[1].split(",")
                    x_ruoka = int(xy[0])
                    y_ruoka = int(xy[1])
                elif osat[0] == "pisteet":
                    pisteet = int(osat[1])
                elif osat[0] == "nopeus":
                    nopeus = int(osat[1])

    return mato, x_ruoka, y_ruoka, pisteet, nopeus

# Aloitetaan pelaaminen kysymällä halutaanko aloitaa uusi peli vai latada tallennettu peli
print("TERVETULOA PELAAMAAN MATOPELIÄ!")
print("Uusi peli: valitse 0")
print("Lataa tallennettu peli: valitse 1")
valinta = input("Valinta: ")
uusi_peli = False
if valinta == "0":
    uusi_peli = True

pygame.init()
naytto = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Matopeli")

# matopala = pygame.image.load("square_white.png")
mato = []
x = 320
y = 240

palaleveys = 20 # kaikkien yksittäisten objektien leveys on 20
mato.append((x, y))
    
grow = False

ruoka = pygame.image.load("circle.png")
x_ruoka, y_ruoka = ruoka_koordinaatit(mato)

oikealle = False
vasemmalle = False
ylos = False
alas = False

# Peliä ei käynnistetä ennen kuin madolle on anettu ensimmäinen suunta (tallennettua peliä varten)
game_on = False

game_over = False

pisteet = 0
nopeus = 5


if not uusi_peli:
    mato, x_ruoka, y_ruoka, pisteet, nopeus = lataa_peli()

kello = pygame.time.Clock()

while True:
    for tapahtuma in pygame.event.get():
        if tapahtuma.type == pygame.KEYDOWN and not game_over:
            if tapahtuma.key == pygame.K_LEFT:
                if oikealle:
                    continue
                vasemmalle = True
                oikealle = False
                alas = False
                ylos = False
            if tapahtuma.key == pygame.K_RIGHT:
                if vasemmalle:
                    continue
                oikealle = True
                vasemmalle = False
                alas = False
                ylos = False
            if tapahtuma.key == pygame.K_UP:
                if alas:
                    continue
                ylos = True
                alas = False
                oikealle = False
                vasemmalle = False
            if tapahtuma.key == pygame.K_DOWN:
                if ylos:
                    continue
                alas = True
                ylos = False
                oikealle = False
                vasemmalle = False

        if tapahtuma.type == pygame.QUIT:
            if not game_over:
                print("Tallennetaan peli.")
                tallenna_peli(mato, x_ruoka, y_ruoka, pisteet, nopeus)
            exit()

    if alas or ylos or vasemmalle or oikealle:
        game_on = True
    # Otetaan talteen pään koordinaatit, joita kasvatetaan muuttamatta vielä matoa
    x_head, y_head = mato[0]

    # Liikutetaan matoa pyydettyyn suuntaa yhden yksikön (palaleveys) verran
    if oikealle:
        x_head += palaleveys
    if vasemmalle:
        x_head -= palaleveys
    if ylos:
        y_head -= palaleveys
    if alas:
        y_head += palaleveys

    # liikutetaan ja tarvittaessa kasvatetaan matoa
    if game_on:
        liikuta_matoa(mato, (x_head, y_head), grow)
    # mato kasvoi (jos oli aihetta), joten ei kasvateta uudelleen ennen seuraavaa ruokaa
    grow = False

    # Tarkistetaan osuuko mato seinään tai itseensä, jolloin peli loppuu
    if osuu_seinaan(x_head, y_head) or osuu_itseen(mato, (x_head, y_head)):
        game_over = True
        
    # Jos peli loppui, mato ei liiku enää
    if game_over:
        oikealle = False
        vasemmalle = False
        ylos = False
        alas = False

    # Tarkistetaan osuiko madon pää ruokaan, jolloin pituus ja nopeus kasvavat
    if x_head == x_ruoka and y_head == y_ruoka:
        pisteet += 1
        x_ruoka, y_ruoka = ruoka_koordinaatit(mato)
        grow = True
        if nopeus > 20:
            nopeus += 1
        else:
            nopeus += 2

    # piirretään näyttö, sekä sinne mato ja ruoka
    naytto.fill((0, 0, 0))
    # for i in range(len(mato)):
    #     naytto.blit(matopala, mato[i])
    piirra_mato(mato)
    piirra_ruoka(x_ruoka, y_ruoka)
    fontti = pygame.font.SysFont("Arial", 20)
    teksti_pisteet = fontti.render(f"Score: {pisteet}", True, (255, 0, 0))
    naytto.blit(teksti_pisteet, ((640 - teksti_pisteet.get_width()) - 10, 10))

    if game_over:
        fontti = pygame.font.SysFont("Arial", 50)
        teksti = fontti.render("Game Over!", True, (255, 0, 0))
        naytto.blit(teksti, ((640 - teksti.get_width()) / 2, 100))


    pygame.display.flip()

    kello.tick(nopeus)
