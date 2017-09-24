//   Copyright 2017 Romain Boman
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

#include <fstream>
#include <cmath>
#include "Polynome.h"

extern int compt, nopoly;
extern Polynome *MP;
extern double *Moment, *Tranchant, **MODES, *XX;
extern double enverg, Nmodes, Nperiod, T, F0, np, np2;

void C_to_Matlab_1(double *ValP, double **VectP, int n)
{
    std::ofstream fich("vpvp.m", std::ios::out);
    fich << "vap=[";
    for (int i = 1; i <= n - 1; i++)
        fich << sqrt(ValP[i]) << ",...\n ";
    fich << sqrt(ValP[n]) << "];\n\nvep=[";
    for (int i = 1; i <= n; i++)
    {
        fich << "[";
        for (int j = 1; j <= n - 1; j++)
            fich << VectP[i][j] << ",...\n ";
        fich << VectP[i][n] << "]\n";
    }
    fich << "];";
    fich.close();
    std::cout << "vpvp.m cree.\n";
}

void C_to_Matlab_2()
{
    std::ofstream fich("graphe.m", std::ios::out);
    fich << "x=["; // Vecteur abcisse  : x
    for (int i = 0; i < np; i++)
        fich << XX[i] << ",...\n ";
    fich << XX[(int)np] << "];\n\ngrafic=[";
    for (int i = 0; i < Nmodes; i++) // Matrice Yi(x)    : grafic
    {
        fich << "[";
        for (int j = 0; j < np; j++)
            fich << MODES[i][j] << ",...\n ";
        fich << MODES[i][(int)np] << "];\n";
    }
    fich << "];\n\nyo=[";
    for (int j = 0; j < Nmodes; j++) // Valeurs de Yi(0);
        fich << MP[j](0.0) << ",...\n ";
    fich << MP[(int)Nmodes](0.0) << "];\n";
    fich << "\nnp=" << np << ";\n";
    fich << "np2=" << np2 << ";\n";
    fich << "NPERIOD=" << Nperiod << ";\n";
    fich << "T=" << T << ";\n";
    fich << "F0=" << F0 << ";\n";
    fich << "NMOD=" << Nmodes - 1 << ";\n";
    fich << "\ngrafic=grafic'; x=x';\n"; // Commandes de trac�.
    fich << "figure;\n";
    fich << "v=[-" << enverg << "," << enverg << ",-0.04,0.04]; axis(v);\n";
    fich << "plot(x,grafic,'k');\n";
    fich << "title('Modes propres (normes)');\n";
    fich << "xlabel('x');\nylabel('Yi(x)');\n";
    fich.close();
    std::cout << "graphe.m cree.\n";
}

void C_to_Matlab_3()
{
    std::ofstream fich2("mt.m", std::ios::out);
    fich2 << "M=[";
    for (int i = 0; i < compt - 1; i++)
        fich2 << Moment[i] << ",...\n";
    fich2 << Moment[compt - 1] << "];\n\nET=[";
    for (int i = 0; i < compt - 1; i++)
        fich2 << Tranchant[i] << ",...\n";
    fich2 << Tranchant[compt - 1] << "];\n";
    fich2 << "figure;\n";
    fich2 << "plot(0:T/np2:NPERIOD*T,M,'k',0:T/np2:NPERIOD*T,ET,'k');\n";
    fich2 << "%gtext('M(t)');\n";
    fich2 << "%gtext('T(t)');\n";
    fich2 << "grid;\n";
    fich2 << "title(' Moment et effort tranchant a l'' emplanture de l'' aile');\n";
    fich2 << "xlabel('temps');\nylabel('M(t) & T(t) en x=0');\n";
    fich2.close();
    std::cout << "mt.m cree.\n";
}

