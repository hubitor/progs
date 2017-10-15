//   Copyright 1996-2017 Romain Boman
//
//   Licensed under the Apache License, Version 2.0 (the "License");
//   you may not use this file except in compliance with the License.
//   You may obtain a copy of the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
//   Unless required by applicable law or agreed to in writing, software
//   distributed under the License is distributed on an "AS IS" BASIS,
//   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//   See the License for the specific language governing permissions and
//   limitations under the License.

#ifndef ELMFR_H
#define ELMFR_H

#include <cmath>
#include <iostream>
#include <fstream>
#include <string>
#include <time.h>

#include "graph.h"
#include "iofun.h"
#include "matfun.h"
#include "memory.h"
#include "param.h"


class Ndh
{


    int N;                   // Nombre d'�l�ments fronti�res sur le contour.
    int istep;               // Nombre de pas d'int�gration sur un �l�ment.
    int density;             // Densit� de visualisation de la solution
                                    // (nombre de mailles sur un rayon).
    int d_old;               // Ancienne valeur de la densit� (utile pour
                                    // d�truire correctement le tableau des T).
    int range;               // Nbre de ray. sur lesquels la sol. est calcul�e.
    int ideg;                // Type d'int�gration de Newton-Cotes
                                    // (1=trap�ze, 2=Simpson,...).
public:
    int type;                // M�thode de calcul (1=full, 2=sym�trique).
    int probleme;            // Type de probl�me (1=cercle, 2=carr�, 3=qcq.).
private:
    int maillag;             // 1=Dessine le maillage.
    int whitebg;             // 1=Fond blanc pour l'impression.
    int cartesien;           // 1=maillage rectangulaire (density x density)
                                    // (uniquement pour le carr�).
    int calcul;              // 1=calculs effectu�s.

    clock_t time1, time2;    // temps de d�but et de fin de calcul.

    double xo, yo;           // (x,y) de l'origine des axes absolus.
    double zoom;             // Zoom de visualisation.
    double *alpha;           // Vecteur temporaire [N].
    double *xf, *yf;         // (x,y) des extr�mit�s des �l�ments [N+1].
    double *xel, *yel;       // (x,y) des connecteurs [N].
    double *xint, *yint;     // (x,y) des points d'int�gration [istep+1].
    double *fct, *fct2;      // Valeurs des fonctions � int�grer [istep+1].
    double *G1, *H1;         // Vect. auxilaires pour le calcul des T [N].
    double *u;               // Temp�tatures sur les �l�ments [N].
    double *q;               // Flux de chaleur sur les �l�ments [N].
    double **G, **H;         // Matrices G et H [N,N].
    double **T;              // Tableau des T calcul�es [density,range].
    double beta;             // Param�tre du probl�me.
    double k;                // Conductivit� thermique.
    double R;                // Rayon du cercle.
    double a;                // Longueur du c�t� du carr�.
    double pi;               // 3.141592.
    double Tmin, Tmax;       // Valeurs min et max des T calcul�es.

    // Coefficients de l'int�gration de Newton-Cotes:
    double icoeff[6][7]= {{1, 1, 0, 0, 0, 0, 0},
                            {1, 4, 1, 0, 0, 0, 0},
                            {1, 3, 3, 1, 0, 0, 0},
                            {7, 32, 12, 32, 7, 0, 0},
                            {19, 75, 50, 50, 75, 19},
                            {41, 216, 27, 272, 27, 216, 41}};
    double idiv[6] = {2, 6, 8, 90, 288, 840};

public:
    Ndh();

    // protos 

    void define_geometry();
    void eval_GH(double *g, double *h, int i, int j, double x, double y);
    void eval_u();
    void full_calcul();
    void eval_Texact();
    void generate();   //void tester()

    void create_vectors();
private:
    void create_aux();
    void create_GH();

    void destroy_aux();
    void destroy_GH();
    void destroy_vectors();

public:
    void input_data();

    void load_data();
    void save_Mfile();

    void find_minmax();

};


void clrscr();


#endif //ELMFR_H

