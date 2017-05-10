#ifndef CYLINDER_H
#define CYLINDER_H

#include "mailsph.h"
#include "Mesh.h"

class Cylinder : public Mesh
{
public:
    int cyl_creux;      // 1 si creux, 0 si plein
    double centre[3];   // centre

    double rint;        // rayon interne si creuse, demi-diagonale du cube central si pleine
    double rext;        // rayon externe
    double longext;     // longueur du cylindre
    int cyl_ouvert;     // 1 si ouvert, 0 si ferme
    double theta0;      // ouverture en degre si ouvert

    double vec1[3];     // position du premier noeud
    double norm[3];     // normale au plan de l arc
    double ext[3];      // direction extrusion

    int nbe;            // nombre d elements sur l arc d un m�ridien
    int nbc;            // nombre d elements sur l epaisseur
    int nbz;            // nombre d elements sur la hauteur

    int noe_ini;
    int maille_ini;
    int nocyl;




    Cylinder();

    void build();
private:
    void writemco(FILE *fp_out2, int type1, int noe_ini, int nbe2, int nbz, int nbc,  
                int mat1rig, int loi1rig, int mat2rig, int loi2rig, 
                int *liste, int ***tab, 
                int mat1def, int loi1def, int mat2def, int loi2def, 
                int cyl_ouvert, int type2 );
};

#endif