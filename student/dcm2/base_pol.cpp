#include "vararray.h"
#include "base_pol.h"
#include <conio.h>

double **
Base_Poly::ajoute_suivant()
{
//   int new_deg = ((*this)[taille-1]).donne_degre()+1;
   static new_deg = 0;
   new_deg++;
   Polynome temp(new_deg),poly(new_deg);
   temp[temp.donne_degre()] = 1/pow(l,temp.donne_degre());
   Masses *msx;

   for (short i = 0; i<poly.donne_degre(); i++)
   {
      poly[i] = (m * temp * ((*this)[i])).integrale(0.0,l)
	      + (!m * temp * ((*this)[i])).integrale(-l,0.0);
      msx = MsX;
      while(msx->masse)
      {
	 poly[i] = poly[i] + msx->masse * temp(msx->x) * ((*this)[i](msx->x));
	 msx++;
      }
   }

   poly[poly.donne_degre()]= (m * temp * temp).integrale(0.0,l)
			   + (!m * temp * temp).integrale(-l,0.0);
   msx=MsX;
   while(msx->masse)
   {
      poly[poly.donne_degre()] += msx->masse * temp(msx->x) * temp(msx->x);
      msx++;
   }

   for(i=0; i<poly.donne_degre(); i++)
   {
      poly[poly.donne_degre()] -= poly[i] * poly[i];
      temp = temp - (poly[i] * (*this)[i]);
   }

   poly[poly.donne_degre()] = 1/sqrt(poly[poly.donne_degre()]);
   poly = poly[poly.donne_degre()] * temp;

   cout << " orth.(1->" << taille << "):";
   cout << "P=" << poly << '\n';

   (*this)[taille] = poly;
   if(poly.donne_degre()<2)
   {
      Polynome vide(0);
      ddBase[taille]=vide;
   }
   else
      ddBase[taille] = (poly.derive()).derive();

   cout << "TEST : ";
   for(i=0; i<=taille; i++)
   {
      double test;
      test = (m * poly * ((*this)[i])).integrale(0.0,l)
	   + (!m * poly * ((*this)[i])).integrale(-l,0.0);
      msx=MsX;
      while(msx->masse)
      {
	 test += msx->masse * ((*this)[i](msx->x)) * poly(msx->x);
	 msx++;
      }
      cout << test <<' ';
   }
   cout <<'\n';

   build_k();
   taille++;
   return K;
}

void Base_Poly::build_k()
{
   double **KK;
   KK = new double*[taille+1];
   KK[taille] = new double[taille+1];
   for (int j=0; j<taille; ++j)
   {
      KK[j] = new double[taille+1];
      for(int k=0; k<=j; ++k)
	 KK[j][k] = KK[k][j] = K[j][k];
      KK[taille][j] = KK[j][taille]
		    = (young * I * ddBase[taille] * ddBase[j]).integrale(0.0,l)
		    + (young * !I * ddBase[taille] * ddBase[j]).integrale(-l,0.0);
   }
   KK[taille][taille]
       = (young * I * ddBase[taille] * ddBase[taille]).integrale(0.0,l)
       + (young * !I * ddBase[taille] * ddBase[taille]).integrale(-l,0.0);

   for(j=0; j<taille; ++j)
      delete K[j];
   delete K;
   K=KK;
/* for(j=0;j<=taille; ++j)
   K[j]=KK[j];               */
}


ostream &operator << (ostream & outp,Base_Poly &bp)
{for (Base_Poly::indice i=0 ; i< bp.taille ; i++)
	outp << i <<":(�"<< bp[i].donne_degre() <<") = " << bp[i] <<'\n';
 return outp;
}

void Base_Poly::affiche_K(int dim)
{
   cout << "Matrice K:" << '\n';
   for(int i = 0; i<dim; i++)
   {
      for(int j = 0; j<dim; j++)
	cout << K[i][j] << '\t';
      cout << '\n';
   }
   cout << '\n';
}