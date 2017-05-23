/*
 * Splines cubiques de LITT
 */

#include "ehd.h"

#include "tdilib.h"

//#define STANDALONE

/*********************************************************************/

/*
 * Calcule un morceau de spline en n points x[0-(n-1)] 
 * si xi[0-1], yi[0-1], ki[0-1] sont connus
 * (renvoie y[0-(n-1)] et yp[0-(n-1)])
 */

int ehd_spline_seg(double *xi, double *yi, double *ki,
                   double *x, double *y, double *yp, int n)
{

    double ai, bi, hi, k2, hi2;
    int i;
    double t, t2, t3;

    // ctes du segment concerne
    bi = yi[0];
    hi = xi[1] - xi[0];
    ai = (yi[1] - yi[0]) / hi - hi / 6.0 * (ki[1] + 2.0 * ki[0]);

    k2 = ki[1] - ki[0];
    hi2 = hi * hi;

    for (i = 0; i < n; i++)
    {
        t = (x[i] - xi[0]) / hi;
        t2 = t * t;
        t3 = t2 * t;

        yp[i] = hi * ki[0] * t + hi * k2 * t2 / 2.0 + ai;

        y[i] = hi2 * ki[0] * t2 / 2.0 + hi2 * k2 * t3 / 6.0 + hi * ai * t + bi;
    }

    return 0;
}

/*********************************************************************/

/*
 * Evalue une spline en x et renvoie y (y=f(x)) et y' (derivee)
 *
 */

int ehd_spline_y(int nn, double *xi, double *yi, double *ki,
                 double x, double *y, double *yp)
{
    int iop = 0;
    int i;

    // recherche du morceau

    for (i = 0; i < nn - 1; i++)
        if (x >= xi[i] && x <= xi[i + 1])
            break;

    if (i == nn - 1)
        goto ERR1;

    // evaluation sur le segment 'i'

    iop = ehd_spline_seg(&(xi[i]), &(yi[i]), &(ki[i]),
                         &x, y, yp, 1);
    if (iop != 0)
        goto FIN;

FIN:
    if (iop > 900)
        printf("\n\t-->"__FILE__
               "\n");
    return iop;
ERR1:
    printf("\nerreur: evaluation hors de la spline !");
    iop = 990;
    goto FIN;
}

/*********************************************************************/

/*
 * Calcule les ki (derivees 2nd)
 *
 */

int ehd_spline_ki(S_TDIMAT *K, int nn, double *xi, double *yi, double *ki)
{
    int iop = 0;
    int i;
    double *rhs = (double *)malloc(nn * sizeof(double));

    double hi1, hi2, di1, di2;

    iop = tdi_setsize(K, nn);
    if (iop != 0)
        goto FIN;

    // assemblage

    iop = tdi_ass(K, 0, 0, 1.0);
    iop = tdi_ass(K, 0, 1, 0.0);
    if (iop != 0)
        goto FIN;

    rhs[0] = 0.0;

    for (i = 1; i < nn - 1; i++)
    {

        hi1 = xi[i] - xi[i - 1];
        hi2 = xi[i + 1] - xi[i];
        di1 = (yi[i] - yi[i - 1]) / hi1;
        di2 = (yi[i + 1] - yi[i]) / hi2;

        iop = tdi_ass(K, i, i - 1, hi1);
        iop = tdi_ass(K, i, i, 2.0 * (hi1 + hi2));
        iop = tdi_ass(K, i, i + 1, hi2);
        if (iop != 0)
            goto FIN;

        rhs[i] = 6.0 * (di2 - di1);
    }
    iop = tdi_ass(K, nn - 1, nn - 2, 0.0);
    iop = tdi_ass(K, nn - 1, nn - 1, 1.0);
    if (iop != 0)
        goto FIN;

    rhs[nn - 1] = 0.0;

    /*
  mlab_tdi("tri.m","",K,TDI_A,MLAB_NEW);
  mlab_vec("tri.m","rhs",rhs,nn,MLAB_OLD);
  */

    // resolution

    iop = tdi_solve(K, rhs, ki, TDI_DO_LU | TDI_DO_SUBST);
    tdi_print_err(stdout, iop);
    if (iop != 0)
        goto FIN;

    /***/

    free(rhs);

FIN:
    if (iop > 900)
        printf("\n\t-->"__FILE__
               "\n");
    return iop;
}

/*********************************************************************
 *                             ROUTINE DE TEST                         *
 *********************************************************************/

#ifdef STANDALONE

int main()
{
    int iop = 0;
    S_TDIMAT K;
    int nn = 10;
    double xi[nn], yi[nn], ki[nn];
    int i;
    double x, y, yp;
    FILE *fich;
    double dx = 0.01;

    double xx[10] = {0.0, 0.5, 1.5, 3.0, 4.2, 5.1, 7.0, 7.3, 8.0, 9.1};

    // init matrice tridiag

    iop = tdi_init(&K);
    if (iop != 0)
        goto FIN;

    iop = tdi_setname(&K, "K");
    if (iop != 0)
        goto FIN;

    // fichier resultat

    fich = fopen("spl.m", "w");
    if (fich == NULL)
    {
        printf("erreur fichier!\n");
        iop = 990;
        goto FIN;
    }

    for (i = 0; i < nn; i++)
    {
        xi[i] = (double)i;
        xi[i] = xx[i];
        yi[i] = (double)i;
        ki[i] = 0.0; // inutile
    }

    yi[1] = 4.0;
    yi[5] = -4.0;

    // calcul des derivees secondes (ki)

    iop = ehd_spline_ki(&K, nn, xi, yi, ki);
    if (iop != 0)
        goto FIN;

    // ecriture des poles + derivees

    for (i = 0; i < nn; i++)
    {
        fprintf(fich, "xi(%d)  = %E;\n", i + 1, xi[i]);
        fprintf(fich, "yi(%d)  = %E;\n", i + 1, yi[i]);
        fprintf(fich, "ki(%d)  = %E;\n", i + 1, ki[i]);
    }

    // evaluation sur l'ensemble de la courbe

    i = 0;
    for (x = xi[0]; x <= xi[nn - 1]; x += dx)
    {
        i++;
        iop = ehd_spline_y(nn, xi, yi, ki,
                           x, &y, &yp);
        if (iop != 0)
            goto FIN;

        fprintf(fich, "x(%d)  = %E;\n", i, x);
        fprintf(fich, "y(%d)  = %E;\n", i, y);
        fprintf(fich, "yp(%d) = %E;\n", i, yp);
    }

    // purge memoire du systeme tridiag

    iop = tdi_reinit(&K);
    if (iop != 0)
        goto FIN;

    // fermeture fichier

    fclose(fich);

FIN:
    if (iop > 900)
        printf("\n\t-->"__FILE__
               "\n");
    return iop;
}

#endif

/*********************************************************************/
