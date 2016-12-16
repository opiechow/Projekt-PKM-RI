# coding=utf-8
from PyQt4 import QtCore
# Zachowanie pociągu:
# -pola: obecna strefa, następna strefa, trasa, indeks strefy na trasie, lista zmian kierunków ruchu, kierunek ruchu
# -przy wjeździe:
# 	+ aktualizacja obecnej strefy
# 	+ aktualizacja kolejnej strefy
# 	+ sprawdzić kolejny odcinek trasy (pole klasy pociągu) i ustawić zwrotnice tak, aby przejechać
# 	+ sprawdzenie, na jak długo mam się zatrzymać w tej strefie (jeśli 0 to jadę dalej, inaczej stop)
# 	+ sprawdzenie zajętości następnej strefy
# 	+ sprawdzenie obecnej strefy pod kątem zajętości sąsiednich stref
#
# ZMIANY KIERUNKU SĄ WYKONYWANE W FUNKCJI WYWOŁUJĄCEJ POSTÓJ, WIĘC ŻEBY ZMIENIĆ KIERUNEK NALEŻY SIĘ ZATRZYMAĆ W DANEJ STREFIE
#
# Strefa:
# -klasa, pola: nr_strefy, lista sąsiednich stref, do których trzeba ustawić zwrotnice i zwrotnic do przestawienia, lista stref do sprawdzenia pod kątem zajętości, wjedź powoli (jeśli ta strefa jest strefą następną, to ustaw prędkość na minimalną)
#
# PRZY SPRAWDZANIU ZAJĘTOŚCI W STREFIE, JEŚI JEST ZAJĘTA, TO SIĘ ZATRZYMUJEMY. NATOMIAST KIEDY SIĘ ZWOLNI CZEKAMY LOSOWĄ ILOŚĆ CZASU OD 1 SEKUNDY DO 3 SEKUND, SPRAWDZAMY ZAJĘTOŚĆ TORU - JEŚLI JEST WOLNY TO USTAWIAMY ZWROTNICE I JEDZIEMY
#
# Pole trasa:
# -lista list
# -pojedynczy element listy list: [numer strefy, czas postoju]
#
# Trasy konkretnych pociągów:
#
# Pierwszy (zaczyna z Wrzeszcza) wrzeszcz - stzyża - kiełpinek i z powrotem, zmieniając tor
# [[23,0],[30,0],[24,0],[26,0],[20,0],[8,0],[9,0],[12,15],[13,0],[14,0],[15,0],[16,15],[17,0],[18,0],[29,0],[19,15],[22,0],[21,0],[26,0],[25,0],[30,0],[23,15]]
#
# [[23,'p'],[16,'t']]
#
# Drugi (zaczyna z Kiełpinka) wrzeszcz - stzyża - kiełpinek i z powrotem, zmieniając tor
# [[16,0],[17,0],[18,0],[29,0],[19,15],[22,0],[21,0],[26,0],[25,0],[30,0],[23,15],[30,0],[24,0],[26,0],[20,0],[8,0],[9,0],[12,15],[13,0],[14,0],[15,0],[16,15]]
#
# [[23,'t'],[16,'p']]
#
# wrzeszcz - osowa - wrzeszcz - kiełpinek - osowa - wrzeszcz
# [[6,0],[28,0],[7,0],[8,0],[9,1],[10,0],[11,15],[10,0],[9,0],[12,15],[13,0],[14,0],[15,0],[16,15],[17,0],[18,0],[29,0],[19,15],[22,0],[21,0],[26,0],[27,0],[28,0],[6,1],[28,0],[7,0],[8,0],[9,1],[10,0],[11,15],[10,0],[9,1],[8,0],[7,0],[28,0],[6,15]]
#
# [[6,'p'],[16,'t'],[9,'t'],[11,'p']]
#
# osowa - wrzeszcz - osowa
#
# [[1,0],[2,0],[3,15],[4,1],[5,0],[1,15]]
#
# [[1,'p'],[4,'t']]
#
# Listy zajętości stref
#
# 1-6 brak
# 7 [8,20]
# 8 [[9,12]]
# 9 [12]
# 10 [8]
# 11-13 brak
# 14 [[15,16]]
# 15 [16]
# 16,17 brak
# 18 [[29,19]]
# 19 brak
# 20 [8]
# 21 [26,24]
# 22 [21]
# 23 [30,24]
# 24 [26,21]
# 25 [30,23]
# 26 brak
# 27 brak
# 28 brak
# 29 [19]
# 30 brak
#
# Listy przejscia stref
# 1 brak
# 2 [[3, [27, False], [25, False]]]
# 3 [[4, [1, False]]]
# 4 [[5, [1, True]]]
# 5 [[1, [28, False], [27, True]]]
# 6 brak
# 7 [[8, [5, True], [4, False]]]
# 8 [[9,[4, False],[5, True]],[10,[4, True]]]
# 9 brak
# 10 [[11,[313, True]]]
# 11 brak
# 12 brak
# 13 brak
# 14 brak
# 15 [[16,[7,False], [9, False]]]
# 16 [[16,[9,True], [8,True]]]
# 17 brak
# 18 brak
# 19 brak
# 20 brak
# 21 [[26,[12,True]]]
# 22 brak
# 23 brak
# 24 [[26,[21,True]]]
# 25 [[30,[20,True]]]
# 26 [[20,[12, False],[15,False],[14,False],[13,True]],[25,[13,False]],[27,[13,True],[14,False],[15,True],[17,True],[16,False]]]
# 27 [[28,[22,True],[23,True],[24,True],[29,True]]]
# 28 [[7,[29,True],[24,False],[18,False]]]
# 29 brak
# 30 [[23,[33,False]],[24,[33,True],[32,False]]]

class Strefa():

    def __init__(self, nr, przejscia, zajetosci):
        self.przejscia = przejscia
        self.nr = nr
        self.zajetosci = zajetosci

class Pociag():

    def __init__(self, nr, trasa, zmiany):
        self.trasa = trasa
        self.nr = nr
        self.strefa = trasa[0]
        self.strefaNast = trasa[1]
        self.zmiany = zmiany
        self.kierunek = 'n'
        self.stopWhile = []
        for num, kier in self.zmiany:
            if num == self.strefa:
                self.kierunek = kier
        if self.kierunek == 'n':
            self.kierunek = 'p'
        self.indeksStrefy = 0

wymiarA = 4
wymiarB = 4

# punkty zmiany strefy - prosotkąty, po wjechaniu w które pociąg przechodzi do innej strefy
# lista jest zapisana w formacie [prostokąt, [dawna strefa, nowa strefa]]
# przejście nastąpi tylko jeśli nowa strefa jest następną na trasie pociągu
punktyZmianyStrefy = []
punktyZmianyStrefy.append([QtCore.QRect(1182, 13, wymiarA, wymiarB),[5,1]])
punktyZmianyStrefy.append([QtCore.QRect(1158, 13, wymiarA, wymiarB),[1,2]])
punktyZmianyStrefy.append([QtCore.QRect(5, 25, wymiarA, wymiarB),[3,4]])
punktyZmianyStrefy.append([QtCore.QRect(28, 19, wymiarA, wymiarB),[4,5]])
punktyZmianyStrefy.append([QtCore.QRect(63, 24, wymiarA, wymiarB),[2,3]])
punktyZmianyStrefy.append([QtCore.QRect(70, 50, wymiarA, wymiarB),[10,11]])
punktyZmianyStrefy.append([QtCore.QRect(708, 97, wymiarA, wymiarB),[10,8],[9,10]])
# punktyZmianyStrefy.append([QtCore.QRect(718, 85, wymiarA, wymiarB),[7,8]])
punktyZmianyStrefy.append([QtCore.QRect(712, 127, wymiarA, wymiarB),[7,8],[9,7]])
punktyZmianyStrefy.append([QtCore.QRect(740, 78, wymiarA, wymiarB),[22,21]])
punktyZmianyStrefy.append([QtCore.QRect(742, 68, wymiarA, wymiarB),[20,8]])
punktyZmianyStrefy.append([QtCore.QRect(808, 22, wymiarA, wymiarB),[28,7]])
punktyZmianyStrefy.append([QtCore.QRect(912, 50, wymiarA, wymiarB),[26,20]])
punktyZmianyStrefy.append([QtCore.QRect(815, 60, wymiarA, wymiarB),[21,26]])
punktyZmianyStrefy.append([QtCore.QRect(1078, 35, wymiarA, wymiarB),[26,25]])
punktyZmianyStrefy.append([QtCore.QRect(1112, 33, wymiarA, wymiarB),[25,30]])
punktyZmianyStrefy.append([QtCore.QRect(1003, 39, wymiarA, wymiarB),[26,27]])#zweryfikwoac
punktyZmianyStrefy.append([QtCore.QRect(1167, 18, wymiarA, wymiarB),[28,6]])
punktyZmianyStrefy.append([QtCore.QRect(1108, 19, wymiarA, wymiarB),[27,28]]) #zweryfikowac
punktyZmianyStrefy.append([QtCore.QRect(1122, 33, wymiarA, wymiarB),[30,24]])
# punktyZmianyStrefy.append([QtCore.QRect(1132, 43, wymiarA, wymiarB),[30,23]])#zweryfikowac
punktyZmianyStrefy.append([QtCore.QRect(1162, 33, wymiarA, wymiarB),[23,30]])
punktyZmianyStrefy.append([QtCore.QRect(1190, 33, wymiarA, wymiarB),[30,23]])
punktyZmianyStrefy.append([QtCore.QRect(713, 145, wymiarA, wymiarB),[8,9],[31, 9]])
punktyZmianyStrefy.append([QtCore.QRect(713, 138, wymiarA, wymiarB),[9,8]])
punktyZmianyStrefy.append([QtCore.QRect(727, 212, wymiarA, wymiarB),[9, 12]])
punktyZmianyStrefy.append([QtCore.QRect(721, 163, wymiarA, wymiarB),[19,22]])
punktyZmianyStrefy.append([QtCore.QRect(736, 235, wymiarA, wymiarB),[12,13]])
punktyZmianyStrefy.append([QtCore.QRect(742, 233, wymiarA, wymiarB),[29,19]])
punktyZmianyStrefy.append([QtCore.QRect(865, 425, wymiarA, wymiarB),[18,19]])
punktyZmianyStrefy.append([QtCore.QRect(957, 473, wymiarA, wymiarB),[17,18]])
punktyZmianyStrefy.append([QtCore.QRect(865, 425, wymiarA, wymiarB),[18,29]])
punktyZmianyStrefy.append([QtCore.QRect(948, 392, wymiarA, wymiarB),[13,14]])
punktyZmianyStrefy.append([QtCore.QRect(824, 480, wymiarA, wymiarB),[14,15]])
punktyZmianyStrefy.append([QtCore.QRect(697, 507, wymiarA, wymiarB),[16,17]])
punktyZmianyStrefy.append([QtCore.QRect(1065, 35, wymiarA, wymiarB),[24,26]])
punktyZmianyStrefy.append([QtCore.QRect(612, 508, wymiarA, wymiarB),[15,16]])
punktyZmianyStrefy.append([QtCore.QRect(623, 51, wymiarA, wymiarB),[11,31]])
punktyZmianyStrefy.append([QtCore.QRect(1162, 18, wymiarA, wymiarB),[6,28]])

stacje = []
stacje.append([QtCore.QRect(30,18,5,60),"Osowa1"])
stacje.append([QtCore.QRect(30,24,5,60),"Osowa2"])
stacje.append([QtCore.QRect(30,50,5,60),"Osowa3"])
stacje.append([QtCore.QRect(550,502,5,60),"Kielpinek1"])
stacje.append([QtCore.QRect(550,509,5,60),"Kielpinek2"])
stacje.append([QtCore.QRect(719,180,20,5),"Strzyza1"])
stacje.append([QtCore.QRect(724,198,20,5),"Strzyza1"])
stacje.append([QtCore.QRect(729,216,20,5),"Strzyza1"])
stacje.append([QtCore.QRect(729,180,20,5),"Strzyza2"])
stacje.append([QtCore.QRect(734,198,20,5),"Strzyza2"])
stacje.append([QtCore.QRect(739,216,20,5),"Strzyza2"])
stacje.append([QtCore.QRect(1172,13,5,20),"Wrzeszcz1"])
stacje.append([QtCore.QRect(1172,18,5,20),"Wrzeszcz2"])
stacje.append([QtCore.QRect(1175,42,5,20),"Wrzeszcz3"])

# lista stref
# strefy są obiektami klasy Strefa. Konstruktor strefy przyjmuje argumenty: numer strefy, lista przejść do kolejnych
# stref, lista do sprawdzenia zajętości
# lista przejść to lista list w następującym formacie [numer strefy następnej, [numer zwrotnicy, stan zwrotnicy]]
# opisuje konieczne ustawienia zwrotnic przy przejściu do kolejnych stref
# lista do sprawdzenia zajętości zawiera strefy, które należy sprawdzić pod względem zajętości. Jeśli któryś pociąg
# znajduje się w jednej z tych stref, to pociąg zatrzyma się i poczeka
# jeśli elementem listy zajętości jest lista oznacza to, że obydwie strefy muszą być zajęte, aby pociąg się zatrzymał

strefy = []
strefy.append(Strefa(1,[[2, [27, False], [25, False]]],[]))
strefy.append(Strefa(2,[[3, [27, False], [25, False]]],[]))
strefy.append(Strefa(3,[[4, [1, False]]],[]))
strefy.append(Strefa(4,[[5, [1, True]]],[]))
strefy.append(Strefa(5,[[1, [28, False], [27, True]]],[]))
strefy.append(Strefa(6,[],[]))
strefy.append(Strefa(7,[[8, [5, True], [4, False]]],[8,20,9,12]))
strefy.append(Strefa(8,[[7, [5, True], [4, False]], [9,[4, False],[5, False]]],[[9,12]]))
strefy.append(Strefa(9,[[10,[4, True]],[7, [5, True], [4, False]]],[12]))
strefy.append(Strefa(10,[[11,[3, True]]],[8]))
strefy.append(Strefa(11,[],[]))
strefy.append(Strefa(12,[],[]))
strefy.append(Strefa(13,[],[]))
strefy.append(Strefa(14,[],[[15,16]]))
strefy.append(Strefa(15,[[16,[7,False], [9, False]]],[16]))
strefy.append(Strefa(16,[[17,[9,True], [8,True]]],[]))
strefy.append(Strefa(17,[],[]))
strefy.append(Strefa(18,[],[[29,19]]))
strefy.append(Strefa(19,[],[]))
strefy.append(Strefa(20,[[8,[4, False],[5, False]]],[8,7,9,31]))
strefy.append(Strefa(21,[[26,[12,True]]],[26,24, 30, 25, 23]))
strefy.append(Strefa(22,[],[21]))
strefy.append(Strefa(23,[[30,[15,True]]],[30,24]))
strefy.append(Strefa(24,[[26,[17,False],[15,True],[14,False],[13,True],[12,False]]],[26]))
strefy.append(Strefa(25,[[30,[20,True]]],[30,23]))
strefy.append(Strefa(26,[[20,[12, False],[15,True],[17,False],[14,False],[13,True]],[25,[13,True],[14,False],[15,True],[21,True], [31, True]],[27,[13,True],[14,False],[15,True],[17,True],[16,False]]],[]))
strefy.append(Strefa(27,[[28,[22,True],[23,True],[24,True],[29,True]]],[]))
strefy.append(Strefa(28,[[7,[29,True],[24,False],[18,False]]],[]))
strefy.append(Strefa(29,[],[19]))
strefy.append(Strefa(30,[[23,[31,True]],[24,[31,True],[14,False]]],[]))
strefy.append(Strefa(31,[[9,[4,True]]],[8, 9, 12]))

# lista pociągów
# pociąg jest obietem klasy Pociąg. Jej konstruktor przyjmuje następujące argumenty:
# numer pociągu, trasę, listę zmian kierunku
# trasa to lista list o formacie [numer strefy, czas postoju] i zawiera kolejne wypisane strefy na trasie
# lista zmian kierunku zawiera listę list o formacie [numer strefy, kierunek opisany jako przód ('p') lub tył ('t')
# należy pamiętać, że ustawienie kierunku nastąpi tylko po zatrzymaniu pociągu, samo wjechanie do stefy nic nie zmieni
pociagi = []
pociagi.append(Pociag(0, [[23,0],[30,0],[24,0],[26,0],[20,0],[8,0],[9,0],[12,15],[13,0],[14,0],[15,0],[16,15],[17,0],[18,0],[29,0],[19,15],[22,0],[21,0],[26,0],[25,0],[30,0],[23,15]], [[23,'p'],[16,'t']]))
pociagi.append(Pociag(1, [[16,0],[17,0],[18,0],[29,0],[19,15],[22,0],[21,0],[26,0],[25,0],[30,0],[23,15],[30,0],[24,0],[26,0],[20,0],[8,0],[9,0],[12,15],[13,0],[14,0],[15,0],[16,15]], [[23,'t'],[16,'p']]))
# pociagi.append(Pociag(2, [[6,0],[28,0],[7,0],[8,0],[9,7],[10,0],[11,15],[31,0],[9,0],[12,15],[13,0],[14,0],[15,0],[16,15],[17,0],[18,0],[29,0],[19,15],[22,0],[21,0],[26,0],[27,0],[28,0],[6,7],[28,0],[7,0],[8,0],[9,7],[10,0],[11,15],[10,0],[8,0],[9,7],[8,0],[7,0],[28,0],[6,15]], [[6,'p'],[16,'t'],[9,'t'],[11,'p']]))
pociagi.append(Pociag(2, [[6,0],[28,0],[7,0],[8,0],[9,7],[10,0],[11,3600],[31,0],[9,7],[7,0],[28,0],[6,15]], [[6,'p'],[16,'t'],[9,'t'],[11,'p']]))
pociagi.append(Pociag(3, [[1,0],[2,0],[3,15],[4,7],[5,0],[1,15]], [[1,'p'],[4,'t']]))

speedP = [14, 11, 12, 14]
speedT = [14, 11, 12.5, 14]
speedWP = 0.1

def getStrefa(index):
    for strefa in strefy:
        if strefa.nr == index:
            return strefa
    return -1