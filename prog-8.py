import math
import pygame
import sys

# Fonctions

def dessiner_pointilles_h(surface, couleur, y):
    n = dimensions_fenetre[0] // (longueur_pointille * 2)

    for i in range(n + 1):
        x1 = int((i - 0.25) * longueur_pointille * 2)
        x2 = x1 + longueur_pointille
        pygame.draw.line(surface, couleur, (x1, y), (x2, y))

    return

def dessiner_pointilles_v(surface, couleur, x):
    n = dimensions_fenetre[1] // (longueur_pointille * 2)

    for i in range(n + 1):
        y1 = (i - 0.25) * longueur_pointille * 2
        y2 = y1 + longueur_pointille
        pygame.draw.line(surface, couleur, (x, y1), (x, y2))

    return

def afficher_grille():
    yc = dimensions_fenetre[1] // 2
    nh = yc // taille_grille

    for i in range(1, nh + 1):
        dessiner_pointilles_h(fenetre, GRIS, yc + i * taille_grille)
        dessiner_pointilles_h(fenetre, GRIS, yc - i * taille_grille) 

    pygame.draw.line(fenetre, GRIS, (0, yc), (dimensions_fenetre[0], yc))

    nv = dimensions_fenetre[0] // taille_grille
    for i in range(0, nv + 1):
        dessiner_pointilles_v(fenetre, GRIS, i * taille_grille)
    
    return

def generer_signaux(delta_t):
    PERIODE_2 = 0.004
    R = 1000 #ohm
    C = 470*1e-9

    AMPL_1 = 5
    
    global signaux_initialises, a1, tension_condesateur
    if not signaux_initialises:
        a1 = 0
        tension_condesateur = 0
        signaux_initialises = True
        return (0, 0, 0, 0)

    a1 = math.fmod(a1 + delta_t * 2 * math.pi / PERIODE_2, 2 * math.pi)
    V1 = AMPL_1 * math.cos(a1)
    I = (V1 - tension_condesateur)/R
    tension_condesateur +=  I*delta_t/C
    P = tension_condesateur*I
    

    return (V1, tension_condesateur, I, P)

def acquisition(t):
    global acquisition_initialisee, t_signaux_prec

    if acquisition_initialisee:
        dt = t - t_signaux_prec
        if dt <= 0:
            print("erreur de timing")
            sys.exit()
            
        while dt > t_echantillons:
            generer_signaux(t_echantillons)
            dt -= t_echantillons

        s = generer_signaux(dt)    
    else:
        s = (0, 0, 0, 0)
        acquisition_initialisee = True
        
    t_signaux_prec = t
    
    return s

def afficher_signal(x, v, couleur, gain):
    y = dimensions_fenetre[1] // 2 - v * gain
    pygame.draw.line(fenetre, couleur, (x, y - 5), (x, y + 5))
    return

def afficher_trame(temps_maintenant):
    signaux_prec = acquisition(temps_maintenant)
    
    for x in range(dimensions_fenetre[0]):
        temps_maintenant += t_echantillons
        signaux = acquisition(temps_maintenant)

        if (signaux[0] >= seuil_trigger and
            signaux_prec[0] < seuil_trigger):
            break

        signaux_prec = signaux

    for x in range(dimensions_fenetre[0]):
        temps_maintenant += t_echantillons
        signaux = acquisition(temps_maintenant)
        for i in range(4):
            afficher_signal(x, signaux[i], couleur_signaux[i],
                            gain_signaux[i])
    return

def afficher_trigger():
    y =  dimensions_fenetre[1] // 2 - seuil_trigger * gain_signaux[0]
    pygame.draw.line(fenetre, ROUGE, (0, y), (20, y), 5)
    return

# Constantes

BLEUCLAIR = (127, 191, 255)
CYAN = (0, 255, 255)
GRIS = (127, 127, 127)
JAUNE = (255, 255, 0)
MAGENTA = (255, 0, 255)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)

# Paramètres

dimensions_fenetre = (800, 600)  # en pixels
images_par_seconde = 25

taille_grille = 100
longueur_pointille = 10

t_trame = 0.010
t_echantillons = t_trame / dimensions_fenetre[0]

seuil_trigger = 5
seuil_trigger_delta = 0.2

couleur_signaux = [ JAUNE, CYAN, MAGENTA, VERT ]
gain_signaux = [ 20, 20, 20000, 20000 ]
                            
# Initialisation

pygame.init()

fenetre = pygame.display.set_mode(dimensions_fenetre)
pygame.display.set_caption("Programme 8 & 9")

horloge = pygame.time.Clock()
couleur_fond = BLEUCLAIR

pygame.key.set_repeat(10, 10)

acquisition_initialisee = False
signaux_initialises = False

# Dessin

while True:
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif evenement.type == pygame.KEYDOWN:
            if evenement.key == pygame.K_UP:
                seuil_trigger += seuil_trigger_delta
            elif evenement.key == pygame.K_DOWN:
                seuil_trigger -= seuil_trigger_delta
                
    temps_maintenant = pygame.time.get_ticks() / 1000

    fenetre.fill(couleur_fond)
    afficher_trame(temps_maintenant)
    afficher_trigger()
    afficher_grille()        
    pygame.display.flip()
    horloge.tick(images_par_seconde)
