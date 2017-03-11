#include "Global.h"
#include "OofelieMeshExporter.h"
#include "Mesh.h"

OofelieMeshExporter::OofelieMeshExporter(Mesh &_mesh) : MeshExporter(_mesh)
{
}

void
OofelieMeshExporter::writeHeader()
{
    fprintf(fich,"# fichier cr�e par \'genmai\'\n#\n");

    fprintf(fich,"Function int mydomain(Domain domain)\n{\n");

    fprintf(fich,"Refer nset(domain[NODESET_PO]);\n");
    fprintf(fich,"nset.build_hash();\n");
    fprintf(fich,"Refer eset(domain[ELEMSET_PO]);\n\n");
    fprintf(fich,"Refer gset(domain[GEOMETRY_PO][GROUPSET_PO]);\n\n");
    fprintf(fich,"int eltyp=Meta_gd_2D;\n");
}

void
OofelieMeshExporter::writeNodes()
{
    int i;
    fprintf(fich, "# Nodes\n");
    for(i=0; i<mesh.numberOfNodes(); i++) 
    {
        fprintf(fich,"nset.define(%d,%lf,%lf,0);\n",
            mesh.getNodeNumber(IntNumber(i)),mesh.getNodeX(i), mesh.getNodeY(i));
    }
}

void
OofelieMeshExporter::writeElements()
{
    int i;
    fprintf(fich, "# Elems\n");
    for(i=0; i<mesh.numberOfElements(); i++) {
        fprintf(fich,"eset.define(%d, eltyp, %d,%d,%d,%d);\n", 
            i+1, 
            mesh.getNodeNumber(mesh.getNodeNumberFromElement(i,0)),
            mesh.getNodeNumber(mesh.getNodeNumberFromElement(i,1)),
            mesh.getNodeNumber(mesh.getNodeNumberFromElement(i,2)),
            mesh.getNodeNumber(mesh.getNodeNumberFromElement(i,3))   );
    }
}

void
OofelieMeshExporter::writeContactElements()
{
    fprintf(fich, "# Contact group\n");
    fprintf(fich,"Group group1(1); gset.copy(group1);\n");
    fprintf(fich,"Refer g1(gset[1]);\n");

    int k;
    for(k=mesh.getFirstContactNode(); k<=mesh.getLastContactNode(); ++k)
    {
         fprintf(fich,"g1.add_node(%d);\n",mesh.getNodeNumber(IntNumber(k)));
    }
}

void
OofelieMeshExporter::writeFooter()
{
    fprintf(fich,"\nreturn 0\n};\n\n");
}

std::string 
OofelieMeshExporter::getFileExtension() const
{
    return ".e";
}

std::string 
OofelieMeshExporter::getName() const 
{ 
    return "Oofelie"; 
}
