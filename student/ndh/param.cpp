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
#include "param.h"

//--------------------------------------------------------------------
// Routine d'introduction d'un float au clavier
//--------------------------------------------------------------------

void param(char *texte, float *par)
{
      char entree[20];
      float prm = 0.0;
      printf("  %s [%f] =", texte, *par);
      //gets(entree);
      sscanf(entree, "%f", &prm);
      if (fabs(prm) > 1E-10)
            *par = prm;
}

//--------------------------------------------------------------------
// Routine d'introduction d'un integer au clavier
//--------------------------------------------------------------------

void param2(char *texte, int *par)
{
      char entree[20];
      int prm = 0.0;
      printf("  %s [%d] =", texte, *par);
      //gets(entree);
      sscanf(entree, "%d", &prm);
      if (abs(prm) > 0)
            *par = prm;
}

//--------------------------------------------------------------------
// Routine de modification des param�tres
//--------------------------------------------------------------------

void input_data()
{
      void destroy_vectors(), create_vectors(), define_geometry();
      void param(char *, float *), param2(char *, int *), titre();
      char entree[20];
      int j;

      //clrscr();
      titre();
      param2("Probl�me (1=cercle,2=carr�,3=autre)", &probleme);
      param("Beta", &beta);
      param("k", &k);
      if (probleme == 1)
            param("Rayon", &R);
      else
            param("Cot�", &a);
      param2("Nbre d'�l�ments aux fronti�res", &N);
      if (probleme == 2) // Le nbre d'�l�m. doit �tre un multiple de 4.
      {
            j = N / 4;
            N = 4 * j;
      } // si le probl�me est le carr�.
      if (N < 2)
            N = 20;
      param2("Nbre de pas d'int�gration par �l�ment", &istep);
      if (istep < 2)
            istep = 5;
      if (probleme == 1)
            zoom = 200.0 / R;
      else
            zoom = 200.0 / a;
      param2("Type d'int�gration (1=trap�ze,2=Simpson,...,6=Weddle)", &ideg);
      if ((ideg < 1) || (ideg > 6))
            ideg = 1;
      j = istep / ideg;
      istep = j * ideg; // le nbre d'intervalles d'int�gr.
      if (istep == 0)
            istep = ideg; // doit �tre un mult. de 'ideg'.
      param2("Densit� de visualisation", &density);
      param2("Maillage (1=on 2=off)", &maillag);
      param2("White Bg (1=on 2=off)", &whitebg);

      // Re-dimensionement des tableaux:
      destroy_vectors();
      create_vectors();
      define_geometry();
}