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

#include "elmfr.h"

// VARIABLES GLOBALES! ------------------------

int N = 40;        // Nombre d'�l�ments fronti�res sur le contour.
int istep = 20;    // Nombre de pas d'int�gration sur un �l�ment.
int density = 15;  // Densit� de visualisation de la solution
                   // (nombre de mailles sur un rayon).
int d_old;         // Ancienne valeur de la densit� (utile pour
                   // d�truire correctement le tableau des T).
int range;         // Nbre de ray. sur lesquels la sol. est calcul�e.
int ideg = 1;      // Type d'int�gration de Newton-Cotes
                   // (1=trap�ze, 2=Simpson,...).
int type = 1;      // M�thode de calcul (1=full, 2=sym�trique).
int maillag = 1;   // 1=Dessine le maillage.
int probleme = 1;  // Type de probl�me (1=cercle, 2=carr�, 3=qcq.).
int whitebg = 1;   // 1=Fond blanc pour l'impression.
int cartesien = 0; // 1=maillage rectangulaire (density x density)
                   // (uniquement pour le carr�).
int calcul = 0;    // 1=calculs effectu�s.

clock_t time1 = 0, time2 = 0; // temps de d�but et de fin de calcul.

float xo = 220, yo = 240; // (x,y) de l'origine des axes absolus.
float zoom = 200.0 / 1.2; // Zoom de visualisation.
float *alpha;             // Vecteur temporaire [N].
float *xf, *yf;           // (x,y) des extr�mit�s des �l�ments [N+1].
float *xel, *yel;         // (x,y) des connecteurs [N].
float *xint, *yint;       // (x,y) des points d'int�gration [istep+1].
float *fct, *fct2;        // Valeurs des fonctions � int�grer [istep+1].
float *G1, *H1;           // Vect. auxilaires pour le calcul des T [N].
float *u;                 // Temp�tatures sur les �l�ments [N].
float *q;                 // Flux de chaleur sur les �l�ments [N].
float **G, **H;           // Matrices G et H [N,N].
float **T;                // Tableau des T calcul�es [density,range].
float beta = 80;          // Param�tre du probl�me.
float k = 400;            // Conductivit� thermique.
float R = 1.2;            // Rayon du cercle.
float a = 1.2;            // Longueur du c�t� du carr�.
float pi;                 // 3.141592.
float Tmin, Tmax;         // Valeurs min et max des T calcul�es.

// Coefficients de l'int�gration de Newton-Cotes:
float icoeff[6][7] = {{1, 1, 0, 0, 0, 0, 0},
                      {1, 4, 1, 0, 0, 0, 0},
                      {1, 3, 3, 1, 0, 0, 0},
                      {7, 32, 12, 32, 7, 0, 0},
                      {19, 75, 50, 50, 75, 19},
                      {41, 216, 27, 272, 27, 216, 41}};
float idiv[6] = {2, 6, 8, 90, 288, 840};

// ---------------------------------------------------








//--------------------------------------------------------------------
// Routine de d�finition de la g�om�trie :
//  Remplit les vecteurs xf,yf et xel,yel.
//  . si probleme=1 -> cr�ation d'un cercle.
//  . si probleme=2 -> cr�ation d'un carr�.
//--------------------------------------------------------------------

void define_geometry()
{
    int i, j;
    //void fillvector(float *, float, float, int);

    if (probleme == 1)
    {
        fillvector(alpha, 0.0, (2 * pi) / N, N + 1);
        for (i = 0; i < N + 1; i++)
        {
            xf[i] = R * cos(alpha[i]);
            yf[i] = R * sin(alpha[i]);
        }
    }
    else if (probleme == 2)
    {
        j = N / 4;
        N = 4 * j;
        fillvector(alpha, -a, (2 * a) / j, j + 1);
        for (i = 0; i <= j; i++)
        {
            xf[i] = a;
            yf[i] = alpha[i];
            xf[i + j] = alpha[j - i];
            yf[i + j] = a;
            xf[i + 2 * j] = -a;
            yf[i + 2 * j] = alpha[j - i];
            xf[i + 3 * j] = alpha[i];
            yf[i + 3 * j] = -a;
        }
    }
    for (i = 0; i < N; i++)
    {
        xel[i] = (xf[i] + xf[i + 1]) / 2;
        yel[i] = (yf[i] + yf[i + 1]) / 2;
    }
}

//--------------------------------------------------------------------
// Routine d'�valuation d'un �l�m. des matrices G et H.
//   .re�oit -les indices i et j de l'�l�m. � calculer.
//           -les coord. x,y de l'origine des axes.
//--------------------------------------------------------------------

void eval_GH(float *g, float *h, int i, int j, float x, float y)
{
    int t, tt;
    float dx, dy, dL, temp, r, nx, ny;
    //void fillvector(float *, float, float, int);

    if (j == i)
    { // terme diagonal -> on applique les formules sp�ciales.
        // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        dx = xf[i + 1] - xf[i];
        dy = yf[i + 1] - yf[i];
        dL = sqrt(dx * dx + dy * dy);
        *g = dL / (2 * pi) * (log(2 / dL) + 1);
        *h = 0.5;
    }
    else
    { // cas g�n�ral d'un terme non diagonal.
        // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        // calcul de la normale (norm�e) � l'�l�ment:
        nx = yf[j + 1] - yf[j];
        ny = xf[j] - xf[j + 1];
        temp = sqrt(nx * nx + ny * ny);
        nx = nx / temp;
        ny = ny / temp;

        // calcul des coord. des points d'int�gration (xint,yint):
        fillvector(xint, xf[j], (xf[j + 1] - xf[j]) / istep, istep + 1);
        fillvector(yint, yf[j], (yf[j + 1] - yf[j]) / istep, istep + 1);

        // �valuation des deux fonctions � int�grer sur l'�l�ment
        // et stockage des valeurs dans fct et fct2:
        for (t = 0; t < istep + 1; t++)
        {
            temp = sqrt((xint[t] - x) * (xint[t] - x) + (yint[t] - y) * (yint[t] - y));
            fct[t] = (log(1.0 / temp) / (2 * pi));
            fct2[t] = (-nx * (xint[t] - x) - ny * (yint[t] - y)) / (2 * pi * temp * temp);
        }

        // initialisation des �l�ments � calculer:
        *g = 0.0;
        *h = 0.0;

        // calcul de la longueur d'un pas d'int�gration:
        dx = xint[1] - xint[0];
        dy = yint[1] - yint[0];
        dL = sqrt(dx * dx + dy * dy);

        // int�gration de Newton-Cotes:
        for (t = 0; t < istep - ideg + 1; t += ideg)
            for (tt = 0; tt <= ideg; tt++)
            {
                *g = *g + fct[t + tt] * icoeff[ideg - 1][tt] / idiv[ideg - 1];
                *h = *h + fct2[t + tt] * icoeff[ideg - 1][tt] / idiv[ideg - 1];
            }
        *g = *g * dL * ideg;
        *h = *h * dL * ideg;
    }
}

//--------------------------------------------------------------------
// Routine d'�valuation des temp�ratures sur chaque �l�ment.
//--------------------------------------------------------------------

void eval_u()
{
    for (int i = 0; i < N; i++)
        u[i] = -beta / (2 * k) * (xel[i] * xel[i] + yel[i] * yel[i]);
}

//--------------------------------------------------------------------
// Routine de calcul des temp�tatures (remplissage du tableau T).
// (Cette routine r�soud le probl�me pos�)
//   .re�oit le 'type' de calculs � effectuer:
//         - type=1 : calculs sans tenir compte de la sym�trie.
//         - type=2 : calculs optimis�s compte tenu de la sym�trie.
//--------------------------------------------------------------------

void full_calcul()
{
    int i, j, i1, j1, t;
    float temp, r, xb, yb;
    /*
    void titre(), destroy_aux(), create_aux(), create_GH(), eval_u();
    void destroy_GH(), visu(), fillvector(float *, float, float, int);
    void gauss(int, float **, float *, float *);
    void mmv(int, float **, float *, float *);
    void eval_GH(float *, float *, int, int, float, float);
    void copy_block(float **, int, int, int, int, int);
*/

    //clrscr();
    titre();
    if (((probleme < 1) || (probleme > 2)) && (type == 2))
    { // Cas du probl�me qcq. avec calculs optimis�s.
        // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        std::cout << "\nPas de solution rapide pour un probl�me QCQ !\n<ESPACE>";
        //getch();
    }
    else
    {
        time1 = clock(); // on commence � compter le temps CPU.
        calcul = 1;      // le calcul va �tre effectu�.
        destroy_aux();   // lib�ration de la m�moire.
        std::cout << "\n\nCr�ation des matrices H et G...";
        create_GH();
        std::cout << "Ok\nCalcul des matrices H et G...";
        if (type == 1)
            // Cas du probl�me non optimis�:
            // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            for (i = 0; i < N; i++)
                for (j = 0; j < N; j++)
                    eval_GH(&(G[i][j]), &(H[i][j]), i, j, xel[i], yel[i]);
        else
        { // Cas du probl�me optimis�:
            // ~~~~~~~~~~~~~~~~~~~~~~~~~
            if (probleme == 1) // *** CERCLE ***
            {                  // Une seule ligne de H utile:            ******
                for (j = 0; j < N; j++)
                    eval_GH(&(G[0][j]), &(H[0][j]), 0, j, xel[0], yel[0]);
                // Utilisation de la sym. pour construire G:
                for (i = 1; i < N; i++)
                {
                    for (j = 0; j < i; j++)
                        G[i][j] = G[0][N - i + j];
                    for (j = i; j < N; j++)
                        G[i][j] = G[0][j - i];
                }
            }
            if (probleme == 2) // *** CARRE ***
            {
                t = N / 4; //     *****
                for (i = 0; i < t; i++)
                    for (j = 0; j < N; j++)
                        eval_GH(&(G[i][j]), &(H[i][j]), i, j, xel[i], yel[i]);
                for (i = 1; i < 4; i++)
                {
                    for (j = 0; j < i; j++)
                    {
                        copy_block(G, i * t, j * t, 0, (4 - i + j) * t, t);
                        copy_block(H, i * t, j * t, 0, (4 - i + j) * t, t);
                    }
                    for (j = i; j < 4; j++)
                    {
                        copy_block(G, i * t, j * t, 0, (j - i) * t, t);
                        copy_block(H, i * t, j * t, 0, (j - i) * t, t);
                    }
                }
            }
        }
        // Evaluation des T sur la fronti�re et r�solution du
        // syst�me par Gauss:
        std::cout << "Ok\nR�solution de G q = H u...";
        eval_u();
        if ((type == 2) && (probleme == 1)) // cas du cercle optimis�
        {
            temp = 0.0;
            for (j = 0; j < N; j++)
                temp = temp + H[0][j] * u[j];
            for (j = 0; j < N; j++)
                alpha[j] = temp;
        }
        else // cas g�n�ral
            mmv(N, H, u, alpha);
        gauss(N, G, q, alpha);

        // Lib�ration de la m�moire occup�e par les matrices G et H:
        std::cout << "Ok\nDestruction des matrices H et G...";
        destroy_GH();

        std::cout << "Ok\nCalcul des T int�rieures...";
        if ((probleme == 1) && (type == 2))
            range = 1;
        else if ((probleme == 2) && (type == 2))
            range = density;
        else
            range = N;
        if ((probleme == 2) && (type == 2))
            cartesien = 1;
        else
            cartesien = 0;
        create_aux();

        // Calcul des points xb,yb o� va �tre �valu�e la T.
        for (i1 = 0; i1 < density; i1++)
            for (j1 = 0; j1 < range; j1++)
            {
                if ((probleme == 1) && (type == 2))
                {
                    xb = R / (density)*i1;
                    yb = 0.0;
                }
                else if ((probleme == 2) && (type == 2))
                {
                    xb = a / density * i1;
                    yb = a / range * j1;
                }
                else
                {
                    xb = xel[j1] / density * i1 + (xel[j1] / density) / 2.0;
                    yb = yel[j1] / density * i1 + (yel[j1] / density) / 2.0;
                }
                for (j = 0; j < N; j++)
                    eval_GH(&(G1[j]), &(H1[j]), j - 1, j, xb, yb);
                // Calcul de la solution du probl�me de Poisson
                temp = 0.0;
                for (j = 0; j < N; j++)
                    temp = temp + G1[j] * q[j] - H1[j] * u[j];
                // Calcul de la solution du probl�me pos�
                r = sqrt(xb * xb + yb * yb);
                T[i1][j1] = temp + beta / (2 * k) * r * r;
            }

        time2 = clock(); // les calculs sont termin�s !

        // Affichage de la solution
        std::cout << "Ok\nSolution :";
        for (i = 0; i < density; i++)
            std::cout << "\n"  << T[i][0];

        // Visualisation graphique:
        std::cout << "\n       <SPACE> pour solution graphique";
        //getch();
        visu();
    }
}

//--------------------------------------------------------------------
// Routine de calcul des temp�tatures exactes (dans le tableau T).
//--------------------------------------------------------------------

void eval_Texact()
{
    //void titre(), visu(), find_minmax();
    int i1, j1, i;
    float temp, xb, yb, r;

    //clrscr();
    titre();
    if ((probleme < 1) || (probleme > 2))
        std::cout << "\n\nPas de solution exacte disponible !";
    else
    {
        time1 = clock(); // d�but des calculs.
        calcul = 1;
        for (i1 = 0; i1 < density; i1++)
            for (j1 = 0; j1 < range; j1++)
            {
                if ((probleme == 1) && (range == 1))
                {
                    xb = R / (density)*i1;
                    yb = 0.0;
                }
                else if ((probleme == 2) && (cartesien == 1))
                {
                    xb = a / density * i1;
                    yb = a / range * j1;
                }
                else
                {
                    xb = xel[j1] / density * i1 + (xel[j1] / density) / 2.0;
                    yb = yel[j1] / density * i1 + (yel[j1] / density) / 2.0;
                }
                r = sqrt(xb * xb + yb * yb);
                if (probleme == 1)
                    T[i1][j1] = beta / (2 * k) * (r * r - R * R);
                if (probleme == 2)
                {
                    temp = 0.0;
                    for (i = 1; i < 100; i += 2)
                        temp = temp + (1.0 / (i * i * i)) * pow(-1.0, (i - 1) / 2.0) * (1 - cosh((i * pi * yb) / (2.0 * a)) / cosh((i * pi) / 2.0)) * cos((i * pi * xb) / (2.0 * a));
                    T[i1][j1] = -32 * beta * a * a / (pi * pi * pi * k) * temp;
                }
            }
        time2 = clock();
        find_minmax();
        std::cout << "\nCalcul effectu�\n<ESPACE> pour voir la solution...";
        //getch();
        visu(); // Visualisation graphique des r�sultats.
    }
}

//--------------------------------------------------------------------
//  Proc�dure main() : boucle principale
//--------------------------------------------------------------------

void main()
{
    // Initialisation des variables
    // ----------------------------
    char entree[20];
    int i, j, t, i1, j1, prm, exit = 0, choix;

    float nx, ny, temp, dL, dx, dy, r;
    /*
    void tester(), create_vectors(), define_geometry(), titre();
    void full_calcul(), input_data(), load_data(), visu();
    void eval_Texact(), save_Mfile();*/

    // Initialisation
    // --------------
    pi = 4 * atan(1);
    d_old = density;
    range = N;

    create_vectors();
    define_geometry();

    // Menu
    // ----

    while (exit == 0)
    {
        //clrscr();
        titre();
        std::cout << "\n\nProbl�me courant :";
        if (probleme == 1)
            std::cout << " CERCLE de rayon a";
        else if (probleme == 2)
            std::cout << " CARRE de c�t� a";
        else
            std::cout << "QUELCONQUE";
        std::cout << "\n\n\t [1]  Lancer le calcul complet.";
        std::cout << "\n\t [2]  Lancer le calcul rapide.";
        std::cout << "\n\t [3]  Param�tres.";
        std::cout << "\n\t [4]  Charger fichier donn�es.";
        std::cout << "\n\t [5]  Visualisation graphique.";
        std::cout << "\n\t [6]  Evaluation de la solution analytique.";
        std::cout << "\n\t [7]  Sauvegarde vers MATLAB";
        std::cout << "\n\t [0]  Quitter.";
        std::cout << "\n\nChoix \?";
        std::cout << "\n\n\n\nFLOPS     : non disponible";
        std::cout << "\nTemps CPU : " << (double)(time2 - time1) / CLK_TCK << " sec.";
        choix = 1; //getch();
        switch (choix)
        {
        case '1':
        {
            type = 1;
            full_calcul();
        }
        break;
        case '2':
        {
            type = 2;
            full_calcul();
        }
        break;
        case '3':
            input_data();
            break;
        case '4':
            load_data();
            break;
        case '5':
            visu();
            break;
        case '6':
            eval_Texact();
            break;
        case '7':
            save_Mfile();
            break;
        case '0':
            exit = 1;
            break;
        }
    }
    //clrscr();
}

//--------------------------------------------------------------------
// Routine de g�n�ration d'une g�om�trie donn�e et sauvegarde
// dans un fichier *.DAT
//--------------------------------------------------------------------

//void tester()
void generate()
{
    int i;
    char nom_fich[50];
    /*
    void fillvector(float *, float, float, int);
    void create_vectors(), visu();
    */
    R = 1;
    N = 50;
    zoom = 200.0 / R;
    pi = 4 * atan(1);
    range = N;
    probleme = 3;
    create_vectors();

    // G�n�ration:
    fillvector(alpha, 0.0, (2 * pi) / N, N + 1);
    for (i = 0; i < N + 1; i++)
    {
        xf[i] = (R - 0.2 + 0.2 * cos(3 * alpha[i])) * cos(alpha[i]);
        yf[i] = (R - 0.2 + 0.2 * cos(3 * alpha[i]) * 0.01 * (-alpha[i] * alpha[i] * alpha[i] + 2 * pi)) * sin(alpha[i]);
    }
    for (i = 0; i < N; i++)
    {
        xel[i] = (xf[i] + xf[i + 1]) / 2;
        yel[i] = (yf[i] + yf[i + 1]) / 2;
    }
    // Sortie vers fichier.DAT
    std::cout << "\nNom du fichier (.DAT) :";
    //gets(nom_fich);
    std::ofstream fich(nom_fich, std::ios::out);
    fich << N;
    fich << "\n"
         << zoom;
    for (i = 0; i <= N; i++)
    {
        fich << "\n"
             << xf[i];
        fich << "\n"
             << yf[i];
    }
    fich.close();
    calcul = 0;
    visu();
}



