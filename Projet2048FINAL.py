import pygame
from colorsys import hsv_to_rgb
from pygame.locals import *
from random import choice, randint
from ast import literal_eval
import pygame_textinput
class block(pygame.sprite.Sprite):
    direction = ""
    blocConfig = ""
    oldConfigA = ""
    oldConfigB = ""
    def __init__(self, pos, level):
        super().__init__()
        self.posX, self.posY = pos[0], pos[1]
        self.rect = pygame.rect.Rect((tailleCarre*pos[0]+(pos[0]+1)*ecart,tailleCarre*pos[1]+(pos[1]+1)*ecart,tailleCarre,tailleCarre))
        self.color = color(level)
        self.rect_interieur = pygame.draw.rect(rect_principale, color(level), self.rect)
        self.level = addBlocks(level, self)
        self.graphicLevel = str(2**self.level)

    def showLevel(self):
        self.label = police.render(self.graphicLevel, 1, (255-self.color[0],255-self.color[1],255-self.color[2]))
        rect_principale.blit(self.label, (self.rect[0]+((self.rect[2]-ecart)/2)-5*len(self.graphicLevel), self.rect[1]+((self.rect[3]-2*ecart)/2)))
    def move(self):
        if block.direction == "gauche":
            if not self.posX <= 0:
                self.posX -= 1
        elif block.direction == "droite":
            if not self.posX >= nombre_bloc[0]-1:
                  self.posX += 1
        elif block.direction == "bas":
            if not self.posY >= nombre_bloc[1]-1:
                self.posY += 1
        elif block.direction == "haut":
            if not self.posY <= 0:
                self.posY -= 1



    def updatePos(self):
        self.rect.x = tailleCarre*self.posX+(self.posX+1)*ecart
        self.rect.y = tailleCarre*self.posY+(self.posY+1)*ecart
    def update(self):
        self.oldPos = (self.posX, self.posY)
        if block.direction != "":
            if not collisionGroupe(self, blocks[self.level]):
                self.move()
                self.updatePos()
            if collisionGroupe(self, blocks[self.level]):
                self.posX, self.posY = self.oldPos[0], self.oldPos[1]
        self.updatePos()
        collisionBloc(self)
        self.rect_interieur = pygame.draw.rect(rect_principale, color(self.level), self.rect)
        self.showLevel()
def color(niveau): #Recuperation d'une couleur en RGB en fonction du niveau
    return(tuple(round(i * 255) for i in hsv_to_rgb((10/345)*niveau,1,1))) #Utilise la teinte/saturation/lumière pour changer la couleur puis convertie celle ci en RGB

def addBlocks(niv, bloc): #Ajout du bloc dans le dictionnaire de bloc
    try: #Tente d'ajouter le bloc à son groupe
        blocks[niv].add(bloc)
    except: #S'il n'y arrive pas, créer son groupe
        blocks[niv] = pygame.sprite.Group()
        blocks[niv].add(bloc)
    return niv
def collisionBloc(sprite): #Test de la collision entre blocs de même niveau en prenant en paramètre un bloc qui testera la collision entre d'autre bloc
    global score
    level = sprite.level
    for bloc in [i for i in blocks[sprite.level] if i != sprite]: #itère dans les groupes de bloc
        if pygame.sprite.collide_rect(sprite, bloc): #Verifie une collision entre un bloc de la liste et lui-même
            #S'il y a une collision
            score += int(sprite.graphicLevel)*2 #Incrémenter le score
            #Supprimer les blocs où il y a une collision
            blocks[sprite.level].remove(sprite)
            blocks[sprite.level].remove(bloc)
            #Faire apparaitre un bloc à l'endroit de la collision
            block((sprite.posX, sprite.posY), level+1)

def collisionGroupe(sprite, groupe): #Test de la collision entre plusieurs blocs de niveau (groupe) differant
    for groupBloc in [groupe[1] for groupe in blocks.items() if groupe[0] != sprite.level]: #itère dans les groupes sauf lui-même (son propre groupe)
        if pygame.sprite.groupcollide(blocks[sprite.level], groupBloc, False, False): #Vérifie s'il y a une collision entre lui et d'autre groupe de bloc
            return True #Retourne vrai
    #Retourne faux s'il n'y a pas de collision
    return False


def getPos(): #Recuperation de la position de tous les blocs
    positions = []
    for blocGroupe in blocks.values(): #Itère les groupes
        for bloc in blocGroupe: #Itère les blocs dans le groupe
            positions.append((bloc.posX,bloc.posY)) #Ajoute la position du bloc dans une iste
    return positions

def getFree(): #Recuperation de la position des cases vides
    positionsTotal = set() #Crée un ensemble vide
    positionsOccupe = set(getPos()) #Crée un ensemble comportant les positions de blocs
    #Ajoute à l'ensemble vide 'positionTotal' la grille de position du nombre de blocs
    for y in range(0,int(nombre_bloc[1])):
        for x in range(0,int(nombre_bloc[0])):
            positionsTotal.add((x,y))
    return list(positionsTotal - positionsOccupe) #Soustrait l'ensemble "positionTotal" par l'ensemble "positionsOccupe" pour avoir la liste des positions libres

def spawnRandom(): #Fais apparaitre un bloc au hasard

    if block.oldConfigB != getPos(): #Verifie si la précedente configuration position de bloc = la configuration position de bloc actuelle
        try: #Essaie de faire apparaitre un bloc
            block(choice(getFree()),choice([1,2,1]))
        except:
            pass

def saveConfig(): #Sauvegarde de la configuration du jeu (position des blocs, niveau des blocs, score actuel)
    global score
    blocConfig = []
    for blocGroupe in blocks.values():
        for bloc in blocGroupe:
            blocConfig.append([(bloc.posX, bloc.posY), bloc.level, score])
    return blocConfig

def saveFile(blocConfig): #Créer un fichier de sauvegarde
    fichier = open("2048userconfig.txt", "w")
    fichier.write(str(blocConfig))
    fichier.close()

def restoreConfig(blocConfig): #Restaure une sauvegarde
    global blocks, score

    block.oldConfigB = ""
    blocks = {}
    for bloc in blocConfig:
        block((bloc[0][0], bloc[0][1]), bloc[1])
        score = bloc[2]

def gameOver(): #Verifie si la partie est terminé en verifiant s'il est possible de faire un mouvement
    config = saveConfig()
    for direction in ["gauche", "droite", "haut", "bas"]:
        block.direction = direction
        for bloc in list(blocks.values()):
            bloc.update()
        if config != saveConfig():
            restoreConfig(config)
            block.direction = ""
            return False
    return True
def initBlankArea(cancel, save, score): #Affiche l'ecran principal
    global fin, saveBlit, cancelBlit, restoreBlit
    fenetre.fill((0,0,0))
    rect_principale.fill((190,176,163))

    for y in range(0,int(nombre_bloc[1])): #Affiche l'écran de la grille
        for x in range(0,int(nombre_bloc[0])):
            rect_interieur = pygame.draw.rect(rect_principale, (204,194,180), (tailleCarre*x+(x+1)*ecart,tailleCarre*y+(y+1)*ecart,tailleCarre,tailleCarre))

    if not fin: #Affiche les icones de: sauvegarder/restaurer/annuler/fps
        saveBlit = fenetre.blit(save, (startX,startY+carreLH[1]))
        cancelBlit = fenetre.blit(cancel, (startX+save.get_width(), startY+carreLH[1]))
        restoreBlit = fenetre.blit(restore, (startX+save.get_width()+cancel.get_width(),startY+carreLH[1]))
        fenetre.blit(fps.get_surface(), (int(2.5*25),0))
        fenetre.blit(fpsText, (0,1))
    #Affiche le score
    scoreText = police.render("Score: "+score, 1, (255,204,0))
    fenetre.blit(scoreText, (fenTaille[0]-int(25*((len(score)+7)/2+0.5)),1))

def createRectText(surface, text, rectColor, textColor, rect, contour = 3, police = 25): #Permet la creation d'un rectangle avec un text centré à l'interieur + animation quand on defile sur
    police = pygame.font.SysFont("arial", police, True)
    pos = (rect[0], rect[1])
    taille = (rect[2], rect[3])
    policeX, policeY = police.size(text)
    surfaceRectangle = pygame.Surface(taille)
    rect = pygame.draw.rect(surfaceRectangle, rectColor, ((0,0), taille))

    textRect = pygame.rect.Rect((pos, taille))
    surface.blit(surfaceRectangle, pos)
    if textRect.collidepoint(pygame.mouse.get_pos()):

        pygame.draw.rect(surfaceRectangle,(255-rectColor[0],255-rectColor[1],255-rectColor[2]),((0,0), taille))
        pygame.draw.rect(surfaceRectangle,(0,0,0),((0,0), taille),contour)
        if textColor == (0,0,0):
            textColor = (255,255,255)
    texte = police.render(text, 1, textColor)
    surfaceRectangle.blit(texte, (taille[0]//2-policeX//2, taille[1]//2-policeY//2))
    surface.blit(surfaceRectangle, pos)
    return textRect

def finishWindow(events): #Affiche l'écran de fin
    global blocks, score, finish, fin
    rect_fin = pygame.Surface((350,100))
    rect_fin.fill((46, 204, 113))
    scoreFin = police.render("Score: "+ str(score), 1 ,(0,0,0))
    rect_fin.blit(scoreFin, (0,0))
    rectangle = createRectText(rect_fin, "Rejouer", (155,155,155),(0,0,0),(0,30,100,50))
    for event in events:
        if event.type == MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if rectangle.collidepoint(pos):
                block.oldConfigB = ""
                blocks = {}
                score=0
                rect_principale.set_alpha(1000)
                fin = False
    fenetre.blit(rect_fin,(0,0))
def arc_en_ciel():
#création d'une fonction qui crée une couleur aléatoirement
    couleur_1 = randint(0,255)
    couleur_2 = randint(0,255)
    couleur_3 = randint(0,255)
    return(couleur_1,couleur_2,couleur_3)
def loadGameRessource(n): #Charge les ressources necessaire au lancement de la partie
    global fenTaille, carreLH, startX, startY, tailleCarre, cancel, save, restore, rect_principale, ecart, cancelRect, saveRect, restoreRect, nombre_bloc, moyenne
    nombre_bloc = (int(n[0]), int(n[1]))
    moyenne = (nombre_bloc[0]+nombre_bloc[1])//2
    fenTaille = (int(75*nombre_bloc[0]),int(125*nombre_bloc[1])) #Taille fenetre
    carreLH = (70*nombre_bloc[0],70*nombre_bloc[1]) #Taille grille
    startX, startY = 10,100 #Position de la grille en haut à droite
    tailleCarre, ecart = int((70*moyenne-10)/moyenne)-10,10 #Taille d'un bloc, ecart entre 2 bloc
    fenetre = pygame.display.set_mode(fenTaille)


    """
    CHARGEMENT DES RESSOURCES
    """
    #Chargement image
    cancel = pygame.image.load("cancel.png").convert_alpha()
    cancel = pygame.transform.scale(cancel, (15*moyenne, 15*moyenne))

    save = pygame.image.load("save.png").convert_alpha()
    save = pygame.transform.scale(save, (15*moyenne, 15*moyenne))

    restore = pygame.image.load("restore.png").convert_alpha()
    restore = pygame.transform.scale(restore, (15*moyenne, 15*moyenne))

    rect_principale = pygame.Surface(carreLH)
    rect_principale.fill((190,176,163))

    block((0,0),1)
    block.oldConfigB = getPos()

pygame.display.set_caption('2048')
fenetre=pygame.display.set_mode((300,500))
listeNiveau = []
ecran_actuel = "principal"
#création de l'accueil
fenetre.fill((250,248,239))

#Chargement des images
logo=pygame.image.load('capture.png').convert_alpha()
logo = pygame.transform.scale(logo, (120, 120))
fleches=pygame.image.load('fleches.png').convert_alpha()
fleches=pygame.transform.scale(fleches,(30,30))
croix=pygame.image.load('croix.png').convert_alpha()
croix=pygame.transform.scale(croix,(20,20))


# et préparation de textes et polices
font=pygame.font.SysFont("arial", 25)
font2=pygame.font.SysFont("arial", 30)
font3=pygame.font.SysFont("arial", 15)
#CHARGEMENT DE L'AFFICHAGE DU TEXTE DE L'ECRAN PRINCIPAL


#CHARGEMENT DE L'AFFICHAGE DES REGLES
text_regle1=font2.render('2048',1,(0,0,0))
text_niveaux=font.render('Choisir le niveau',False,(0,0,0))
text_fleches=font3.render('Pour déplacer les tuiles',False,(0,0,0))


#on définit des variables
continuer=True
affichageniveaux = False
affichagedesregles = False
compteur=0
clock=pygame.time.Clock()
couleur=arc_en_ciel()



pygame.init()

pygame.display.set_caption('2048')
icon = pygame.image.load('2048.png')
pygame.display.set_icon(icon)
blocks = {}

#Creation de la fenetre en fonction de la grille demandé
fin = False

police = pygame.font.SysFont("arial", 25, True)


#Chargement fps
fps = pygame_textinput.TextInput(initial_string = "", text_color = (255,204,0), font_family = "arial", font_size = 25)
fps.set_text("60")
fpsText = police.render("FPS:", 1, (255,204,0))


#Creation de la grille dans la fenetre



score = 0


#initBlankArea(cancel, save, str(score)) #58:((carreLH[0]-10)/nb_bloc)-10


pygame.display.update()
continuer = 1
fpsVal = 60
clock = pygame.time.Clock()
game = False
while continuer:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            continuer = 0
    if game:
        if fps.update(events):
            fpsVal = fps.get_text()
            if fpsVal == "" or int(fpsVal) <= 0:
                fps.set_text("1")
                fpsVal = 1
        clock.tick(int(fpsVal))
        for event in events:
            if event.type == MOUSEBUTTONUP and not fin:
                mouse = pygame.mouse.get_pos()
                if cancelBlit.collidepoint(mouse):
                    restoreConfig(block.blocConfig)
                if saveBlit.collidepoint(mouse):
                    saveFile(saveConfig())
                if restoreBlit.collidepoint(mouse):
                    fichier = open("2048userconfig.txt", "r")
                    config = fichier.read()
                    fichier.close()
                    restoreConfig(literal_eval(config))
            if event.type == KEYDOWN:
                if block.oldConfigA == getPos(): #Vérifie que plus aucune tuile ne bouge
                    block.oldConfigB = getPos() #Recupere la position des tuiles avant un déplacement
                    if event.key == K_LEFT:
                        block.blocConfig = saveConfig()
                        block.direction = "gauche"
                    if event.key == K_RIGHT:
                        block.blocConfig = saveConfig()
                        block.direction = "droite"
                    if event.key == K_DOWN:
                        block.blocConfig = saveConfig()
                        block.direction = "bas"
                    if event.key == K_UP:
                        block.blocConfig = saveConfig()
                        block.direction = "haut"




        initBlankArea(cancel, save, str(score))
        block.oldConfigA = getPos() #Récupère la position des tuiles
        for bloc in list(blocks.values()):
            bloc.update()
        if block.direction != "" and block.oldConfigA == getPos(): #Vérifie que plus aucune tuile ne bouge
            block.direction = ""
            spawnRandom()
        fenetre.blit(rect_principale,(startX, startY))
        if block.oldConfigB == getPos():
            if gameOver():
                fin = True
                rect_principale.set_alpha(100)
                finishWindow(events)
    else:
        fenetre.fill((250,248,239))
        fenetre.blit(logo,(96,20))


        pygame.draw.rect(fenetre,couleur,(0,0,300,500),5)

        text=font.render("by David & Tergel", 1, couleur)
        fenetre.blit(text,(10,450))
        compteur+=1     #création d'un compteur afin que le contour change de couleurs automatiquement
        if compteur==10:
            couleur=arc_en_ciel()
            pygame.draw.rect(fenetre,couleur,(0,0,300,500),5)
            text=font.render("by David & Tergel", 1, couleur)
            fenetre.blit(text,(10,450))
            compteur=0

        curseur=pygame.mouse.get_pos()
        #création des boutons d'événements
        rect_jouer = createRectText(fenetre, "Jouer", (236,193,47),(0,0,0),(100,165,110,70))
        rect_regle = createRectText(fenetre, "Règles", (236,193,47),(0,0,0),(100,295,110,70))

        for event in events:
            if event.type == QUIT:
                continuer = False

            if event.type==MOUSEBUTTONUP:
                    if ecran_actuel=='principal':
                        if rect_jouer.collidepoint(curseur) :
                            affichageniveaux=True
                            ecran_actuel = "niveau"

                        if rect_regle.collidepoint(curseur):
                            affichagedesregles = True
                            ecran_actuel = "regle"

                    elif ecran_actuel == "regle":
                        if boutonOK.collidepoint(curseur):
                            ecran_actuel = "principal"
                            affichagedesregles = False

                    elif ecran_actuel == "niveau":
                        if listeNiveau[0].collidepoint(curseur):
                            loadGameRessource((3,3))
                            game = True
                        elif listeNiveau[1].collidepoint(curseur):
                            loadGameRessource((4,4))
                            game = True
                        elif listeNiveau[2].collidepoint(curseur):
                            loadGameRessource((5,5))
                            game = True
                        elif listeNiveau[3].collidepoint(curseur):
                            loadGameRessource((6,6))
                            game = True
                        elif listeNiveau[4].collidepoint(curseur):
                            fichier = open("2048personnalise.txt")
                            loadGameRessource(fichier.read().split("x"))
                            game = True
                            fichier.close()
                        elif croixRect.collidepoint(curseur) :
                            affichageniveaux=False
                            ecran_actuel = "principal"


        if affichageniveaux == True:        #si on clique sur le bouton 'Jouer'
            pygame.draw.rect(fenetre,(0,0,0),(55,100,200,300),5)
            pygame.draw.rect(fenetre,(255,255,255),(55,100,200,300))

            for i, niveau in enumerate(range(3,7)):
                niveau = createRectText(fenetre, '{}x{}'.format(niveau,niveau), (255,255,255),(0,0,0),(105,150+50*i,100,30), 1)
                listeNiveau.append(niveau)
            listeNiveau.append(createRectText(fenetre, 'Personnalisé', (255,255,255),(0,0,0),(105,150+50*4,100,20), 1, 15))

            fenetre.blit(text_niveaux,(65,105))
            croixRect = fenetre.blit(croix,(230,100))
        if affichagedesregles == True:      #si on clique sur le bouton 'règles'
            pygame.draw.rect(fenetre,(0,0,0),(55,100,200,300),5)
            pygame.draw.rect(fenetre,(255,255,255),(55,100,200,300))
            fenetre.blit(text_regle1,(122,105))
            for i, texte in enumerate(["Le but est de faire glisser des ", 'tuiles sur une grille pour les', 'combiner entre eux.',"L'objectif est d'atteindre la tuile", 'portant le nombre 2048.']):
                fenetre.blit(font3.render(texte,False,(0,0,0)), (59,150+(15*i)))

            fenetre.blit(fleches,(58,240))
            fenetre.blit(text_fleches,(102,253))
            boutonOK = createRectText(fenetre, "OK", (236,193,47),(0,0,0),(110,350,90,40))





        clock.tick(20)

    pygame.display.update()
pygame.quit()