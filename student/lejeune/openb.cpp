#include <math.h>
#include <iostream.h>
#include <fstream.h>

double Q0 = 0.1, // d�bit initial
	H0 = 50,	 // hauteur manom�trique initiale
	Hs = 70,	 // hauteur manom�trique � d�bit nul
	D = 0.25,	// diam�tre de la conduite
	L = 400,	 // longueur de la conduite
	a1 = 0,		 // cte pompe
	a = 1200,	// c�l�rit� de l'onde
	f = 0.02,	// coefficient de frottement
	tau = 2.5;   // param�tre d'ouverture de vanne

int div = 15,   // nbre de tron�ons de la conduite
	tmax = 170; // nbre de pas de temps

double a2 = (H0 - Hs - a1 * Q0) / (pow(Q0, 2)), // cte pompe
	Section = M_PI * pow(D, 2) / 4,
	   g = 9.81,
	   B = a / (g * Section),							 // voir rappel
	R = f * (L / div) / (2 * g * D * pow(Section, 2)),   //  th�orique
	C1 = f * pow(Q0, 2) / (2 * g * D * pow(Section, 2)), // pertes de charge
	Cv = pow(Q0 * tau, 2) / (2 * (H0 - C1 * L));		 // cte vanne

double **Q, **H;
double CM, CP, rho;

ofstream sortie("OPENB.M", ios::out); // ouverture fichier MatLab

void main()
{
	Q = new double *[div + 1]; // d�claration des tableaux
	H = new double *[div + 1]; // de d�bit et de charge
	for (int i = 0; i <= div; i++)
	{
		Q[i] = new double[tmax];
		H[i] = new double[tmax];
	}
	for (i = 0; i <= div; i++) // conditions initiales
	{
		Q[i][0] = Q0;
		H[i][0] = H0 - C1 * i * L / div;
	}
	for (int k = 1; k < tmax; k++)
	{
		// condition limite � la pompe

		CM = H[1][k - 1] - B * Q[1][k - 1] + R * Q[1][k - 1] * abs(Q[1][k - 1]);

		// choix du bon d�bit (fct. du signe de a2)

		rho = sqrt(pow(B - a1, 2) + 4 * a2 * (CM - Hs));
		if (a2 > 0)
			Q[0][k] = (B - a1 + rho) / (2 * a2);
		else
			Q[0][k] = (B - a1 - rho) / (2 * a2);

		H[0][k] = Hs + Q[0][k] * (a1 + a2 * Q[0][k]);

		// calcul des points interm�diaires

		for (i = 1; i < div; i++)
		{
			CP = H[i - 1][k - 1] + B * Q[i - 1][k - 1] + R * Q[i - 1][k - 1] * abs(Q[i - 1][k - 1]);
			CM = H[i + 1][k - 1] - B * Q[i + 1][k - 1] - R * Q[i + 1][k - 1] * abs(Q[i + 1][k - 1]);
			Q[i][k] = (CP - CM) / (2 * B);
			H[i][k] = (CP + CM) / 2;
		}

		// condition limite � la vanne

		CP = H[div - 1][k - 1] + B * Q[div - 1][k - 1] - R * Q[div - 1][k - 1] * abs(Q[div - 1][k - 1]);
		Q[div][k] = -B * Cv + sqrt(pow(B * Cv, 2) + 2 * Cv * CP);
		H[div][k] = CP - B * Q[div][k];
	}

	for (int j = 0; j < tmax; j++) // Transfert vers MatLab
	{
		for (int i = 0; i <= div; i++)
		{
			sortie << "H(" << i + 1 << "," << j + 1 << ")=" << H[i][j] << ";";
			sortie << "Q(" << i + 1 << "," << j + 1 << ")=" << Q[i][j] << ";\n";
		}
		sortie << "t(" << j + 1 << ")=" << j * (L / (div * a)) << ";\n";
	}
	for (i = 0; i <= div; i++)
		sortie << "x(" << i + 1 << ")=" << i * L / div << ";\n";
	sortie << "figure(1); plot(t,H(" << div + 1 << ",:)); grid\n";
	sortie << "  title('Charge a la vanne'), xlabel('t [s]'),";
	sortie << "  ylabel('Hv [m]')\n";
	sortie << "figure(2); plot(t,Q(1,:)); grid\n";
	sortie << "  title('Debit a la pompe'), xlabel('t [s]'),";
	sortie << "  ylabel('Qp [m^3/s]')\n";
	sortie << "figure(3); mesh(t,x,Q); grid\n";
	sortie << "  title('Debit'), xlabel('t [s]'), ylabel(' x [m]'),";
	sortie << "  zlabel('Q [m^3/s]')\n";
	sortie << "figure(4); mesh(t,x,H); grid\n";
	sortie << "  title('Charge'), xlabel('t [s]'), ylabel('x [m]'),";
	sortie << "  zlabel('H [m]'),view(10,40)\n";

	sortie.close();
}